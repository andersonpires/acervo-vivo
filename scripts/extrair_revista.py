"""Extrai o texto de uma Revista Iteva em PDF para Markdown.

Uso:
    python -I scripts/extrair_revista.py acervo/revistas/revista2016.pdf acervo/texto

Gera, na pasta de saída:
    <nome>.md      texto em português, com marcador de página
    <nome>.en.md   texto em inglês (só nas edições bilíngues)
    <nome>.log     decisões que merecem conferência humana

O PDF original nunca é alterado: é aberto só para leitura.

O que o script trata:
    - cabeçalho repetido ("10 ITEVA 2016") e número de página;
    - ordem de leitura por colunas;
    - capitular (letra grande separada do resto da palavra);
    - hifenização: hífen invisível (U+00AD) e hífen comum em fim de linha;
    - legendas e destaques, separados do corpo;
    - idioma, por bloco, nas edições bilíngues.
"""

import collections
import json
import re
import sys
from pathlib import Path

import pymupdf

HIFEN_INVISIVEL = chr(0xAD)
ACENTOS_PT = set("ãõçáéíóúâêôàÃÕÇÁÉÍÓÚÂÊÔÀ")
PALAVRAS_EN = set(
    "the and of to in is for with which that are was by its from has have "
    "this it on at an be their were who through our we they been".split()
)
PALAVRAS_PT = set(
    "de da do que com para em os uma um no na dos das pelo pela são foi é "
    "ao à se mais não por seu sua como também nos nas".split()
)
CABECALHO = re.compile(r"^\s*(\d{1,3}\s+)?(ITEVA|Projeto\s+M[ií]dia\s*COM|REVISTA)\s+20\d\d(\s+\d{1,3})?\s*$", re.I)
SO_NUMERO = re.compile(r"^\s*\d{1,3}\s*$")
FIM_DE_FRASE = re.compile(r"[.!?:;…\"”)]\s*$")


def palavras(texto):
    return re.findall(r"[A-Za-zÀ-ú]+", texto.lower())


def idioma(texto, tamanho, tamanho_en, lexico=None):
    """'pt', 'en' ou None (sem pista).

    Ordem das pistas: palavras funcionais e acento; depois o léxico próprio
    de cada idioma na edição (montado dos parágrafos longos); por fim o corpo
    da letra. O corpo sozinho não serve: o inglês de 2016 vai de 7,4 a 15 pt.
    """
    ws = palavras(texto)
    # Acento em nome próprio ("Perpétua Araújo, 18 years old") não é pista de idioma.
    acentos = sum(c in ACENTOS_PT for w in re.findall(r"[A-Za-zÀ-ú]+", texto) if w[0].islower() for c in w)
    en = sum(w in PALAVRAS_EN for w in ws)
    pt = sum(w in PALAVRAS_PT for w in ws) + 2 * acentos
    if en >= 2 and en > pt:
        return "en"
    if pt >= 2 and pt > en:
        return "pt"
    if lexico:
        so_en = en + sum(w in lexico["en"] and w not in lexico["pt"] for w in ws)
        so_pt = pt + sum(w in lexico["pt"] and w not in lexico["en"] for w in ws)
        if so_en > so_pt:
            return "en"
        if so_pt > so_en:
            return "pt"
    if tamanho_en and abs(tamanho - tamanho_en) < 0.3 and acentos == 0 and ws:
        return "en"
    return None


def separar_idiomas(bloco, tamanho_en, lexico):
    """Divide um bloco em trechos de um idioma só.

    Há blocos mistos: "Evento de abertura do projeto" e "Project launch event"
    na mesma caixa, ou o cargo em inglês colado ao depoimento em português.
    """
    texto_bloco = " ".join(l["texto"] for l in bloco["linhas"])
    geral = idioma(texto_bloco, bloco["tamanho"], tamanho_en, lexico) or "pt"
    rotulos = [idioma(l["texto"], l["tamanho"], tamanho_en, lexico) or geral for l in bloco["linhas"]]
    trechos = []
    for ln, lg in zip(bloco["linhas"], rotulos):
        if trechos and trechos[-1][0] == lg:
            trechos[-1][1].append(ln)
        else:
            trechos.append((lg, [ln]))
    saida = []
    for lg, linhas in trechos:
        x0 = min(l["bbox"][0] for l in linhas)
        y0 = min(l["bbox"][1] for l in linhas)
        x1 = max(l["bbox"][2] for l in linhas)
        y1 = max(l["bbox"][3] for l in linhas)
        saida.append((lg, dict(bloco, linhas=linhas, bbox=(x0, y0, x1, y1))))
    return saida


def ler_blocos(pagina):
    """Blocos de texto com linhas, posição e corpo de letra predominante."""
    blocos = []
    for b in pagina.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        linhas = []
        for ln in b["lines"]:
            texto = "".join(s["text"] for s in ln["spans"])
            # Texto em curva ou girado (selo da p. 20 de 2023) sai letra a letra,
            # fora de ordem: não entra no corpo.
            if abs(ln["dir"][1]) > 0.2 or (len(texto.strip()) == 1 and abs(ln["dir"][1]) > 0.03):
                continue
            # Efeito de sombra: a mesma linha desenhada duas vezes no mesmo lugar.
            if any(l["texto"] == texto and abs(l["bbox"][1] - ln["bbox"][1]) < 4 for l in linhas):
                continue
            if texto.strip():
                linhas.append({"texto": texto, "bbox": ln["bbox"], "tamanho": max(round(s["size"], 1) for s in ln["spans"])})
        if not linhas:
            continue
        pesos = collections.Counter()
        fontes = collections.Counter()
        for ln in b["lines"]:
            for s in ln["spans"]:
                pesos[round(s["size"], 1)] += len(s["text"].strip())
                fontes[s["font"]] += len(s["text"].strip())
        blocos.append({
            "bbox": b["bbox"],
            "linhas": linhas,
            "tamanho": pesos.most_common(1)[0][0],
            "fonte": fontes.most_common(1)[0][0],
        })
    return blocos


def unir_linhas(linhas, largura, vocab, log, onde):
    """Junta as linhas de um bloco num parágrafo, desfazendo a hifenização."""
    # Bloco de linhas curtas sem pontuação final: lista de nomes, créditos, contatos.
    # Cada linha é um item e não pode ser colada na seguinte.
    lista = len(linhas) > 1 and all(
        len(l["texto"].strip()) < 35 and not FIM_DE_FRASE.search(l["texto"]) and not l["texto"].rstrip().endswith(("-", HIFEN_INVISIVEL))
        for l in linhas
    )
    if lista:
        return "\n".join(re.sub(r"[ \t]+", " ", l["texto"]).strip() for l in linhas)
    texto = ""
    for i, ln in enumerate(linhas):
        t = ln["texto"].strip()
        if i == 0:
            texto = t
            continue
        anterior = texto
        if anterior.endswith(HIFEN_INVISIVEL):
            texto = anterior[:-1] + t
        elif anterior.endswith("-") and (t[:1].islower() or (anterior[-2:-1].isupper() and t[:1].isupper())):
            texto = juntar_hifen(anterior, t, vocab, log, onde)
        else:
            ln_ant = linhas[i - 1]
            larg_ant = ln_ant["bbox"][2] - ln_ant["bbox"][0]
            curta = larg_ant < 0.6 * largura
            # Linha curta seguida de maiúscula sem pontuação: lista, nomes, créditos.
            if curta and t[:1].isupper() and not FIM_DE_FRASE.search(anterior):
                texto = anterior + "\n" + t
            else:
                texto = anterior + " " + t
    texto = texto.replace(HIFEN_INVISIVEL, "")
    return re.sub(r"[ \t]+", " ", texto).strip()


def juntar_hifen(anterior, seguinte, vocab, log, onde):
    """'for-' + 'mações' vira 'formações'; 'mesas-' + 'redondas' continua composto."""
    m1 = re.search(r"([A-Za-zÀ-ú]+)-$", anterior)
    m2 = re.match(r"([A-Za-zÀ-ú]+)", seguinte)
    if not (m1 and m2):
        return anterior + seguinte
    a, b = m1.group(1), m2.group(1)
    composto = f"{a}-{b}".lower()
    colado = f"{a}{b}".lower()
    if composto in vocab["compostos"] and colado not in vocab["simples"]:
        log.append(f"{onde}: mantido o hífen em '{a}-{b}' (a forma composta aparece no meio de linha)")
        return anterior + seguinte
    # Só merece olho humano quando as duas metades existem sozinhas ("volta-da"):
    # aí tanto pode ser palavra partida quanto composto.
    if colado not in vocab["simples"] and a.lower() in vocab["simples"] and b.lower() in vocab["simples"]:
        log.append(f"{onde}: hífen de fim de linha removido, conferir: '{a}-{b}' virou '{a}{b}'")
    return anterior[:-1] + seguinte


def vocabulario(doc):
    """Palavras e compostos que aparecem inteiros, no meio de linha, em toda a edição."""
    simples, compostos = set(), set()
    for pagina in doc:
        for ln in pagina.get_text().splitlines():
            ln = ln.replace(HIFEN_INVISIVEL, "").rstrip()
            ln = re.sub(r"\S+-$", "", ln)
            for w in re.findall(r"[A-Za-zÀ-ú]+(?:-[A-Za-zÀ-ú]+)*", ln):
                (compostos if "-" in w else simples).add(w.lower())
    return {"simples": simples, "compostos": compostos}


def colunas(blocos):
    """Ordem de leitura: colunas da esquerda para a direita, cada uma de cima para baixo."""
    grupos = []
    for b in sorted(blocos, key=lambda b: b["bbox"][0]):
        for g in grupos:
            if abs(g["x"] - b["bbox"][0]) < 18:
                g["blocos"].append(b)
                break
        else:
            grupos.append({"x": b["bbox"][0], "blocos": [b]})
    ordem = []
    for g in sorted(grupos, key=lambda g: g["x"]):
        ordem.extend(sorted(g["blocos"], key=lambda b: b["bbox"][1]))
    return ordem


def colar_capitular(letra, texto, vocab):
    """'A' + 'quiraz é' vira 'Aquiraz é'; 'A' + 'metodologia' vira 'A metodologia'.

    A, E, O, É, À são palavras sozinhas: só cola quando a palavra colada
    existe na edição e a parte solta não existe.
    """
    m = re.match(r"\s*([A-Za-zÀ-ú]+)", texto)
    if not m:
        return letra + " " + texto.lstrip()
    resto = m.group(1).lower()
    colada = (letra + resto).lower()
    # "A" + "o longo" vira "Ao longo": resto de uma ou duas letras gruda.
    gruda = colada in vocab["simples"] and (resto not in vocab["simples"] or len(resto) <= 2)
    if letra in "AEOÉÀÓ" and not gruda:
        return letra + " " + texto.lstrip()
    return letra + texto.lstrip()


def capitulares(blocos, vocab, log, onde):
    """Junta a letra capitular ao bloco que ela abre.

    A capitular aparece de três jeitos: bloco próprio, linha dentro de outro
    bloco (em 2016 p. 10 ela está na caixa do olho da matéria), ou colada à
    palavra com espaço ("T entamos"). A comparação é sempre pela linha, não
    pelo bloco: o bloco do corpo começa à esquerda da letra, embaixo dela.
    """
    for b in blocos:
        for ln in b["linhas"]:
            t = ln["texto"]
            m = re.match(r"^\s*([B-DF-NP-ZÇ]) ([a-zà-ú]+)", t)
            if m and m.group(2) not in vocab["simples"]:
                ln["texto"] = t.replace(m.group(0), m.group(1) + m.group(2), 1)

    letras = []
    for b in blocos:
        for ln in list(b["linhas"]):
            # Tamanho mínimo de 20 pt (2015 usa 26,6) e letra minúscula aceita (2013 usa "p").
            if re.fullmatch(r"[A-Za-zÀ-ú]", ln["texto"].strip()) and ln["tamanho"] >= 20:
                letras.append(ln)
                b["linhas"].remove(ln)
    resto = [b for b in blocos if b["linhas"]]

    for c in letras:
        x1, y0, y1 = c["bbox"][2], c["bbox"][1], c["bbox"][3]
        candidatos = [
            b for b in resto
            if b["linhas"][0]["texto"].strip()[:1].isalpha()
            and y0 - 5 <= b["linhas"][0]["bbox"][1] <= y1
            # A caixa da letra inclui o espaço depois dela e invade a primeira linha.
            and -20 < b["linhas"][0]["bbox"][0] - x1 < 45
        ]
        alvo = min(candidatos, key=lambda b: b["linhas"][0]["bbox"][0] - x1, default=None)
        letra = c["texto"].strip().upper()
        if not alvo:
            log.append(f"{onde}: capitular '{letra}' sem texto colado ao lado; descartada (ornamento, ou letra repetida do texto)")
            continue
        primeira = alvo["linhas"][0]["texto"].strip()
        if primeira[:1].islower():
            alvo["linhas"][0]["texto"] = colar_capitular(letra, alvo["linhas"][0]["texto"], vocab)
        elif primeira[:1].upper() == letra:
            # Capitular decorativa: o texto já traz a letra ("C" + "Coaching").
            pass
        elif letra in "AOEÉÀ":
            # Artigo como capitular: "O" + "Iteva nasceu em 1993".
            alvo["linhas"][0]["texto"] = letra + " " + alvo["linhas"][0]["texto"].lstrip()
            log.append(f"{onde}: capitular '{letra}' lida como palavra: '{letra} {primeira[:30]}'")
        else:
            log.append(f"{onde}: capitular '{letra}' antes de '{primeira[:30]}'; descartada, conferir")
    return resto


def extrair(caminho_pdf, pasta_saida):
    doc = pymupdf.open(caminho_pdf)
    nome = Path(caminho_pdf).stem
    vocab = vocabulario(doc)
    log = []

    todos = []
    for n, pagina in enumerate(doc, start=1):
        for b in ler_blocos(pagina):
            b["pagina"] = n
            b["texto_bruto"] = " ".join(l["texto"] for l in b["linhas"])
            todos.append(b)

    # Edição bilíngue: o inglês costuma vir num corpo menor e fixo.
    amostra = [(b["tamanho"], idioma(b["texto_bruto"], b["tamanho"], None)) for b in todos if len(b["texto_bruto"]) > 120]
    en_tam = collections.Counter(t for t, i in amostra if i == "en")
    bilingue = len([1 for _, i in amostra if i == "en"]) > 0.2 * len(amostra)
    tamanho_en = en_tam.most_common(1)[0][0] if bilingue and en_tam else None

    # Corpo de texto em português: o tamanho que carrega mais caracteres.
    pesos = collections.Counter()
    for b in todos:
        if not bilingue or idioma(b["texto_bruto"], b["tamanho"], tamanho_en) == "pt":
            pesos[b["tamanho"]] += len(b["texto_bruto"])
    corpo = pesos.most_common(1)[0][0]

    # Léxico de cada idioma, tirado dos parágrafos longos, onde a decisão é segura.
    # Serve para decidir rótulos curtos ("Since 2014", "Principal", "Students").
    lexico = None
    if bilingue:
        lexico = {"pt": set(), "en": set()}
        for b in todos:
            if len(b["texto_bruto"]) > 120:
                lg = idioma(b["texto_bruto"], b["tamanho"], None)
                if lg:
                    lexico[lg].update(palavras(b["texto_bruto"]))
        # Nome próprio não diz idioma: "Camila Souza" do expediente puxava a
        # legenda em inglês para o português. Nome próprio é a palavra que vem
        # com maiúscula também no meio da frase, e nunca em minúscula.
        maiuscula_no_meio, minuscula = set(), set()
        for b in todos:
            texto = b["texto_bruto"].replace(HIFEN_INVISIVEL, "")
            for m in re.finditer(r"(?<=[A-Za-zÀ-ú,] )[A-ZÀ-Ú][a-zà-ú]+|(?<![A-Za-zÀ-ú])[a-zà-ú]+", texto):
                w = m.group(0)
                (minuscula if w[0].islower() else maiuscula_no_meio).add(w.lower())
        proprios = maiuscula_no_meio - minuscula
        for lg in lexico:
            lexico[lg] -= proprios
        # Palavra funcional de um idioma que aparece no outro ("in loco") não conta.
        lexico["pt"] -= PALAVRAS_EN
        lexico["en"] -= PALAVRAS_PT

    saida = {"pt": [], "en": []}
    resumo = {"paginas": doc.page_count, "bilingue": bilingue, "corpo_pt": corpo, "corpo_en": tamanho_en,
              "cabecalhos_removidos": 0, "legendas": 0, "destaques": 0, "titulos": 0, "paginas_sem_texto": []}

    for n, pagina in enumerate(doc, start=1):
        onde = f"p. {n}"
        largura_pag = pagina.rect.width
        blocos = []
        for b in ler_blocos(pagina):
            bruto = " ".join(l["texto"] for l in b["linhas"]).replace(HIFEN_INVISIVEL, "")
            if CABECALHO.match(bruto) or SO_NUMERO.match(bruto):
                resumo["cabecalhos_removidos"] += 1
                continue
            blocos.append(b)
        blocos = capitulares(blocos, vocab, log, onde)

        por_idioma = {"pt": [], "en": []}
        for b in blocos:
            if not bilingue:
                por_idioma["pt"].append(b)
                continue
            for lg, parte in separar_idiomas(b, tamanho_en, lexico):
                por_idioma[lg].append(parte)

        # O corpo muda de matéria para matéria (em 2023, 12 pt nas páginas 6 a 12
        # e 10 pt no resto): vale o da página, quando ela tem texto suficiente.
        pesos_pag = collections.Counter()
        for b in por_idioma["pt"]:
            pesos_pag[b["tamanho"]] += sum(len(l["texto"].strip()) for l in b["linhas"])
        corpo_pag = pesos_pag.most_common(1)[0][0] if sum(pesos_pag.values()) > 600 else corpo

        for lg, bls in por_idioma.items():
            if not bls:
                continue
            ref = corpo_pag if lg == "pt" else tamanho_en
            titulos, corpo_txt, destaques, legendas = [], [], [], []
            for b in bls:
                t = b["tamanho"]
                if t >= max(16, ref * 1.6):
                    titulos.append(b)
                elif t > ref + 1.5:
                    destaques.append(b)
                elif lg == "pt" and t < ref - 0.6:
                    legendas.append(b)
                else:
                    corpo_txt.append(b)

            def texto(b):
                largura = b["bbox"][2] - b["bbox"][0]
                return unir_linhas(b["linhas"], largura, vocab, log, onde)

            partes = []
            for b in sorted(titulos, key=lambda b: (b["bbox"][1], b["bbox"][0])):
                partes.append("### " + texto(b).replace("\n", " "))
                resumo["titulos"] += lg == "pt"
            # Parágrafo que termina sem pontuação continua no próximo bloco quando
            # este começa em minúscula, ou quando o anterior é texto corrido longo
            # ("conhecido hoje como Programa" + "Midiacom. Porém...").
            paragrafos = []
            for b in colunas(corpo_txt):
                t = texto(b)
                ant = paragrafos[-1] if paragrafos else ""
                corrido = len(ant) > 200 and "\n" not in ant[-80:] and re.search(r"[A-Za-zÀ-ú]$", ant)
                if ant and not FIM_DE_FRASE.search(ant) and (t[:1].islower() or corrido):
                    ant = paragrafos[-1]
                    if ant.endswith("-"):
                        paragrafos[-1] = juntar_hifen(ant, t, vocab, log, onde)
                    else:
                        paragrafos[-1] = ant + " " + t
                else:
                    paragrafos.append(t)
            partes.extend(paragrafos)
            if lg == "pt":
                for par in paragrafos:
                    if par.endswith("-") or par[:1].islower():
                        log.append(f"{onde}: ordem de leitura suspeita, parágrafo partido: '{par[:50]}'")
            # Olho de matéria vem às vezes um bloco por linha: junta os vizinhos
            # de mesmo corpo, alinhados e encostados verticalmente.
            juntos = []
            for b in sorted(destaques, key=lambda b: (round(b["bbox"][0] / 20), b["bbox"][1])):
                if juntos:
                    a = juntos[-1]
                    if (abs(a["tamanho"] - b["tamanho"]) < 0.3 and abs(a["bbox"][0] - b["bbox"][0]) < 25
                            and 0 <= b["bbox"][1] - a["bbox"][3] < a["tamanho"]):
                        a["linhas"] = a["linhas"] + b["linhas"]
                        a["bbox"] = (min(a["bbox"][0], b["bbox"][0]), a["bbox"][1], max(a["bbox"][2], b["bbox"][2]), b["bbox"][3])
                        continue
                juntos.append(dict(b))
            for b in colunas(juntos):
                d = texto(b).replace("\n", " ")
                # Efeito de sombra: o mesmo texto desenhado duas vezes.
                ws = d.split(" ")
                for k in range(1, len(ws) // 2 + 1):
                    if ws[:k] == ws[k:2 * k] and len(" ".join(ws[:k])) > 20:
                        d = " ".join(ws[:k] + ws[2 * k:])
                        break
                partes.append("> [destaque] " + d)
                resumo["destaques"] += lg == "pt"
            for b in colunas(legendas):
                partes.append("[legenda ou nota] " + texto(b).replace("\n", " / "))
                resumo["legendas"] += lg == "pt"
            saida[lg].append((n, partes))

        if not por_idioma["pt"] and not por_idioma["en"]:
            resumo["paginas_sem_texto"].append(n)

    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)
    escrever(pasta / f"{nome}.md", nome, "português", saida["pt"], resumo["paginas_sem_texto"], doc.page_count)
    if bilingue:
        escrever(pasta / f"{nome}.en.md", nome, "inglês", saida["en"], [], doc.page_count)
    (pasta / f"{nome}.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False))
    print(f"{len(log)} decisões no log")


def escrever(caminho, nome, lingua, paginas, sem_texto, total):
    linhas = [
        f"# {nome} ({lingua})",
        "",
        f"Extraído de `acervo/revistas/{nome}.pdf` por `scripts/extrair_revista.py`.",
        "Cite pela página: o marcador `## Página N` é a página do PDF.",
        "",
    ]
    tem = {n: partes for n, partes in paginas}
    for n in range(1, total + 1):
        if n in tem:
            linhas += [f"## Página {n}", ""]
            for p in tem[n]:
                linhas += [p, ""]
        elif n in sem_texto:
            linhas += [f"## Página {n}", "", "(sem texto extraível: página só com imagem)", ""]
    caminho.write_text("\n".join(linhas), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    extrair(sys.argv[1], sys.argv[2])
