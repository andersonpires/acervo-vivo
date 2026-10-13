"""Transcreve o áudio dos vídeos com o Whisper local (faster-whisper).

Uso:
    python scripts/transcrever_videos.py PASTA_DOS_AUDIOS PASTA_DE_SAIDA [modelo] [cpu|cuda]

Para cada "<n>-<id>.audio.m4a" (ou .webm) grava "<n>-<id>.json" com os trechos
(início, fim, texto). Nada sai do computador: o modelo roda aqui.
Por padrão roda no processador. A GPU desta máquina (GTX 1650) carrega o
modelo, mas falta a cuBLAS da NVIDIA para transcrever; "cuda" só vale
depois de instalar as bibliotecas CUDA 12.

Rodar sem a opção -I do Python: o faster-whisper foi instalado com
--user, e o modo isolado ignora esses pacotes.
"""

import json
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel


def ler_audio(caminho):
    """Áudio em 16 kHz, mono, float32, como o Whisper espera.

    Decodifica aqui porque o faster-whisper 1.2 chama a biblioteca av com
    um parâmetro que a av 19 removeu; entregar o áudio pronto evita isso.
    """
    import av
    import numpy as np

    partes = []
    with av.open(str(caminho)) as arq:
        conversor = av.AudioResampler(format="s16", layout="mono", rate=16000)
        for quadro in arq.decode(audio=0):
            for q in conversor.resample(quadro):
                partes.append(q.to_ndarray().reshape(-1))
        for q in conversor.resample(None):
            partes.append(q.to_ndarray().reshape(-1))
    return np.concatenate(partes).astype(np.float32) / 32768.0


def carregar(modelo, dispositivo):
    if dispositivo == "cpu":
        return WhisperModel(modelo, device="cpu", compute_type="int8"), "cpu"
    try:
        m = WhisperModel(modelo, device="cuda", compute_type="float16")
        return m, "cuda"
    except Exception as e:  # sem CUDA ou sem as bibliotecas dela
        print(f"GPU indisponível ({str(e)[:80]}); usando o processador")
        return WhisperModel(modelo, device="cpu", compute_type="int8"), "cpu"


def main():
    origem, destino = Path(sys.argv[1]), Path(sys.argv[2])
    modelo = sys.argv[3] if len(sys.argv) > 3 else "medium"
    destino.mkdir(parents=True, exist_ok=True)
    dispositivo = sys.argv[4] if len(sys.argv) > 4 else "cpu"
    m, onde = carregar(modelo, dispositivo)
    print(f"modelo {modelo} em {onde}")
    for audio in sorted(a for a in origem.glob("*.audio.*") if a.suffix in (".m4a", ".webm")):
        nome = audio.name.split(".audio.")[0]
        saida = destino / f"{nome}.json"
        if saida.exists():
            print("já feito", nome)
            continue
        t0 = time.time()
        trechos, info = m.transcribe(
            ler_audio(audio), language="pt", vad_filter=True, beam_size=5,
            condition_on_previous_text=False,
        )
        lista = [{"inicio": round(s.start, 1), "fim": round(s.end, 1), "texto": s.text.strip()} for s in trechos]
        saida.write_text(json.dumps({"duracao": round(info.duration, 1), "modelo": modelo, "trechos": lista},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{nome}: {info.duration:.0f}s de áudio em {time.time() - t0:.0f}s, {len(lista)} trechos")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
