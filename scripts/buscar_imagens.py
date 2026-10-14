"""Busca imagens no catálogo para sugerir num texto ou roteiro.

Uso:
    python -I scripts/buscar_imagens.py --projeto Construcom --busca "tijolo idosos" [opções]

Opções:
    --projeto NOME     projeto do cadastro (pode repetir); sem ele, busca em todos
    --busca "termos"   palavras procuradas nas tags, na descrição e na matéria
    --tipo TIPO        foto, montagem, ilustracao, logo, grafico, capa, outro
                       (pode repetir). Padrão: foto e montagem, porque as
                       demais só entram quando quem pede quer esse tipo
    --qualidade Q      mínima: baixa, media ou boa (padrão: baixa)
    --sem-criancas     tira imagens com criança ou com dúvida
    --desde ANO        só publicadas a partir desse ano
    --n N              quantas devolver (padrão: 12)
    --todas            inclui as que não devem ser sugeridas (banco de
                       imagem, curadoria), para consulta

Ordem (decisão do usuário, 14/10/2026): fotos de revista primeiro, depois
fotos de notícia e do site, depois montagens; dentro de cada faixa, mais
termos achados, melhor qualidade e mais recente. Cada grupo de duplicatas
aparece uma vez, pela melhor versão.
"""
import argparse
import json
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / "acervo" / "imagens" / "catalogo.jsonl"
QUALIDADE = {"baixa": 1, "media": 2, "boa": 3}


def simples(texto):
    """Minúsculas e sem acento, para comparar palavras."""
    t = unicodedata.normalize("NFD", str(texto).lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--projeto", action="append", default=[])
    p.add_argument("--busca", default="")
    p.add_argument("--tipo", action="append", default=[])
    p.add_argument("--qualidade", default="baixa", choices=QUALIDADE)
    p.add_argument("--sem-criancas", action="store_true")
    p.add_argument("--desde", type=int)
    p.add_argument("--n", type=int, default=12)
    p.add_argument("--todas", action="store_true")
    a = p.parse_args()

    tipos = set(a.tipo) or {"foto", "montagem"}
    termos = [simples(t) for t in a.busca.split() if len(t) > 2]
    projetos = {simples(x) for x in a.projeto}
    linhas = [json.loads(l) for l in CATALOGO.read_text(encoding="utf-8").splitlines() if l.strip()]

    achadas = []
    for l in linhas:
        if l["id"] != l["melhor"]:
            continue
        if not a.todas and not l["sugerivel"]:
            continue
        if l["tipo"] not in tipos or QUALIDADE.get(l["qualidade"], 0) < QUALIDADE[a.qualidade]:
            continue
        if a.sem_criancas and l["criancas"] != "nao":
            continue
        if a.desde and (l["ano"] or 0) < a.desde:
            continue
        if projetos and not projetos & {simples(x) for x in l["projetos"]}:
            continue
        texto = simples(" ".join([" ".join(l["tags"]), l["descricao"], l["materia"], l["local"]]))
        acertos = sum(1 for t in termos if t in texto)
        if termos and not acertos:
            continue
        achadas.append((l["prioridade"], -acertos, -QUALIDADE.get(l["qualidade"], 0), -(l["ano"] or 0), l["id"], l))

    achadas.sort(key=lambda x: x[:5])
    print(f"{len(achadas)} imagens; as {min(a.n, len(achadas))} primeiras:\n")
    for *_, l in achadas[: a.n]:
        avisos = []
        if l["criancas"] != "nao":
            avisos.append("criança" if l["criancas"] == "sim" else "criança?")
        if not l["sugerivel"]:
            avisos.append("NÃO SUGERIR")
        if l["duplicatas"]:
            avisos.append(f"outras versões: {', '.join(l['duplicatas'])}")
        print(f"- {l['id']}  [p{l['prioridade']}, {l['tipo']}, {l['ano'] or 's/ano'}, {l['qualidade']}, {l['orientacao']}, "
              f"{l['largura']}x{l['altura']}{'; ' + '; '.join(avisos) if avisos else ''}]")
        print(f"  {', '.join(l['projetos'])} | {l['materia'][:90]}")
        print(f"  {l['descricao'][:220]}")
        print(f"  ficha: {l['ficha']}")


if __name__ == "__main__":
    main()
