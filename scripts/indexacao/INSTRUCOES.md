# Instruções para indexar o acervo do Iteva

Você vai ler textos já extraídos e produzir linhas de índice. Não escreva
nada fora do arquivo de saída indicado na sua tarefa. Não altere nenhum
arquivo em `d:\projetos\acervo-vivo`.

## Regra de ouro

Indexe, não interprete. Nunca invente título, projeto ou página. Se um
título não existir no texto, descreva o assunto entre colchetes, por
exemplo `[depoimentos de alunos do estágio]`, para ficar claro que o
título é seu e não da revista.

## Uma linha por texto

- **Revista:** uma linha por matéria (texto com começo, meio e fim sobre
  um assunto). Uma matéria pode ocupar várias páginas. Notas curtas
  agrupadas numa seção (por exemplo "Ligeirinhas", "Quickies") viram
  uma linha por nota. Ignore capa, índice/sumário, expediente,
  anúncio e página só de logos ou contatos.
- **Notícia:** uma linha por arquivo.

O marcador `## Página N` no texto da revista é a página do PDF. Use-o
para as páginas: `6-9` para matéria contínua, `10; 12` se pular.

## Campos (JSON, um objeto por linha)

```json
{"fonte": "revista", "arquivo": "revista2016.md", "ano": 2016,
 "titulo": "A tecnologia aliada ao desenvolvimento humano",
 "projetos": ["Institucional"], "paginas_ou_url": "6-9",
 "tipo": "reportagem", "obs": ""}
```

- `fonte`: `revista` ou `noticia`.
- `arquivo`: nome do arquivo lido (sem pasta).
- `ano`: ano da edição (revista) ou da data da notícia.
- `titulo`: título como está no texto, com a grafia original. Sem
  travessão: se o título original tiver travessão, troque por dois-pontos.
- `projetos`: lista de nomes **exatamente** da lista abaixo. Inclua um
  projeto só se o texto falar dele de forma substantiva (não basta uma
  menção numa lista). Texto sobre a instituição como um todo leva
  `Institucional`. Se aparecer projeto que não está na lista, use
  `NOVO: <nome como aparece>`.
- `paginas_ou_url`: páginas (revista) ou o campo `url` do cabeçalho
  (notícia).
- `tipo`: um destes: `reportagem`, `editorial`, `entrevista`, `nota`,
  `notícia`, `artigo` (texto assinado de opinião ou análise, por
  pessoa de fora ou de dentro), `depoimento` (fala em primeira pessoa
  de beneficiário, parceiro ou equipe, apresentada como depoimento).
  Toda linha de `fonte: noticia` tem `tipo: notícia`.
- `obs`: curta, só se houver algo útil: matéria com depoimentos de
  parceiros, linha do tempo, números relevantes, "texto em inglês só"
  etc. Pode ficar vazio.

## Lista de projetos (use estes nomes)

| Nome | O que é / como pode aparecer |
|---|---|
| Midiacom | o programa ou projeto Midiacom/MídiaCOM em si: formação de jovens em TIC na sede, metodologia Midiacom, empresa-escola |
| Midiacom.net | a empresa social / negócio social Midiacom.net |
| Centro de Inclusão Digital Dragão do Mar | Midiacom em Fortaleza com Lanlink e Prefeitura |
| CDF | Projeto Cidadão do Futuro, livros e jogos CDF |
| Professores Digitais | formação de professores em multimídia |
| Técnico em Multimídia | curso técnico nas EEEPs com a Seduc |
| Sisger | sistema de gestão para OSCs |
| Provedor Social | internet para ONGs e escolas |
| Desenvolvimento de Software | área/setor de desenvolvimento de software |
| Empodera Jovem | arte urbana, graffiti, empreendedorismo para adolescentes |
| Delart | projeto Disciplina, Esporte, Lazer e Arte em Aquiraz |
| Bem-estar +60 | o programa para idosos como um todo |
| Construcom | tijolo ecológico e construção com idosos; reformas de casas |
| Conectividade +60 | inclusão digital de idosos (também "ConectivIdade", "Conectividade") |
| Idoso Conectado | cursos de tecnologia para 60+ com este nome |
| Termodinâmica | climatização de baixo custo, P&D ANEEL/Coelce |
| Eólica | aerogeradores, rotor Savonius, cata-vento |
| Solar | energia solar fotovoltaica |
| Geodésica | domo/estrutura geodésica |
| Estação de Tratamento de Esgoto | reúso de água, tratamento de esgoto residencial |
| Parafix | paraquedas ancorado |
| Fortalecimento do Terceiro Setor | programa de formação e assessoria a OSCs, seminários, encontros de fortalecimento |
| Bem-te-vi | TV do Bem, TV web |
| Institucional | a instituição como um todo, gestão, parcerias em geral, aniversário, conselhos, visitas institucionais sem projeto específico |

## Saída

Grave **somente** linhas JSON (JSONL, UTF-8, um objeto por linha, sem
vírgula entre linhas, sem texto antes ou depois) no arquivo indicado na
tarefa, com a ferramenta Write. Depois, confira que cada linha é JSON
válido, por exemplo:

```
python -I -c "import json,sys;[json.loads(l) for l in open(sys.argv[1],encoding='utf-8') if l.strip()];print('ok')" ARQUIVO
```

Na sua resposta final, diga quantas linhas gravou por arquivo lido e
liste os `NOVO:` que apareceram, com o arquivo e a página.
