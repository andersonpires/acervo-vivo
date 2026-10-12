"""Monta acervo/indice.csv a partir das linhas JSONL da indexação.

Uso:
    python -I scripts/montar_indice.py PASTA_COM_JSONL

Cada linha JSONL traz fonte, arquivo, ano, título, projetos, páginas ou
URL, tipo e observação. O programa NÃO vem da indexação: é atribuído
aqui, pelo cadastro em projetos/cadastro.csv, para ser o mesmo em todo o
índice.

Saídas:
    acervo/indice.csv     UTF-8 com BOM e separador ";" (abre em colunas
                          no Excel pt-BR; sem linha "sep=;", que faria o
                          Excel ignorar o BOM)
    acervo/volume.md      material por projeto e por ano
"""

import collections
import csv
import glob
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Programa e situação de cada projeto vêm de projetos/cadastro.csv, a fonte
# única: quem decide programa ou situação edita o cadastro, não este script.
CADASTRO = RAIZ / "projetos" / "cadastro.csv"


def ler_cadastro():
    with open(CADASTRO, encoding="utf-8-sig", newline="") as f:
        return {r["projeto"]: r for r in csv.DictReader(f, delimiter=";")}


PROJETOS = ler_cadastro()
PROGRAMAS = {nome: r["programa"] for nome, r in PROJETOS.items()}

# Grafia única para o que os agentes de indexação marcaram como "NOVO: ...".
NOVOS = {
    "Academia Cisco": "Academia Cisco",
    "Academia Cisco (Cisco Networking Academy)": "Academia Cisco",
    "Programa Microsoft Students to Business (S2B)": "Microsoft S2B",
    "Curso Introdução às TICs": "Curso Introdução às TICs",
    "Estudo de viabilidade de Ensino Híbrido para o Município de Eusébio": "Estudo de Ensino Híbrido do Eusébio",
    "Gestão de Projetos": "Gestão de Projetos (negócio social)",
    "Condomínio de Empresas Sociais": "Condomínio de Empresas Sociais",
    "Plataforma Sala de Aula Iteva": "Sala de Aula Iteva",
    "TSC Construções": "TSC Construções",
    "OrangeBOX": "OrangeBOX",
    "Ninho de Ideias": "Ninho de Ideias",
    "Scriple": "Scriple",
    "Empodera Mulher": "Empodera Mulher",
    "Contação de Histórias Reversas": "Contação de Histórias Reversas",
    "Projeto Água de Beber": "Água de Beber",
    "Festival CumbuCOR": "Festival CumbuCOR",
    "NoCorre": "NoCorre",
}


def normalizar(p):
    if p.startswith("NOVO:"):
        nome = p[5:].strip()
        return NOVOS.get(nome, "NOVO: " + nome)
    return p

COLUNAS = ["fonte", "arquivo", "ano", "titulo", "programa", "projetos", "paginas_ou_url", "tipo", "obs"]
TIPOS = {"reportagem", "editorial", "entrevista", "nota", "notícia", "artigo", "depoimento"}


def main(pasta):
    linhas, problemas = [], []
    for f in sorted(glob.glob(os.path.join(pasta, "*.jsonl"))):
        for n, bruta in enumerate(open(f, encoding="utf-8"), start=1):
            if not bruta.strip():
                continue
            r = json.loads(bruta)
            onde = f"{Path(f).name}:{n}"
            projetos = [normalizar(p) for p in r.get("projetos") or []]
            desconhecidos = [p for p in projetos if p not in PROGRAMAS]
            if desconhecidos:
                problemas.append(f"{onde}: projeto fora da tabela {desconhecidos}")
            if r.get("tipo") not in TIPOS:
                problemas.append(f"{onde}: tipo '{r.get('tipo')}' fora da lista")
            programas = []
            for p in projetos:
                prog = PROGRAMAS.get(p, f"[programa a definir: {p}]")
                if prog not in programas:
                    programas.append(prog)
            linhas.append({
                "fonte": r["fonte"],
                "arquivo": r["arquivo"],
                "ano": int(r["ano"]),
                "titulo": r["titulo"],
                "programa": "; ".join(programas),
                "projetos": "; ".join(projetos),
                "paginas_ou_url": r["paginas_ou_url"],
                "tipo": r["tipo"],
                "obs": r.get("obs", ""),
            })

    linhas.sort(key=lambda r: (r["ano"], r["fonte"] != "revista", r["arquivo"], primeira_pagina(r["paginas_ou_url"])))

    destino = RAIZ / "acervo" / "indice.csv"
    with open(destino, "w", encoding="utf-8-sig", newline="") as saida:
        w = csv.DictWriter(saida, fieldnames=COLUNAS, delimiter=";")
        w.writeheader()
        w.writerows(linhas)

    escrever_volume(linhas)
    print(f"{len(linhas)} linhas em {destino.relative_to(RAIZ)}")
    for p in problemas:
        print("PROBLEMA", p)


def primeira_pagina(v):
    try:
        return int(str(v).split("-")[0].split(";")[0].strip())
    except ValueError:
        return 0


def curto(programa):
    """Programa sem as notas de fonte, para caber na tabela."""
    return re.sub(r" \([^)]*\)", "", programa).split(";")[0]


def escrever_volume(linhas):
    """Tabela projeto x ano: quantos textos citam o projeto de forma substantiva."""
    anos = sorted({r["ano"] for r in linhas})
    por = collections.defaultdict(collections.Counter)
    fontes = collections.defaultdict(collections.Counter)
    for r in linhas:
        for p in filter(None, r["projetos"].split("; ")):
            por[p][r["ano"]] += 1
            fontes[p][r["fonte"]] += 1
    ordem = sorted(por, key=lambda p: -sum(por[p].values()))

    md = [
        "# Volume de material por projeto",
        "",
        "Número de textos (matérias de revista e notícias do site) que tratam",
        "do projeto de forma substantiva, por ano. Um texto pode contar para",
        "mais de um projeto. Gerado por `scripts/montar_indice.py` a partir de",
        "`acervo/indice.csv`.",
        "",
        "| Projeto | Programa | Situação | Revista | Notícia | Total | " + " | ".join(str(a)[2:] for a in anos) + " |",
        "|---|---|---|---|---|---|" + "---|" * len(anos),
    ]
    for p in ordem:
        celulas = [str(por[p][a]) if por[p][a] else "" for a in anos]
        situacao = PROJETOS.get(p, {}).get("situacao", "?")
        md.append(f"| {p} | {curto(PROGRAMAS.get(p, '?'))} | {situacao} | {fontes[p]['revista']} | {fontes[p]['noticia']} | {sum(por[p].values())} | " + " | ".join(celulas) + " |")
    md.append("")
    md.append("Anos na tabela: " + ", ".join(str(a) for a in anos) + ". Revistas cobrem 2010 a 2023; notícias, 2011 a 2026.")
    md.append("")
    (RAIZ / "acervo" / "volume.md").write_text("\n".join(md), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1])
