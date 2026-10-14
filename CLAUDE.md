# Orientações do projeto: Acervo Vivo

Base de conhecimento do Iteva, montada a partir do que a casa já
publicou, para produzir conteúdo novo com a voz e os fatos da casa. O
`README.md` diz o propósito e o papel de cada acervo; este arquivo diz
como trabalhar. Leia também `PENDENCIAS.md` (o que ficou para depois) e
`divergencias.md` (decisões entre fontes) antes de começar.

## Estado atual (14/10/2026)

| Acervo | Pasta | Situação |
|---|---|---|
| Revistas 2010 a 2023 | `acervo/texto` | pronto; principal modelo de escrita |
| Notícias do site | `acervo/noticias` | pronto (97, conferidas contra /noticias) |
| Páginas do site | `acervo/site` | pronto (30 páginas e rodapé) |
| Vídeos | `acervo/videos` | pronto (19; 4 são produção externa) |
| Transparência | `acervo/transparencia` | pronto; atualizar a cada lançamento |
| Clipping | `acervo/clipping` | pronto (105 matérias, 40 com o texto original; 32 à espera do Internet Archive); consulta, nunca modelo de escrita |
| Imagens (revistas, notícias, site) | `acervo/imagens` | pronto (1.285 fichas, 1.161 sugeríveis; catálogo e buscador); plano e método em `prd-imagens.md` |
| Propostas de projeto e relatórios | | futuros; o usuário indica onde estão os arquivos |

Produtos prontos: índice (`acervo/indice.csv`, `acervo/volume.md`),
cadastro de projetos (`projetos/cadastro.csv`), fichas
(`projetos/iteva.md`, `projetos/construcom.md`), guias de voz
(`voz/revista.md`, `voz/noticia.md`, `voz/roteiro.md`, `voz/imagens.md`),
o acervo de imagens (`acervo/imagens`, com `catalogo.jsonl` e
`scripts/buscar_imagens.py`) e as skills `conteudo-iteva` (notícia,
matéria, post e legenda de qualquer projeto, com imagens sugeridas) e
`roteiro-video` (em `.claude/skills/`), testadas (`testes/`). As
divergências 1 a 23 estão decididas. A 20 vale para tudo: Fábio
Beneduce não é nomeado em texto novo ("um dos fundadores").

## Mapa

```
acervo/revistas/   PDFs originais (fora do git; integridade em SHA256SUMS)
acervo/texto/      revistas em texto, "## Página N" para citar
acervo/noticias/   uma notícia por arquivo
acervo/site/       páginas do site publicado
acervo/videos/     ficha e transcrição por vídeo (+ transcricoes-brutas/)
acervo/transparencia/  convênios, resumo.csv, conferir.md, historico/
acervo/indice.csv  tudo indexado por fonte, ano, projeto, tipo
projetos/          cadastro.csv (fonte única de programa e situação) e fichas
voz/               guias de escrita medidos nos textos reais
scripts/           extratores, índice e indexacao/*.jsonl
testes/            testes das skills contra textos e vídeos reais
```

## Regras permanentes

1. **Originais intocáveis.** Nada em `acervo/revistas` se altera, move ou
   renomeia. Conferir: `cd acervo/revistas && sha256sum -c SHA256SUMS`.
   Se faltar PDF, a origem é `../site_iteva/site_legado/public/download/`.
2. **Trabalhe em fases.** Ao fim de cada fase, mostre o resultado e espere
   aprovação. Commit ao fim de cada fase.
3. **Nunca invente** número, nome, data, local ou depoimento. O que não
   está na fonte vira `[FALTA: descrição]`. Fala só tem autor quando a
   fonte o mostra (na revista, conferido na página; no vídeo, nome na
   tela).
4. **Todo fato em ficha leva fonte:** arquivo e página, URL e data, ou
   "Curadoria" (decisão do usuário registrada em `divergencias.md`).
5. **Fontes que divergem vão para `divergencias.md`**, para o usuário
   decidir. O site é fonte, não verdade: tem trechos desatualizados.
6. **Português do Brasil, sem travessão nem meia-risca** em tudo que se
   escreve: fichas, guias, comentários, commits. Use vírgula, dois-pontos,
   parênteses ou duas frases.
7. **Modelo de escrita** só das revistas (principalmente), notícias e
   páginas do site. Clipping e produções externas são consulta.
8. **Fatos institucionais** (matriz em Eusébio desde 2026, unidades,
   contato, fundação) vêm de `projetos/iteva.md`. Telefone em texto novo:
   quem pede define; senão, (85) 3362-3210.

## Método que funcionou

Para cada acervo novo, a mesma sequência:

1. **Reconhecimento:** volume, formato, onde está, o que falta. Parar.
2. **Extração** por script re-executável, com fonte e data em cada
   arquivo. Conferir por amostragem lendo o resultado.
3. **Índice:** linhas em `scripts/indexacao/<acervo>.jsonl`; projeto novo
   entra antes em `projetos/cadastro.csv`.
4. **Confronto** com o resto do acervo: o que diverge vai para
   `divergencias.md`; o que é só desatualizado do site vai para
   `PENDENCIAS.md`.
5. **Fichas e guias** só com fato de fonte; números de guia medidos
   (`scripts/medir_voz.py`), nunca impressão.
6. **Teste** de skill: reduzir um texto real (fora dos exemplos do guia)
   a briefing, gerar sem acesso ao original, comparar e corrigir o guia.

Trabalho de leitura em volume (indexar revistas, fichas de vídeo) foi
dividido entre agentes com um arquivo comum de instruções; revise por
amostragem o que voltar e confira toda afirmação numérica antes de
gravar em guia ou ficha. Várias das minhas próprias generalizações
caíram nessa conferência.

## Comandos de cada acervo

| O quê | Comando | Observação |
|---|---|---|
| Revista | `python -I scripts/extrair_revista.py <pdf> acervo/texto` | descarta o inglês das edições bilíngues |
| Notícias | `node scripts/exportar_noticias.cjs` | lê o banco do site, só leitura |
| Páginas | `python -I scripts/extrair_site.py` | lê o HTML publicado a partir do sitemap |
| Vídeos | yt-dlp, `transcrever_videos.py`, `quadros_videos.py`, `quadro_em.py` | ver armadilhas; mídia fica fora do git |
| Clipping | `node scripts/exportar_clipping.cjs`, depois `python -I scripts/extrair_clipping.py` | busca o original (página ou Internet Archive); recortes escaneados transcritos à mão em `acervo/clipping/recortes` |
| Transparência | `node scripts/exportar_transparencia.cjs` | gera `conferir.md` e `mudancas.md`; valores por data não provam liberação |
| Imagens | `node scripts/exportar_imagens_site.cjs`, `python -I scripts/extrair_imagens_revista.py [ano...]`, depois `cd acervo/imagens && sha256sum arquivos/* > SHA256SUMS` | arquivos e páginas fora do git; contexto em `acervo/imagens/contexto` |
| Fichas de imagem | `python -I scripts/paginas_especiais_revista.py` (capas e parceiros), `python -I scripts/preparar_imagens.py` (prévias, lotes, folhas), agentes com `acervo/imagens/INSTRUCOES.md`, `python -I scripts/conferir_fichas_imagens.py [lote]` | uma ficha por imagem em `acervo/imagens/fichas` |
| Catálogo de imagens | `python -I scripts/catalogar_imagens.py`, depois o índice | `acervo/imagens/catalogo.jsonl` (busca, prioridade, duplicatas) |
| Índice | `python -I scripts/montar_indice.py scripts/indexacao` | rodar depois de qualquer exportação |
| Medidas de voz | `python -I scripts/medir_voz.py > voz/medidas.md` | |

Os scripts de Node leem o projeto do site ao lado (`../site_iteva`): o
driver `pg` vem de `site_novo/node_modules` e a `DATABASE_URI` do `.env`
de lá. Esse banco é compartilhado com outros sistemas: só a role do site,
só o banco do site, e escrita apenas quando o usuário pedir correção no
site (seguir então o `CLAUDE.md` de `../site_iteva`).

## Armadilhas desta máquina (Windows)

- **Barra invertida reduzida.** Código passado por heredoc ou `python -c`
  perdeu barras: `\b` virou caractere de controle e `\n` virou quebra de
  linha dentro de string. A ferramenta Write também converte escapes
  `\uXXXX` em caracteres. Para patch com barra invertida, gravar um `.py`
  no scratchpad e montar a barra com `chr(92)`; depois conferir que o
  arquivo não tem caractere de controle (`node --check` nos `.cjs`).
- **Mojibake.** Conferir depois de gravar texto com acento:

  ```powershell
  $pat = "[\u00C2\u00C3\u00E2][\u0080-\u00BF]|\uFFFD"
  $txt = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes("CAMINHO"))
  [regex]::Matches($txt, $pat) | ForEach-Object { $_.Value }
  ```

  Saída de Python redirecionada com `>` sai em cp1252: o script precisa
  de `sys.stdout.reconfigure(encoding="utf-8")`. Com `-I`, o Python ignora
  `PYTHONIOENCODING`.
- **`python -I` ignora pacotes `--user`.** yt-dlp, faster-whisper e av
  foram instalados assim: os scripts de vídeo rodam sem `-I`.
- **YouTube** pede login e um desafio em JavaScript: `python -m yt_dlp
  --cookies-from-browser firefox --js-runtimes node` (o Firefox está
  logado; Chrome e Edge cifram os cookies e falham).
- **Whisper:** faster-whisper 1.2 não abre arquivo com av 19; o script
  decodifica o áudio antes. A GPU (GTX 1650) não tem a cuBLAS: roda no
  processador, cerca de metade da duração do vídeo.
- **Folhas de quadros** cortam legenda em animação e o alto das cartelas:
  completar com `quadro_em.py` em quadros inteiros.
- **CSV para Excel pt-BR:** UTF-8 com BOM, separador `;`, sem linha
  `sep=;`.

## Limites conhecidos do acervo

- **Revistas:** depoimentos agrupados (2016, p. 10 a 16, 19 e 25),
  linhas do tempo (anos separados dos eventos) e páginas de logos de
  parceiros precisam de leitura da página; estão em `PENDENCIAS.md`. Em
  2023, p. 8 e 9, os títulos dos projetos estão em imagem.
- **Vídeos:** fala sem nome na tela fica sem autor; o vídeo da Discovery
  saiu traduzido pelo Whisper e incompleto.
- **Transparência:** o painel é atualizado pela contabilidade; o que não
  fecha está em `acervo/transparencia/conferir.md`.
