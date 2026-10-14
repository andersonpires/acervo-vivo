# PRD: acervo de imagens

Versão de 14/10/2026. Fase 1 (reconhecimento) feita; as fases seguintes
esperam aprovação.

## Problema

Quem pede um texto ao Acervo Vivo recebe só o texto. A foto ainda é
garimpada à mão em revistas, no site e em pastas, sem saber em que
contexto ela já foi usada nem o que mostra. As imagens que a casa já
publicou estão espalhadas e sem descrição: no banco do site, nenhuma
das 640 tem legenda ou crédito, e o texto alternativo é quase sempre o
título da notícia.

## Objetivo

Criar `acervo/imagens`, com cada imagem publicada nas revistas e nas
notícias guardada em arquivo e descrita numa ficha que junta três
leituras:

1. **Onde foi usada:** fonte (revista e página, ou notícia e URL),
   data, título e subtítulo da matéria, trecho do texto em volta,
   legenda quando houver.
2. **O que a imagem é:** descrição visual (cena, lugar, ação, quantas
   pessoas, objetos, se é foto, ilustração, logo ou montagem),
   qualidade e orientação.
3. **Para que serve:** projeto, ação e ano a que pertence e usos que ela
   sustenta (capa, abertura de matéria, ilustração de dado, post).

Com isso, as skills passam a sugerir imagens: texto ou roteiro sai com
as fotos indicadas; quem pede uma foto recebe opções; relatório e
página de site já vêm montados com a imagem ao lado do texto.

## Escopo

Entram, por decisão do usuário (14/10/2026): fotos, ilustrações,
montagens, logos de parceiros, gráficos e infográficos, das revistas,
das notícias e das páginas do site e de projetos (cerca de 35 imagens
a mais). Fundos, texturas e ícones decorativos ficam de fora.

## Fora do escopo (por ora)

- Quadros de vídeo. Entram depois, se o usuário quiser.
- Editar, tratar ou publicar imagens. O acervo só guarda e descreve.
- Reconhecimento facial. Ver regras.

## O que o reconhecimento achou

### Notícias (97 publicadas)

| Item | Quantidade |
|---|---|
| Capas | 97 (todas as notícias têm) |
| Fotos de galeria | 275, em 84 notícias |
| Imagens no corpo do texto | 3, em 2 notícias |
| Imagens distintas | 372 (cerca de 210 MB) |
| Largura | mediana 1070 px; de 377 a 6000 px |

Os arquivos estão no site publicado (`/api/imagens/file/...`) e, todos
os 372, também na cópia do site antigo
(`site_legado/public/adm/images/noticias`). O banco do site liga cada
imagem à notícia (capa ou galeria, com a ordem). O exportador atual de
notícias troca a imagem do corpo por "(imagem)" e ignora capa e
galeria.

### Revistas (14 edições)

| Edições | Imagens distintas no PDF | Com 400 px ou mais no menor lado |
|---|---|---|
| 2010 a 2012 | 8.674 | 76 |
| 2013 a 2023 | 1.210 | 371 |
| Total | 9.884 | 447 |

O número cru engana. Nas revistas há:

- **fotos inteiras**, o caso fácil;
- **ilustrações vetoriais picadas em centenas de pedaços** (2019, p. 8,
  tem 100 pedaços para dois desenhos);
- **montagens**: várias fotos compostas numa só imagem (2012, p. 8,
  uma faixa de filme com umas dez fotos e um retrato recortado);
- **fundos, ícones e logos**.

Por isso a extração não pode salvar cada objeto do PDF: precisa
recortar a área que o leitor vê na página. Estimativa: entre 400 e 500
imagens úteis nas revistas, a confirmar na fase 2.

### Volume total estimado

Entre 800 e 950 imagens com as do site, cerca de 400 MB. Pesado demais para o git, como
os PDFs.

### Resultado da extração (fase 2, 14/10/2026)

| Fonte | Imagens | Observação |
|---|---|---|
| Notícias | 372 | 375 usos (capa, galeria, corpo); todas baixadas do site publicado |
| Site | 88 | projetos (bloco, carrossel, seção, logos), página Parceria, banners e parceiros da home, convidados e parceiros dos Painéis Temáticos |
| Revistas | 1.268 | 1.316 usos; 1.115 com o original do PDF, 153 só com o recorte da página |
| Total | 1.728 | 646 MB em `arquivos/` |

A estimativa de 400 a 500 imagens nas revistas era baixa: o filtro final
(40 pt na página e 80 px) mantém os retratos pequenos dos depoimentos,
que são úteis. Os milhares de "pedaços" de 2010 a 2012 eram lascas de
altura zero (restos de degradê), não fotos fatiadas; as fotos são
objetos inteiros. As folhas de contato mostram três grupos que a regra
não separa e que ficam para a triagem visual da fase 3:

- **grafismos:** fundos lisos, molduras, faixas de título, formas da
  diagramação, páginas de 2010 rasterizadas com o texto; não ganham
  ficha, vão para uma lista de descartadas com o motivo;
- **imagens de banco** (boneco 3D, cadeado, moedas): ganham ficha com
  `origem: banco de imagem provável`, e a skill não as sugere como foto
  do Iteva;
- **a mesma foto em dois objetos** (com e sem moldura): ligadas como
  duplicatas na fase 4.

## Requisitos

### Arquivos

- `acervo/imagens/arquivos/` guarda as imagens, **fora do git**, com
  integridade em `SHA256SUMS` (o mesmo esquema das revistas). Os scripts
  refazem a pasta a partir das fontes.
- Nome estável e legível: `rev2016-p12-1.jpg` (revista, página, ordem
  na página), `not-2024-05-10-123-capa.jpg` e `-g03` (data e id da
  notícia no site), `site-construcom-carrossel03.jpg`.
- Notícias e site: arquivo original, sem recompressão, baixado do site
  publicado; se falhar, copiado do legado.
- Revistas: recorte da área visível da página (`-pagina.jpg`, 200 dpi,
  com o texto que estiver por cima) e, quando dá, o original do PDF
  (costuma ter mais resolução e mostrar o que a página cortou). Também
  a página inteira em tamanho pequeno (`paginas/`), para quem analisa
  ver o leiaute.
- O contexto bruto de cada imagem (usos, matérias do índice, texto em
  volta, tamanho, resolução na página) fica em
  `acervo/imagens/contexto/*.jsonl`, no git.

### Ficha (uma por imagem)

`acervo/imagens/fichas/<id>.md`, com cabeçalho YAML e texto livre,
greppável e no padrão dos outros acervos:

```yaml
id: rev2016-p12-1
arquivo: arquivos/rev2016-p12-1.jpg
fonte: acervo/revistas/revista2016.pdf, p. 12
data: 2016            # da publicação; data da foto só se a fonte disser
tipo: foto            # foto | ilustracao | montagem | logo | grafico | outro
origem: iteva         # iteva | banco de imagem provável | terceiro | incerto
projeto: Construcom   # do cadastro; vazio se não der para saber
programa: Bem-estar +60
materia: "título | subtítulo"
legenda: ""           # só o que está publicado
credito: ""           # só o que está publicado (expediente vale)
largura: 2480
altura: 1650
orientacao: paisagem
qualidade: boa        # boa | media | baixa (para impressão e tela)
pessoas: 4
pessoas_nomeadas: []  # só nomes que a fonte liga à imagem
criancas: nao         # sim | nao | incerto
duplicatas: [not2017-03-02-g01]
usos: [abertura de matéria, post, relatório]
tags: [tijolo ecológico, idosos, obra, prensa]
```

Corpo: **Contexto** (o que a matéria conta e por que a imagem está
ali), **Descrição** (o que se vê) e **Uso sugerido**, cada afirmação
de contexto com a fonte.

### Catálogo e índice

- `acervo/imagens/catalogo.jsonl` gerado das fichas por
  `scripts/catalogar_imagens.py`: uma linha por ficha, com prioridade,
  se pode ser sugerida, duplicatas e a melhor versão de cada grupo. É a
  base de busca das skills. O usuário dispensou o CSV para Excel
  (14/10/2026).
- Linhas em `scripts/indexacao/imagens.jsonl`, que entram no
  `acervo/indice.csv` com o tipo `imagem`; o `volume.md` continua
  contando só textos.
- Duplicatas (a mesma foto na revista e na notícia, ou em dois anos):
  bytes iguais, ou hash de diferença de 256 bits próximo **e**
  correlação dos tons numa miniatura acima de 0,93. Calibrado em
  14/10/2026: o hash sozinho juntava retratos diferentes sobre fundo
  liso. Ficam no catálogo, não nas fichas.
- Capas e páginas de parceiros desenhadas em vetor: renderizadas da
  página inteira por `scripts/paginas_especiais_revista.py`.

### Uso pelas skills

- **Prioridade (decisão do usuário, 14/10/2026):** a sugestão de imagem
  começa pelas **fotos das revistas**. Fotos das notícias e do site vêm
  depois. Ilustração, montagem, gráfico e logo só entram quando quem
  pede disser que quer esse tipo.
- Instrução comum em `voz/imagens.md`: como escolher, quantas sugerir,
  como citar (sempre id e fonte), e o que avisar (baixa resolução,
  criança, imagem de outro ano ou de outro projeto).
- `conteudo-construcom` e `roteiro-video` ganham um passo final:
  "imagens sugeridas", com 3 a 5 opções por bloco do texto.
- Pedido avulso ("preciso de uma foto de X") é atendido por busca nas
  fichas, com opções e o motivo de cada uma.

## Regras

1. **Pessoa só tem nome quando a fonte liga o nome à imagem** (legenda,
   texto que diz "na foto", crédito). Nunca por semelhança de rosto nem
   por dedução do texto em volta. É a regra 3 do projeto aplicada a
   imagens.
2. **Contexto só de fonte.** O que a descrição visual sugere e a fonte
   não confirma fica como "parece" na descrição, nunca como fato na
   ficha (por exemplo: lugar, ano da foto, nome do evento).
3. **Data da foto não é data da publicação.** A revista de 2016 pode
   trazer foto de 2014. A ficha guarda a data da publicação e só põe a
   da foto se a fonte disser.
4. **Crianças e adolescentes** ficam marcados. A skill avisa ao sugerir
   uma imagem com criança que o uso novo depende da autorização de
   imagem (LGPD e ECA), que o acervo não tem como provar.
5. **Crédito e direito de uso** só do que estiver publicado. Imagem de
   banco ou de terceiro (quando der para saber) é marcada.
6. Originais intocáveis: os PDFs e o site só são lidos.
7. Português do Brasil, sem travessão nem meia-risca.

## Fases

| Fase | Entrega | Para e mostra |
|---|---|---|
| 1. Reconhecimento | este PRD | sim (agora) |
| 2. Extração | scripts `exportar_imagens_site.cjs` (notícias e páginas) e `extrair_imagens_revista.py`; arquivos, `SHA256SUMS` e contexto bruto por imagem (título, subtítulo, trecho, legenda, página); filtro de fundos e ícones | amostra de 20 imagens das revistas, com recorte conferido |
| 3. Análise | fichas, por agentes com um arquivo comum de instruções (`acervo/imagens/INSTRUCOES.md`), em lotes por revista e por ano de notícia; revisão por amostragem | 15 fichas para o usuário avaliar antes do lote todo |
| 4. Índice e duplicatas | `catalogo.csv`, `imagens.jsonl`, índice remontado, duplicatas ligadas | resumo por projeto e ano |
| 5. Confronto | a mesma foto contada de formas diferentes (ano, projeto, lugar) vai para `divergencias.md` | lista |
| 6. Skills e teste | `voz/imagens.md`, passo nas duas skills; teste: briefing de uma notícia real, a skill sugere imagens sem saber quais a notícia usou, e compara | resultado do teste |

Commit ao fim de cada fase.

## Riscos

- **Recorte errado nas revistas** (montagens, fotos sangradas, texto
  sobre a foto). Mitigação: agrupar blocos vizinhos, conferir amostra na
  fase 2 e deixar o agente da fase 3 marcar "recorte ruim".
- **Descrição que inventa.** Mitigação: separar o que é contexto (com
  fonte) do que é descrição visual, e conferir por amostragem.
- **Custo de análise:** 1.728 imagens. Na fase 3, os agentes fazem
  primeiro a triagem pelas folhas de contato (grafismo sai sem ficha) e
  só depois leem uma a uma as que ficam. Lotes por revista e por ano de
  notícia.

## Decisões do usuário (14/10/2026)

- Arquivos fora do git, com `SHA256SUMS`; fichas e catálogo no git.
- Escopo amplo (ver Escopo).
- Análise dividida entre agentes, em lotes, com revisão por amostragem.

Consequências no desenho:

- **Logos:** a ficha nomeia a organização só quando o nome está escrito
  no logo ou no texto da página. Assim as páginas de logos das revistas
  (pendência antiga) ganham lista de parceiros com fonte.
- **Gráficos e infográficos:** a ficha transcreve os números que se
  leem na imagem, marcados "lido na imagem". Número tirado dali só vai
  para texto novo depois de conferido com a fonte escrita.
- **Páginas do site:** as imagens vêm do banco do site (blocos de
  imagem e seções com imagem de páginas e projetos), com a página e a
  seção como contexto.
