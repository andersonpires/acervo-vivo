# Instruções para descrever as imagens do acervo do Iteva

Você vai olhar imagens já extraídas das revistas, das notícias e do site
do Iteva e escrever uma ficha para cada uma. A ficha junta três
leituras: onde a imagem foi usada (fonte), o que ela mostra (descrição)
e para que pode servir (uso). Mais tarde, quem pedir um texto ou uma
foto vai receber sugestões tiradas destas fichas; por isso a ficha
precisa ser exata e fácil de buscar.

Pasta de trabalho: `d:\projetos\acervo-vivo\acervo\imagens` (abaixo,
caminhos relativos a ela). Grave **só** nas saídas indicadas: `triagem/`
e `fichas/`. Não altere nenhum outro arquivo do projeto.

## Regra de ouro

Descreva o que se vê; afirme só o que a fonte diz. Separe sempre as
duas coisas:

- **Fato de fonte** (nome de pessoa, lugar, data, evento, projeto): só
  se estiver escrito na fonte (legenda, texto da matéria, título,
  campo do site) e ligado a esta imagem. Cite de onde veio.
- **Leitura visual** (o que aparece): descreva com palavras concretas.
  O que você deduz e a fonte não confirma vai como aparência: "parece
  uma sala de aula", "aparentemente em área externa", nunca como fato.

Nunca invente. O que faltar fica vazio ou vira `[FALTA: descrição]`.

## Decisões de curadoria (valem acima da fonte)

Decididas pelo usuário em 14/10/2026 (`divergencias.md`):

- **Fábio Beneduce** não pertence mais à organização e **não é
  nomeado** em nada, nem como histórico. Na ficha: não entra em
  `pessoas_nomeadas`; em `legenda`, troque o nome por
  `[nome de um dos fundadores]`; no texto da ficha, diga "um dos
  fundadores" ou "antigos associados" no lugar do nome, mesmo quando
  a fonte imprime o nome. `usos_sugeridos: []` e, em Uso sugerido,
  "Não sugerir: retrata um dos fundadores, que não pertence mais à
  organização (Curadoria, divergência 20)". Fotos de grupo em que ele
  aparece não ficam proibidas, mas a ficha não o identifica.
- **Sede em Aquiraz:** foto ou legenda que diga "sede do Iteva em
  Aquiraz" vale como "sede antiga do Iteva em Aquiraz". A matriz é em
  Eusébio desde 2026.
- **Andressa Meirelles** (jornalista da BemTeVi): use esta grafia no
  texto da ficha, mesmo onde a revista escreve "Meireles".

## Entradas

Sua tarefa indica um lote, por exemplo `rev2016-2`. Dele você usa:

| Arquivo | O que tem |
|---|---|
| `lotes/<lote>.jsonl` | uma linha por imagem: id, arquivos, tamanho em pixels e os usos (onde aparece, com contexto) |
| `folhas/<lote>-N.png` | folha de contato com todas as imagens do lote e o id de cada uma |
| `previas/<id>.jpg` | a imagem em tamanho leve; é ela que você abre para olhar |
| `paginas/revAAAA-pNN.jpg` | (revistas) a página inteira, pequena, para ver o leiaute |
| `../texto/revistaAAAA.md` | (revistas) o texto da revista; procure `## Página N` |
| `../noticias/*.md`, `../site/**/*.md` | (notícias e site) o texto onde a imagem foi usada; o caminho está em `usos[].arquivo_acervo` |
| `../../projetos/cadastro.csv` | nomes válidos de projeto (coluna `projeto`) |

Se uma prévia parecer vazia ou toda branca, a imagem pode ser branca
sobre fundo transparente: olhe o recorte da página (`recorte`) ou a
página inteira antes de descartar.

Nos usos das revistas, `materias` traz as matérias do índice que cobrem
a página (título, projetos, tipo) e `texto_perto` traz os blocos de
texto logo acima, logo abaixo e por cima da imagem: é ali que costuma
estar a legenda ou o nome de quem dá o depoimento. Confira na página
inteira se o texto é mesmo da imagem.

Nas notícias, `texto_alternativo` do site é quase sempre o título da
notícia repetido: não é legenda. As fotos de galeria não têm legenda;
o contexto é a notícia.

## Passo 1: triagem pela folha de contato

Abra as folhas do lote e decida, para cada id, se ganha ficha. Fica
**sem ficha** (descarte) o que não é imagem que alguém reusaria:

- **grafismo**: fundo liso ou degradê, textura, moldura, forma da
  diagramação, faixa ou caixa de título, fio, seta, número de seção;
- **página rasterizada**: bloco de texto, sumário, índice ou página
  inteira que virou imagem (comum em 2010);
- **ilegível**: pedaço sem sentido sozinho, recorte vazio. Em várias
  revistas (2019, por exemplo) as ilustrações vetoriais foram gravadas
  em pedaços: cada pedaço solto (uma mancha, uma mão, um monitor) é
  descarte; diga no motivo "pedaço de ilustração".

- **duplicata pior**: a mesma foto de outro id do lote, mas com
  moldura, texto da página ou menos resolução; diga no motivo
  "duplicata de <id>" e cite o descarte em Observações da ficha que
  ficou. Se as duas versões têm a mesma qualidade, as duas ganham ficha.

Ganham ficha: fotos, ilustrações, montagens, logos, gráficos,
infográficos e capas de revista. **Na dúvida, faça a ficha.**

Grave `triagem/<lote>.jsonl`, uma linha por id do lote (todos):

```json
{"id": "rev2018-p02-1", "decisao": "descarte", "motivo": "grafismo: fundo azul liso"}
{"id": "rev2018-p02-2", "decisao": "ficha", "motivo": ""}
```

## Passo 2: uma ficha por imagem que ficou

Para cada id com `decisao: ficha`: abra a prévia, leia o contexto do
lote e o texto da fonte (a página da revista, a notícia, a página do
site) e, nas revistas, olhe a página inteira. Depois grave
`fichas/<id>.md` com a ferramenta Write, neste formato:

```markdown
---
id: rev2016-p08-10
arquivo: arquivos/rev2016-p08-10.jpg
fonte: acervo/revistas/revista2016.pdf, p. 8
data: 2016
data_da_foto: ""
tipo: foto
origem: iteva
projetos: [Midiacom]
materia: "Sentimento Jovem"
legenda: ""
credito: ""
local: ""
pessoas: 1
pessoas_nomeadas: []
criancas: nao
largura: 1050
altura: 1050
orientacao: quadrada
qualidade: media
usos_sugeridos: [retrato de depoimento, post]
tags: [jovem, retrato, sorriso, fundo laranja, camisa preta]
---

## Contexto

O que a fonte conta e por que a imagem está ali, com a fonte de cada
afirmação (página, notícia, campo do site).

## Descrição

O que se vê: cena, pessoas (quantas, faixa etária aparente, roupas,
ação), objetos, lugar aparente, enquadramento, cores, texto que
aparece na imagem.

## Uso sugerido

Para que a imagem serve e quando evitar (baixa resolução, texto por
cima, criança, foto de outro ano ou de outro projeto).
```

Acrescente `## Observações` só se houver: recorte ruim, a mesma foto em
outro id que você viu no lote, imagem usada em mais de um lugar
(liste os usos), dúvida de pareamento de nome.

### Campos

- `arquivo`, `largura`, `altura`: copie do lote (`arquivo` é o original
  quando existe; o recorte da página fica em `recorte`).
- `fonte`: revista: `acervo/revistas/revistaAAAA.pdf, p. N`; notícia:
  a URL; site: a URL. Se a imagem tem vários usos, a fonte é o primeiro
  e os outros vão em Observações.
- `data`: da **publicação** (ano da revista; data da notícia, AAAA-MM-DD;
  vazio no site). `data_da_foto` só se a fonte disser quando a foto foi
  feita ou o evento aconteceu e ligar o evento a esta foto.
- `tipo`: `foto`, `ilustracao`, `montagem` (várias fotos compostas numa
  imagem), `logo`, `grafico` (gráfico, infográfico, tabela em imagem),
  `capa` (capa de revista ou publicação), `outro`.
- `origem`: `iteva` (produção ou ação do Iteva, o caso comum),
  `banco de imagem provável` (foto ou ilustração genérica de banco:
  boneco 3D, executivo sorrindo em fundo branco, objeto isolado,
  ícone de mercado), `terceiro` (logo, foto cedida ou divulgada por
  outra organização, retrato oficial), `incerto`.
- `projetos`: nomes **exatamente** como na coluna `projeto` de
  `projetos/cadastro.csv`, tirados das matérias do índice (revista),
  de `projetos_do_indice` (notícia e site) ou do texto. Se a matéria
  tem vários projetos e só um combina com a imagem pela legenda ou pelo
  texto ao lado, use só ele. Instituição como um todo: `Institucional`.
  Ação, oficina, evento ou negócio que não está no cadastro **não** vira
  projeto novo: use `Institucional` e escreva em Observações "Atividade
  extra: <nome como aparece>" (Curadoria, 14/10/2026).
- `materia`: título da matéria (revista), título da notícia, título da
  página do site. Sem travessão: troque por dois-pontos.
- `legenda`: só texto **publicado** junto da imagem e que é dela
  (revista: texto colado à foto; site: campo `legenda`). Não invente
  legenda.
- `credito`: só se publicado (crédito na foto, "Foto: fulano"). Nas
  notícias, a linha "Fotos: ..." no fim do texto vale para a capa e a
  galeria daquela notícia. O expediente geral da revista não vale como
  crédito de foto.
- `local`: só se a fonte disser (por exemplo "na sede do Iteva, em
  Aquiraz", escrito na matéria e ligado à cena).
- Notícia que relata **um só evento** (uma entrega, uma formatura):
  as fotos da capa e da galeria são desse evento, então `local` e
  `data_da_foto` podem vir da notícia, desde que a imagem combine com
  ele. Escreva em Contexto "local e data do evento da notícia". Não vale
  para foto de "antes", foto de arquivo ou notícia que junta vários
  momentos.
- `pessoas`: quantas pessoas se veem (número; `0` se nenhuma; para
  multidão, uma estimativa redonda como `30`, e diga "cerca de" na
  descrição). Conta só gente fotografada: figura desenhada conta `0`.
  Foto de gente dentro de uma tela ou maquete conta, e vale também para
  `criancas`.
- `pessoas_nomeadas`: lista de nomes **só** quando a fonte liga o nome
  à imagem: legenda, nome impresso junto do retrato, "na foto, ...",
  campo `nome` do site, nome escrito na própria imagem. Nunca por
  semelhança de rosto, nunca porque o nome aparece em outro lugar da
  matéria. Editorial com um só retrato e uma só assinatura: o nome da
  assinatura vale para o retrato. Nas páginas de depoimentos, o nome só vale se o leiaute
  junta claramente aquele nome àquele retrato (confira na página
  inteira); se houver dúvida, deixe vazio e escreva em Observações
  "na página há depoimentos de A, B e C; pareamento não confirmado".
- `criancas`: `sim`, `nao` ou `incerto` (há pessoa que parece ter menos
  de 18 anos).
- `orientacao`: `paisagem`, `retrato` ou `quadrada` (diferença menor que
  10%).
- `qualidade`, pensando em reuso:
  - `boa`: menor lado de 1500 px ou mais, nítida, sem nada por cima;
    serve para impressão;
  - `media`: entre 600 e 1500 px, ou nítida mas com pequeno defeito;
    serve para site e redes. Foto nítida do tamanho das galerias do
    site (cerca de 1070 ou 1170 por 592 px) também é `media`;
  - `baixa`: menos de 600 px, borrada, pixelada, com texto ou grafismo
    por cima, ou só existe o recorte da página com texto.
- `usos_sugeridos`: dois a quatro de: `capa`, `abertura de matéria`,
  `ilustração de trecho`, `retrato de depoimento`, `galeria`, `post`,
  `relatório`, `apresentação`, `página de projeto`, `lista de
  parceiros`.
- `tags`: três a oito palavras concretas, minúsculas, em português, que
  alguém usaria para buscar a imagem (o que aparece e o assunto): por
  exemplo `tijolo ecológico`, `prensa`, `idosos`, `formatura`,
  `laboratório de informática`, `certificado`.

### Por tipo

- **Logo:** diga de quem é **só** pelo nome escrito no logo ou no
  texto da página que o acompanha. `pessoas: 0`. Em `materia`, diga
  onde aparece (por exemplo "página de parceiros"). Use
  `lista de parceiros` nos usos.
- **Gráfico e infográfico:** transcreva na Descrição os números e
  rótulos que se leem, marcados "(lido na imagem)". Avise em Uso
  sugerido que número tirado dali só vai para texto novo depois de
  conferido na fonte escrita.
- **Capa de revista:** transcreva as chamadas que se leem.
- **Ilustração e montagem:** descreva o que representa; numa montagem,
  diga quantas fotos há e o que cada uma mostra, em poucas palavras.
- **Imagem de banco:** ficha curta; em Uso sugerido, diga que não é
  registro do Iteva e não serve para ilustrar ação real.

### Escrita

Português do Brasil, frases curtas e concretas. **Sem travessão nem
meia-risca**: use vírgula, dois-pontos, parênteses ou duas frases.
Nada de adjetivo de propaganda ("linda", "emocionante").

Não atribua gênero a ninguém pela aparência. Descreva a faixa etária e
o que se vê: "pessoa jovem de camiseta do Midiacom", "pessoa idosa de
cabelos brancos e chapéu", "três adolescentes", "uma criança de
uniforme escolar". Use o gênero só quando a fonte o dá (por exemplo
"a estudante Haniele Monteiro", "Dona Santina") e o nome está ligado
à imagem.

## Conferência antes de terminar

1. Rode o conferidor com o nome do lote e corrija até não sobrar
   problema:

   ```
   python -I scripts/conferir_fichas_imagens.py <lote>
   ```

   (na pasta `d:\projetos\acervo-vivo`). Ele confere a triagem completa,
   o cabeçalho, os campos fechados, os projetos do cadastro, o arquivo
   da imagem, as seções e os caracteres proibidos.
2. Releia cada nome em `pessoas_nomeadas` e confirme que a fonte o liga
   àquela imagem. O conferidor não tem como checar isso.
3. Releia as descrições procurando gênero atribuído pela aparência
   ("uma jovem", "um senhor", "duas adolescentes") e troque.

Na resposta final, diga: quantas fichas e quantos descartes; as
atividades extras que apareceram; os nomes de pessoa que você registrou, com a fonte de
cada um; e qualquer dúvida que valha a revisão de uma pessoa.
