# Orientações do projeto: Acervo Vivo

Leia antes de qualquer alteração. O `README.md` diz o que o projeto é e
para que serve; este arquivo diz como trabalhar nele. O que ficou para
depois está em `PENDENCIAS.md`; decisões entre fontes, em
`divergencias.md`.

## Regras permanentes

1. **Os arquivos em `acervo/revistas` são originais: nunca alterar, mover
   ou renomear.** Tudo que se extrai deles vai para outra pasta. Os PDFs
   **não ficam no git** (pesados demais; estão no `.gitignore`). A
   integridade se confere com
   `cd acervo/revistas && sha256sum -c SHA256SUMS`; se faltar algum, a
   origem é `../site_iteva/site_legado/public/download/`.
2. **Trabalhe em fases.** Ao fim de cada fase, pare, mostre o resultado e
   espere a aprovação do usuário antes de seguir.
3. **Nunca invente número, nome, data, local ou depoimento.** O que não
   estiver na fonte fica marcado como `[FALTA: descrição]`.
4. **Todo fato registrado em ficha leva a fonte**: arquivo e página, ou
   URL e data da notícia.
5. **Quando duas fontes divergirem, registre em `divergencias.md`** para o
   usuário decidir. Não escolha por conta própria. O site tem trechos
   desatualizados (linha do tempo parada em 2020, cidade da sede), então
   trate-o como fonte, não como verdade.
6. **Tudo em português do Brasil. Faça um commit ao fim de cada fase.**

## Estilo

- **Fatos institucionais** (matriz, unidades, contato, fundação,
  números da instituição) estão em `projetos/iteva.md`. Telefone em
  texto novo: quem pede define; se não definir, (85) 3362-3210.
- **Modelo de escrita** vem só das revistas (principalmente), das
  notícias e das páginas do site. O clipping é acervo de consulta, não
  de estilo: é a voz da imprensa, não a do Iteva. Proposta de projeto e
  relatório, quando chegarem, são modelo apenas dos próprios formatos.
- Sem travessão (—) nem meia-risca (–) em nada que se escreva aqui:
  fichas, guias, textos gerados, comentários e mensagens de commit. Onde
  ele entraria, use vírgula, dois-pontos, parênteses ou duas frases.
- Depois de criar ou editar arquivo com acento, confira se não há
  mojibake (ambiente Windows):

  ```powershell
  $pat = "[\u00C2\u00C3\u00E2][\u0080-\u00BF]|\uFFFD"
  $txt = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes("CAMINHO"))
  [regex]::Matches($txt, $pat) | ForEach-Object { $_.Value }
  ```

  Grave com as ferramentas Write/Edit. Evite `Out-File`, `Set-Content` e
  `echo` do PowerShell para texto com acento.

  Atenção ao gravar este próprio padrão: ao criar este arquivo, a
  ferramenta Write converteu os escapes de barra invertida em caracteres
  literais, e o padrão passou a acusar a si mesmo. Depois de gravar,
  confira com `grep -n 'pat = ' CLAUDE.md` que os escapes continuam
  escritos como texto.

## Ferramentas disponíveis nesta máquina

- Python 3.12 com PyMuPDF (`import pymupdf`) para extrair texto com
  posição dos blocos, o que permite reordenar colunas.
- `pdftotext` (Git Bash, `/mingw64/bin`).
- Sem Tesseract: se aparecer página que precise de OCR, avise antes de
  instalar qualquer coisa.
- **Extrator:** `python -I scripts/extrair_revista.py <pdf> acervo/texto`
  gera `<nome>.md` (português, com `## Página N` para citar) e
  `<nome>.log` com o que merece conferência humana. Nas edições
  bilíngues, separa e descarta o inglês: a base é só em português. É
  re-executável: sobrescreve a saída.
- **Barra invertida em comando:** ao passar código Python por heredoc no
  Bash, `\b` e `\n` chegaram ao arquivo como caractere de controle e
  quebra de linha. Para patch com barra invertida, grave um `.py` no
  scratchpad e monte a barra com `chr(92)`; depois confira que o arquivo
  não tem caractere de controle.

- **Notícias:** `node scripts/exportar_noticias.cjs` relê as notícias
  publicadas do banco do site (`../site_iteva`, só leitura) e regrava
  `acervo/noticias/`, um `.md` por notícia com título, data, URL e texto.
  Em 11/10/2026 eram 97, de 16/11/2011 a 28/05/2026, o mesmo número
  listado em iteva.org.br/noticias. Não há notícia publicada de 2023, e
  2021 e 2022 têm uma e três. Os 16 rascunhos do banco ficam de fora.

- **Páginas do site:** `python -I scripts/extrair_site.py` lê o
  sitemap.xml, baixa as páginas institucionais, de projeto, de evento e
  a home, e regrava `acervo/site/` (um `.md` por página, com URL e data
  da consulta, mais `rodape.md`). Lê o HTML publicado, não o banco: no
  banco o conteúdo fica em blocos aninhados e parte se perde. Ficam de
  fora as páginas de outros acervos (notícias, vídeos, clipping,
  publicações, transparência). As 30 páginas estão no índice como
  `scripts/indexacao/site.jsonl`, tipo "página do site", sem ano (o
  site não data as páginas; vale a data da consulta).

- **Vídeos:** fluxo em quatro scripts, rodados sem `-I` (pacotes
  instalados com `--user`): baixar com yt-dlp
  (`--cookies-from-browser firefox --js-runtimes node`; o YouTube exige
  login e o desafio em JavaScript), `transcrever_videos.py` (Whisper
  medium no processador; a GTX 1650 não tem a cuBLAS),
  `quadros_videos.py` (folhas com a metade de baixo da tela a cada 4 s,
  para ler o nome de quem fala) e `quadro_em.py` (quadros inteiros em
  tempos específicos, para legenda em animação e cartela final). As
  fichas ficam em `acervo/videos/`, uma por vídeo, e a transcrição
  bruta em `acervo/videos/transcricoes-brutas/`. Falas só têm autor
  quando o nome aparece na tela. Áudio e vídeo não entram no git.

- **Índice:** `python -I scripts/montar_indice.py scripts/indexacao`
  regrava `acervo/indice.csv` (UTF-8 com BOM, separador `;`, sem linha
  `sep=;`) e `acervo/volume.md`. As linhas vêm de
  `scripts/indexacao/*.jsonl`, feitas por leitura de cada texto segundo
  `scripts/indexacao/INSTRUCOES.md`. O **programa** não vem da leitura:
  sai de `projetos/cadastro.csv`, a fonte única de programa e situação
  (ativo, encerrado, a confirmar) de cada projeto. Projeto novo entra no
  cadastro antes de entrar no índice; o script avisa quando falta.

## O que a extração não resolve (Fase 1)

Antes de levar um fato destas situações para uma ficha, confira a página
no PDF:

- **Depoimento e autor.** Quando a página reúne vários depoimentos (2016,
  p. 10 a 16, 19 e 25), nomes e cargos saem separados das falas. A
  extração não garante quem disse o quê. Regra 3: depoimento só entra
  com autor conferido na página.
- **Linha do tempo.** Os anos saem agrupados num título ("2002 2003
  2004...") e os eventos soltos, sem o ano de cada um (2016, p. 6 a 9).
  Data de evento de linha do tempo se lê na página.
- **Caixas com título em imagem.** Em 2023, p. 8 e 9, o nome de cada
  projeto está numa imagem: os parágrafos saem sem dizer de qual projeto
  falam, e a ordem entre caixas pode trocar.

## O que já se sabe sobre o acervo (Fase 0)

- 14 revistas, uma por ano, de 2010 a 2023, iguais às listadas em
  iteva.org.br/publicacoes. Todas têm texto extraível; não há edição
  escaneada.
- Edições bilíngues (português e inglês): **2014, 2015 e 2016**. O
  inglês não entra na base.
- De 2010 a 2015 o cabeçalho das páginas diz "Projeto MídiaCOM <ano>"
  (2010 e 2011) ou "Projeto Midiacom <ano>" (2012 a 2015); de 2016 em
  diante diz "ITEVA <ano>". As primeiras edições são a revista do
  programa Midiacom, não da instituição inteira.
- A edição publicada como 2023 traz "ITEVA 2024" no cabeçalho. Vale
  2023 (`divergencias.md`, item 1).
- Texto que só existe como imagem: capas, anúncios da Midiacom.net,
  algumas frases de destaque e as **páginas de logos de parceiros**
  (por exemplo 2010 p. 27 e 2016 p. 28). Os parceiros dessas páginas
  não saem na extração de texto e precisam ser lidos olhando a página.
- Fonte das revistas: cópia byte a byte de
  `site_iteva/site_legado/public/download/`. O site legado tem também
  um `revista2012-old.pdf`, versão anterior da edição de 2012, que não
  foi copiado.
