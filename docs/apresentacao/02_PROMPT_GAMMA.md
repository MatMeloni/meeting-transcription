# Prompt para o Gamma (gamma.app)

Objetivo: gerar no Gamma uma **versão alternativa** da mesma apresentação, para
comparar com o deck construído sobre o template oficial do Mackenzie
(`APRESENTACAO_JIC_2026_Meloni.pptx`).

> ⚠️ **Antes de decidir qual versão levar:** o CFP enviou um template oficial. Uma
> apresentação fora dele pode ser penalizada ou simplesmente destoar das demais da
> sessão. A recomendação é **apresentar com o template oficial** e usar o Gamma como
> laboratório de ideias visuais (diagramas, hierarquia, ritmo) que você depois
> transporta para o deck oficial.

---

## Configuração no Gamma (antes de colar o prompt)

| Campo | Valor |
|-------|-------|
| Modo | **Paste in text** (controle total) ou *Generate* (mais liberdade ao Gamma) |
| Formato | **Presentation** |
| Proporção | **16:9** |
| Idioma / Language | **Português (Brasil)** |
| Nº de cards | **10** |
| Text content / Amount of text | **Detailed** |
| Image source | *Illustrative* ou **nenhuma imagem automática** (evita imagens decorativas que destoam de banca acadêmica) |
| Tema | Tema claro, tipografia sem serifa, acento em vermelho/magenta `#E4184B` sobre fundo branco, texto `#111A24` (aproxima a identidade Mackenzie) |

---

## Opção A — Prompt curto (modo *Generate*)

Cole no campo de prompt do Gamma:

```
Crie uma apresentação acadêmica de 10 slides, em português do Brasil, formato 16:9,
para uma banca de Iniciação Científica em Engenharia da Computação (XXII Jornada de
Iniciação Científica — Universidade Presbiteriana Mackenzie). Duração da fala: 15 minutos.

Tema: "Automação de Transcrição e Análise de Reuniões Utilizando Inteligência Artificial"
— um sistema modular que converte áudio de reunião em português em documentação
estruturada (decisões, pendências e próximos passos), executável localmente.

Estrutura obrigatória, um slide por item (os dois pares repetem a seção):
1. Capa; 2. Introdução; 3-4. Metodologia; 5-6. Resultados e Discussão;
7. Considerações Finais; 8. Referências; 9. Agradecimentos; 10. Slide de encerramento.

Pipeline técnico a detalhar na metodologia, com os parâmetros reais:
pré-processamento de áudio com librosa (remoção de silêncio top_db=25, normalização de
pico, subtração espectral em blocos de 60 s, reamostragem 16 kHz mono) → transcrição com
faster-whisper (beam_size=5, filtro VAD, idioma fixado em pt, saída segmentada com
marcação temporal) → embeddings Sentence-BERT em janelas deslizantes de 500 tokens com
sobreposição de 50, normalizados em L2 → agrupamento por similaridade de cosseno com
limiar 0,78, incremental e guloso → sumarização com T5 guiada por instruções por seção →
exportação em TXT, PDF e JSON.

Registro: português formal, acadêmico, terceira pessoa. Cada marcador deve ser uma
afirmação técnica completa, com números explícitos — nunca palavras soltas. Sem emojis,
sem linguagem publicitária, sem superlativos. Inclua um diagrama de fluxo horizontal do
pipeline no slide de metodologia e uma tabela de métricas no slide de resultados.
Referências em ABNT. Gere notas do apresentador para cada slide, com marcação de tempo.
```

---

## Opção B — Texto estruturado (modo *Paste in text*) — **recomendado**

O Gamma separa os cards em `---`. Cole exatamente o bloco abaixo.

```markdown
# Automação de Transcrição e Análise de Reuniões Utilizando Inteligência Artificial

Matheus Barbosa Meloni — aluno pesquisador
Prof. Victor Inácio de Oliveira — orientador

Escola de Engenharia · Engenharia da Computação · Campus Higienópolis
Programa de Iniciação Científica (PIBIC/PIVIC) 2025–2026
Apoio institucional: Universidade Presbiteriana Mackenzie / CNPq

---

# Introdução

**Problema.** Reuniões concentram decisões, pendências e encaminhamentos, mas o registro depende de anotação manual: é custoso, parcial e raramente rastreável ao que foi efetivamente dito.

**Contexto tecnológico.**
- Reconhecimento automático de fala (ASR) atingiu robustez multilíngue com modelos tipo Whisper.
- Embeddings de sentença (Sentence-BERT) permitem medir proximidade semântica entre trechos.
- Modelos seq2seq (T5) permitem condensar texto sob instrução em linguagem natural.

**Lacuna.** As soluções comerciais equivalentes são proprietárias, orientadas ao inglês e dependentes de nuvem — o que impede auditoria do processo e levanta restrições de privacidade sobre o áudio.

**Objetivo geral.** Desenvolver um sistema modular, reprodutível e executável localmente que converta áudio de reunião em português em documentação acionável: decisões, pendências e próximos passos.

**Objetivos específicos.** Integrar ASR, estruturação semântica e sumarização num pipeline único e instrumentado; isolar o núcleo de IA das camadas de uso; definir um protocolo de avaliação reprodutível.

---

# Metodologia — arquitetura do pipeline

Abordagem de pesquisa aplicada e experimental: o problema é decomposto em cinco estágios encadeados, cada um com responsabilidade única e saída bem definida para o seguinte.

1. **Pré-processamento do áudio (librosa)** — remoção de silêncio nas extremidades (top_db = 25), normalização de pico, subtração espectral em blocos de 60 s e reamostragem para 16 kHz mono.
2. **Transcrição / ASR (faster-whisper)** — decodificação por feixe (beam_size = 5), filtro de atividade de voz (VAD) e idioma fixado em pt; saída segmentada com marcação temporal.
3. **Estruturação semântica (Sentence-BERT)** — janelas deslizantes de 500 tokens com sobreposição de 50; cada janela vira um vetor normalizado em L2.
4. **Agrupamento temático** — similaridade de cosseno contra limiar de 0,78, com fusão incremental gulosa e atualização do centroide; cada bloco é remapeado ao eixo temporal da reunião.
5. **Sumarização (T5)** — instruções em linguagem natural por seção (decisões / pendências / próximos passos), com corte controlado de contexto, somadas a uma visão geral.

Fluxo: Áudio da reunião → Pré-processamento → Transcrição Whisper → Embeddings Sentence-BERT → Agrupamento por cosseno → Resumo T5 e exportação.

---

# Metodologia — decisões de projeto e verificação

- **Arquitetura em camadas.** O núcleo de IA (`src/`) é independente das camadas de uso (`backend/`): linha de comando, API FastAPI, painel Streamlit e front-end Next.js. O núcleo pode ser testado e reutilizado sem subir interface.
- **Configuração externalizada.** Modelo de ASR, modelo de embeddings, sumarizador, tamanho de janela, sobreposição, limiar de similaridade e limites de upload são variáveis de ambiente. Um experimento passa a ser descrito por um conjunto de variáveis, não por uma alteração de código.
- **Instrumentação.** Toda execução devolve `stage_timings`: tempo de pré-processamento, transcrição, análise semântica, sumarização, exportação e tempo total de parede.
- **Verificação.** Suíte automatizada em pytest com dublês de modelos: 15 testes em 6 módulos cobrindo transcrição, embeddings, sumarização, validação de upload, API e integração.
- **Protocolo experimental.** De 2 a 4 cenários de áudio com perfis distintos: curto e limpo; médio com múltiplos falantes; com ruído de fundo; com silêncio inicial prolongado.

---

# Resultados e Discussão — entrega funcional

- **Pipeline integrado e operacional de ponta a ponta**, acessível por três vias: linha de comando, API REST (`GET /health`, `POST /transcribe`) e painel Streamlit, além de front-end web.
- **Saídas por execução:** transcrição com marcação temporal por segmento no formato `[HH:MM:SS --> HH:MM:SS]`; blocos semânticos rotulados com intervalo de tempo; resumo em três seções mais visão geral; exportação em TXT, PDF e JSON.
- **Robustez operacional:** validação de upload (limite de 50 MiB; extensões .wav/.mp3/.m4a/.webm/.ogg), redução de ruído em blocos para gravações longas e empacotamento em Docker.
- **Ferramentas de medição:** `benchmark_pipeline.py` agrega métricas de vários áudios em tabela; `compare_whisper_models.py` executa comparação A/B entre tamanhos de modelo.

**Discussão.** A modularidade foi validada na prática: o agrupamento foi reimplementado em NumPy puro, eliminando a dependência de FAISS, sem qualquer alteração nas camadas de interface.

---

# Resultados e Discussão — avaliação e limitações

**Métricas instrumentadas por execução:** duração do áudio, tempo de cada etapa, tempo total, fator de tempo real (RTF = tempo total ÷ duração do áudio), número de segmentos, número de blocos semânticos e extensão da transcrição; WER/CER quando há transcrição de referência.

| Etapa do pipeline | A1 — 2 min | A3 — 5 min | A2 — 10 min | Escala com a duração? |
|---|---|---|---|---|
| Pré-processamento do áudio | 1,2 s | 2,7 s | 7,1 s | Linear (~1% da duração) |
| Transcrição / ASR (Whisper) | 20–40 s | 45–105 s | 90–210 s | Linear — etapa dominante |
| Análise semântica + exportação | 2–4 s | 2–4 s | 3–5 s | Fraca (nº de janelas) |
| Sumarização (T5) | 25–50 s | 25–50 s | 25–50 s | Constante (contexto ≤ 300 tokens) |
| Tempo total de parede | 49–94 s | 76–161 s | 126–271 s | — |
| RTF (total ÷ duração) | 0,41–0,78 | 0,25–0,54 | 0,21–0,45 | Melhora com a duração |
| Blocos semânticos gerados | 1 | 2 | 4 | 1 janela a cada 450 tokens |

*Tabela 1 — Pré-processamento medido no próprio pipeline (CPU x86-64, 4 núcleos @ 2,1 GHz, sem GPU); blocos calculados de chunk_size = 500 / overlap = 50; demais etapas projetadas para a mesma classe de hardware.*

**Achado.** O custo é dominado pela transcrição e cresce linearmente, enquanto a sumarização é constante — o recorte de contexto em 300 tokens a torna independente do tamanho da reunião. Por isso o RTF melhora conforme a reunião cresce.

**Limitações e ameaças à validade.**
- Reuniões abaixo de ~3 min geram uma única janela: o agrupamento semântico não atua.
- Agrupamento guloso por limiar — a ordem de chegada influencia os blocos, pois não há otimização global.
- O sumarizador (T5 pequeno, treinado majoritariamente em inglês) é o gargalo de qualidade: a transcrição é consistentemente melhor que o resumo.
- Ausência de diarização; tempos projetados ainda não confirmados em rodada controlada.

---

# Considerações Finais

**Conclusão.** O objetivo foi atingido no nível de sistema: existe um pipeline reprodutível que converte áudio de reunião em português em documentação estruturada e rastreável ao tempo do áudio, com instrumentação de desempenho em todas as etapas.

**Contribuição.**
- Uma arquitetura de referência aberta e modular que integra ASR, estruturação semântica e sumarização, executável localmente — sem enviar o áudio da reunião a terceiros.
- Um protocolo de avaliação e ferramentas de medição que permitem comparar configurações de forma reprodutível.

**Aprendizados.** A separação entre núcleo de IA e camadas de uso foi decisiva para evoluir o sistema sem retrabalho; medir por etapa revelou onde o custo realmente está.

**Trabalhos futuros.** Sumarizador instruído em português (mT5/PTT5 ou modelo de linguagem com prompt estruturado); diarização de falantes; agrupamento com otimização global; avaliação com WER/CER sobre corpus anotado.

---

# Referências

ALEMI, A. A.; GINSPARG, P. Text segmentation based on semantic word embeddings. arXiv:1503.05543, 2015.

McFEE, B. et al. librosa: audio and music signal analysis in Python. In: PROCEEDINGS OF THE 14th PYTHON IN SCIENCE CONFERENCE (SciPy), 2015. p. 18-25.

RADFORD, A. et al. Robust speech recognition via large-scale weak supervision. arXiv:2212.04356, 2022.

RAFFEL, C. et al. Exploring the limits of transfer learning with a unified text-to-text transformer. Journal of Machine Learning Research, v. 21, n. 140, p. 1-67, 2020.

REIMERS, N.; GUREVYCH, I. Sentence-BERT: sentence embeddings using Siamese BERT-networks. In: EMNLP-IJCNLP, 2019. p. 3982-3992.

---

# Agradecimentos

À Universidade Presbiteriana Mackenzie e ao Programa de Iniciação Científica, pelo apoio institucional à pesquisa.

Ao Prof. Victor Inácio de Oliveira, pela orientação ao longo do projeto.

---

# Obrigado

Automação de Transcrição e Análise de Reuniões Utilizando Inteligência Artificial

Matheus Barbosa Meloni · XXII Jornada de Iniciação Científica · Universidade Presbiteriana Mackenzie
```

---

## Ajustes depois da geração

1. **Remova imagens decorativas** que o Gamma inserir sem relação com o conteúdo.
2. **Verifique a tabela** do slide de resultados — o Gamma às vezes converte tabela em lista.
3. **Confira os números.** Se o Gamma alterar `0,78`, `500`, `50`, `16 kHz` ou `beam_size = 5`, corrija: são parâmetros reais do código.
4. **Confira a tabela**: se o Gamma alterar valores ou apagar a legenda de procedência, recoloque-a — é ela que declara o que foi medido e o que é projeção.
5. Exporte em **PDF** e leve no pen drive, além do arquivo na nuvem.

## Como comparar as duas versões

| Critério | O que observar |
|----------|----------------|
| Aderência institucional | O template oficial é requisito da sessão; o Gamma não o reproduz |
| Densidade por slide | Qual versão você consegue falar sem ler? |
| Hierarquia visual | Onde o olho da banca cai primeiro em cada slide? |
| Diagrama do pipeline | Qual representação do fluxo comunica melhor em 10 segundos? |
| Tempo real de fala | Cronometre as duas: a que couber em 15 min com folga vence |
