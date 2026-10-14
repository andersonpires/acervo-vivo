# Imagens: como sugerir

Guia comum das skills para indicar imagens do acervo junto de um texto,
roteiro, relatório ou página. A base é `acervo/imagens/catalogo.jsonl`
(uma linha por ficha) e as fichas em `acervo/imagens/fichas/`. O método
de montagem está em `prd-imagens.md`.

## Ordem de preferência

Decisão do usuário (14/10/2026):

1. **Fotos das revistas.**
2. Fotos das notícias e das páginas do site.
3. Montagens.
4. Ilustração, gráfico, logo, capa: **só quando quem pede quer esse
   tipo** (por exemplo, "uma imagem com os logos dos parceiros").

Dentro da mesma faixa, prefira a foto do mesmo projeto, com mais
qualidade e mais recente. Para história e linha do tempo, a antiga é a
certa.

**Capa, abertura e impressão** pedem qualidade `media` ou melhor (`boa`
para impressão grande). Se nenhuma foto de revista do projeto chega
lá, use a melhor foto de notícia ou do site e diga por quê; a ordem vale
entre as que têm qualidade para o lugar.

Nunca sugira imagem com `sugerivel: false`: banco de imagem provável, ou
fora por curadoria (um dos fundadores, divergência 20). Nem como "opção
reserva".

## Como achar

```
python -I scripts/buscar_imagens.py --projeto "<projeto do cadastro>" --busca "<2 a 4 palavras do assunto>"
```

- Comece com o projeto e um assunto concreto ("tijolo idosos",
  "formatura certificados", "graffiti muro escola"). Se vier pouco,
  tire a busca e fique só com o projeto; se o projeto for novo, busque
  só por assunto.
- `--sem-criancas` quando o uso for público e a autorização de imagem
  não estiver garantida.
- `--qualidade media` para site e redes; `--qualidade boa` para
  impressão grande (capa, banner, revista).
- Antes de indicar, **abra a ficha** de cada imagem escolhida: o
  catálogo resume, a ficha diz o que não pode ser dito da foto.

## Quantas e onde

- Notícia: uma de capa e duas a quatro de galeria.
- Matéria de revista: uma de abertura e uma por intertítulo.
- Post: uma, no máximo três (carrossel).
- Roteiro: imagens de apoio para os blocos sem gravação própria (veja
  a skill `roteiro-video`).
- Relatório e página de site: uma por seção.
- Pedido avulso ("preciso de uma foto de..."): de três a cinco opções.

## Como indicar cada imagem

Uma linha por imagem, sempre com o id e o arquivo:

> **Abertura:** `rev2021-p12-1` (`acervo/imagens/arquivos/rev2021-p12-1.jpg`):
> pessoa idosa de luvas segurando um tijolo ecológico (revista 2021,
> p. 12). Por quê: é o gesto central do Construcom. Atenção: 1245 px,
> serve para site, não para capa impressa.

- **Por quê:** a ligação com o trecho do texto, em uma frase.
- **Atenção:** o que a ficha manda avisar. Sempre que houver:
  - criança ou adolescente (`criancas: sim` ou `incerto`): o reuso
    depende de autorização de imagem (LGPD e ECA), que o acervo não
    prova;
  - qualidade baixa, ou só o recorte da página com texto por cima;
  - foto de outro ano ou de outra ação.

## O que nunca fazer

- **Não apresentar foto antiga como registro da ação nova.** Se a ação
  do briefing não tem foto no acervo, a imagem sugerida é *ilustrativa*
  e a legenda diz de quando e de qual ação ela é, com a fonte da ficha:
  "Turma do Construcom em Eusébio, 2019 (Revista Iteva 2019)". Se a
  ficha não dá ano nem lugar, a legenda também não dá.
- **Não atribuir gênero pela aparência** na descrição e na legenda:
  "duas pessoas adolescentes pintam um mural", não "duas adolescentes".
  Gênero só quando a ficha nomeia a pessoa e a fonte o dá.
- **Não nomear quem a ficha não nomeia.** Nome em legenda só de
  `pessoas_nomeadas`. Se o texto fala de uma pessoa e a ficha diz
  "pareamento não confirmado", a foto não ilustra essa pessoa.
- **Não tirar fato da imagem.** Número, local ou data que só aparecem
  na foto (placa, telão, crachá) não entram no texto sem fonte escrita.
- **Não sugerir duas versões da mesma foto.** O catálogo já devolve a
  melhor de cada grupo de duplicatas.

## Legenda pronta

Quando o formato pede legenda (notícia, matéria, relatório), escreva-a
só com o que está na ficha: quem (se nomeado), o quê, onde e quando (se
a ficha tem). Crédito: o campo `credito` da ficha; vazio vira
`[FALTA: crédito da foto]`.
