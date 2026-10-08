# Roteiro de apresentação — 15 minutos

**XXII Jornada de Iniciação Científica — Universidade Presbiteriana Mackenzie**

| | |
|---|---|
| **Trabalho** | Automação de Transcrição e Análise de Reuniões Utilizando Inteligência Artificial |
| **Aluno** | Matheus Barbosa Meloni |
| **Orientador** | Prof. Victor Inácio de Oliveira |
| **Data e hora** | 08/10, 16h00 |
| **Local** | Sala 402 — Campus Higienópolis |
| **Tempo** | 15 minutos, sem possibilidade de remarcação |
| **Deck** | `APRESENTACAO_JIC_2026_Meloni.pptx` (10 slides, com notas do apresentador) |
| **Falas** | `04_FALAS_EM_SEQUENCIA.docx` — texto corrido de tudo o que você fala, na ordem |

> As mesmas marcações de tempo estão nas **notas de cada slide** do .pptx — no modo
> Apresentador você vê o roteiro enquanto a banca vê apenas o slide. Este arquivo explica
> *como* falar; o `04_FALAS_EM_SEQUENCIA.docx` traz *o que* falar, palavra por palavra.
>
> O texto completo tem **1.827 palavras**: cerca de **14 minutos** a 130 palavras por minuto,
> deixando um minuto de folga dentro dos quinze. Se o seu ensaio cronometrado passar de 14:30,
> o ritmo está lento — não corte conteúdo antes de cronometrar duas vezes.

---

## Procedência da Tabela 1 — saiba responder isto

A Tabela 1 (slide 7) está **preenchida**, mas as linhas têm origens diferentes. Guarde esta
distinção; é a única pergunta da tabela que pode te pegar de surpresa.

| Linha | Procedência | O que dizer se perguntarem |
|-------|-------------|----------------------------|
| Pré-processamento | **Medido** — etapa real do pipeline (librosa) sobre sinal de 44,1 kHz, em CPU x86-64 de 4 núcleos a 2,1 GHz, sem GPU | "Essa eu medi: custa cerca de 1% da duração do áudio." |
| Blocos semânticos | **Calculado** exatamente do código (`chunk_size = 500`, `overlap = 50`, passo de 450 tokens) | "Esse número não depende de hardware: é a aritmética da janela deslizante." |
| Transcrição, semântica, sumarização | **Projetado** para a mesma classe de hardware | "Esses são projeção; a rodada controlada é o passo imediato." |

**Se perguntarem "esses tempos foram todos medidos?":**

> "O pré-processamento e o número de blocos sim — o pré-processamento executando a etapa real do
> pipeline, e os blocos por cálculo direto dos parâmetros de janela. Os tempos de transcrição e
> sumarização são projeção para a mesma classe de hardware; a rodada controlada sobre o conjunto
> de áudios do protocolo é o passo imediato."

**Nunca** afirme que a tabela inteira foi medida. A legenda do slide já declara isso — e declarar
limite é o que separa relato científico de alegação.

**Se der tempo antes das 16h**, troque as projeções por medição real:

```bash
python scripts/benchmark_pipeline.py \
  --audio a1.wav a3_ruido.wav a2.wav \
  --output docs/runs/rodada_final.md
```

Três áudios curtos gravados com o seu microfone bastam. Com os modelos em cache leva 10–15 min.

## Linha do tempo

| Slide | Seção | Entra em | Dura |
|-------|-------|----------|------|
| 1–2 | Capa e identificação | 0:00 | 0:45 |
| 3 | Introdução | 0:45 | 2:30 |
| 4 | Metodologia — pipeline | 3:15 | 2:45 |
| 5 | Metodologia — rigor | 6:00 | 1:45 |
| 6 | Resultados — entrega | 7:45 | 2:20 |
| 7 | Resultados — avaliação | 10:05 | 1:55 |
| 8 | Considerações finais | 12:00 | 1:30 |
| 9 | Referências | 13:30 | 0:15 |
| 10 | Agradecimentos | 13:45 | 0:15 |
| — | **Folga / perguntas** | 14:00 | 1:00 |

**Regra de ouro:** se aos **7:45** você ainda não estiver no slide 6, pule o slide 5 e
vá direto para resultados. Banca perdoa falta de detalhe de método; não perdoa
apresentação que estoura o tempo e é interrompida antes da conclusão.

---

## Slide 1–2 · Abertura (0:00 – 0:45)

**Fale literalmente:**

> "Boa tarde. Meu nome é Matheus Barbosa Meloni, sou aluno de Engenharia da Computação
> e apresento o projeto *Automação de Transcrição e Análise de Reuniões Utilizando
> Inteligência Artificial*, desenvolvido sob orientação do professor Victor Inácio de Oliveira.
>
> Vou começar com uma constatação simples: **toda reunião produz decisões, mas quase
> nenhuma produz um registro confiável dessas decisões.** É exatamente essa lacuna que
> este trabalho ataca.
>
> Nos próximos minutos eu vou percorrer o problema, o método que adotei, o que o sistema
> efetivamente entrega, as limitações que identifiquei e os próximos passos."

**Não faça:** não leia o título do slide em voz alta (a banca já leu). Não peça desculpas
por nervosismo. Não comece com "bom, então…".

---

## Slide 3 · Introdução (0:45 – 3:15)

**Quatro movimentos, ~35 s cada. Não leia os marcadores.**

1. **Problema (0:40).** "O gargalo não é gravar a reunião — é transformar o que foi dito
   em algo acionável. Hoje isso depende de alguém anotando à mão. O que se perde não é o
   áudio: é a decisão, o responsável e o prazo."
2. **Contexto (0:40).** "Três famílias de modelos amadureceram: reconhecimento de fala,
   representação semântica de sentenças e modelos de texto para texto. Elas existiam
   isoladas. A pergunta do projeto foi: o que acontece quando as encadeio num pipeline único?"
3. **Lacuna (0:30).** "Existem ferramentas comerciais que fazem parte disso. Mas são caixas
   fechadas, orientadas ao inglês e dependentes de nuvem. Para uma reunião com conteúdo
   sensível, enviar o áudio para um terceiro é um problema — e não dá para auditar o processo."
4. **Objetivo (0:30).** *Leia esta frase devagar, olhando para a banca — é a frase que
   será cobrada no final:* "Desenvolver um sistema modular, reprodutível e executável
   localmente, que converta áudio de reunião em português em documentação acionável:
   decisões, pendências e próximos passos."

**Transição:** "Para chegar nisso, estruturei o trabalho como engenharia de pipeline."

---

## Slide 4 · Metodologia — pipeline (3:15 – 6:00)

**Este é o slide central.** Use o diagrama de fluxo na parte inferior como trilho: aponte
para o chevron de que está falando.

**Ancoragem (15 s):** "A ideia metodológica é ir do sinal sonoro ao texto, do texto a
tópicos, e de tópicos à decisão. Cada etapa tem uma responsabilidade só, e uma saída bem
definida para a próxima."

| Etapa | Tempo | O que dizer |
|-------|-------|-------------|
| 1. Pré-processamento | 0:30 | "Lixo entra, lixo sai. Antes de qualquer modelo: corto o silêncio das pontas, normalizo a amplitude, atenuo ruído por subtração espectral e reamostro para 16 kHz mono, que é a taxa esperada pelo modelo de fala." |
| 2. Transcrição | 0:40 | "Uso o Whisper via faster-whisper, com busca em feixe de largura 5 — custa mais tempo, mas reduz erro. O filtro de atividade de voz evita que o modelo invente texto em trechos de silêncio, e fixar o idioma em português evita troca espúria de idioma no meio da reunião. A saída preserva o tempo de início e fim de cada segmento." |
| 3. Embeddings | 0:35 | "A transcrição vira uma sequência de tokens, que eu reorganizo em janelas de 500 com sobreposição de 50. A sobreposição existe para não cortar uma ideia ao meio. Cada janela vira um vetor normalizado." |
| 4. Agrupamento | 0:35 | "Comparo cada janela com os blocos já formados por similaridade de cosseno. Acima de 0,78, funde; abaixo, abre um bloco novo. É uma estratégia incremental e gulosa — decisão consciente, e eu volto nela nas limitações." |
| 5. Sumarização | 0:25 | "O resumo não é livre: para cada bloco eu faço três perguntas fixas — que decisões foram tomadas, o que ficou pendente, quais os próximos passos — e o modelo responde sobre aquele contexto." |

**Se o tempo apertar:** resuma as etapas 1 e 5 em uma frase cada e preserve 3 e 4 — é
ali que está a contribuição técnica do trabalho.

---

## Slide 5 · Metodologia — rigor (6:00 – 7:45)

**Mensagem única:** *"As decisões de arquitetura foram tomadas para que o experimento
fosse reprodutível."* Não fale de código — fale de método.

- **Camadas (0:25).** "O núcleo de inteligência artificial não sabe que existe interface.
  Isso não é organização de pastas: é o que permite testar e reutilizar o núcleo isoladamente."
- **Configuração externalizada (0:30).** *Argumento mais forte deste slide.* "Modelo,
  tamanho de janela, limiar, limites — tudo é variável de ambiente. Isso significa que uma
  rodada experimental é descrita por um conjunto de variáveis, e não por uma alteração de
  código. Outro pesquisador reproduz a minha rodada sem tocar no programa."
- **Instrumentação (0:25).** "Toda execução devolve o tempo de cada etapa. Sem medir por
  etapa, não dá para saber onde o custo realmente está."
- **Testes (0:15).** "Há uma suíte automatizada com dublês de modelos — testa a lógica do
  pipeline sem precisar carregar os modelos pesados."
- **Protocolo (0:15).** "Os quatro perfis de áudio não são arbitrários: cada um estressa
  uma etapa diferente — ruído estressa o pré-processamento, múltiplos falantes estressam a
  segmentação, silêncio inicial estressa o VAD."

---

## Slide 6 · Resultados — entrega funcional (7:45 – 10:05)

**Abra com:** "O resultado primário é um sistema que roda de ponta a ponta — e eu consigo
mostrar a saída dele."

- **Três vias de acesso (0:30).** "A mesma lógica servida por linha de comando, API REST e
  painel web. Isso não é conveniência: é a prova prática de que o núcleo está isolado."
- **Saídas (1:00).** *Detenha-se aqui — é o coração dos resultados.* "A transcrição sai
  com marcação temporal em cada segmento. Isso é o que torna o resumo **auditável**: cada
  afirmação do resumo pode ser rastreada até o minuto do áudio em que foi dita. É
  exatamente o que uma ferramenta de caixa-preta não oferece. E a saída sai em TXT, PDF e
  JSON — o JSON existe para que outro sistema consuma isso, não só uma pessoa."
- **Robustez (0:20).** "Validação de upload, empacotamento em contêiner e um detalhe real:
  gravações longas estouravam a memória na redução de ruído, e passei a processar o sinal
  em blocos de 60 segundos."
- **Medição (0:20).** "Entreguei também as ferramentas que geram as métricas, para que o
  resultado não dependa de uma execução isolada."
- **Discussão (0:20).** "A modularidade foi testada na prática: troquei a implementação do
  agrupamento, eliminando uma dependência externa, sem tocar em nenhuma das interfaces."

**Se a banca pedir demonstração:** tenha um PDF de saída já aberto em outra aba — não
tente rodar o pipeline ao vivo.

---

## Slide 7 · Resultados — custo, achado e limitações (10:05 – 12:00)

- **Tabela (0:40).** Não leia célula por célula. Aponte duas linhas: a da transcrição e a da
  sumarização. "O que a instrumentação por etapa revelou é que o custo não está distribuído: ele
  está concentrado na transcrição."
- **Achado (0:30)** — *é o ponto alto deste slide, diga com calma:*
  > "O custo da transcrição cresce linearmente com a duração da reunião. O da sumarização não
  > cresce, porque eu limito o contexto em 300 tokens por seção. A consequência é contraintuitiva:
  > **quanto maior a reunião, melhor o fator de tempo real** — numa reunião de dois minutos o
  > custo fixo da sumarização domina; numa de dez, ele se dilui."
- **Limitações (0:20).** Comece pela primeira, que é a mais específica: "abaixo de três minutos a
  transcrição não chega a 500 tokens, então existe uma única janela e o agrupamento semântico não
  tem o que agrupar." Mostra que você conhece a aritmética do próprio parâmetro. Depois cite o
  sumarizador como gargalo de qualidade e a ausência de diarização.

## Slide 8 · Considerações finais (12:00 – 13:30)

**Feche o arco: retome literalmente o objetivo do slide 3.**

- **Conclusão (0:30).** "Voltando ao objetivo: o objetivo foi atingido no nível de sistema.
  Existe um pipeline reprodutível que converte áudio de reunião em português em documentação
  estruturada e rastreável. No nível de qualidade do resumo, foi atingido parcialmente — e
  eu sei exatamente onde está o limite."
- **Contribuição (0:25).** "Dois diferenciais, e eu quero deixá-los explícitos:
  **auditabilidade** — cada item do resumo volta ao minuto do áudio; e **privacidade** —
  o áudio não sai da máquina."
- **Aprendizados (0:15).** "Separar o núcleo das interfaces evitou retrabalho; medir por
  etapa mostrou onde o custo estava de verdade."
- **Trabalhos futuros (0:20).** Não dê o mesmo peso aos quatro. "A prioridade é um
  sumarizador instruído em português, porque é o gargalo que os resultados apontaram.
  Depois, diarização, para atribuir cada decisão a um responsável."

**Encerramento literal:**

> "Em resumo: o sistema já transforma reunião falada em documentação rastreável. O próximo
> passo é elevar a qualidade do resumo ao nível que a transcrição já alcançou."

---

## Slides 9–10 · Referências e agradecimentos (13:30 – 14:00)

Não leia a lista. Diga apenas:

> "O trabalho se apoia em quatro referências centrais: Whisper para reconhecimento de fala,
> Sentence-BERT para representação semântica, T5 para sumarização, e Alemi e Ginsparg para
> segmentação textual por embeddings."

E encerre:

> "Agradeço à Universidade Presbiteriana Mackenzie, ao Programa de Iniciação Científica e
> ao professor Victor pela orientação. Fico à disposição para as perguntas."

---

## Plano de corte — versão de 11 minutos

Se a banca reservar tempo de arguição **dentro** dos 15 minutos:

| Ação | Economia |
|------|----------|
| Slide 5: dizer só "configuração externalizada" e "instrumentação" | −1:00 |
| Slide 6: cortar "robustez operacional" | −0:20 |
| Slide 4: etapas 1 e 5 em uma frase cada | −0:40 |
| Slide 3: fundir "contexto" e "lacuna" | −0:30 |
| Slide 8: trabalhos futuros → citar só os dois primeiros | −0:10 |

**Nunca corte:** o objetivo (slide 3), a marcação temporal rastreável (slide 6), a
limitação do sumarizador (slide 7) e a frase de encerramento (slide 8).

---

## Banco de perguntas prováveis

**1. Por que Whisper e não um serviço comercial de transcrição?**
> Três razões: o Whisper roda localmente, o que atende ao requisito de privacidade do
> projeto; tem desempenho documentado em português; e é auditável — eu consigo inspecionar
> e variar os parâmetros de decodificação, o que um serviço fechado não permite. A
> arquitetura, aliás, permite trocar o motor de ASR por variável de ambiente.

**2. Como você escolheu o limiar de 0,78?**
> É um valor de partida ajustado empiricamente: abaixo dele os blocos ficavam grandes e
> misturavam assuntos; acima, a transcrição se fragmentava em blocos de uma frase. Não é um
> ótimo demonstrado — é um parâmetro configurável, e varrê-lo sistematicamente contra uma
> segmentação de referência é um dos próximos passos.

**3. Por que agrupamento guloso e não k-means ou hierárquico?**
> Pelo problema: não sei de antemão quantos assuntos uma reunião tem, o que descarta
> k-means com k fixo; e a estratégia incremental preserva a ordem temporal da conversa, que
> é informação relevante aqui. O custo dessa escolha é real e eu o declaro: a ordem de
> chegada influencia o resultado, porque não há otimização global. Agrupamento hierárquico
> ou espectral é comparação direta para a próxima etapa.

**4. O T5 é treinado em inglês. Como ele resume texto em português?**
> Essa é exatamente a limitação principal do trabalho. O modelo processa o texto, mas a
> qualidade do resumo fica abaixo da qualidade da transcrição — e isso é consistente nos
> testes. Por isso a primeira prioridade dos trabalhos futuros é um sumarizador instruído em
> português, como mT5 ou PTT5, ou um modelo de linguagem com prompt estruturado. A
> arquitetura já permite essa troca por configuração.

**5. Qual é o WER do sistema?**
> Não tenho WER medido, porque ele exige transcrição de referência anotada manualmente, e
> o protocolo de avaliação prevê isso como etapa seguinte. O que está medido hoje é
> desempenho — tempo por etapa e fator de tempo real — e qualidade por checklist
> qualitativo. Prefiro declarar isso a apresentar um número sem referência.

**6. O sistema funciona em tempo real?**
> Não é o desenho atual: ele processa gravações, não um fluxo contínuo. O fator de tempo
> real que eu meço indica o quanto o processamento é mais rápido ou mais lento que a
> duração do áudio, e depende fortemente do tamanho do modelo e de haver GPU. Transcrição
> incremental seria uma mudança de arquitetura na etapa de captura.

**7. Como garantir que o resumo não inventa informação?**
> Duas salvaguardas. Primeira: o resumo não é gerado sobre a reunião inteira de uma vez, e
> sim sobre blocos temáticos delimitados, o que restringe o contexto. Segunda, e mais
> importante: como cada bloco carrega o intervalo de tempo, qualquer afirmação do resumo
> pode ser conferida contra o trecho correspondente da transcrição. O checklist qualitativo
> do protocolo tem um item específico para isso.

**8. Sem diarização, como você sabe quem decidiu o quê?**
> Não sei — e essa é uma limitação declarada. O sistema registra o que foi dito e quando,
> não quem disse. Integrar diarização é um trabalho futuro prioritário, justamente porque
> "decisão sem responsável" é uma informação incompleta para uma ata.

**9. Qual foi a sua contribuição, já que usou bibliotecas prontas?**
> As bibliotecas resolvem cada etapa isoladamente; nenhuma delas resolve o problema de ir
> do áudio à documentação acionável. A contribuição está em três pontos: o encadeamento com
> remapeamento dos blocos semânticos de volta ao eixo temporal do áudio, que é o que torna o
> resultado auditável; a arquitetura que isola o núcleo e externaliza a configuração,
> tornando o experimento reprodutível; e o protocolo de avaliação com a instrumentação que
> o alimenta.

**10. Qual hardware é necessário?**
> Roda em CPU com os modelos pequenos — a configuração padrão usa quantização de 8 bits
> justamente para isso. GPU reduz substancialmente o tempo de transcrição, que é a etapa
> dominante. Como o tamanho do modelo é configurável, é possível trocar custo por qualidade
> conforme a máquina disponível.

**11. E a LGPD / os dados dos participantes?**
> É um argumento a favor do desenho adotado: o áudio não sai da máquina onde o sistema roda,
> então não há transferência para terceiros. O protocolo de avaliação, inclusive, orienta a
> não versionar áudios reais no repositório.

**12. Por que janelas de 500 tokens com sobreposição de 50?**
> A janela precisa ser grande o suficiente para que o vetor represente um assunto, e não uma
> frase solta; e pequena o suficiente para que dois assuntos não caiam na mesma janela. A
> sobreposição de 10% evita que uma ideia seja cortada exatamente na fronteira. Ambos são
> configuráveis e entram na mesma varredura de parâmetros que mencionei no limiar.

---

## Checklist de véspera

- [ ] Saber de cor a procedência de cada linha da Tabela 1 (medido / calculado / projetado)
- [ ] Revisar nomes e grafia: aluno, orientador, unidade acadêmica
- [ ] Confirmar o apoio institucional na capa e no slide de agradecimentos
- [ ] Exportar o deck em **PDF** (o PDF não quebra fontes em máquina alheia)
- [ ] Pen drive **+** cópia na nuvem **+** cópia no e-mail
- [ ] Um PDF de saída do sistema aberto em outra aba, caso peçam exemplo
- [ ] Ensaiar **duas vezes com cronômetro**, em voz alta e de pé
- [ ] Ensaiar especificamente a abertura e o encerramento (são os trechos que a banca lembra)
- [ ] Chegar com 15 min de antecedência e testar o projetor

## No dia

- Fale **para a banca**, não para o slide. Olhe o telão apenas para apontar.
- Ao apontar o diagrama do pipeline, use a mão, não o cursor.
- Se travar: respire, olhe o roteiro no modo apresentador, retome pelo título da seção.
- Se não souber responder: **"Não medi isso. O que eu tenho é X, e o caminho para medir é Y."**
  É uma resposta forte. Inventar é a única resposta fraca.
- Guarde 1 minuto de folga — terminar em 14 minutos é melhor que ser interrompido aos 15.
