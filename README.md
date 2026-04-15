# Meeting Transcription

Aplicação modular para transcrever reuniões com Whisper, gerar embeddings com Sentence-BERT e produzir resumos estruturados com T5. A arquitetura separa o núcleo de IA (`src/`) dos componentes de controle e API (`backend/`), permitindo reutilização do pipeline em outros projetos.

```
Usuário → Interface (Streamlit / Frontend) → Backend (FastAPI + Controller) → IA Core (src) → Modelos & Relatórios
```

## Estrutura do repositório

```
├── backend/          # API FastAPI, controladores e modelos Pydantic
│   ├── api/
│   ├── controller/
│   └── model/
├── frontend/         # Demo estática (`demo.html`) e espaço para UI web completa
├── scripts/          # Benchmark e comparação A/B de modelos Whisper
├── docs/             # Integração Vercel, protocolo de avaliação e template de resultados
├── src/              # Núcleo de IA (serviços, modelos, utilitários, configuração)
│   ├── app.py
│   ├── config/
│   ├── models/
│   ├── outputs/
│   ├── services/
│   └── utils/
├── tests/            # Testes com pytest
├── Dockerfile
├── requirements.txt
└── README.md
```

## Configuração

Requisitos:

- Python 3.10+
- FFmpeg e libsndfile instalados no sistema
- Dependências do `requirements.txt`

Instalação:

```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

As configurações principais ficam em `src/config/settings.py`. Use variáveis de ambiente para trocar modelos (por exemplo `WHISPER_MODEL`, `EMBEDDING_MODEL`, `OUTPUT_DIR`).

## Execução

### Linha de comando

```bash
python app.py --audio caminho/para/reuniao.wav --meeting-name "Sprint Review"
```

Parâmetros úteis:

- `--serve` para iniciar a API
- `--duration 60` para capturar áudio do microfone por 60s
- `--no-export` para desabilitar PDFs/JSON

### API FastAPI

```bash
python app.py --serve --host 0.0.0.0 --port 8000
```

Endpoints:

- `GET /health`
- `POST /transcribe` (multipart com `file` + `meeting_name`; resposta inclui `stage_timings` com segundos por etapa do pipeline)

Limites de upload (configuráveis por ambiente): `MAX_UPLOAD_BYTES`, `ALLOWED_AUDIO_EXTENSIONS`.

### Interface Streamlit

```bash
streamlit run app.py
```

O módulo detecta o contexto Streamlit e renderiza o painel para upload, captura pelo microfone e download dos relatórios.

### Demo HTML estática

Em `frontend/demo.html` há um formulário mínimo de upload contra a API (configure a URL base). Sirva a pasta com um servidor HTTP local (por exemplo `python -m http.server` dentro de `frontend/`) para evitar bloqueios de CORS ao abrir o arquivo diretamente do disco.

## Avaliação e resultados (parecer / relatório)

- [`docs/evaluation_protocol.md`](docs/evaluation_protocol.md) — protocolo para coletar métricas e evidências antes da seção de resultados.
- [`docs/results_template.md`](docs/results_template.md) — tabela e campos qualitativos para preencher.
- `python scripts/benchmark_pipeline.py --audio arquivo1.wav arquivo2.wav --output docs/runs/sua_rodada.md`
- `python scripts/compare_whisper_models.py --audio arquivo.wav --models base small`

## Testes

Execute os testes automatizados:

```bash
pytest
```

Os testes cobrem utilidades de transcrição, normalização semântica e sumarização usando dublês de modelos, além de validação de upload na API e um fluxo integrado do pipeline com serviços dubados.

## Agrupamento semântico

O agrupamento de trechos usa **similaridade de cosseno** entre embeddings normalizados e uma fusão incremental por limiar (`SIMILARITY_THRESHOLD`). **Não** se utiliza FAISS no código atual; dependências antigas foram removidas para refletir a implementação real.

## Deploy com Docker (Railway, Render, Fly.io, etc.)

```bash
docker build -t meeting-transcription .
docker run -p 8000:8000 -v "%cd%/outputs:/app/src/outputs" meeting-transcription
```

Monte um volume para `src/outputs` se quiser persistir relatórios. Em provedores como Railway/Render, configure o serviço como Web e aponte para o `Dockerfile`.

## Integração com Front-end na Vercel

- Hospede o backend em um provedor com processos persistentes (Railway, Render, Fly.io).
- Aponte o front-end Next.js (na Vercel) para a URL pública do backend (`POST /transcribe`).
- Utilize o guia `docs/vercel_frontend_integration.md` para código de upload e opções de proxy.

## Referências

- Whisper – Radford et al. (2022)
- Sentence-BERT – Reimers & Gurevych (2019)
- T5 – Raffel et al. (2020)
- Segmentação semântica textual – Alemi & Ginsparg (2015)
