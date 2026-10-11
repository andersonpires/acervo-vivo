"""Mede o texto das revistas e das notícias para os guias de voz.

Uso:
    python -I scripts/medir_voz.py > voz/medidas.md

Só corpo de texto entra na conta: títulos, destaques, legendas e linhas
curtas (listas, nomes, créditos) ficam de fora. Os grupos de anos seguem
as fases editoriais: revista do Midiacom (2010 a 2015), revista do Iteva
(2016 a 2023); notícias antigas (2011 a 2016), do meio (2017 a 2022) e
recentes (2024 a 2026).
"""

import collections
import glob
import re
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PALAVRA = re.compile(r"[A-Za-zÀ-ú]+(?:-[A-Za-zÀ-ú]+)*|\d[\d.,]*")
FRASE = re.compile(r"(?<=[.!?…])[”\"]?\s+(?=[“\"A-ZÀ-Ú0-9])")
PRIMEIRA_PLURAL = re.compile(r"\b(nós|nosso|nossa|nossos|nossas|[a-zà-ú]{2,}(?:amos|emos|imos))\b", re.I)
FALSOS_PLURAL = {"ramos", "mesmos", "extremos", "termos", "supremos", "primos"}
VERBO_FALA = re.compile(r"[”\"]\s*,\s*(\w+)", re.I)
STOP = set("""a o e é de da do das dos em no na nos nas um uma uns umas que com para por pelo pela pelos pelas
ao aos à às se os as mais como mas também sua seu suas seus ou já foi são ser ter tem isso essa esse esta este
entre sobre quando onde muito muitos muita muitas cada todo toda todos todas não sim há até ainda pois nós eles
elas ele ela lhe lhes seja sido está estão era eram vai vão foram será podem pode após através desde mesmo
the""".split())


def paragrafos_revista(arquivo):
    for ln in open(arquivo, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith(("#", ">", "[legenda", "Extraído", "Cite pela")):
            continue
        if len(ln) < 120:
            continue
        yield ln


def paragrafos_noticia(arquivo):
    t = open(arquivo, encoding="utf-8").read().split("---", 2)[2]
    for ln in t.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith(("#", "(imagem)")) or re.match(r"^(Texto|Fotos?|Imagens?)\s*:", ln):
            continue
        if len(ln) < 80:
            continue
        yield ln


def medir(paragrafos):
    frases, tam_par, palavras_todas = [], [], []
    for p in paragrafos:
        fs = [f for f in FRASE.split(p) if f.strip()]
        frases.extend(fs)
        ws = PALAVRA.findall(p)
        tam_par.append((len(ws), len(fs)))
        palavras_todas.extend(w.lower() for w in ws)
    tam_frase = sorted(len(PALAVRA.findall(f)) for f in frases)
    n = len(palavras_todas) or 1
    texto = " ".join(frases)
    plural = [m.group(0).lower() for m in PRIMEIRA_PLURAL.finditer(texto) if m.group(0).lower() not in FALSOS_PLURAL]
    numeros = len(re.findall(r"\b\d[\d.,]*\b", texto))
    return {
        "paragrafos": len(tam_par),
        "frases": len(frases),
        "palavras": n,
        "frase_mediana": statistics.median(tam_frase) if tam_frase else 0,
        "frase_p75": tam_frase[int(len(tam_frase) * 0.75)] if tam_frase else 0,
        "frase_p90": tam_frase[int(len(tam_frase) * 0.9)] if tam_frase else 0,
        "frases_acima_35": sum(t > 35 for t in tam_frase) / max(1, len(tam_frase)),
        "par_palavras_mediana": statistics.median([p[0] for p in tam_par]) if tam_par else 0,
        "par_frases_mediana": statistics.median([p[1] for p in tam_par]) if tam_par else 0,
        "nos_por_mil": 1000 * len(plural) / n,
        "voce_por_mil": 1000 * len(re.findall(r"\bvocê(s)?\b", texto, re.I)) / n,
        "pergunta_por_cem_frases": 100 * texto.count("?") / max(1, len(frases)),
        "exclamacao_por_cem_frases": 100 * texto.count("!") / max(1, len(frases)),
        "numeros_por_mil": 1000 * numeros / n,
        "ou_seja_etc": sum(texto.lower().count(x) for x in ("ou seja", "isto é", "por exemplo", "imagine", "parecido com", "ou melhor")),
        "verbos_fala": collections.Counter(m.group(1).lower() for m in VERBO_FALA.finditer(texto)).most_common(8),
        "Iteva_ITEVA": (len(re.findall(r"\bIteva\b", texto)), len(re.findall(r"\bITEVA\b", texto))),
        "idoso_pessoa_idosa": (len(re.findall(r"\bidos[oa]s?\b", texto, re.I)), len(re.findall(r"\bpessoas? idosas?\b", texto, re.I))),
        "palavras_frequentes": [w for w, _ in collections.Counter(w for w in palavras_todas if w not in STOP and len(w) > 4 and not w[0].isdigit()).most_common(25)],
    }


def grupo(nome, arquivos, leitor):
    paras = [p for a in arquivos for p in leitor(a)]
    return nome, medir(paras)


def aberturas_noticias(arquivos):
    linhas = []
    for a in arquivos:
        paras = list(paragrafos_noticia(a))
        if paras:
            primeira = FRASE.split(paras[0])[0]
            linhas.append(f"- `{Path(a).name[:10]}` {' '.join(primeira.split()[:14])}...")
    return linhas


def fechos_noticias(arquivos):
    linhas = []
    for a in arquivos:
        paras = list(paragrafos_noticia(a))
        if paras:
            ultima = FRASE.split(paras[-1])[-1]
            linhas.append(f"- `{Path(a).name[:10]}` ...{' '.join(ultima.split()[-14:])}")
    return linhas


def main():
    # No Windows o console usa a codepage local: sem isto, "> voz/medidas.md"
    # grava em cp1252 e o arquivo vira mojibake para quem lê em UTF-8.
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    rev = sorted(glob.glob(str(RAIZ / "acervo/texto/revista20??.md")))
    noti = sorted(glob.glob(str(RAIZ / "acervo/noticias/*.md")))
    ano = lambda a: int(re.search(r"(20\d\d)", Path(a).name).group(1))
    grupos = [
        grupo("Revista 2010 a 2015 (Midiacom)", [a for a in rev if ano(a) <= 2015], paragrafos_revista),
        grupo("Revista 2016 a 2023 (Iteva)", [a for a in rev if ano(a) >= 2016], paragrafos_revista),
        grupo("Notícias 2011 a 2016", [a for a in noti if ano(a) <= 2016], paragrafos_noticia),
        grupo("Notícias 2017 a 2022", [a for a in noti if 2017 <= ano(a) <= 2022], paragrafos_noticia),
        grupo("Notícias 2024 a 2026", [a for a in noti if ano(a) >= 2024], paragrafos_noticia),
    ]
    print("# Medidas de texto do acervo\n")
    print("Gerado por `scripts/medir_voz.py`. Só corpo de texto; títulos, destaques,")
    print("legendas e linhas curtas ficam de fora. Palavras contadas como sequências")
    print("de letras ou números.\n")
    chaves = [
        ("paragrafos", "Parágrafos medidos", "{:.0f}"),
        ("palavras", "Palavras medidas", "{:.0f}"),
        ("frase_mediana", "Frase: mediana de palavras", "{:.0f}"),
        ("frase_p75", "Frase: 75% têm até", "{:.0f}"),
        ("frase_p90", "Frase: 90% têm até", "{:.0f}"),
        ("frases_acima_35", "Frases com mais de 35 palavras", "{:.0%}"),
        ("par_palavras_mediana", "Parágrafo: mediana de palavras", "{:.0f}"),
        ("par_frases_mediana", "Parágrafo: mediana de frases", "{:.0f}"),
        ("nos_por_mil", "1ª pessoa do plural, por mil palavras", "{:.1f}"),
        ("voce_por_mil", "\"você\", por mil palavras", "{:.1f}"),
        ("pergunta_por_cem_frases", "Perguntas, por cem frases", "{:.1f}"),
        ("exclamacao_por_cem_frases", "Exclamações, por cem frases", "{:.1f}"),
        ("numeros_por_mil", "Números em algarismo, por mil palavras", "{:.1f}"),
        ("ou_seja_etc", "\"ou seja\", \"por exemplo\", \"imagine\"... (total)", "{:.0f}"),
    ]
    print("| Medida | " + " | ".join(n for n, _ in grupos) + " |")
    print("|---|" + "---|" * len(grupos))
    for k, rotulo, fmt in chaves:
        print(f"| {rotulo} | " + " | ".join(fmt.format(m[k]) for _, m in grupos) + " |")
    print("| \"Iteva\" / \"ITEVA\" no corpo | " + " | ".join(f"{m['Iteva_ITEVA'][0]} / {m['Iteva_ITEVA'][1]}" for _, m in grupos) + " |")
    print("| \"idoso(s)\" / \"pessoa(s) idosa(s)\" | " + " | ".join(f"{m['idoso_pessoa_idosa'][0]} / {m['idoso_pessoa_idosa'][1]}" for _, m in grupos) + " |")
    print()
    for nome, m in grupos:
        print(f"## {nome}\n")
        print("Verbos depois de citação (`”, verbo`): " + ", ".join(f"{v} ({n})" for v, n in m["verbos_fala"]) + "\n")
        print("Palavras mais frequentes (fora as funcionais): " + ", ".join(m["palavras_frequentes"]) + "\n")
    recentes = [a for a in noti if ano(a) >= 2024]
    print("## Como abrem as notícias de 2024 a 2026\n")
    print("\n".join(aberturas_noticias(recentes)) + "\n")
    print("## Como fecham as notícias de 2024 a 2026\n")
    print("\n".join(fechos_noticias(recentes)) + "\n")
    creditos = sum(1 for a in recentes if re.search(r"^Texto\s*:", open(a, encoding="utf-8").read(), re.M))
    print(f"Notícias de 2024 a 2026 com linha de crédito \"Texto:\": {creditos} de {len(recentes)}.\n")


if __name__ == "__main__":
    main()
