"""Extrai as imagens das Revistas Iteva para acervo/imagens.

Uso:
    python -I scripts/extrair_imagens_revista.py            (todas)
    python -I scripts/extrair_imagens_revista.py 2016 2019  (só essas)

O PDF original nunca é alterado: é aberto só para leitura.

Para cada imagem que o leitor vê na página, grava:
  arquivos/revAAAA-pNN-K.<ext>         o original embutido no PDF, quando
                                       dá para tirá-lo (costuma ter mais
                                       resolução e mostrar o que a página
                                       cortou)
  arquivos/revAAAA-pNN-K-pagina.jpg    o recorte da página como o leitor
                                       vê, em 200 dpi, com o texto por cima
  paginas/revAAAA-pNN.jpg              a página inteira, pequena, para
                                       quem analisa ver o leiaute
  contexto/revistas.jsonl              uma linha por imagem: página,
                                       matérias do índice, texto em volta

Ficam de fora o que não é imagem para o leitor: lascas e ícones
(menos de 40 pt no menor lado), imagens de menos de 80 px e o que se
repete em três páginas ou mais (logos de rodapé, enfeites).
"""
import collections
import datetime
import json
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parent.parent
REVISTAS = RAIZ / "acervo" / "revistas"
PASTA = RAIZ / "acervo" / "imagens"
ARQUIVOS = PASTA / "arquivos"
PAGINAS = PASTA / "paginas"
CONTEXTO = PASTA / "contexto" / "revistas.jsonl"
INDEXACAO = RAIZ / "scripts" / "indexacao"

MENOR_LADO_PT = 40
MENOR_LADO_PX = 80
REPETIDA_EM = 3
DPI_RECORTE = 200
DPI_PAGINA = 60
PERTO_PT = 30


def materias_do_indice():
    """Matérias das revistas por arquivo, com o intervalo de páginas."""
    por_revista = collections.defaultdict(list)
    for jsonl in sorted(INDEXACAO.glob("rev_*.jsonl")):
        for linha in jsonl.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            m = json.loads(linha)
            paginas = set()
            for parte in str(m.get("paginas_ou_url", "")).replace(" ", "").split(","):
                if "-" in parte:
                    a, b = parte.split("-", 1)
                    if a.isdigit() and b.isdigit():
                        paginas.update(range(int(a), int(b) + 1))
                elif parte.isdigit():
                    paginas.add(int(parte))
            m["_paginas"] = paginas
            por_revista[m["arquivo"]].append(m)
    return por_revista


def texto_perto(blocos, caixa):
    """Blocos de texto logo acima, logo abaixo ou dentro da imagem."""
    acima, abaixo, dentro = [], [], []
    for b in blocos:
        r = pymupdf.Rect(b[:4])
        t = " ".join(b[4].split())
        if not t:
            continue
        sobrepoe_x = min(r.x1, caixa.x1) - max(r.x0, caixa.x0) > 0
        if caixa.contains(r) or (r & caixa).get_area() > 0.5 * r.get_area():
            dentro.append(t)
        elif sobrepoe_x and 0 <= caixa.y0 - r.y1 <= PERTO_PT:
            acima.append(t)
        elif sobrepoe_x and 0 <= r.y0 - caixa.y1 <= PERTO_PT:
            abaixo.append(t)
    return {"acima": acima, "abaixo": abaixo, "sobre_a_imagem": dentro}


def original(doc, xref, destino_sem_ext):
    """Tira a imagem embutida, com a máscara, em RGB. Devolve o caminho."""
    pix = pymupdf.Pixmap(doc, xref)
    smask = doc.xref_get_key(xref, "SMask")
    if smask[0] == "xref":
        try:
            pix = pymupdf.Pixmap(pix, pymupdf.Pixmap(doc, int(smask[1].split()[0])))
        except Exception:
            pass
    if pix.colorspace and pix.colorspace.n not in (1, 3):
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    if pix.alpha:
        caminho = destino_sem_ext.with_suffix(".png")
        pix.save(caminho)
    else:
        caminho = destino_sem_ext.with_suffix(".jpg")
        pix.save(caminho, jpg_quality=92)
    return caminho


def extrair(pdf, materias):
    ano = pdf.stem.replace("revista", "")
    doc = pymupdf.open(pdf)
    paginas_do_xref = collections.Counter()
    for pagina in doc:
        for x in {im[0] for im in pagina.get_images(full=True)}:
            paginas_do_xref[x] += 1

    entradas, vistos, descartes = [], {}, collections.Counter()
    for pagina in doc:
        n = pagina.number + 1
        area = pagina.rect
        candidatas = []
        for info in pagina.get_image_info(xrefs=True):
            caixa = pymupdf.Rect(info["bbox"]) & area
            xref = info["xref"]
            if caixa.is_empty or min(caixa.width, caixa.height) < MENOR_LADO_PT:
                descartes["pequena na página"] += 1
                continue
            if min(info["width"], info["height"]) < MENOR_LADO_PX:
                descartes["poucos pixels"] += 1
                continue
            if xref and paginas_do_xref[xref] >= REPETIDA_EM:
                descartes["repetida em 3+ páginas"] += 1
                continue
            candidatas.append((caixa, xref, info))

        # A mesma imagem desenhada duas vezes (sombra, máscara) ou duas
        # imagens com a mesma caixa: fica a de mais pixels.
        unicas = []
        for c in sorted(candidatas, key=lambda c: -c[2]["width"] * c[2]["height"]):
            iguais = [u for u in unicas if (u[0] & c[0]).get_area() > 0.85 * max(u[0].get_area(), c[0].get_area())]
            if iguais:
                descartes["mesma caixa de outra"] += 1
                continue
            unicas.append(c)
        if not unicas:
            continue
        unicas.sort(key=lambda c: (round(c[0].y0 / 20), c[0].x0))

        id_pagina = f"rev{ano}-p{n:02d}"
        pagina.get_pixmap(dpi=DPI_PAGINA).save(PAGINAS / f"{id_pagina}.jpg", jpg_quality=75)
        blocos = pagina.get_text("blocks")
        doc_materias = [
            {k: m[k] for k in ("titulo", "projetos", "tipo", "paginas_ou_url", "obs") if k in m}
            for m in materias.get(f"revista{ano}.md", [])
            if n in m["_paginas"]
        ]

        for k, (caixa, xref, info) in enumerate(unicas, 1):
            uso = {
                "pagina": n,
                "caixa_pt": [round(v, 1) for v in caixa],
                "fracao_da_pagina": round(caixa.get_area() / area.get_area(), 3),
                "materias": doc_materias,
                "texto_perto": texto_perto(blocos, caixa),
            }
            if xref and xref in vistos:
                vistos[xref]["usos"].append(uso)
                continue
            id_ = f"{id_pagina}-{k}"
            recorte = ARQUIVOS / f"{id_}-pagina.jpg"
            pagina.get_pixmap(dpi=DPI_RECORTE, clip=caixa).save(recorte, jpg_quality=88)
            arq_original = ""
            if xref:
                try:
                    arq_original = original(doc, xref, ARQUIVOS / id_).name
                except Exception as erro:
                    arq_original = f"[FALTA: original não extraído ({erro})]"
            # Pixels por polegada da imagem como impressa na página.
            dpi = round(min(info["width"] / (caixa.width / 72), info["height"] / (caixa.height / 72)))
            entrada = {
                "id": id_,
                "arquivo": f"arquivos/{arq_original}" if arq_original and not arq_original.startswith("[") else f"arquivos/{recorte.name}",
                "recorte": f"arquivos/{recorte.name}",
                "original": arq_original,
                "pagina_inteira": f"paginas/{id_pagina}.jpg",
                "fonte": f"acervo/revistas/{pdf.name}",
                "texto_da_revista": f"acervo/texto/revista{ano}.md",
                "ano_publicacao": int(ano),
                "largura": info["width"],
                "altura": info["height"],
                "dpi_na_pagina": dpi,
                "transformacao": [round(v, 3) for v in info["transform"]],
                "usos": [uso],
            }
            entradas.append(entrada)
            if xref:
                vistos[xref] = entrada
    return entradas, descartes


def main():
    anos = sys.argv[1:]
    pdfs = sorted(REVISTAS.glob("revista*.pdf"))
    if anos:
        pdfs = [p for p in pdfs if p.stem.replace("revista", "") in anos]
    for pasta in (ARQUIVOS, PAGINAS, CONTEXTO.parent):
        pasta.mkdir(parents=True, exist_ok=True)

    # Re-executável: apaga só o que é das revistas processadas agora.
    prefixos = tuple(f"rev{p.stem.replace('revista', '')}-" for p in pdfs)
    for pasta in (ARQUIVOS, PAGINAS):
        for f in pasta.iterdir():
            if f.name.startswith(prefixos):
                f.unlink()
    antigas = []
    if CONTEXTO.exists():
        antigas = [l for l in CONTEXTO.read_text(encoding="utf-8").splitlines() if l and not json.loads(l)["id"].startswith(prefixos)]

    materias = materias_do_indice()
    hoje = datetime.date.today().isoformat()
    novas = []
    for pdf in pdfs:
        entradas, descartes = extrair(pdf, materias)
        usos = sum(len(e["usos"]) for e in entradas)
        print(f"{pdf.name}: {len(entradas)} imagens ({usos} usos); descartes {dict(descartes)}")
        novas += [json.dumps({**e, "extraido_em": hoje}, ensure_ascii=False) for e in entradas]
    linhas = sorted(antigas + novas, key=lambda l: json.loads(l)["id"])
    CONTEXTO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"{len(novas)} imagens gravadas; {len(linhas)} no total em {CONTEXTO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
