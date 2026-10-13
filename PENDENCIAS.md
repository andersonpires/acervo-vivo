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
  `.claude/skills/conteudo-construcom/`.
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
  - Quem Somos diz "matriz em Aquiraz"; desde 2026 a matriz é em
    Eusébio e a unidade de Aquiraz foi fechada (divergência 10);
  - Linha do Tempo escreve "Bruno Sousa Lessa"; o certo é "Bruno de
    Souza Lessa" (divergência 12).
- **Erros publicados:** a notícia de 28/04/2026 dá o dia 24/04 como
  sexta-feira e como quinta-feira; a de 28/05/2026 escreve "Instituto
  Tecnológico Vocacional Avançado", sem o "e"; a de 21/06/2012 traz a
  entrevista duas vezes.

## Do acervo das páginas do site

- **Ficha do Construcom:** a página do projeto no site não trouxe fato
  novo; a ficha já cita a data de início dela.

## Acervos futuros

Na ordem em que o usuário os citou: clipping, vídeos (com transcrição),
transparência (a atualizar sempre), propostas de projeto e relatórios.
O papel de cada um está no `README.md`.

## Do projeto como um todo

- **Repositório remoto:** quando as skills estiverem prontas, criar o
  repositório privado no GitHub. Os PDFs não vão (estão no
  `.gitignore`).
- **Guias e skills dos outros formatos:** post, roteiro de vídeo e
  relatório para parceiro (objetivo 4). Hoje post e roteiro usam regra
  provisória.
- **Fichas dos demais projetos ativos** (objetivo 2), começando quando
  o usuário pedir. A skill do Construcom serve de modelo e deve ser
  generalizada na segunda ficha.
- **Documentar o método para outras OSCs** (objetivo 7).
