"""Confere as fichas de acervo/imagens/fichas.

Uso:
    python -I scripts/conferir_fichas_imagens.py [lote ou prefixo...]

Um lote (nome de lotes/<lote>.jsonl) confere só as imagens dele.

Para cada ficha: cabeçalho YAML válido, id igual ao nome do arquivo,
campos na ordem do modelo, valores dos campos fechados dentro da lista,
projetos no cadastro, arquivo existente, corpo com as três seções e
nenhum travessão, meia-risca ou mojibake. Também confere se cada id
das triagens com decisão "ficha" tem ficha.
"""
import csv
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "acervo" / "imagens"
CAMPOS = [
    "id", "arquivo", "fonte", "data", "data_da_foto", "tipo", "origem", "projetos", "materia",
    "legenda", "credito", "local", "pessoas", "pessoas_nomeadas", "criancas", "largura", "altura",
    "orientacao", "qualidade", "usos_sugeridos", "tags",
]
FECHADOS = {
    "tipo": {"foto", "ilustracao", "montagem", "logo", "grafico", "capa", "outro"},
    "origem": {"iteva", "banco de imagem provável", "terceiro", "incerto"},
    "criancas": {"sim", "nao", "incerto"},
    "orientacao": {"paisagem", "retrato", "quadrada"},
    "qualidade": {"boa", "media", "baixa"},
}
USOS = {
    "capa", "abertura de matéria", "ilustração de trecho", "retrato de depoimento", "galeria",
    "post", "relatório", "apresentação", "página de projeto", "lista de parceiros",
}
PROIBIDOS = re.compile("[" + chr(0) + "-" + chr(8) + chr(11) + "-" + chr(31) + chr(0x2014) + chr(0x2013) + chr(0xFFFD) + "]|[" + chr(0xC2) + chr(0xC3) + "][" + chr(0x80) + "-" + chr(0xBF) + "]")


def valor(bruto):
    """Valor do cabeçalho plano das fichas: texto, número ou lista [a, b]."""
    bruto = bruto.strip()
    if bruto.startswith("[") and bruto.endswith("]"):
        return [valor(v) for v in bruto[1:-1].split(",") if v.strip()]
    if len(bruto) >= 2 and bruto[0] == bruto[-1] == '"':
        return bruto[1:-1]
    if bruto.isdigit():
        return int(bruto)
    return bruto


def cabecalho(texto):
    """Lê o cabeçalho (uma chave por linha). Devolve dict ou erro."""
    d = {}
    for n, linha in enumerate(texto.splitlines(), 1):
        if ":" not in linha or linha.startswith(" "):
            raise ValueError(f"linha {n} fora do formato: {linha!r}")
        chave, resto = linha.split(":", 1)
        if chave in d:
            raise ValueError(f"campo repetido: {chave}")
        d[chave] = valor(resto)
    return d


def projetos_validos():
    with open(RAIZ / "projetos" / "cadastro.csv", encoding="utf-8-sig") as f:
        return {linha["projeto"] for linha in csv.DictReader(f, delimiter=";")}


def conferir(ficha, validos):
    erros = []
    texto = ficha.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", texto, re.S)
    if not m:
        return ["sem cabeçalho YAML"]
    try:
        d = cabecalho(m.group(1))
    except ValueError as erro:
        return [f"cabeçalho inválido: {erro}"]
    if list(d) != CAMPOS:
        erros.append(f"campos fora do modelo: {[c for c in d if c not in CAMPOS]} faltam {[c for c in CAMPOS if c not in d]}")
    if d.get("id") != ficha.stem:
        erros.append("id diferente do nome do arquivo")
    for campo, aceitos in FECHADOS.items():
        if d.get(campo) not in aceitos:
            erros.append(f"{campo}: {d.get(campo)!r}")
    for p in d.get("projetos") or []:
        if p not in validos and not str(p).startswith("NOVO:"):
            erros.append(f"projeto fora do cadastro: {p}")
    for u in d.get("usos_sugeridos") or []:
        if u not in USOS:
            erros.append(f"uso fora da lista: {u}")
    if not (PASTA / str(d.get("arquivo"))).exists():
        erros.append(f"arquivo não existe: {d.get('arquivo')}")
    for secao in ("## Contexto", "## Descrição", "## Uso sugerido"):
        if secao not in m.group(2):
            erros.append(f"falta {secao}")
    ruins = PROIBIDOS.findall(texto)
    if ruins:
        erros.append(f"caracteres proibidos: {ruins[:5]}")
    return erros


def main():
    filtros = sys.argv[1:]
    validos = projetos_validos()
    fichas = sorted((PASTA / "fichas").glob("*.md"))
    triagens = sorted((PASTA / "triagem").glob("*.jsonl")) if (PASTA / "triagem").exists() else []
    if filtros:
        ids = set()
        for filtro in filtros:
            lote = PASTA / "lotes" / f"{filtro}.jsonl"
            if lote.exists():
                do_lote = {json.loads(l)["id"] for l in lote.read_text(encoding="utf-8").splitlines() if l.strip()}
                ids |= do_lote
                if not (PASTA / "triagem" / f"{filtro}.jsonl").exists():
                    print(f"{filtro}: falta triagem/{filtro}.jsonl")
                else:
                    vistos = {json.loads(l)["id"] for l in (PASTA / "triagem" / f"{filtro}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
                    for falta in sorted(do_lote - vistos):
                        print(f"{filtro}: {falta} sem linha na triagem")
        fichas = [f for f in fichas if f.stem in ids or (not ids and f.stem.startswith(tuple(filtros)))]
        triagens = [t for t in triagens if t.stem in filtros or (not ids and t.stem.startswith(tuple(filtros)))]
    problemas = 0
    for ficha in fichas:
        erros = conferir(ficha, validos)
        if erros:
            problemas += 1
            print(f"{ficha.name}: " + "; ".join(erros))
    for t in triagens:
        for linha in t.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                e = json.loads(linha)
                if e["decisao"] == "ficha" and not (PASTA / "fichas" / f"{e['id']}.md").exists():
                    problemas += 1
                    print(f"{t.name}: {e['id']} marcado ficha e sem ficha")
    print(f"{len(fichas)} fichas, {len(triagens)} triagens conferidas; {problemas} com problema")


if __name__ == "__main__":
    main()
