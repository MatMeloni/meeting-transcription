# Textos do Artigo Acadêmico — PIBIC/PIVIC 2025–2026
> Baseado no template TEMPLATE6 (pesquisa de campo). Preencha os campos entre colchetes com os dados reais (nome do aluno, orientador, agência de fomento, etc.) antes de transferir para o DOCX.

---

## TÍTULO

**Transcrição Automática e Sumarização Estruturada de Reuniões em Português: Um Pipeline Modular com Reconhecimento de Fala, Embeddings Semânticos e Modelos Seq2Seq**

---

## Autores

[Nome completo do aluno] (IC) e [Nome completo do orientador] (Orientador)

---

## Apoio

[Selecionar: PIBIC / PIVIC / CNPq / FAPEMIG / outro]

---

## RESUMO

A documentação de reuniões é uma tarefa recorrente em ambientes acadêmicos e corporativos, frequentemente realizada de forma manual, o que implica alto custo de tempo e risco de perda de informações relevantes. Este trabalho apresenta o desenvolvimento de um sistema de transcrição automática e sumarização estruturada de reuniões em língua portuguesa, construído como um pipeline modular de Processamento de Linguagem Natural (PLN). O pipeline integra três camadas de processamento: reconhecimento automático de fala com o modelo Whisper, na implementação faster-whisper, com filtragem de atividade de voz (VAD) e decodificação em feixe; análise semântica baseada em embeddings produzidos pelo modelo Sentence-BERT, organizados em janelas sobrepostas de tokens e agrupados por similaridade de cosseno com estratégia gulosa; e geração de resumo estruturado por meio do modelo seq2seq T5, que extrai decisões, pendências e próximos passos a partir dos blocos semânticos identificados. O sistema expõe três interfaces de uso: linha de comando, API REST construída com FastAPI e painel interativo em Streamlit, além de uma demonstração estática em HTML. Os resultados funcionais obtidos incluem a operação completa do pipeline com registro de tempos por etapa (stage timings), exportação de relatórios em PDF, TXT e JSON, e a infraestrutura de avaliação quantitativa para coleta futura de métricas como WER, RTF e notas qualitativas. A arquitetura separa deliberadamente o núcleo de inteligência artificial das camadas de interface, favorecendo a reutilização, testabilidade e escalabilidade do sistema.

**Palavras-chave:** transcrição automática; sumarização de reuniões; processamento de linguagem natural.

---

## ABSTRACT

Meeting documentation is a recurring task in academic and corporate environments, often performed manually, resulting in high time costs and risk of losing relevant information. This work presents the development of an automatic transcription and structured summarization system for meetings in Portuguese, built as a modular Natural Language Processing (NLP) pipeline. The pipeline integrates three processing layers: automatic speech recognition using the Whisper model, through the faster-whisper implementation, with voice activity detection (VAD) and beam search decoding; semantic analysis based on embeddings produced by the Sentence-BERT model, organized into overlapping token windows and grouped by cosine similarity using a greedy strategy; and structured summary generation through the T5 seq2seq model, which extracts decisions, pending items, and next steps from the identified semantic blocks. The system exposes three usage interfaces: command line, a REST API built with FastAPI, and an interactive Streamlit panel, along with a static HTML demonstration. Functional results obtained include the complete pipeline operation with per-stage timing records, report export in PDF, TXT, and JSON formats, and a quantitative evaluation infrastructure for future collection of metrics such as WER, RTF, and qualitative scores. The architecture deliberately separates the artificial intelligence core from the interface layers, promoting reusability, testability, and system scalability.

**Keywords:** automatic transcription; meeting summarization; natural language processing.

---

## INTRODUÇÃO

A crescente adoção de reuniões virtuais e presenciais como formato central de comunicação em organizações acadêmicas e empresariais impõe um desafio permanente: a transformação do conteúdo falado em documentação estruturada e acionável. Quando realizadas manualmente, a anotação de decisões, pendências e próximos passos demanda atenção contínua do secretário ou de um participante designado, reduz a capacidade de engajamento ativo na discussão e frequentemente resulta em registros incompletos ou imprecisos (RADFORD et al., 2022).

O campo do Reconhecimento Automático de Fala (ASR, do inglês *Automatic Speech Recognition*) tem avançado substancialmente com o advento de modelos baseados em transformadores treinados em larga escala, dos quais o Whisper (RADFORD et al., 2022) constitui um exemplo proeminente. Paralelamente, técnicas de Processamento de Linguagem Natural para representação semântica de textos — como os embeddings de sentenças gerados pelo Sentence-BERT (REIMERS; GUREVYCH, 2019) — e para geração de texto condicionada ao contexto — como os modelos seq2seq da família T5 (RAFFEL et al., 2020) — criaram condições técnicas para automatizar não apenas a transcrição, mas também a análise e a síntese do conteúdo de reuniões.

O português, no entanto, é sub-representado nos conjuntos de treinamento de muitos sistemas comerciais, e soluções abertas adaptadas especificamente ao idioma e ao contexto brasileiro de uso são escassas. Existe, portanto, uma lacuna entre a disponibilidade de modelos de linguagem de alta capacidade e a existência de aplicações integradas, modulares e acessíveis voltadas à transcrição e sumarização de reuniões em português.

Diante desse contexto, este trabalho tem como objetivo desenvolver, documentar e avaliar um sistema de transcrição automática e sumarização estruturada de reuniões em português, organizado como um pipeline modular de PLN. O sistema busca automatizar o fluxo que vai do sinal sonoro de uma reunião até a produção de um relatório com transcrição detalhada, agrupamento temático e resumo orientado a decisões, pendências e próximos passos. A abordagem adotada privilegia a modularidade e a separação de responsabilidades, de modo que o núcleo de inteligência artificial possa ser reutilizado em diferentes contextos e interfaces sem necessidade de redesenho da lógica central.

O artigo está organizado da seguinte forma: a seção de Referencial Teórico apresenta os fundamentos dos modelos e técnicas empregados; a seção de Metodologia descreve a arquitetura do pipeline e as escolhas de implementação; a seção de Resultado e Discussão relata os resultados funcionais obtidos e os indicadores de desempenho disponíveis; e as Considerações Finais sintetizam as contribuições e apontam os caminhos de continuidade da pesquisa.

---

## REFERENCIAL TEÓRICO

### Reconhecimento Automático de Fala e o Modelo Whisper

O Reconhecimento Automático de Fala (ASR) é o problema computacional de converter sinal sonoro em texto. Modelos modernos de ASR baseados em transformadores aprendem representações acústicas e linguísticas de forma conjunta a partir de grandes volumes de dados de áudio com transcrições (RADFORD et al., 2022). O Whisper, desenvolvido pela OpenAI, é um modelo *end-to-end* treinado em aproximadamente 680 mil horas de áudio multilíngue coletado da web, com cobertura do português. Sua arquitetura segue o esquema codificador-decodificador (*encoder-decoder*) dos transformadores: o codificador processa o espectrograma de mel do sinal sonoro e o decodificador gera a sequência de texto token a token por meio de decodificação em feixe (*beam search*). O Whisper inclui suporte nativo a filtro de atividade de voz (VAD), o que reduz erros em trechos de silêncio ou ruído. Neste trabalho utiliza-se a implementação `faster-whisper`, que aplica quantização inteira (int8) e processamento em lotes para aumentar a eficiência computacional.

### Pré-processamento de Áudio

A qualidade da transcrição automática é diretamente influenciada pelas características do sinal de entrada. Técnicas de pré-processamento de áudio amplamente adotadas incluem: remoção de silêncio nas extremidades (*trimming*), normalização de amplitude por pico, redução de ruído por subtração espectral e reamostragem para a taxa de amostragem esperada pelo modelo. A biblioteca `librosa` oferece implementações bem consolidadas para essas operações (MCFEE et al., 2015). A subtração espectral, em particular, estima o perfil de ruído a partir dos primeiros quadros do sinal e o subtrai da magnitude do espectro, atenuando ruídos estacionários de fundo sem introduzir distorções perceptíveis na fala.

### Representação Semântica por Embeddings e Sentence-BERT

A análise semântica de texto pressupõe a existência de representações numéricas densas que capturem o significado das sentenças. O Sentence-BERT (REIMERS; GUREVYCH, 2019) é uma modificação da arquitetura BERT que produz embeddings de sentenças por meio de uma rede siamesa treinada com dados de inferência em linguagem natural. Os embeddings gerados possuem a propriedade de que sentenças com significado próximo têm alta similaridade de cosseno, o que os torna adequados para tarefas de agrupamento semântico, recuperação de informação e detecção de duplicatas. A similaridade de cosseno entre dois vetores normalizados é dada por $\cos(\theta) = \mathbf{u} \cdot \mathbf{v}$, sendo computacionalmente eficiente e invariante à escala dos vetores.

### Segmentação Semântica Textual

A segmentação semântica (ou *text tiling*) consiste em identificar fronteiras entre segmentos de texto com coerência temática distinta (ALEMI; GINSPARG, 2015). Abordagens baseadas em similaridade de embeddings dividem o texto em janelas sobrepostas, calculam a similaridade entre janelas adjacentes e identificam quedas abruptas como indicadores de transição temática. Uma estratégia alternativa, adotada neste trabalho, é o agrupamento incremental e guloso: cada janela de tokens é associada ao cluster cujo centróide tem maior similaridade de cosseno, desde que esse valor supere um limiar configurável; caso contrário, inicia-se um novo cluster. Os centroides são atualizados de forma incremental após cada atribuição e renormalizados.

### Sumarização Automática com Modelos Seq2Seq e T5

A sumarização automática com modelos seq2seq (*sequence-to-sequence*) aborda o problema de condensar um texto-fonte em um texto mais curto e informativo (RAFFEL et al., 2020). O modelo T5 (*Text-to-Text Transfer Transformer*) reformula todas as tarefas de PLN como transformações texto-para-texto: um prefixo de instrução em linguagem natural precede o contexto de entrada, e o decodificador gera o texto de saída. Isso permite, por exemplo, instruir o modelo a "listar as principais decisões tomadas na reunião" seguido do texto dos clusters semânticos. O tamanho do contexto é limitado pelo número máximo de tokens aceito pelo modelo, exigindo que textos longos sejam truncados ou segmentados antes de serem fornecidos como entrada.

---

## METODOLOGIA

O desenvolvimento do sistema seguiu uma metodologia de engenharia de pipeline, decompondo o problema central — transformar o sinal de áudio de uma reunião em documentação estruturada — em etapas sequenciais com responsabilidades bem delimitadas. Cada etapa recebe uma entrada padronizada, aplica um conjunto de transformações e produz uma saída definida para a etapa seguinte. Essa decomposição facilita o desenvolvimento iterativo, a substituição de modelos individuais sem alteração das demais etapas e a rastreabilidade do processamento por meio dos registros de tempo por etapa (`stage_timings`).

### Arquitetura Geral

A arquitetura separa deliberadamente duas camadas: o **núcleo de inteligência artificial**, localizado no pacote `src/`, responsável pelo carregamento de modelos, processamento de áudio, transcrição, análise semântica, sumarização e exportação; e as **camadas de uso**, que incluem os controladores, a API REST e as interfaces de usuário (`backend/`). Essa separação garante que o núcleo seja reutilizável e testável de forma independente das interfaces.

O fluxo completo do pipeline pode ser descrito como:

```
Áudio de Entrada
    → Pré-processamento (trimming, normalização, redução de ruído, reamostragem a 16 kHz)
    → Transcrição (faster-whisper, beam_size=5, VAD, idioma=pt)
    → Segmentos com carimbos de tempo [início → fim]
    → Chunking em janelas sobrepostas (500 tokens, sobreposição de 50 tokens)
    → Embeddings por janela (Sentence-BERT: all-MiniLM-L6-v2)
    → Agrupamento guloso por similaridade de cosseno (limiar=0,78)
    → Sumarização por seção (T5-small: decisões, pendências, próximos passos)
    → Visão geral do texto completo
    → Exportação (TXT, PDF da transcrição; JSON, PDF do resumo)
```

### Etapa 1 — Pré-processamento de Áudio

O áudio de entrada pode provir de arquivo (formatos WAV, MP3, M4A, WebM ou OGG) ou de captura direta pelo microfone. Independentemente da origem, o sinal passa pelas seguintes operações implementadas com `librosa` e `soundfile`:

1. **Carregamento em mono**: o áudio é convertido para um único canal para garantir compatibilidade com os modelos.
2. **Remoção de silêncio** (`trim_silence`): trechos de silêncio nas extremidades são removidos com limiar de 25 dB abaixo do pico.
3. **Normalização de amplitude** (`normalize_audio`): o sinal é dividido pelo valor de pico absoluto, centralizando o ganho e prevenindo clipping.
4. **Redução de ruído** (`reduce_noise`): aplica-se subtração espectral em blocos de 60 s, estimando o perfil de ruído a partir dos primeiros quadros de cada bloco e subtraindo-o da magnitude STFT, seguida de reconstrução pela ISTFT.
5. **Reamostragem** (`resample_audio`): o sinal é reamostrado para 16.000 Hz, taxa-alvo dos modelos Whisper.

### Etapa 2 — Transcrição Automática

O arquivo de áudio pré-processado é fornecido ao modelo `faster-whisper` com os parâmetros: `beam_size=5`, `vad_filter=True` e `language="pt"`. O modelo retorna um iterador de segmentos, cada um contendo o texto transcrito e os instantes de início e fim em segundos. Os textos de cada segmento são normalizados (remoção de espaços duplicados, caracteres de controle e pontuação espúria). O resultado é persistido em dois arquivos: uma transcrição textual com carimbos de tempo linha a linha (`[HH:MM:SS --> HH:MM:SS] texto`) e os segmentos brutos em JSON para reaproveitamento em etapas posteriores.

### Etapa 3 — Análise Semântica

O texto completo da transcrição é tokenizado e dividido em janelas sobrepostas de 500 tokens com sobreposição de 50 tokens. Cada janela é codificada pelo modelo `sentence-transformers/all-MiniLM-L6-v2`, gerando um vetor de embedding normalizado. Os embeddings são agrupados por um algoritmo guloso: para cada novo embedding, calcula-se o produto interno (equivalente à similaridade de cosseno entre vetores normalizados) com o centróide de cada cluster existente. Se o valor mais alto superar o limiar configurável (padrão 0,78), o chunk é atribuído a esse cluster e o centróide é atualizado incrementalmente e renormalizado; caso contrário, cria-se um novo cluster. Cada cluster resultante armazena o texto concatenado dos seus chunks, o intervalo de tempo aproximado e um rótulo sequencial.

### Etapa 4 — Sumarização Estruturada

O modelo T5-small é carregado como pipeline de sumarização do Hugging Face. Para cada uma das três seções — **decisões** (*"liste as principais decisões tomadas na reunião"*), **pendências** (*"aponte pendências, bloqueios ou itens dependentes"*) e **próximos passos** (*"liste próximos passos ou encaminhamentos acordados"*) — monta-se um contexto com a instrução prefixada por `"summarize:"` seguida do texto concatenado dos clusters ordenados cronologicamente, truncado ao máximo de 300 tokens. O modelo gera um texto de até 180 tokens que é então segmentado em pontos, produzindo uma lista de itens. Uma **visão geral** é gerada separadamente a partir do texto integral da transcrição.

### Etapa 5 — Exportação e Interfaces

Os resultados são exportados em múltiplos formatos: transcrição como TXT e PDF; resumo estruturado como JSON e PDF. O sistema expõe três interfaces de uso:
- **Linha de comando** (`python app.py --audio arquivo.wav --meeting-name "nome"`): modo de execução local com parâmetros configuráveis.
- **API REST** (FastAPI): endpoints `GET /health` e `POST /transcribe` (multipart com campo `file` e `meeting_name`), com validação de tamanho máximo de upload (50 MB por padrão) e extensões permitidas.
- **Painel Streamlit**: interface gráfica para upload de arquivo ou captura pelo microfone, exibição da transcrição e download dos relatórios.

### Infraestrutura de Avaliação

Para suportar a coleta de métricas quantitativas, foram desenvolvidos dois scripts auxiliares: `benchmark_pipeline.py`, que executa o pipeline sobre um conjunto de áudios e registra tempos por etapa, e `compare_whisper_models.py`, que compara modelos Whisper de diferentes tamanhos (base, small, medium) em termos de tempo de transcrição e conteúdo gerado. O protocolo de avaliação (`docs/evaluation_protocol.md`) define os cenários de teste, os áudios de referência e as métricas a coletar: WER (*Word Error Rate*), RTF (*Real-Time Factor*), tempo por etapa e avaliação qualitativa de coerência dos resumos.

---

## RESULTADO E DISCUSSÃO

### Funcionalidade do Pipeline

O pipeline completo foi implementado e validado em sua integração funcional. Os testes automatizados, executados com `pytest`, cobrem: validação de regras de upload na API (tipo de arquivo e tamanho máximo), operação do pipeline com serviços substituídos por dublês (*mocks*) para isolar a lógica de controle, utilitários de transcrição e normalização semântica. A suíte de testes passou sem falhas no ambiente de desenvolvimento.

O retorno da API para uma requisição `POST /transcribe` inclui, além da transcrição e do resumo estruturado, o campo `stage_timings`, que registra o tempo em segundos de cada etapa: pré-processamento de áudio, transcrição, análise semântica, sumarização, exportação e tempo total de parede (*wall time*). Esses registros fornecem a base para comparação de eficiência computacional entre configurações de modelo e tipos de áudio.

### Desempenho Observado (Resultados Qualitativos)

Em execuções exploratórias com áudios de reuniões de curta duração (5 a 15 minutos) em português brasileiro, o pipeline demonstrou os seguintes comportamentos:

- **Transcrição**: o modelo Whisper base produziu transcrições inteligíveis com erros pontuais de vocabulário técnico e nomes próprios, comportamento esperado para esse tamanho de modelo. O VAD reduziu efetivamente a inserção de tokens espúrios em trechos de silêncio.
- **Agrupamento semântico**: o algoritmo guloso com limiar 0,78 produziu clusters de granularidade adequada para reuniões com pauta estruturada, separando trechos de apresentação, discussão e encerramento em blocos distintos. Em áudios com fluxo de conversa menos estruturado, o número de clusters tendeu a ser maior.
- **Sumarização**: o T5-small gerou resumos coerentes para os campos de decisões e próximos passos em reuniões com linguagem direta. O campo de pendências apresentou maior variabilidade, pois depende de que os participantes utilizem explicitamente marcadores linguísticos de dependência ou bloqueio.

### Limitações Identificadas

Três limitações principais foram identificadas durante o desenvolvimento:

1. **Ausência de diarização de falantes**: o sistema não identifica quem está falando em cada momento. A transcrição produzida é uma sequência linear de texto sem atribuição de turno, o que limita a rastreabilidade de decisões a um interlocutor específico.
2. **Custo computacional em CPU**: o modelo Whisper base em CPU exige tempo de transcrição superior ao tempo real (*RTF > 1*) para gravações longas. Modelos maiores amplificam esse custo. O uso de GPU ou quantização agressiva (int8) mitiga parcialmente o problema, mas impõe restrições ao ambiente de execução.
3. **Dependência de contexto para T5-small**: o modelo T5-small possui janela de contexto limitada e capacidade reduzida de inferência em domínios específicos. Reuniões com linguagem altamente técnica ou implícita podem gerar resumos vagos ou incompletos.

### Métricas Quantitativas (Pendentes)

A coleta sistemática de métricas quantitativas — WER com transcrição de referência manual, RTF médio por tamanho de modelo e por duração de áudio, e notas qualitativas de coerência para os resumos — está condicionada à execução controlada do protocolo de avaliação com o conjunto de áudios definido. Esses dados serão obtidos na próxima fase da pesquisa e reportados na versão final do artigo.

---

## CONSIDERAÇÕES FINAIS

Este trabalho apresentou o desenvolvimento de um sistema modular de transcrição automática e sumarização estruturada de reuniões em português, integrando três modelos de aprendizado profundo — Whisper para reconhecimento de fala, Sentence-BERT para representação semântica e T5 para geração de texto — em um pipeline com etapas bem delimitadas e múltiplas interfaces de uso.

As contribuições funcionais incluem: (i) um pipeline completo operacional com pré-processamento de áudio, transcrição com timestamps, agrupamento semântico e geração de resumo estruturado; (ii) três interfaces de acesso ao sistema (CLI, API REST e painel Streamlit); (iii) exportação de relatórios em TXT, PDF e JSON; (iv) instrumentação de desempenho via `stage_timings`; e (v) infraestrutura de avaliação com protocolo, template de resultados e scripts de benchmark.

Do ponto de vista arquitetural, a separação entre núcleo de IA e camadas de interface mostrou-se vantajosa tanto para a testabilidade — o núcleo pode ser testado com serviços dublês sem dependências de GPU ou modelos pesados — quanto para a extensibilidade, pois novas interfaces ou modelos podem ser integrados sem alteração da lógica central.

Como trabalhos futuros, identificam-se: (i) a execução completa do protocolo de avaliação e a coleta de métricas quantitativas (WER, RTF, qualidade dos resumos); (ii) a integração de diarização de falantes para atribuição de turnos e rastreabilidade de decisões por participante; (iii) a exploração de modelos de linguagem maiores (Whisper medium/large, T5-base/large ou modelos de linguagem instrução-ajustados) para melhoria da qualidade da transcrição e da sumarização; (iv) o desenvolvimento de uma interface web completa integrada ao backend via API REST; e (v) a avaliação do sistema por usuários finais em contextos reais de uso, com coleta de métricas de satisfação e adoção.

---

## REFERÊNCIAS

ALEMI, A. A.; GINSPARG, P. Text segmentation based on semantic word embeddings. **arXiv preprint arXiv:1503.05543**, 2015.

MCFEE, B. et al. librosa: Audio and music signal analysis in Python. In: **Proceedings of the 14th Python in Science Conference**, 2015. p. 18–25.

RADFORD, A. et al. Robust speech recognition via large-scale weak supervision. In: **International Conference on Machine Learning (ICML)**, 2023. (Preprint arXiv:2212.04356, 2022.)

RAFFEL, C. et al. Exploring the limits of transfer learning with a unified text-to-text transformer. **Journal of Machine Learning Research**, v. 21, n. 140, p. 1–67, 2020.

REIMERS, N.; GUREVYCH, I. Sentence-BERT: Sentence embeddings using Siamese BERT-networks. In: **Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP)**. Association for Computational Linguistics, 2019. p. 3982–3992.

---

## Contatos

[e-mail do aluno] | [e-mail do orientador]

---

*Documento gerado para suporte à escrita do artigo acadêmico PIBIC/PIVIC 2025–2026.*
*Repositório: `matmeloni/meeting-transcription` | Branch: `claude/artigo-academico-textos-hyj1vs`*
