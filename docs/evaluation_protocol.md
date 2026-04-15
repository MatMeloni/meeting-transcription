# Protocolo de avaliação (parecer parcial / resultados)

Este documento define como coletar **evidências reprodutíveis** antes de redigir a seção *Apresentação resumida dos resultados obtidos até o momento*.

## 1. Conjunto mínimo de cenários (2 a 4 áudios)

Recomenda-se preparar arquivos com perfis distintos, por exemplo:

| ID | Descrição | Objetivo |
|----|-----------|-----------|
| A1 | Trecho curto (30 s a 2 min), um locutor, ambiente calmo | Baseline de qualidade e tempo |
| A2 | Reunião média (5 a 15 min), múltiplos falantes | Segmentação e clusters |
| A3 | Gravação com ruído de fundo leve ou microfone distante | Robustez do pré-processamento |
| A4 | (Opcional) Áudio com silêncio inicial longo | Validação de trim + VAD |

**Privacidade:** não versionar áudios reais no Git; mantenha caminhos locais ou use `SAMPLE_AUDIO_RELATIVE_PATH` apenas para um clipe anonimizado de demonstração.

## 2. Configuração experimental (registrar em cada execução)

Anotar (copiar do ambiente ou do início do log):

- `WHISPER_MODEL`, `WHISPER_DEVICE`, `WHISPER_COMPUTE_TYPE`
- `EMBEDDING_MODEL`, `SUMMARIZER_MODEL`
- `CHUNK_SIZE`, `CHUNK_OVERLAP`, `SIMILARITY_THRESHOLD`, `SUMMARY_MAX_TOKENS`
- `TARGET_SAMPLERATE`, `OUTPUT_DIR`

O pipeline passa a expor tempos por etapa no campo **`stage_timings`** da resposta (API, JSON do CLI e Streamlit): `preprocess_seconds`, `transcribe_seconds`, `semantic_seconds`, `summarize_seconds`, `export_seconds`, `total_wall_seconds`.

## 3. Execução

1. Linha de comando (um arquivo):

   ```bash
   python app.py --audio "caminho/para/cenario_a1.wav" --meeting-name "Cenario_A1"
   ```

2. Vários arquivos e tabela Markdown (métricas agregadas):

   ```bash
   python scripts/benchmark_pipeline.py --audio a1.wav a2.wav --output docs/runs/ultima_execucao.md
   ```

3. Comparação A/B de tamanho do Whisper (processos separados, mesmo áudio):

   ```bash
   python scripts/compare_whisper_models.py --audio a1.wav --models base small
   ```

## 4. Métricas automáticas (preenchidas pelo script ou pela API)

Para cada áudio, registre:

- Duração do áudio (`duration_seconds` nos metadados da transcrição, quando disponível)
- `total_wall_seconds` e cada chave de `stage_timings`
- Número de segmentos (`len(segments)`)
- Número de clusters semânticos (`len(semantic_clusters)`)
- Tamanho do texto (caracteres ou tokens aproximados)
- RTF aproximado: `total_wall_seconds / duration_audio` (valores menores que 1 indicam processamento mais rápido que o tempo real do áudio)

## 5. Avaliação qualitativa (checklist manual)

**Transcrição**

- [ ] Nomes próprios e termos técnicos aceitáveis
- [ ] Números e datas corretos ou corrigíveis
- [ ] Poucos trechos ilógicos ou repetições espúrias

**Clusters**

- [ ] Blocos coerentes com mudança de assunto
- [ ] Tempos alinhados com a conversa (aproximado)

**Resumo (decisões / pendências / próximos passos)**

- [ ] Itens factuais (sem invenção grave)
- [ ] Separação razoável entre seções
- [ ] Visão geral condizente com a transcrição

Opcional: nota 1 a 5 por critério e segundo avaliador.

## 6. Artefatos para anexar ao parecer

- PDFs/JSON gerados em `outputs/` (transcrições e resumos)
- Capturas do Streamlit ou trecho da resposta JSON da API (incluindo `stage_timings`)
- Tabela preenchida a partir de [`results_template.md`](results_template.md) ou do Markdown gerado por `benchmark_pipeline.py`

## 7. Limitações a mencionar nos resultados

- Idioma da transcrição forçado para `pt` no serviço atual
- Clustering greedy por limiar, não otimização global
- Resumo dependente do recorte por tokens e do modelo T5 escolhido
