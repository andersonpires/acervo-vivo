# Pendências

O que ficou para depois, por decisão do usuário ou por depender dele.
Ao resolver um item, apague-o daqui e registre o resultado onde ele
vive (ficha, cadastro, divergências).

## Do acervo das revistas

- **Leitura visual das páginas que a extração não resolve** (o usuário
  resolve depois). Três tipos:
  - depoimentos agrupados, em que a fala saiu separada do autor
    (sobretudo `revista2016.pdf`, p. 10 a 16, 19 e 25);
  - linhas do tempo, em que o evento saiu sem o ano
    (`revista2013.pdf`, p. 21 a 23; `revista2016.pdf`, p. 6 a 9;
    `revista2020.pdf`, p. 6 e 7);
  - páginas de logos de parceiros, que só existem como imagem (por
    exemplo `revista2010.pdf`, p. 27, e `revista2016.pdf`, p. 28).
- **Revisão geral pelo usuário:** `acervo/indice.csv` (classificação
  feita por leitura automática, conferida só por amostragem), a ficha
  `projetos/construcom.md`, os guias em `voz/` e a skill
  `.claude/skills/conteudo-iteva/`.
- **Situação dos projetos "a confirmar"** em `projetos/cadastro.csv`:
  Idoso Conectado, Provedor Social, Midiacom.net, Centro de Inclusão
  Digital Dragão do Mar, Desenvolvimento de Software, Microsoft S2B,
  Curso Introdução às TICs, Sala de Aula Iteva, Termodinâmica, Eólica,
  Solar, Geodésica, Estação de Tratamento de Esgoto, Estudo de Ensino
  Híbrido do Eusébio, Contação de Histórias Reversas, Água de Beber e
  Festival CumbuCOR. Também confirmar se "Gestão de Projetos" era
  mesmo negócio do condomínio social.

## Do site iteva.org.br (fora deste projeto)

- **Menu desatualizado em relação às decisões de 11/10/2026:** Sisger
  ainda em Midiacom; Construcom também em Construção Sustentável; sem o
  programa Mais Saúde, o ItevaLab e o Empodera Mulher.
- **Página Parceria quebrada:** /p/parceria não mostra nenhum logo; no
  HTML, no lugar das imagens, há só quebras de linha. A home mostra os
  parceiros, mas o primeiro item ("Parceiros do Iteva") é uma imagem
  única com vários logos, sem os nomes em texto.
- **Página Destaques vazia:** /p/destaques só tem o título.
- **Páginas desatualizadas** (achadas no confronto de 12/10/2026):
  - Programa Midiacom lista Sisger e BemTeVi entre os projetos dele;
  - Linha do Tempo para em 2020;
  - Geodésica usa "Cientista do Futuro" e diz que "uma segunda geodésica
    está sendo construída", mas a Linha do Tempo registra as duas
    cúpulas em 2016; atribui a geodésica a "o alemão Richard Fuller"
    (pelo conhecimento geral, Buckminster Fuller era norte-americano;
    conferir antes de corrigir);
  - Idoso Conectado é um anúncio antigo de turma do ConectivIDADE +60;
  - Trabalhe Conosco só tem vagas de 2018, já preenchidas, e uma delas
    dá prazo de envio "até 23/02/2017", antes da data da vaga;
  - Política de Privacidade dá como sede do Iteva "Rodovia CE 04, s/n,
    Caixa Postal 66, Aquiraz - CE, CEP 61.700-000", na abertura e no
    contato do controlador dos dados. A matriz é em Eusébio desde 2026
    (divergência 10). Texto jurídico: corrigir com quem responde pela
    LGPD no Iteva.
  - Política de Privacidade (contato do controlador) e Trabalhe Conosco
    (quatro vagas) mostram ao público "[email protected]" no lugar do
    e-mail: o texto veio do site antigo já embaralhado pela proteção
    contra spam da Cloudflare, sem o código que permitiria recuperá-lo.
    Precisa ser redigitado (iteva@iteva.org.br, se for esse o certo).
- **Clipping do site** (achado na extração de 13/10/2026):
  - a matéria da Rádio Dom Bosco (01/04/2026) aponta para o OneDrive
    pessoal de uma funcionária, que pede login: o público não abre;
  - quatro matérias de 2005 a 2008 apontam para `https://arquivos/...`,
    endereço quebrado do site antigo; os recortes existem em
    `site_legado/public/arquivos/reportagens` e poderiam ir para o site;
  - o campo "veículo" está vazio nas 105 matérias;
  - o título de uma matéria de 05/07/2017 diz "site O Estado Doce" (é o
    jornal O Estado);
  - cerca de metade dos links não abre mais (lista em `situacao` de cada
    arquivo de `acervo/clipping`);
  - dois recortes do site antigo não estão no clipping: Folha de
    S.Paulo, 08/02/2000 (forragem hidropônica), e uma revista,
    provavelmente a ARede, de 2005.
  - a matéria do O Estado sobre o Conectividade+60 no cinema foi
    publicada em 09/06/2025; o site a data em 09/07/2025;
  - o resumo da matéria da Prefeitura do Eusébio sobre o Centro Dia
    (15/01/2026) atribui a ação ao "Projeto Circuito NoCorre", nome que a
    matéria não usa (ela cita hidroterapia, fisioterapia e pilates);
  - o resumo da posse de conselhos de 19/11/2019 grafa COMDIM e CONDIM
    para o mesmo conselho.
- **Nome de Fábio Beneduce no site** (levantamento de 14/10/2026, pela
  decisão da divergência 20; o usuário decide o que tirar):
  - páginas: Quem Somos ("sonho do casal Fábio Beneduce e Vanessa
    Belém"), Linha do Tempo (2018, "Participação de Fábio Beneduce,
    coordenador geral", no Global Engagement Forum) e Eólica ("pesquisas
    desenvolvidas pelo coordenador geral do Iteva, Fábio Beneduce");
  - 22 notícias de 2012 a 2020, uma delas inteira sobre ele
    (28/06/2019, "Coordenador do Iteva é homenageado pela Câmara
    Municipal de Aquiraz"); lista: `grep -l "Beneduce" acervo/noticias`
    menos as que só citam Sara Beneduce;
  - fora do site, nas revistas (13 edições), no clipping (24 matérias) e
    em dois vídeos (Discovery e Microsoft, com o nome na tela).
- **Erros publicados:** a notícia de 28/04/2026 dá o dia 24/04 como
  sexta-feira e como quinta-feira; a de 28/05/2026 escreve "Instituto
  Tecnológico Vocacional Avançado", sem o "e"; a de 21/06/2012 traz a
  entrevista duas vezes.

## Do acervo das páginas do site

- **Ficha do Construcom:** a página do projeto no site não trouxe fato
  novo; a ficha já cita a data de início dela.

## Do acervo da transparência

- **Pontos a conferir com a contabilidade**, listados em
  `acervo/transparencia/conferir.md` e refeitos a cada exportação: soma
  das parcelas diferente do valor total (NoCorre 2024, Conectividade
  Eusébio 2023, CDF 2020, Construcom 2019, Midiacom 2018, Conectividade
  2020), convênio sem tabela de parcelas (Conectividade Eusébio 2024),
  cinco sem situação da prestação de contas e o Midiacom Aquiraz 2017
  com "Aguardando (Município em atraso)".

## Do acervo do clipping

- **32 matérias à espera do Internet Archive:** o Archive bloqueou as
  consultas (429) em 13/10/2026. Rodar de novo `python -I
  scripts/extrair_clipping.py` (sem `--sem-arquivo`) outro dia; só essas
  vão à rede. Estão marcadas "consulta ao Internet Archive pendente".
- **14 sem texto a extrair:** 6 vídeos do YouTube (dá para transcrever
  com o fluxo dos vídeos, se for útil), 7 posts de Instagram e 1 do
  LinkedIn (pedem login) e o áudio da Rádio Dom Bosco (no OneDrive).

## Acervos futuros

Clipping, vídeos e transparência estão prontos (a transparência, a
atualizar sempre). Faltam propostas de projeto e relatórios.
O papel de cada um está no `README.md`.

## Do projeto como um todo

- **Repositório remoto:** quando as skills estiverem prontas, criar o
  repositório privado no GitHub. Os PDFs não vão (estão no
  `.gitignore`).
- **Guias e skills dos outros formatos:** post e relatório para
  parceiro (objetivo 4). Hoje o post usa regra provisória. O roteiro já
  tem guia (`voz/roteiro.md`) e skill (`roteiro-video`), testados em
  `testes/roteiro/`; falta testar o Modo B (montagem com gravação
  bruta), que pede gravação ainda não editada.
- **Vídeo da Discovery:** o Whisper traduziu as falas em inglês em vez
  de transcrevê-las, e parou em 3:01. Produção externa; refazer só se
  for útil.
- **Fichas dos demais projetos ativos** (objetivo 2), começando quando
  o usuário pedir. A skill de conteúdo já é geral (`conteudo-iteva`,
  14/10/2026): sem ficha, ela busca os fatos do projeto no acervo pelo
  índice; uma ficha nova só deixa isso mais rápido e mais seguro.
- **Documentar o método para outras OSCs** (objetivo 7).
