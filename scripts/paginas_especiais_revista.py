"""Grava a capa e a página de parceiros de cada revista como imagem.

Uso:
    python -I scripts/paginas_especiais_revista.py

Capas desenhadas em vetor e logos de parceiros em vetor não saem como
imagem embutida (scripts/extrair_imagens_revista.py só pega imagens).
Aqui a página inteira é renderizada, com tudo o que o leitor vê:
  arquivos/revAAAA-capa.jpg            capa (p. 1), 150 dpi
  arquivos/revAAAA-parceiros-pNN.jpg   página de parceiros, 150 dpi
  contexto/paginas_especiais.jsonl     uma linha por imagem

As páginas de parceiros foram escolhidas olhando as páginas
(14/10/2026). De 2020 a 2023 o painel de logos já sai como imagem única
na extração comum.
"""
import datetime
import json
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "acervo" / "imagens"
DPI = 150
PARCEIROS = {
    "2010": 27, "2011": 4, "2012": 4, "2013": 4, "2014": 4, "2015": 4,
    "2016": 28, "2017": 4, "2018": 4, "2019": 4,
}


def main():
    hoje = datetime.date.today().isoformat()
    linhas = []
    for pdf in sorted((RAIZ / "acervo" / "revistas").glob("revista*.pdf")):
        ano = pdf.stem.replace("revista", "")
        doc = pymupdf.open(pdf)
        alvos = [("capa", 1, "capa da edição")]
        if ano in PARCEIROS:
            n = PARCEIROS[ano]
            alvos.append((f"parceiros-p{n:02d}", n, "página de parceiros"))
        for sufixo, n, papel in alvos:
            id_ = f"rev{ano}-{sufixo}"
            pix = doc[n - 1].get_pixmap(dpi=DPI)
            pix.save(PASTA / "arquivos" / f"{id_}.jpg", jpg_quality=88)
            linhas.append(json.dumps({
                "id": id_,
                "arquivo": f"arquivos/{id_}.jpg",
                "recorte": f"arquivos/{id_}.jpg",
                "original": "",
                "pagina_inteira": f"paginas/rev{ano}-p{n:02d}.jpg",
                "fonte": f"acervo/revistas/{pdf.name}",
                "texto_da_revista": f"acervo/texto/revista{ano}.md",
                "ano_publicacao": int(ano),
                "largura": pix.width,
                "altura": pix.height,
                "usos": [{"pagina": n, "papel": papel}],
                "extraido_em": hoje,
            }, ensure_ascii=False))
    (PASTA / "contexto" / "paginas_especiais.jsonl").write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(linhas)} páginas gravadas")


if __name__ == "__main__":
    main()
