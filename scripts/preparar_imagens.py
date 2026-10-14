"""Prepara o acervo de imagens para a análise (fase 3).

Uso:
    python -I scripts/preparar_imagens.py

Lê acervo/imagens/contexto/*.jsonl e grava, fora do git:
  previas/<id>.jpg        cópia leve (lado maior até 1000 px) para ver
                          rápido; do original quando há, senão do recorte
  lotes/<lote>.jsonl      o contexto de cada imagem do lote, com os
                          projetos do índice (notícias e páginas do site)
  folhas/<lote>-N.png     folha de contato do lote, com o id de cada imagem

Lotes: revistas por edição, notícias por ano, site em um lote; nenhum
lote passa de TAMANHO imagens.
"""
import collections
import json
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "acervo" / "imagens"
INDEXACAO = RAIZ / "scripts" / "indexacao"
LADO = 1000
TAMANHO = 45
POR_FOLHA = 48


def projetos_do_indice():
    """Projetos por arquivo do acervo (notícias e páginas do site)."""
    projetos = {}
    for jsonl in list(INDEXACAO.glob("not_*.jsonl")) + [INDEXACAO / "site.jsonl"]:
        for linha in jsonl.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                m = json.loads(linha)
                chave = m["arquivo"] if m["fonte"] == "site" else "noticias/" + m["arquivo"]
                projetos[chave] = m.get("projetos", [])
    return projetos


def abrir(caminho):
    tipo = "jpg" if caminho.suffix.lower() in (".jfif", ".jpeg") else None
    return pymupdf.open(caminho, filetype=tipo) if tipo else pymupdf.open(caminho)


def previa(origem, destino):
    pagina = abrir(origem)[0]
    escala = LADO / max(pagina.rect.width, pagina.rect.height)
    if origem.suffix.lower() != ".svg":
        escala = min(escala, 1)
    pagina.get_pixmap(matrix=pymupdf.Matrix(escala, escala), alpha=False).save(destino, jpg_quality=80)


def folha(ids, destino):
    col, cel = 8, 150
    lin = (len(ids) + col - 1) // col
    doc = pymupdf.open()
    pg = doc.new_page(width=col * cel, height=lin * (cel + 14))
    for i, id_ in enumerate(ids):
        x, y = (i % col) * cel, (i // col) * (cel + 14)
        pg.insert_image(pymupdf.Rect(x + 3, y + 3, x + cel - 3, y + cel - 3), filename=str(PASTA / "previas" / f"{id_}.jpg"), keep_proportion=True)
        pg.insert_text((x + 4, y + cel + 9), id_, fontsize=7)
    pg.get_pixmap(dpi=90).save(destino)


def main():
    for nome in ("previas", "lotes", "folhas"):
        (PASTA / nome).mkdir(exist_ok=True)
        for f in (PASTA / nome).iterdir():
            f.unlink()
    projetos = projetos_do_indice()
    grupos = collections.defaultdict(list)

    for linha in (PASTA / "contexto" / "site.jsonl").read_text(encoding="utf-8").splitlines():
        if not linha:
            continue
        e = json.loads(linha)
        for u in e["usos"]:
            chave = u["arquivo_acervo"].removeprefix("acervo/")
            u["projetos_do_indice"] = projetos.get(chave, [])
        grupo = f"not{e['id'][4:8]}" if e["id"].startswith("not-") else "site"
        grupos[grupo].append(e)
    for linha in (PASTA / "contexto" / "revistas.jsonl").read_text(encoding="utf-8").splitlines():
        if linha:
            e = json.loads(linha)
            # Imagem achada sob outra na mesma caixa (id "-sK") vai para um
            # lote à parte, para não mudar a composição dos lotes já feitos.
            grupo = "revsob" if "-s" in e["id"].rsplit("-p", 1)[1] else e["id"][:7]
            grupos[grupo].append(e)
    # Capas e páginas de parceiros renderizadas inteiras.
    especiais = PASTA / "contexto" / "paginas_especiais.jsonl"
    if especiais.exists():
        for linha in especiais.read_text(encoding="utf-8").splitlines():
            if linha:
                grupos["revpag"].append(json.loads(linha))

    falhas = []
    for grupo in sorted(grupos):
        itens = grupos[grupo]
        partes = max(1, -(-len(itens) // TAMANHO))
        tam = -(-len(itens) // partes)
        for p in range(partes):
            lote = f"{grupo}-{p + 1}" if partes > 1 else grupo
            parte = itens[p * tam:(p + 1) * tam]
            for e in parte:
                origem = PASTA / e["arquivo"]
                e["previa"] = f"previas/{e['id']}.jpg"
                try:
                    previa(origem, PASTA / e["previa"])
                except Exception as erro:
                    falhas.append(f"{e['id']}: {erro}")
                    previa(PASTA / e.get("recorte", e["arquivo"]), PASTA / e["previa"])
            (PASTA / "lotes" / f"{lote}.jsonl").write_text(
                "\n".join(json.dumps(e, ensure_ascii=False) for e in parte) + "\n", encoding="utf-8", newline="\n")
            ids = [e["id"] for e in parte]
            for f in range(0, len(ids), POR_FOLHA):
                folha(ids[f:f + POR_FOLHA], PASTA / "folhas" / f"{lote}-{f // POR_FOLHA + 1}.png")
            print(f"{lote}: {len(parte)}")
    print(f"{sum(len(v) for v in grupos.values())} imagens em lotes")
    if falhas:
        print("prévia do recorte no lugar do original:", *falhas, sep="\n  ")


if __name__ == "__main__":
    main()
