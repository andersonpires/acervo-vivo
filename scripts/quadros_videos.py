"""Monta folhas de quadros dos vídeos, para ler o nome de quem fala.

Uso:
    python scripts/quadros_videos.py PASTA_DOS_VIDEOS PASTA_DE_SAIDA [segundos]

Para cada "<n>-<id>.video.mp4", tira um quadro a cada N segundos (padrão
4), recorta a metade de baixo da tela, onde costuma vir a legenda com
nome e papel de quem fala, e junta os recortes em folhas PNG com o tempo
de cada um. As folhas servem para conferir a autoria das falas: pela
regra 3 do projeto, depoimento só entra com autor.

Rodar sem a opção -I do Python (pacotes instalados com --user).
"""

import sys
from pathlib import Path

import av
from PIL import Image, ImageDraw

LARGURA = 400
COLUNAS = 3
LINHAS = 8


def quadros(video, passo):
    with av.open(str(video)) as arq:
        fluxo = arq.streams.video[0]
        proximo = 0.0
        for q in arq.decode(fluxo):
            t = float(q.pts * fluxo.time_base) if q.pts is not None else 0.0
            if t + 1e-6 < proximo:
                continue
            img = q.to_image()
            w, h = img.size
            baixo = img.crop((0, int(h * 0.5), w, h))
            escala = LARGURA / w
            yield t, baixo.resize((LARGURA, int(baixo.height * escala)))
            proximo = t + passo


def main():
    origem, destino = Path(sys.argv[1]), Path(sys.argv[2])
    passo = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
    destino.mkdir(parents=True, exist_ok=True)
    for video in sorted(origem.glob("*.video.mp4")):
        nome = video.name.replace(".video.mp4", "")
        lista = list(quadros(video, passo))
        if not lista:
            continue
        alt = lista[0][1].height + 18
        por_folha = COLUNAS * LINHAS
        for f in range(0, len(lista), por_folha):
            lote = lista[f:f + por_folha]
            folha = Image.new("RGB", (COLUNAS * LARGURA, LINHAS * alt), "white")
            d = ImageDraw.Draw(folha)
            for i, (t, img) in enumerate(lote):
                x, y = (i % COLUNAS) * LARGURA, (i // COLUNAS) * alt
                folha.paste(img, (x, y + 18))
                d.text((x + 4, y + 3), f"{int(t // 60)}:{int(t % 60):02d}", fill="black")
            folha.save(destino / f"{nome}_{f // por_folha + 1}.png")
        print(nome, len(lista), "quadros")


if __name__ == "__main__":
    main()
