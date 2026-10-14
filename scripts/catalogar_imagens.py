"""Monta o catálogo do acervo de imagens a partir das fichas.

Uso:
    python -I scripts/catalogar_imagens.py

Lê acervo/imagens/fichas/*.md e grava:
  acervo/imagens/catalogo.jsonl     uma linha por ficha, para busca rápida
                                    (skills e Claude); traz prioridade,
                                    se pode ser sugerida e as duplicatas
  scripts/indexacao/imagens.jsonl   linhas para o acervo/indice.csv

Duplicatas: mesma imagem em dois ids (capa e galeria, revista e notícia,
recorte e original). Acha por bytes iguais e por hash de diferença (dHash
de 256 bits da prévia) com até DISTANCIA bits diferentes e proporção
parecida, confirmado pela correlação dos tons de cinza numa miniatura
32x32 (CORRELACAO). Calibrado em 14/10/2026: o hash sozinho juntava
retratos diferentes sobre fundo liso e montagens de mesmo leiaute. Logos e gráficos só entram por bytes iguais: em fundo branco o
hash de logos diferentes coincide. Em cada grupo, `melhor` é a versão a
sugerir.

Prioridade de sugestão (decisão do usuário, 14/10/2026): 1 foto de
revista; 2 foto de notícia ou do site; 3 montagem; 4 os demais tipos,
só quando pedidos.
"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "acervo" / "imagens"
LADO = 16
DISTANCIA = 50
CORRELACAO = 0.93
QUALIDADE = {"boa": 3, "media": 2, "baixa": 1}


def valor(bruto):
    bruto = bruto.strip()
    if bruto.startswith("[") and bruto.endswith("]"):
        return [str(valor(v)) for v in bruto[1:-1].split(",") if v.strip()]
    if len(bruto) >= 2 and bruto[0] == bruto[-1] == '"':
        return bruto[1:-1]
    if bruto.isdigit():
        return int(bruto)
    return bruto


def ler_ficha(f):
    texto = f.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", texto, re.S)
    d = {}
    for linha in m.group(1).splitlines():
        chave, resto = linha.split(":", 1)
        d[chave] = valor(resto)
    corpo = m.group(2)
    secao = lambda nome: (re.search(rf"## {nome}\n\n(.*?)(?=\n## |\Z)", corpo, re.S) or [None, ""])[1]
    d["_descricao"] = " ".join(secao("Descrição").split())
    d["_uso"] = " ".join(secao("Uso sugerido").split())
    return d


def dhash(caminho):
    pagina = pymupdf.open(caminho)[0]
    r = pagina.rect
    pix = pagina.get_pixmap(matrix=pymupdf.Matrix((LADO + 1) / r.width, LADO / r.height), colorspace=pymupdf.csGRAY, alpha=False)
    px = pix.samples
    w = pix.width
    bits = 0
    for y in range(LADO):
        for x in range(LADO):
            bits = (bits << 1) | (px[y * w + x] > px[y * w + x + 1])
    return bits


def miniatura(caminho, n=32):
    pagina = pymupdf.open(caminho)[0]
    r = pagina.rect
    pix = pagina.get_pixmap(matrix=pymupdf.Matrix(n / r.width, n / r.height), colorspace=pymupdf.csGRAY, alpha=False)
    s, w = pix.samples, pix.width
    v = [s[y * w + x] for y in range(n) for x in range(n)]
    m = sum(v) / len(v)
    v = [x - m for x in v]
    norma = sum(x * x for x in v) ** 0.5
    return [x / norma for x in v] if norma else v


def prioridade(d):
    if d["tipo"] == "foto":
        return 1 if d["id"].startswith("rev") else 2
    return 3 if d["tipo"] == "montagem" else 4


def main():
    fichas = [ler_ficha(f) for f in sorted((PASTA / "fichas").glob("*.md"))]
    por_id = {d["id"]: d for d in fichas}
    for d in fichas:
        d["_sha"] = hashlib.sha256((PASTA / d["arquivo"]).read_bytes()).hexdigest()
        previa = PASTA / "previas" / f"{d['id']}.jpg"
        d["_dhash"] = dhash(previa) if previa.exists() else None
        d["_mini"] = miniatura(previa) if previa.exists() else None
        d["_proporcao"] = d["largura"] / d["altura"] if d["altura"] else 0

    # União de grupos: bytes iguais ou hash próximo.
    pai = {d["id"]: d["id"] for d in fichas}
    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i
    def unir(a, b):
        pai[raiz(a)] = raiz(b)
    por_sha = collections.defaultdict(list)
    for d in fichas:
        por_sha[d["_sha"]].append(d["id"])
    for ids in por_sha.values():
        for i in ids[1:]:
            unir(ids[0], i)
    candidatas = [d for d in fichas if d["_dhash"] is not None and d["tipo"] not in ("logo", "grafico")
                  and 32 <= bin(d["_dhash"]).count("1") <= 224]
    for i, a in enumerate(candidatas):
        for b in candidatas[i + 1:]:
            if (bin(a["_dhash"] ^ b["_dhash"]).count("1") <= DISTANCIA
                    and abs(a["_proporcao"] - b["_proporcao"]) <= 0.12 * max(a["_proporcao"], b["_proporcao"])
                    and sum(x * y for x, y in zip(a["_mini"], b["_mini"])) >= CORRELACAO):
                unir(a["id"], b["id"])
    grupos = collections.defaultdict(list)
    for d in fichas:
        grupos[raiz(d["id"])].append(d["id"])

    def sugerivel(d):
        return bool(d["usos_sugeridos"]) and d["origem"] != "banco de imagem provável"

    linhas, indice = [], []
    for d in fichas:
        grupo = sorted(grupos[raiz(d["id"])])
        melhor = max(grupo, key=lambda i: (sugerivel(por_id[i]), QUALIDADE.get(por_id[i]["qualidade"], 0),
                                            por_id[i]["largura"] * por_id[i]["altura"], i))
        ano = str(d["data"])[:4] if d["data"] else ""
        linhas.append({
            "id": d["id"], "arquivo": f"acervo/imagens/{d['arquivo']}", "ficha": f"acervo/imagens/fichas/{d['id']}.md",
            "fonte": d["fonte"], "ano": int(ano) if ano.isdigit() else None, "data_da_foto": d["data_da_foto"],
            "tipo": d["tipo"], "origem": d["origem"], "projetos": d["projetos"], "materia": d["materia"],
            "local": d["local"], "pessoas": d["pessoas"], "pessoas_nomeadas": d["pessoas_nomeadas"],
            "criancas": d["criancas"], "qualidade": d["qualidade"], "orientacao": d["orientacao"],
            "largura": d["largura"], "altura": d["altura"], "usos_sugeridos": d["usos_sugeridos"], "tags": d["tags"],
            "credito": d["credito"], "sugerivel": sugerivel(d), "prioridade": prioridade(d),
            "duplicatas": [i for i in grupo if i != d["id"]], "melhor": melhor,
            "descricao": d["_descricao"][:400],
        })
        indice.append({
            "fonte": "imagem", "arquivo": f"imagens/fichas/{d['id']}.md", "ano": int(ano) if ano.isdigit() else None,
            "titulo": d["materia"] or d["id"], "projetos": d["projetos"], "paginas_ou_url": d["fonte"],
            "tipo": "imagem", "obs": f"{d['tipo']}; " + ", ".join(d["tags"]),
        })
    (PASTA / "catalogo.jsonl").write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in linhas) + "\n",
                                          encoding="utf-8", newline="\n")
    (RAIZ / "scripts" / "indexacao" / "imagens.jsonl").write_text(
        "\n".join(json.dumps(l, ensure_ascii=False) for l in indice) + "\n", encoding="utf-8", newline="\n")
    multi = [g for g in grupos.values() if len(g) > 1]
    print(f"{len(linhas)} fichas; {len(multi)} grupos de duplicatas ({sum(len(g) for g in multi)} fichas)")
    print(f"sugeríveis: {sum(l['sugerivel'] for l in linhas)}; por prioridade: "
          f"{dict(sorted(collections.Counter(l['prioridade'] for l in linhas if l['sugerivel']).items()))}")


if __name__ == "__main__":
    main()
