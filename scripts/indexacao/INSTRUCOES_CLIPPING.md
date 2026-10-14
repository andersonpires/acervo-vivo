# Instruções para indexar o clipping

Leia antes `scripts/indexacao/INSTRUCOES.md` (regra de ouro, campos,
saída). Este arquivo diz o que muda para o clipping. Não altere nenhum
arquivo do projeto além do arquivo de saída da sua tarefa.

## O que é o clipping

`acervo/clipping/*.md`: uma matéria da imprensa (ou de blog, site de
governo, parceiro) sobre o Iteva por arquivo. Cada arquivo tem um
cabeçalho, o "Resumo publicado no site do Iteva" e o "Texto da matéria",
que às vezes é `[FALTA: ...]` (o original não foi obtido) e às vezes
remete a uma transcrição em `acervo/clipping/recortes/` (leia-a então).
Os dois recortes `recortes/arede.md` e `recortes/Instituto_produz_forragem.md`
não têm arquivo próprio e são indexados direto.

Texto de terceiros: é consulta. Indexe o que ele diz, sem julgar.

## Campos, no clipping

- `fonte`: `clipping`.
- `arquivo`: `clipping/<nome do arquivo>` (ou `clipping/recortes/<nome>`).
- `ano`: ano do campo `data` do cabeçalho (nos recortes, o da matéria; se
  for `[FALTA...]`, use `null`).
- `titulo`: o `titulo` do cabeçalho (é o título que o Iteva deu ao
  registro no site). Sem travessão nem meia-risca: troque por dois-pontos.
- `projetos`: nomes **exatamente** da coluna `projeto` de
  `projetos/cadastro.csv` (a tabela de INSTRUCOES.md está desatualizada;
  vale o cadastro). Classifique pelo texto da matéria quando houver; sem
  ele, pelo título e pelo resumo. Projeto fora do cadastro:
  `NOVO: <nome como aparece>`. Observações úteis:
  - Seminário Compartilhando Saberes com o Terceiro Setor:
    `Compartilhando Saberes` (e `Fortalecimento do Terceiro Setor` só se
    o texto tratar do programa ou de outras ações dele, como os
    Encontros de Fortalecimento das OSCs, que são `Fortalecimento do
    Terceiro Setor`).
  - Corporate Service Corps da IBM, 3M Impact, voluntariado de empresas
    com o Iteva: `Institucional`, salvo se o texto disser em que projeto
    trabalharam.
  - Livros digitalizados infantis de 2020: veja se o texto os liga ao
    CDF; se não ligar, `Institucional` e diga em `obs`.
  - Aulas a distância e salas virtuais do Eusébio em 2020: veja se o
    texto nomeia projeto; se não, `NOVO: <como o texto chama>` ou
    `Institucional`.
- `paginas_ou_url`: o `link_materia` do cabeçalho (nos recortes, o
  caminho do campo `arquivo` do cabeçalho do recorte).
- `tipo`: `notícia` (matéria jornalística, nota de site ou blog que
  noticia), `reportagem` (matéria longa com várias fontes), `entrevista`,
  `artigo` (opinião, relato pessoal em blog, estudo acadêmico) ou
  `vídeo` (TV, YouTube).
- `obs`: comece pelo veículo (campo `veiculo`; se vazio, nada). Depois,
  em poucas palavras: se o texto original não foi obtido ("só resumo do
  site"), idioma se não for português, e fatos que merecem conferência
  (datas, números, nomes de pessoas com cargo). Ex.:
  `"O Povo; só resumo do site"`, `"Blog de Anne Phey; em inglês; relato de voluntária da IBM"`.

## Saída

O arquivo JSONL indicado na tarefa. Confira com o comando de
INSTRUCOES.md. Na resposta final: linhas gravadas, os `NOVO:` com o
arquivo, e qualquer arquivo em que o texto da matéria não pareça ser a
matéria do título (por exemplo, outra notícia ou página genérica).
