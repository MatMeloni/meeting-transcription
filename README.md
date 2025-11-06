# Meeting Transcription

Pipeline modular de captura de áudio, transcrição (Whisper), análise semântica (Sentence-BERT) e sumarização automática (T5). A saída gera relatórios em TXT, PDF e JSON e pode ser orquestrada via CLI, FastAPI ou Streamlit.

## Requisitos

- Python 3.10+
- FFmpeg e libsndfile (para manipular áudio)
- Dependências Python listadas em `requirements.txt`

Instale localmente:

```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

## Execução local

### CLI

```bash
python app.py --audio caminho/para/reuniao.wav --meeting-name "Sprint Review"
```

### API FastAPI

```bash
python app.py --serve --host 0.0.0.0 --port 8000
```

Endpoints:
- `GET /health` – verificação
- `POST /transcribe` – arquivo de áudio + `meeting_name`

### Interface Streamlit

```bash
streamlit run app.py
```

## Uso com Docker (deploy em Railway/Render/Fly)

1. Construa a imagem:
   ```bash
   docker build -t meeting-transcription .
   ```
2. Execute localmente:
   ```bash
   docker run -p 8000:8000 -v "%cd%/outputs:/app/outputs" meeting-transcription
   ```
   Monte o volume `outputs/` para persistir arquivos gerados.

### Deploy sugerido

1. **Railway/Render/Fly.io**
   - Crie um serviço do tipo *Web* e aponte para este repositório.
   - Configure o build para usar `Dockerfile`.
   - Defina variáveis de ambiente (se necessário) no painel.
   - Garanta storage persistente para `/app/outputs`.

2. **HuggingFace Spaces / Streamlit Cloud** (demonstração rápida)
   - Publique a pasta com `app.py`, `src/` e `requirements.txt`.
   - Configure o Space como Streamlit.

## Integração com front-end na Vercel

- Hospede o backend em um provedor persistente (Railway, Render, Fly.io, etc.).
- Na Vercel, desenvolva a UI (Next.js) que:
  1. Envia arquivos `.wav/.mp3` via `POST` para `/transcribe`.
  2. Consome atualizações do resumo exibindo as seções retornadas.
  3. Oferece links de download usando os caminhos retornados no JSON (ou reexpõe via backend).
- Ative CORS no backend (já configurado) e utilize HTTPS em produção.

## Principais arquivos

- `src/app.py` – orquestração FastAPI/CLI/Streamlit.
- `src/services/` – captura, transcrição, embeddings, sumarização, exportação.
- `src/models/` – carregadores dos modelos Whisper, Sentence-BERT e T5.
- `src/utils/` – configuração, utilitários de áudio e texto.
- `Dockerfile` – imagem pronta para deploy em contêiner.
- `requirements.txt` – dependências.
