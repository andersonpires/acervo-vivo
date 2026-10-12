"""Extrai as páginas publicadas de iteva.org.br para acervo/site.

Uso:
    python -I scripts/extrair_site.py

Lê o texto como o público vê (HTML publicado), não do banco: no banco o
conteúdo fica em blocos aninhados e parte dele se perde na leitura.

Quais páginas: as do sitemap.xml que são institucionais (/p/...), de
projeto (/projeto/...), de evento e a home, mais o rodapé (endereço,
CNPJ, contatos), gravado uma vez. Ficam de fora as que formam outros
acervos: notícias, vídeos, clipping, publicações, livros do CDF,
transparência; e ferramentas como /qrcode.

Re-executável: apaga e regrava acervo/site. Cada arquivo leva a data
da consulta, porque o site muda e é fonte, não verdade.
"""

import datetime
import re
import shutil
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "acervo" / "site"
BASE = "https://www.iteva.org.br"
HOJE = datetime.date.today().isoformat()

FORA = re.compile(r"/(noticias?|videos?|clipping|publicac(ao|oes)|livroscdf|transparencia|qrcode)(/|$)")
# Seções que repetem conteúdo de outros acervos ou são navegação.
SECOES_FORA = {"notícias", "vídeos", "outros projetos", "mais vídeos"}
ZWSP = chr(0x200B)
IGNORAR = {"script", "style", "nav", "header", "footer", "form", "button", "svg", "noscript", "iframe"}
TRIVIAL = re.compile(r"^(\d+ de \d+|[‹›«»←→]|anterior|próximo|ver mais|saiba mais)$", re.I)


def baixar(caminho):
    req = urllib.request.Request(BASE + caminho, headers={"User-Agent": "acervo-vivo/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def tipo_de(caminho):
    if caminho == "/":
        return "home"
    if caminho.startswith("/p/") or caminho in ("/contato", "/trabalheConosco"):
        return "institucional"
    if caminho.startswith("/projeto/"):
        return "projeto"
    return "evento"


def paginas_do_sitemap():
    xml = baixar("/sitemap.xml")
    caminhos = []
    for url in re.findall(r"<loc>([^<]+)</loc>", xml):
        c = re.sub(r"^https?://(www\.)?iteva\.org\.br", "", url) or "/"
        if FORA.search(c) or c in caminhos:
            continue
        caminhos.append(c)
    # /trabalheConosco e /p/trabalheConosco são a mesma página.
    if "/p/trabalheConosco" in caminhos and "/trabalheConosco" in caminhos:
        caminhos.remove("/trabalheConosco")
    return caminhos


def texto(el):
    # Sem separador: "<span>I</span>ncentivar" tem de virar "Incentivar".
    # As quebras <br> já viraram espaço em preparar().
    return re.sub(r"\s+", " ", el.get_text("")).replace(ZWSP, "").strip()


def listas_de(li):
    """Listas que pertencem a este item (a lista mais próxima acima é a dele)."""
    return [l for l in li.find_all(["ul", "ol"]) if l.find_parent("li") is li]


def texto_sem_listas(li):
    copia = BeautifulSoup(str(li), "html.parser").li
    for l in copia.find_all(["ul", "ol"]):
        l.decompose()
    # Número de lista em <span> próprio gruda no texto ("1Ler"): separa.
    return re.sub(r"^(\d+)(?=[A-ZÀ-Ú])", r"\1 ", texto(copia))


def preparar(sopa):
    """Ajustes no HTML antes de ler o texto."""
    for br in sopa.find_all("br"):
        br.replace_with(" ")
    # E-mail protegido contra spam pela Cloudflare: o endereço vem cifrado
    # em data-cfemail (primeiro byte é a chave, o resto vai em XOR com ela).
    for el in sopa.find_all(attrs={"data-cfemail": True}):
        b = bytes.fromhex(el["data-cfemail"])
        el.replace_with("".join(chr(x ^ b[0]) for x in b[1:]))
    # Blocos de bloco viram parágrafos separados, mesmo sem <p>.
    for el in sopa.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "div"]):
        el.insert_after(" ")


def itens(el, titulo, nivel=0):
    """Percorre o conteúdo na ordem do documento: (tipo, nível, texto)."""
    for c in el.children:
        if isinstance(c, NavigableString) or not isinstance(c, Tag):
            continue
        if c.name in IGNORAR:
            continue
        if re.fullmatch(r"h[1-6]", c.name):
            yield ("titulo", int(c.name[1]), texto(c))
        elif c.name == "p":
            yield ("par", 0, texto(c))
        elif c.name in ("ul", "ol"):
            for li in c.find_all("li", recursive=False):
                t = texto_sem_listas(li)
                if not t:
                    alts = [i.get("alt", "").strip() for i in li.find_all("img")]
                    t = ", ".join(a for a in alts if a and a != titulo)
                if t:
                    yield ("item", nivel, t)
                for sub in listas_de(li):
                    yield from itens_lista(sub, titulo, nivel + 1)
        elif c.name == "blockquote":
            yield ("citacao", 0, texto(c))
        elif c.name == "figcaption":
            yield ("legenda", 0, texto(c))
        elif c.name == "img":
            alt = (c.get("alt") or "").strip()
            if alt and alt != titulo:
                yield ("imagem", 0, alt)
        else:
            yield from itens(c, titulo, nivel)


def itens_lista(lista, titulo, nivel):
    for li in lista.find_all("li", recursive=False):
        t = texto_sem_listas(li)
        if t:
            yield ("item", nivel, t)
        for sub in listas_de(li):
            yield from itens_lista(sub, titulo, nivel + 1)


def markdown(itens_brutos):
    linhas, pular_ate, vistos = [], None, set()
    for tipo, nivel, t in itens_brutos:
        if not t or TRIVIAL.match(t):
            continue
        if tipo == "titulo":
            if pular_ate is not None and nivel <= pular_ate:
                pular_ate = None
            if t.lower() in SECOES_FORA:
                pular_ate = nivel
                continue
        if pular_ate is not None:
            continue
        if tipo == "imagem":
            if t in vistos:
                continue
            vistos.add(t)
            linhas.append(f"(imagem: {t})")
        elif tipo == "titulo":
            linhas.append("#" * max(2, min(nivel + 1, 4)) + " " + t)
        elif tipo == "item":
            linhas.append("  " * nivel + "- " + t)
        elif tipo == "citacao":
            linhas.append("> " + t)
        elif tipo == "legenda":
            linhas.append("[legenda] " + t)
        else:
            linhas.append(t)
    # Parágrafos separados por linha em branco; itens de lista colados.
    saida = []
    for i, l in enumerate(linhas):
        if i and not (l.lstrip().startswith("- ") and linhas[i - 1].lstrip().startswith("- ")):
            saida.append("")
        saida.append(l)
    return "\n".join(saida)


def nome_arquivo(caminho):
    if caminho == "/":
        return "home"
    return caminho.strip("/").split("/", 1)[-1].replace("/", "-")


def main():
    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    rodape = None
    resumo = []
    for caminho in paginas_do_sitemap():
        html = baixar(caminho)
        sopa = BeautifulSoup(html, "html.parser")
        preparar(sopa)
        if rodape is None and sopa.find("footer"):
            rodape = sopa.find("footer")
        corpo = sopa.find("main") or sopa.body
        # O título da aba traz o nome do site depois de um traço; fica só o da página.
        titulo_html = re.split(r"\s[|\u2014\u2013]\s", sopa.title.get_text(strip=True) if sopa.title else "")[0].strip()
        h = corpo.find(["h1", "h2"])
        titulo = texto(h) if h else titulo_html
        conteudo = markdown(itens(corpo, titulo))
        tipo = tipo_de(caminho)
        destino = SAIDA / f"{nome_arquivo(caminho)}.md" if tipo == "home" else SAIDA / tipo / f"{nome_arquivo(caminho)}.md"
        destino.parent.mkdir(parents=True, exist_ok=True)
        cab = [
            "---",
            f'titulo: "{titulo_html or titulo}"',
            f"url: {BASE}{caminho}",
            f"tipo: {tipo}",
            f"consultado_em: {HOJE}",
            "---",
            "",
            f"# {titulo_html or titulo}",
            "",
            conteudo or "(página sem texto)",
            "",
        ]
        destino.write_text("\n".join(cab), encoding="utf-8", newline="\n")
        palavras = len(re.findall(r"\w+", conteudo))
        resumo.append((tipo, caminho, palavras))
    if rodape is not None:
        partes = [p.strip() for p in rodape.get_text("\n", strip=True).split("\n") if p.strip()]
        (SAIDA / "rodape.md").write_text(
            "\n".join(["---", f"url: {BASE}/ (rodapé de todas as páginas)", f"consultado_em: {HOJE}", "---", "", "# Rodapé do site", ""]
                      + [f"- {p}" for p in partes] + [""]),
            encoding="utf-8", newline="\n")
    for tipo, caminho, palavras in sorted(resumo):
        print(f"{tipo:14} {palavras:6} palavras  {caminho}")
    print(f"{len(resumo)} páginas, {sum(p for *_, p in resumo)} palavras")


if __name__ == "__main__":
    main()
