---
name: conteudo-iteva
description: Escreve conteúdo do Iteva (notícia do site, matéria de revista, post ou legenda) sobre qualquer projeto ou ação, inclusive projeto novo, a partir de um briefing de ação real, com a voz da casa, sem nenhum dado inventado e com imagens do acervo sugeridas. Use quando pedirem texto, notícia, matéria, post, legenda ou relato sobre o Iteva, um projeto dele (Construcom, CDF, Empodera Jovem, Conectividade +60, NoCorre, Sisger e os demais) ou uma ação nova. Roteiro de vídeo vai para a skill roteiro-video.
---

# Conteúdo do Iteva

Você escreve com a voz do Iteva sobre qualquer projeto. Para uma OSCIP
que presta contas a prefeituras, empresas e incentivadores, dado
inventado é risco institucional. Por isso esta skill tem uma ordem fixa,
e nenhum passo se pula.

## Passo 1: carregar a base comum

Leia, inteiros, antes de qualquer outra coisa:

1. `projetos/iteva.md`, a ficha institucional (matriz, unidades,
   contato, programas, fundadores, idade);
2. o guia do canal pedido (tabela do passo 4);
3. `divergencias.md`, para saber o que está decidido e o que está em
   disputa;
4. `voz/imagens.md`, para o passo 5.

## Passo 2: situar o projeto

Ache o projeto em `projetos/cadastro.csv` (nome exato, programa,
situação). Daí, um destes três caminhos:

- **Projeto com ficha** (`projetos/<projeto>.md`, hoje só
  `construcom.md`): o contexto do projeto (o que é, como funciona,
  histórico, números, depoimentos publicados) sai **só da ficha**.
- **Projeto sem ficha:** procure as linhas do projeto em
  `acervo/indice.csv` (coluna `projetos`) e leia os textos mais
  recentes que tratam dele: notícias em `acervo/noticias`, matérias em
  `acervo/texto` (pela página), páginas em `acervo/site`. Use só o que
  precisar para situar o leitor e **anote a fonte de cada fato**
  (arquivo e página, ou URL e data). Histórico tirado do acervo conta
  o fato da fonte ("em agosto de 2024, em Itatira, 25 jovens pintaram
  o muro da escola"), sem conclusão sobre o projeto inteiro a partir de
  um caso ("a arte sempre foi o centro"). Clipping é consulta, nunca modelo
  de texto. O site tem trechos desatualizados: fato de página do site
  que conflite com notícia ou revista mais nova não entra.
- **Projeto novo** (fora do cadastro): todo o contexto vem do briefing.
  Pergunte o que for preciso para apresentar o projeto ao leitor (o que
  é, para quem, com quem). Na entrega, ofereça a linha para o cadastro.

Projeto com situação `encerrado`: avise que o texto trata de projeto
encerrado e confirme a intenção. Situação `a confirmar`: avise e siga.

Lembre as decisões de curadoria que valem para qualquer projeto:
programas à parte, mas uma ação do Fortalecimento pode atender jovens
ou idosos junto de outro programa (divergência 23); ação, oficina ou
evento fora do cadastro é **atividade** do Iteva, não projeto novo
(divergência 22); um dos fundadores não é nomeado (divergência 20).

## Passo 3: exigir o briefing

O texto conta **uma ação real**. Peça o briefing no formato de
`briefing.md` (nesta pasta) e confira se ele tem:

| Campo | Exigência |
|---|---|
| Projeto | nome como no cadastro, ou "novo" com uma frase do que é |
| Município | nome do município |
| Período | data da ação, ou início e fim |
| Participantes | quem e quantos; nome e idade de quem for citado |
| O que foi feito | a ação, em fatos |
| Resultado | o que mudou, com número quando houver |
| Parceiros | quem participou e como |
| Fala real | pelo menos uma, **literal, com nome e papel de quem disse** |
| Formato | notícia, matéria, post ou legenda |
| Fotos da ação | se existem, de quem é o crédito |

**Se faltar qualquer campo, pare e pergunte**, todos de uma vez, numa
lista curta. Não escreva rascunho "para adiantar" com lacuna preenchida
por suposição. Se a pessoa responder que um dado não existe, siga e
marque `[FALTA: ...]` no texto.

Fala sem autor não serve. Fala "adaptada" não serve: a fala entra como
foi dita, ou não entra. Uma correção mínima de transcrição (vírgula,
"tô" mantido) é aceitável; mudança de palavra não.

## Passo 4: escrever no formato pedido

| Formato | Guia | Tamanho de referência |
|---|---|---|
| Notícia do site | `voz/noticia.md` | cerca de 340 palavras; título com verbo no presente; crédito "Texto:" e "Fotos:" no fim |
| Matéria de revista | `voz/revista.md` | 800 a 1.250 palavras; título, linha fina, intertítulos |
| Post | `voz/noticia.md` (provisório) | até 120 palavras; um fato, uma pessoa, um número (escolha provisória, sem base no acervo) |
| Legenda | `voz/imagens.md` | uma ou duas frases, só com fatos da ficha da imagem ou do briefing |
| Roteiro de vídeo | use a skill `roteiro-video` | |

Siga as regras do guia: tamanho de frase e parágrafo, pessoa verbal,
abertura, fecho, como apresentar pessoas, parceiros e números. Para
**post** ainda não há guia próprio: use as regras do guia indicado, e
diga na entrega que o formato usou regra provisória.

Na notícia, quatro pontos que o teste da Fase 7 mostrou fáceis de errar
(detalhes em `voz/noticia.md`):

- frase de 20 a 30 palavras e parágrafo de duas frases; não fragmente;
- se o briefing tem uma cena forte (uma pessoa, um gesto), ela pode
  abrir o texto; imagem sem fato, não;
- depois de cada história, uma frase sobre o que a mudança significou;
- fecho no registro da notícia, sem a tese da revista.

## Passo 5: sugerir imagens

Siga `voz/imagens.md`. Em resumo:

1. Se o briefing traz fotos da ação, elas vêm primeiro: o texto é sobre
   elas.
2. Do acervo, busque com
   `python -I scripts/buscar_imagens.py --projeto "<projeto>" --busca "<assunto>"`.
   A ordem já é a decidida: fotos de revista, depois de notícia e site,
   depois montagens; ilustração, logo e gráfico só se pedidos.
3. Abra a ficha de cada imagem escolhida antes de indicá-la.
4. Imagem do acervo numa ação nova é **ilustrativa**: a legenda diz de
   quando e de qual ação ela é. Nunca a apresente como registro da
   ação do briefing.
5. Avise criança, baixa qualidade e foto de outro ano.

## Regra 3, sem exceção

Nunca invente número, nome, data, local ou depoimento.

- Todo número do texto está no briefing, na ficha do projeto ou num
  texto do acervo citado no passo 2. Nada de arredondar para cima,
  somar períodos que a fonte não somou ou transformar "mais de 700" em
  "centenas de milhares".
- Toda pessoa nomeada está nessas fontes. Não crie personagem
  ilustrativo com nome ("Seu João", "Dona Maria"): use "uma aluna",
  "um participante".
- Toda fala entre aspas está, literal e com autor, no briefing ou num
  texto publicado do acervo (com a fonte). Fala de texto antigo só
  entra como fala daquela época, nunca como se fosse da ação nova.
- Fato que falta vira `[FALTA: descrição]` no próprio texto.
- Fato que está em `divergencias.md` sem decisão: use a forma que a
  ficha indica e avise na entrega. Não escolha entre as fontes.
- Adjetivo não substitui fato: "transformou a vida" só se o briefing
  disser o que mudou; e aí diga o que mudou.

## Estilo do projeto

- Português do Brasil, com acentuação correta.
- **Sem travessão nem meia-risca.** Use vírgula, dois-pontos,
  parênteses ou duas frases. Hífen solto com espaços também não.
- Nome de projeto como no cadastro ("Construcom", "Conectividade +60",
  "Empodera Jovem"); a sigla CDF se apresenta como Cidadão do Futuro
  (divergência 4).
- **Telefone de contato:** quem pede o texto define. Se não definir,
  use (85) 3362-3210.
- "Matriz" para a unidade principal (Eusébio, desde 2026) e "unidade"
  para as demais; "sede" só como sinônimo de unidade. Aquiraz é a sede
  antiga.
- Na notícia, nome completo da instituição na primeira menção:
  "Instituto Tecnológico e Vocacional Avançado (ITEVA)", com o "e".

## Passo 6: entregar com conferência

Entregue, nesta ordem:

1. **O texto**, pronto para publicar, com `[FALTA: ...]` onde houver.
2. **Imagens sugeridas**, no formato de `voz/imagens.md`, com legenda
   quando o formato pede.
3. **Conferência de fatos:** uma lista com cada número, nome, data,
   local e fala do texto, e de onde veio (campo do briefing, trecho da
   ficha ou arquivo do acervo com a página). Se algum item não tiver
   origem, ele não pode estar no texto: volte e tire.
4. **Avisos:** divergências tocadas, formato provisório, projeto
   encerrado ou a confirmar, faltas que impedem publicar.

Depois de publicada a ação, lembre que ela pode atualizar o acervo
(objetivo 6 do projeto): ofereça a linha que entraria na ficha do
projeto (ou no cadastro, se for projeto novo), com a fonte, para o
responsável aprovar.
