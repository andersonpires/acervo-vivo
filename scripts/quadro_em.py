"""Extrai quadros inteiros de um vídeo em tempos específicos.

Uso:
    python scripts/quadro_em.py VIDEO.mp4 PASTA_DE_SAIDA m:ss [m:ss ...] [--passo 0.5 --janela 3]

Para cada tempo pedido, grava quadros inteiros (não só a metade de
baixo) de "tempo" até "tempo + janela", a cada "passo" segundos. Serve
para completar o que as folhas de quadros cortaram: legenda de nome
ainda entrando na tela, cartela de parceiros no fim do vídeo.

Rodar sem a opção -I do Python (pacotes instalados com --user).
"""

import sys
from pathlib import Path

import av


def segundos(t):
    m, s = t.split(":")
    return int(m) * 60 + float(s)


def main():
    args = sys.argv[1:]
    passo, janela = 0.5, 3.0
    if "--passo" in args:
        i = args.index("--passo"); passo = float(args[i + 1]); del args[i:i + 2]
    if "--janela" in args:
        i = args.index("--janela"); janela = float(args[i + 1]); del args[i:i + 2]
    video, destino, tempos = Path(args[0]), Path(args[1]), [segundos(t) for t in args[2:]]
    destino.mkdir(parents=True, exist_ok=True)
    alvos = sorted({round(t + k * passo, 2) for t in tempos for k in range(int(janela / passo) + 1)})
    with av.open(str(video)) as arq:
        fluxo = arq.streams.video[0]
        i = 0
        for q in arq.decode(fluxo):
            if i >= len(alvos):
                break
            t = float(q.pts * fluxo.time_base) if q.pts is not None else 0.0
            if t + 1e-6 >= alvos[i]:
                nome = f"{video.stem.split('.')[0]}_{int(t // 60)}m{t % 60:05.2f}s.png"
                q.to_image().save(destino / nome)
                while i < len(alvos) and alvos[i] <= t + 1e-6:
                    i += 1
    print(len(list(destino.glob('*.png'))), "quadros em", destino)


if __name__ == "__main__":
    main()
