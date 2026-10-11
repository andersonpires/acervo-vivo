# Fase 7: texto real e texto gerado, lado a lado

- **Texto real:** notícia de 20/05/2024, "Projeto Construcom capacita
  idosos através da construção sustentável"
  (`acervo/noticias/2024-05-20-projeto-construcom-capacita-idosos-atraves-da-construcao-sustentavel.md`).
  Não foi usada como exemplo em nenhum guia.
- **Briefing:** `testes/fase7/briefing.md`, só fatos.
- **Texto gerado:** `testes/fase7/gerado.md`, escrito por um agente que
  recebeu só a skill, o briefing, a ficha e o guia, sem acesso ao
  acervo.

## Medidas (mesma régua de `scripts/medir_voz.py`)

| Medida | Real | Gerado | Notícias 2024 a 2026 |
|---|---|---|---|
| Palavras de corpo | 418 | 255 | mediana 344 |
| Frase, mediana de palavras | 24 | **15** | 25 |
| Frase, 90% até | 36 | 26 | 38 |
| Parágrafo, mediana de palavras | 57 | **28** | 48 |
| Primeira pessoa do plural | 0 | 0 | 4,1 por mil |

## Parágrafo a parágrafo

| Trecho | Real | Gerado | Divergência de voz |
|---|---|---|---|
| Título | "Projeto Construcom capacita idosos através da construção sustentável" | "Construcom capacita turma de 40 alunos em construção sustentável em Beberibe" | Gerado põe número e lugar; real fala em "idosos". Os dois seguem sujeito + verbo no presente. |
| Abertura | "No coração de Beberibe-CE, o Projeto Construcom surge como uma luz de esperança para a comunidade idosa. Mais do que apenas oferecer capacitação, o Construcom é um verdadeiro catalisador de mudanças" | "O Instituto Tecnológico e Vocacional Avançado (ITEVA) concluiu, em [FALTA: data], a turma de 2024 do Projeto Construcom em Beberibe" | **Maior diferença.** O real abre por emoção; o gerado, por fato seco. O guia só previa a abertura factual. |
| Conteúdo do curso | um parágrafo de 50 palavras, lista corrida | dois parágrafos curtos | Gerado fragmenta o que o real junta. |
| Depois da fala | "Essa abordagem integral capacita os alunos não apenas com conhecimento teórico, mas também com habilidades práticas" | nada | O real interpreta a fala em uma frase; o gerado não. |
| Histórias | Dona Socorro e Francisca, cada uma seguida de uma frase sobre o que aquilo significou ("um importante passo em sua jornada de autossuficiência") | as mesmas, só o fato | O real diz o que a mudança significou para a pessoa; o gerado para no fato. |
| Fecho | "Para a equipe do Construcom, não há recompensa maior do que testemunhar essas histórias" | "o projeto é inclusivo, e não assistencial: a proposta não é formar pedreiros, mas construtores aptos" | Gerado importa a tese da **revista** para a notícia. O real fecha no registro da notícia: a equipe, as histórias, a comunidade. |
| Nome da instituição | não aparece | nome completo na primeira menção | Gerado segue o guia; o real não traz o nome. |
| Crédito | não há | `[FALTA]` | Gerado segue o guia. |

## O que o teste confirmou

- **Regra 3 cumprida.** Nenhum número, nome ou fala sem origem. O
  agente marcou `[FALTA]` em data, parceiros e crédito, e deixou de fora
  por conta própria os parceiros de Beberibe que a ficha registra, mas
  para outra ação (as reformas). Também não pôs "Dona" em quem o
  briefing não tratava assim.
- **Perguntas certas.** As seis perguntas que faria antes de escrever
  são exatamente as lacunas do briefing.

## O que mudou no guia por causa do teste

Em `voz/noticia.md`:

1. **Duas aberturas, não uma.** A de cena ou emoção também é da casa (5
   das 18 recentes), com uma condição: a cena tem de ser fato do
   briefing. "Luz de esperança" e "catalisador de mudanças" são imagem
   sem fato; "chegou apoiada numa bengala e trocou-a por um pandeiro" é
   cena com fato.
2. **Não fragmentar.** Frase de 20 a 30 palavras e parágrafo de duas
   frases, juntando fato e consequência. Cinco frases de 15 palavras
   seguidas soam como relatório.
3. **Uma frase de sentido depois da história**, com palavras que o
   briefing permita (autonomia, convivência), sem exagerar o fato.
4. **Fecho no registro da notícia:** equipe, comunidade, continuidade.
   A tese da revista ("não assistencial", "construtores aptos") não vai
   para a notícia.

Na skill, o passo 3 passou a lembrar esses quatro pontos.

## O que não mudou, de propósito

- O texto real não tem o nome da instituição nem crédito. O guia
  continua pedindo os dois: são da maioria das notícias recentes e
  ajudam a prestação de contas.
- "Thays" ou "Tays" segue em aberto (divergência 8).
