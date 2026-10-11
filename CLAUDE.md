# Orientações do projeto: Acervo Vivo

Leia antes de qualquer alteração. O `README.md` diz o que o projeto é e
para que serve; este arquivo diz como trabalhar nele.

## Regras permanentes

1. **Os arquivos em `acervo/revistas` são originais: nunca alterar, mover
   ou renomear.** Tudo que se extrai deles vai para outra pasta.
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

## O que já se sabe sobre o acervo (Fase 0)

- 14 revistas, uma por ano, de 2010 a 2023, iguais às listadas em
  iteva.org.br/publicacoes. Todas têm texto extraível; não há edição
  escaneada.
- Edições bilíngues (português e inglês): **2014, 2015 e 2016**.
- De 2010 a 2015 o cabeçalho das páginas diz "Projeto MídiaCOM <ano>"
  (2010 e 2011) ou "Projeto Midiacom <ano>" (2012 a 2015); de 2016 em
  diante diz "ITEVA <ano>". As primeiras edições são a revista do
  programa Midiacom, não da instituição inteira.
- A edição publicada como 2023 traz "ITEVA 2024" no cabeçalho. Está em
  `divergencias.md`, sem decisão.
- Texto que só existe como imagem: capas, anúncios da Midiacom.net,
  algumas frases de destaque e as **páginas de logos de parceiros**
  (por exemplo 2010 p. 27 e 2016 p. 28). Os parceiros dessas páginas
  não saem na extração de texto e precisam ser lidos olhando a página.
- Fonte das revistas: cópia byte a byte de
  `site_iteva/site_legado/public/download/`. O site legado tem também
  um `revista2012-old.pdf`, versão anterior da edição de 2012, que não
  foi copiado.
