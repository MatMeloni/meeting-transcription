# RELATÓRIO PARCIAL

**PIBIC - PIVIC 2025/2026 — Abril**

---

## Objetivo do projeto

O projeto **Meeting Transcription** tem como objetivo oferecer uma solução integrada e reutilizável para **registar, transcrever e sintetizar reuniões em português**, apoiando a documentação do que foi dito e a extração de informação acionável (decisões, pendências e próximos passos). Para isso, combina **reconhecimento automático de fala** com modelos do tipo Whisper, **estruturação do texto** por meio de embeddings e agrupamento semântico dos trechos da transcrição, e **geração de resumos estruturados** com modelos seq2seq (T5), além da **exportação** da transcrição e do resumo em formatos como texto, PDF e JSON. A arquitetura separa o **núcleo de processamento** da **interface e da API** (linha de comando, FastAPI e painel Streamlit, com possibilidade de integração a um front-end hospedado separadamente), de modo que o sistema possa ser usado localmente, exposto como serviço web ou empacotado para deploy, sempre com foco em **automatizar a memória das reuniões** e reduzir o esforço manual de anotação e consolidação.

---

## Metodologia aplicada até o momento

O trabalho adota uma metodologia de **engenharia de pipeline**, isto é, decompõe o problema “transformar uma reunião falada em documentação útil” em **etapas encadeadas**, cada uma com responsabilidade clara e saída bem definida para a etapa seguinte. Essa escolha facilita entender o que o sistema faz em cada momento, repetir o processo com novos áudios, trocar modelos ou parâmetros sem redesenhar o aplicativo inteiro e, no contexto de um parecer parcial, permite relatar o progresso como uma **sequência lógica de tratamento da informação**: do sinal sonoro ao texto bruto, do texto bruto a uma organização por tópicos semânticos e, por fim, de tópicos a um resumo orientado à tomada de decisão.

Do ponto de vista arquitetural, a metodologia separa deliberadamente o **núcleo de inteligência artificial** (localizado em `src/`) das **camadas de uso** (controladores, API e interface em `backend/` e fluxos de execução como linha de comando ou Streamlit). Essa separação não é apenas organização de pastas: ela materializa a ideia de que o “cérebro” do sistema — carregar modelos, normalizar áudio, transcrever, agrupar trechos e resumir — deve permanecer **reutilizável e testável**, enquanto as formas de acionar esse núcleo (upload de arquivo, captura pelo microfone, chamada HTTP) podem evoluir em paralelo.

A primeira etapa operacional do pipeline trata do **áudio**. O sistema parte do pressuposto de que a qualidade do que entra influencia diretamente a qualidade da transcrição; por isso a metodologia inclui um **pré-processamento sistemático** antes de qualquer modelo de fala. Quando o áudio vem de arquivo, ele é carregado e submetido a uma sequência de operações: remoção aproximada de silêncio nas extremidades, normalização de amplitude, redução de ruído e reamostragem para uma taxa de amostragem alvo (tipicamente adequada a modelos de reconhecimento de fala). Quando a fonte é o microfone, registra-se um intervalo contínuo de áudio e aplica-se o mesmo tipo de pós-processamento, gerando um arquivo temporário padronizado.

Na etapa de **transcrição**, o projeto utiliza a família **Whisper** por meio da implementação **faster-whisper**, com decodificação com feixe de busca, filtro de atividade de voz (VAD) e idioma configurado para **português**. O resultado preserva **segmentos com tempo de início e fim**; o texto é normalizado e a transcrição integral é persistida em disco.

Em seguida, a metodologia trata a transcrição como base para **estrutura semântica**: o texto é tokenizado e reorganizado em **janelas sobrepostas** de tokens; cada janela é convertida num **vetor de embedding** (modelo tipo Sentence-BERT), normalizado, e mapeada de volta aos tempos dos segmentos. O agrupamento é **incremental e guloso** por similaridade de cosseno face a um limiar configurável, produzindo blocos temáticos com rótulos e intervalos de tempo aproximados.

A fase de **sumarização** usa um modelo **T5** em pipeline de sumarização, com instruções em linguagem natural para extrair decisões, pendências e próximos passos a partir dos clusters ordenados no tempo, com controlo de tamanho máximo de contexto em tokens; acrescenta-se uma **visão geral** a partir do texto completo da transcrição.

Por fim, a metodologia inclui **exportação** (PDF e/ou TXT da transcrição; PDF e JSON do resumo) e **múltiplas interfaces** (CLI, FastAPI, Streamlit). A configuração centraliza-se em variáveis de ambiente (modelos, pastas, limiares). Referências conceituais: Whisper; Sentence-BERT; T5; segmentação semântica textual.

---

## Apresentação resumida dos resultados obtidos até o momento

Até esta fase foi construído e integrado o **pipeline modular** descrito acima, com **três vias de acesso**: linha de comando, **API REST** (`GET /health`, `POST /transcribe`) e **interface Streamlit**. Foi acrescentada uma **demo estática** (`frontend/demo.html`) para testar upload contra a API. O retorno do pipeline inclui **`stage_timings`** (tempos por etapa: pré-processamento, transcrição, análise semântica, sumarização, exportação e tempo total de parede), o que suporta a documentação de desempenho.

Foram implementadas **validação de upload** (tamanho máximo e extensões permitidas), **testes automatizados** adicionais (validação de regras, API com pipeline dubado, integração leve com serviços dubados), **`pytest.ini`** e ajuste do **Docker** (`PYTHONPATH`). Para apoio à secção de resultados quantitativos e qualitativos existem o **protocolo de avaliação** (`docs/evaluation_protocol.md`), o **template** (`docs/results_template.md`) e os scripts **`scripts/benchmark_pipeline.py`** e **`scripts/compare_whisper_models.py`**. A documentação de integração (Vercel) e o **README** foram actualizados (limites de API; clustering **sem FAISS**, coerente com a implementação em NumPy).

**Nota:** indicadores finais (tempos médios por cenário, RTF, WER/CER com transcrição de referência, notas qualitativas por áudio) dependem da **execução controlada** sobre o conjunto de áudios definido no protocolo e do preenchimento do template ou das saídas dos scripts. Até que essas corridas sejam realizadas e anexadas, os resultados aqui descritos são sobretudo de **implementação funcional, documentação e infra-estrutura de avaliação**.

---

## Comentários gerais

O **tema central do trabalho mantém-se**: transcrição automática de reuniões em português, com estruturação semântica e resumo orientado a decisões, pendências e próximos passos — **não houve alteração de foco temático**.

As **alterações no projeto** limitaram-se a evolução técnica em torno do mesmo objectivo: instrumentação (`stage_timings`, protocolo, template, scripts de benchmark e A/B), robustez da API (validação de upload), alargamento de testes e melhorias de UX (Streamlit, demo HTML), consistência de dependências (remoção de `faiss-cpu` não utilizado; documentação do agrupamento) e ajustes de empacotamento/execução (pytest, Docker).

---

*Documento gerado para arquivo do PIBIC/PIVIC — Abril de 2026. Nome de ficheiro no repositório: `RELATÓRIO PARCIAL - PIBIC - PIVIC 2025-2026 - Abril.md` (a barra “2025/2026” foi substituída por hífen no nome do ficheiro por restrições do sistema de ficheiros).*
