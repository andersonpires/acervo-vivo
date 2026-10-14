"""Grava acervo/clipping: uma matéria por arquivo, com o texto original.

Uso:
    node scripts/exportar_clipping.cjs        (antes: lê o banco do site)
    python -I scripts/extrair_clipping.py [--rebaixar] [--sem-arquivo]

Para cada matéria de scripts/clipping/banco.json:

1. tenta a página original (o link gravado no site);
2. se ela não abre, cai numa página genérica ou não cita o Iteva, busca
   a cópia mais próxima da data da matéria no Internet Archive
   (web.archive.org);
3. links do site antigo para recortes escaneados ("arquivos/reportagens")
   apontam para a transcrição feita à mão em acervo/clipping/recortes,
   que este script nunca altera.

Só aceita como texto da matéria o que cita o Iteva ou um projeto dele
(ver CITA): página que abre mas mostra outra coisa não conta.

O HTML baixado fica em acervo/clipping/brutos (fora do git), com um
.json ao lado dizendo de onde e quando veio. Sem --rebaixar, o script
usa o que já está lá e não consulta a internet de novo.

O Internet Archive bloqueia (429) quem consulta demais, e o bloqueio dura
horas. Consulta bloqueada não vai para o cache: basta rodar de novo mais
tarde. Com --sem-arquivo, o script não faz consulta nova ao Archive (só usa
o cache) e marca essas matérias como pendentes.

Clipping é consulta, nunca modelo de escrita: o texto é de terceiros.

Re-executável: apaga e regrava os .md da pasta de saída (não os
recortes nem os brutos).
"""

import datetime
import json
import re
import sys
import time
import urllib.parse
import warnings
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Comment

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parent.parent
BANCO = RAIZ / "scripts" / "clipping" / "banco.json"
VEICULOS = RAIZ / "scripts" / "clipping" / "veiculos.json"
SAIDA = RAIZ / "acervo" / "clipping"
BRUTOS = SAIDA / "brutos"
RECORTES = SAIDA / "recortes"
HOJE = datetime.date.today().isoformat()
REBAIXAR = "--rebaixar" in sys.argv
SEM_ARQUIVO = "--sem-arquivo" in sys.argv
PAUSA_ARQUIVO = 20  # segundos entre consultas ao Internet Archive
ULTIMA = 0.0

AGENTE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
CITA = re.compile(
    r"iteva|midia ?com|s[íi]sger|cientista do futuro|cidad[ãa]o do futuro|construcom|"
    r"conectividade ?\+ ?60|empodera jovem|compartilhando saberes|bem-estar \+60|beneduce",
    re.I,
)
# Sem texto a extrair: rede social, vídeo, arquivo pessoal.
SEM_TEXTO = re.compile(r"instagram\.com|youtube\.com|youtu\.be|sharepoint\.com|linkedin\.com")

IGNORAR = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript",
           "iframe", "svg", "button", "select", "figure"}
RUIDO = re.compile(r"coment|comment|share|compartilh|relacionad|related|sidebar|widget|menu|"
                   r"newsletter|cookie|rodape|footer|banner|publicidade|advert|social|"
                   r"breadcrumb|tags|author-box|navigation", re.I)
# Botões de compartilhar e afins que sobram no meio do texto.
BOTAO = re.compile(r"^(- )?(facebook|twitter|google\+|whatsapp|linkedin|pinterest|telegram|e-?mail|imprimir|print|"
                   r"compartilhe|compartilhar|share|tweet|curtir)\W*$", re.I)

# Matérias cujo link não aponta para o recorte, mas que têm recorte em
# site_legado/public/arquivos/reportagens (conferido na leitura).
RECORTE_DE = {50: "folha_online.jpg", 47: "governo_do_Ceara.jpg"}

BLOCO = ["p", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td", "table",
         "section", "article", "blockquote", "pre", "dd", "dt"]
CORPO = re.compile(r"post-body|entry-content|post-content|article-body|articlebody|"
                   r"materia|noticia-texto|texto-noticia|content-text|single-content|"
                   r"td-post-content|itemFullText|item-page|story", re.I)


def sessao():
    s = requests.Session()
    s.headers.update({"User-Agent": AGENTE, "Accept-Language": "pt-BR,pt;q=0.9"})
    return s


S = sessao()


def baixar(url):
    """Devolve (status, url_final, html). Certificado vencido não impede ler."""
    try:
        r = S.get(url, timeout=40, allow_redirects=True, verify=False)
    except requests.RequestException as e:
        return f"erro: {type(e).__name__}", "", ""
    r.encoding = r.apparent_encoding if not r.encoding or r.encoding.lower() == "iso-8859-1" else r.encoding
    return r.status_code, r.url, r.text


def no_arquivo(url):
    """GET no Internet Archive com pausa entre consultas. O Archive bloqueia
    (429) quem consulta rápido demais; bloqueio vira erro, não "sem cópia"."""
    global ULTIMA
    espera = PAUSA_ARQUIVO - (time.time() - ULTIMA)
    if espera > 0:
        time.sleep(espera)
    ULTIMA = time.time()
    return S.get(url, timeout=60, verify=False)


def copia_no_arquivo(url, data):
    """Procura no Internet Archive a cópia mais próxima da data da matéria."""
    # O índice CDX lista as cópias; a API "available" responde vazio com
    # frequência mesmo quando a cópia existe.
    alvo = int(data.replace("-", ""))
    api = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(
        {"url": url, "output": "json", "filter": "statuscode:200", "fl": "timestamp,original", "collapse": "digest"})
    linhas = None
    for espera in (10, 30, 60):
        try:
            r = no_arquivo(api)
            if r.status_code == 429:
                return {"erro": "Internet Archive bloqueou as consultas (429)"}
            if r.status_code == 200:
                linhas = r.json() if r.text.strip() else []
                break
        except (requests.RequestException, ValueError):
            pass
        time.sleep(espera)
    if linhas is None:
        return {"erro": "índice do Internet Archive fora do ar"}
    copias = [(ts, orig) for ts, orig in linhas[1:]]
    if not copias:
        return None
    # A mais próxima da data da matéria, preferindo as de depois dela.
    copias.sort(key=lambda c: (int(c[0][:8]) < alvo, abs(int(c[0][:8]) - alvo)))
    for ts, orig in copias[:3]:
        # "id_" devolve a página como foi gravada, sem a barra do Archive.
        try:
            r = no_arquivo(f"https://web.archive.org/web/{ts}id_/{orig}")
        except requests.RequestException:
            return {"erro": "Internet Archive não respondeu"}
        if r.status_code == 429:
            return {"erro": "Internet Archive bloqueou as consultas (429)"}
        r.encoding = r.apparent_encoding if not r.encoding or r.encoding.lower() == "iso-8859-1" else r.encoding
        if r.status_code == 200 and CITA.search(extrair(r.text)[1]):
            return {"url": f"https://web.archive.org/web/{ts}/{orig}", "data": f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}",
                    "html": r.text}
    return None


def guardado(nome):
    meta = BRUTOS / f"{nome}.json"
    if meta.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        html = (BRUTOS / f"{nome}.html").read_text(encoding="utf-8") if m.get("tem_html") else ""
        return m, html
    return None, ""


def guardar(nome, meta, html):
    BRUTOS.mkdir(parents=True, exist_ok=True)
    meta["tem_html"] = bool(html)
    if html:
        (BRUTOS / f"{nome}.html").write_text(html, encoding="utf-8")
    (BRUTOS / f"{nome}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")


def limpo(t):
    t = t.replace(chr(0xA0), " ").replace(chr(0x200B), "")
    return re.sub(r"[ \t\r\f\v]+", " ", t).strip()


def rotulo_de(tag):
    return " ".join(tag.get("class", []) or []) + " " + (tag.get("id") or "")


def extrair(html):
    """Texto principal da página: título, data e parágrafos do corpo."""
    soup = BeautifulSoup(html, "lxml")
    meta = {}
    for prop, chave in (("og:title", "titulo"), ("article:published_time", "publicado"),
                        ("article:author", "autor"), ("og:site_name", "site")):
        m = soup.find("meta", attrs={"property": prop})
        if m and m.get("content"):
            meta[chave] = limpo(m["content"])
    m = soup.find("meta", attrs={"name": "author"})
    if m and m.get("content") and "autor" not in meta:
        meta["autor"] = limpo(m["content"])
    if "titulo" not in meta:
        h1 = soup.find("h1")
        if h1:
            meta["titulo"] = limpo(h1.get_text(" "))

    for c in soup.find_all(string=lambda x: isinstance(x, Comment)):
        c.extract()
    for tag in soup.find_all(list(IGNORAR)):
        tag.decompose()
    # Quem contém o corpo da matéria não sai, mesmo com nome de ruído:
    # no Blogger o post fica dentro de um "widget Blog".
    protegidos = set()
    for t in soup.find_all(True):
        if t.name == "article" or t.get("itemprop") == "articleBody" or CORPO.search(rotulo_de(t)):
            protegidos.add(id(t))
            protegidos.update(id(a) for a in t.parents)
    for tag in soup.find_all(True):
        if tag.attrs is None or id(tag) in protegidos:
            continue
        if RUIDO.search(rotulo_de(tag)) and tag.name not in ("body", "html", "main"):
            tag.decompose()

    candidatos = soup.select("[itemprop=articleBody]") or [
        t for t in soup.find_all(True) if t.attrs is not None and CORPO.search(rotulo_de(t))
    ] or soup.find_all("article")
    if candidatos:
        corpo = max(candidatos, key=lambda t: len(t.get_text(" ", strip=True)))
    else:
        # O pai com mais texto em <p> diretos.
        pontos = {}
        for p in soup.find_all("p"):
            pai = p.parent
            pontos[id(pai)] = (pontos.get(id(pai), (pai, 0))[0], pontos.get(id(pai), (pai, 0))[1] + len(p.get_text(strip=True)))
        corpo = max(pontos.values(), key=lambda x: x[1])[0] if pontos else soup.body or soup

    blocos = []
    blocos_tags = corpo.find_all(["p", "h2", "h3", "h4", "li", "blockquote"])
    for t in blocos_tags:
        if t.find_parent(["p", "li", "blockquote"]) in blocos_tags:
            continue
        s = limpo(t.get_text(" "))
        if t.name in ("h2", "h3", "h4") and s:
            s = "### " + s
        elif t.name == "li" and s:
            s = "- " + s
        elif t.name == "blockquote" and s:
            s = "> " + s
        blocos.append(s)
    texto = sem_repetir(blocos)

    # Página sem <p> (texto solto com <br>, tabelas antigas): lê o bloco
    # linha a linha; se ainda for pouco, a página inteira, só com as linhas
    # longas, que são frases e não menu.
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for t in soup.find_all(BLOCO):
        t.insert_before("\n")
        t.insert_after("\n")
    linhas = sem_repetir(limpo(l) for l in corpo.get_text("").split("\n"))
    if len(texto) < 0.6 * len(linhas):
        texto = linhas
    if len(texto) < 300 and soup.body:
        todas = sem_repetir(l for l in (limpo(x) for x in soup.body.get_text("").split("\n")) if len(l) >= 60)
        if len(todas) > len(texto):
            texto = todas
    return meta, texto


def sem_repetir(blocos):
    vistos, saida = set(), []
    for b in blocos:
        if b and b not in vistos and not BOTAO.match(b):
            vistos.add(b)
            saida.append(b)
    return "\n\n".join(saida)


def generico(url, final):
    """Redirecionou para a home ou para outra seção: a matéria sumiu."""
    if not final:
        return True
    a, b = urllib.parse.urlparse(url), urllib.parse.urlparse(final)
    if b.path in ("", "/") and a.path not in ("", "/"):
        return True
    if "login" in b.netloc:
        return True
    ultimo = [p for p in a.path.split("/") if p]
    ultimo = ultimo[-1][:25] if ultimo else ""
    return a.netloc.replace("www.", "") != b.netloc.replace("www.", "") and ultimo not in final


def buscar(r):
    """Decide a fonte do texto de uma matéria. Devolve um dicionário."""
    url = r["link_materia"]
    nome = str(r["id_legado"] or r["id_site"])
    dominio = urllib.parse.urlparse(url).netloc

    if dominio == "arquivos":
        arq = Path(urllib.parse.urlparse(url).path).name
        return {"situacao": "link quebrado para recorte do site antigo; texto do recorte", "recorte": arq}
    if r["id_legado"] in RECORTE_DE:
        return {"situacao": "texto do recorte guardado no site antigo", "recorte": RECORTE_DE[r["id_legado"]]}
    if SEM_TEXTO.search(url):
        tipo = "vídeo" if re.search(r"youtu", url) else ("arquivo pessoal no OneDrive, pede login" if "sharepoint" in url else "rede social")
        return {"situacao": f"sem texto a extrair ({tipo})"}

    meta, html = (None, "") if REBAIXAR else guardado(nome)
    if meta is None:
        status, final, html = baixar(url)
        meta = {"url": url, "consultado": HOJE, "status": status, "final": final}
        guardar(nome, meta, html if status == 200 else "")
        time.sleep(1)
    vivo_ok = meta["status"] == 200 and not generico(url, meta["final"])
    if vivo_ok:
        info, texto = extrair(html)
        if CITA.search(texto) and len(texto) > 150:
            return {"situacao": "página original no ar", "fonte_texto": url, "data_fonte": meta["consultado"],
                    "info": info, "texto": texto, "status": meta["status"]}

    situacao_link = "abre, mas sem a matéria" if meta["status"] == 200 else f"não abre ({meta['status']})"
    nome_arq = nome + "-arquivo"
    ameta, ahtml = (None, "") if REBAIXAR else guardado(nome_arq)
    if ameta is None and SEM_ARQUIVO:
        return {"situacao": f"link {situacao_link}; consulta ao Internet Archive pendente", "status": meta["status"]}
    if ameta is None:
        c = copia_no_arquivo(url, r["data"])
        if c and c.get("erro"):
            # Não guarda: na próxima execução tenta de novo.
            return {"situacao": f"link {situacao_link}; {c['erro']}", "status": meta["status"]}
        ameta = {"url": url, "consultado": HOJE, "copia": c["url"] if c else "", "data_copia": c["data"] if c else ""}
        guardar(nome_arq, ameta, c["html"] if c else "")
        ahtml = c["html"] if c else ""
        time.sleep(2)
    if ahtml:
        info, texto = extrair(ahtml)
        if CITA.search(texto) and len(texto) > 150:
            return {"situacao": f"link {situacao_link}; texto da cópia no Internet Archive",
                    "fonte_texto": ameta["copia"], "data_fonte": ameta["data_copia"], "info": info, "texto": texto,
                    "status": meta["status"]}
        return {"situacao": f"link {situacao_link}; cópia no Internet Archive sem a matéria", "status": meta["status"],
                "copia": ameta["copia"]}
    return {"situacao": f"link {situacao_link}; sem cópia útil no Internet Archive", "status": meta["status"]}


def yaml(s):
    return json.dumps(s or "", ensure_ascii=False)


def gravar(r, b, veiculos):
    v = veiculos.get(str(r["id_legado"]), "")
    linhas = [
        "---",
        f"titulo: {yaml(r['titulo'])}",
        f"data: {r['data']}",
        f"veiculo: {yaml(v)}",
        "veiculo_origem: deduzido do título ou do endereço (o site não registra)" if v else "veiculo_origem: \"\"",
        f"url_site: {r['url_site']}",
        f"link_materia: {yaml(r['link_materia'])}",
        f"situacao: {yaml(b['situacao'])}",
        f"fonte_texto: {yaml(b.get('fonte_texto') or (('acervo/clipping/recortes/' + Path(b['recorte']).stem + '.md') if b.get('recorte') else ''))}",
        f"data_fonte: {b.get('data_fonte', '')}",
        f"consultado: {HOJE}",
        f"id_site: {r['id_site']}",
        f"id_legado: {r['id_legado'] if r['id_legado'] is not None else ''}",
        "uso: consulta; texto de terceiros, nunca modelo de escrita",
        "---",
        "",
        f"# {r['titulo']}",
        "",
        "## Resumo publicado no site do Iteva",
        "",
        r["resumo"] or "[FALTA: sem resumo no site]",
        "",
        "## Texto da matéria",
        "",
    ]
    info = b.get("info") or {}
    extras = [f"{k}: {info[k]}" for k in ("titulo", "autor", "publicado", "site") if (info.get(k) or "").strip()]
    if b.get("texto"):
        if extras:
            linhas += ["Dados da página: " + "; ".join(extras) + ".", ""]
        linhas.append(b["texto"])
    elif b.get("recorte"):
        rec = RECORTES / (Path(b["recorte"]).stem + ".md")
        if rec.exists():
            linhas.append(f"Transcrição do recorte escaneado: ver `{rec.relative_to(RAIZ).as_posix()}`.")
        else:
            linhas.append(f"[FALTA: transcrever o recorte {b['recorte']} do site antigo]")
    else:
        linhas.append(f"[FALTA: texto original não obtido; {b['situacao']}]")
    linhas.append("")
    # O id entra no nome: há matérias com mesmo título e mesma data.
    base = f"{r['data']}-{r['id_legado'] or r['id_site']}-{r['slug']}"[:90]
    arq = re.sub(r"[^\w.-]", "_", base, flags=re.A) + ".md"
    (SAIDA / arq).write_text("\n".join(linhas), encoding="utf-8")
    return arq


def main():
    registros = json.loads(BANCO.read_text(encoding="utf-8"))
    veiculos = json.loads(VEICULOS.read_text(encoding="utf-8")) if VEICULOS.exists() else {}
    SAIDA.mkdir(parents=True, exist_ok=True)
    for f in SAIDA.glob("*.md"):
        f.unlink()
    resumo, linhas_rel = {}, []
    for r in registros:
        b = buscar(r)
        arq = gravar(r, b, veiculos)
        chave = b["situacao"].split(";")[-1].strip()
        resumo[chave] = resumo.get(chave, 0) + 1
        linhas_rel.append(f"{r['id_legado']}\t{b['situacao']}\t{len(b.get('texto', ''))}\t{arq}")
        print(f"{r['id_legado']:>4} {b['situacao'][:70]:<70} {len(b.get('texto', '')):>6}", flush=True)
    print()
    for k, n in sorted(resumo.items(), key=lambda x: -x[1]):
        print(f"{n:>4}  {k}")


if __name__ == "__main__":
    main()
