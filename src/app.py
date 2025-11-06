from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from services.audio_capture import AudioCaptureService
from services.export_service import ExportService
from services.semantic_service import SemanticAnalyzer, SemanticCluster
from services.summarization_service import SummarizationService
from services.transcription_service import TranscriptionService
from utils.config import AppConfig, ensure_output_dirs, setup_logging

setup_logging()


class MeetingTranscriptionApp:
    """Central orchestration façade for the transcription and summarization pipeline."""

    def __init__(self, config: AppConfig):
        self.config = config
        ensure_output_dirs(config)
        self.audio_service = AudioCaptureService(config)
        self.transcription_service = TranscriptionService(config)
        self.semantic_service = SemanticAnalyzer(config)
        self.summarization_service = SummarizationService(config)
        self.export_service = ExportService(config)

    def process_audio_file(
        self,
        audio_file: Path | str,
        meeting_name: Optional[str] = None,
        export_results: bool = True,
    ) -> Dict[str, Any]:
        """Executes the entire pipeline for a prerecorded audio file."""
        meeting_label = meeting_name or self.config.default_meeting_name
        audio_path = Path(audio_file).resolve()
        if not audio_path.exists():
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")
        logging.info("Processando reunião '%s' a partir de %s", meeting_label, audio_path)
        processed_path = self.audio_service.preprocess_file(audio_path)
        transcription = self.transcription_service.transcribe_audio(
            processed_path, meeting_label
        )
        clusters = self.semantic_service.build_semantic_clusters(transcription.segments)
        summary = self.summarization_service.generate_structured_summary(
            transcription.text, clusters
        )

        exports: Dict[str, Dict[str, str]] = {}
        if export_results:
            transcript_exports = self.export_service.export_transcript(
                transcription.text, transcription.transcript_path, transcription.metadata
            )
            summary_exports = self.export_service.export_summary(
                summary, transcription.metadata
            )
            exports = {
                "transcript": {fmt: str(path) for fmt, path in transcript_exports.items()},
                "summary": {fmt: str(path) for fmt, path in summary_exports.items()},
            }

        response = {
            "meeting_name": transcription.metadata["meeting_name"],
            "timestamp": transcription.metadata["timestamp"],
            "transcript_text": transcription.text,
            "segments": transcription.segments,
            "semantic_clusters": self._serialize_clusters(clusters),
            "summary": summary,
            "exports": exports,
        }
        logging.info("Pipeline concluído com sucesso para %s", response["meeting_name"])
        return response

    def capture_and_process(
        self,
        duration_seconds: float,
        meeting_name: Optional[str] = None,
        export_results: bool = True,
    ) -> Dict[str, Any]:
        """Captures live audio from the microphone and runs the pipeline."""
        meeting_label = meeting_name or self.config.default_meeting_name
        processed_path = self.audio_service.capture_microphone(duration_seconds)
        return self.process_audio_file(processed_path, meeting_label, export_results)

    def _serialize_clusters(self, clusters: list[SemanticCluster]) -> list[dict[str, Any]]:
        """Transforms SemanticCluster objects into JSON serializable dicts."""
        serialized = []
        for cluster in clusters:
            serialized.append(
                {
                    "label": cluster.label,
                    "start_time": cluster.start_time,
                    "end_time": cluster.end_time,
                    "text": cluster.text,
                }
            )
        return serialized


def build_fastapi_app(orchestrator: MeetingTranscriptionApp) -> FastAPI:
    """Creates the FastAPI application exposing the transcription endpoints."""
    api = FastAPI(
        title="Meeting Transcription API",
        version="1.0.0",
        description=(
            "Pipeline modular de transcrição, análise semântica e sumarização automática."
        ),
    )
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api.get("/health")
    async def health() -> Dict[str, str]:
        """Simple health check endpoint."""
        return {"status": "ok"}

    @api.post("/transcribe")
    async def transcribe_endpoint(
        file: UploadFile = File(...), meeting_name: Optional[str] = None
    ) -> JSONResponse:
        """Accepts an audio upload, processes it, and returns transcript plus summary."""
        meeting_label = meeting_name or orchestrator.config.default_meeting_name
        ensure_output_dirs(orchestrator.config)
        payload = await file.read()
        if not payload:
            raise HTTPException(status_code=400, detail="Arquivo de áudio vazio.")
        suffix = Path(file.filename or "upload.wav").suffix or ".wav"
        temp_name = f"upload_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}{suffix}"
        temp_path = orchestrator.config.outputs_dir / temp_name
        temp_path.write_bytes(payload)
        logging.info("Arquivo recebido salvo temporariamente em %s", temp_path)
        try:
            result = orchestrator.process_audio_file(
                temp_path, meeting_label, export_results=True
            )
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
        return JSONResponse(result)

    return api


def _running_with_streamlit() -> bool:
    """Detects whether the script is running under Streamlit."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx  # type: ignore

        return get_script_run_ctx() is not None
    except Exception:
        return False


def _render_streamlit_result(st_module, result: Dict[str, Any]) -> None:
    """Renders pipeline results inside Streamlit widgets."""
    st_module.success("Processamento concluído!")
    summary_tab, transcript_tab, export_tab = st_module.tabs(
        ["Resumo", "Transcrição", "Exportações"]
    )

    with summary_tab:
        st_module.subheader("Resumo Estruturado")
        summary = result["summary"]
        st_module.markdown("**Decisões**")
        for item in summary.get("decisions", []):
            st_module.markdown(f"- {item}")
        st_module.markdown("**Pendências**")
        for item in summary.get("pending", []):
            st_module.markdown(f"- {item}")
        st_module.markdown("**Próximos passos**")
        for item in summary.get("next_steps", []):
            st_module.markdown(f"- {item}")
        if overview := summary.get("overview"):
            st_module.markdown("**Visão geral**")
            for paragraph in overview:
                st_module.write(paragraph)

    with transcript_tab:
        st_module.subheader("Transcrição com timestamps")
        for segment in result["segments"]:
            st_module.markdown(
                f"**[{segment['start']:.2f}s – {segment['end']:.2f}s]** {segment['text']}"
            )

    with export_tab:
        st_module.subheader("Downloads gerados")
        exports = result.get("exports", {})
        for export_group, files in exports.items():
            st_module.markdown(f"**{export_group.capitalize()}**")
            for fmt, path_str in files.items():
                export_path = Path(path_str)
                if export_path.exists():
                    data = export_path.read_bytes()
                    st_module.download_button(
                        label=f"Baixar {export_group} ({fmt.upper()})",
                        data=data,
                        file_name=export_path.name,
                        mime=(
                            "application/pdf"
                            if export_path.suffix.lower() == ".pdf"
                            else (
                                "application/json"
                                if export_path.suffix.lower() == ".json"
                                else "text/plain"
                            )
                        ),
                    )
                else:
                    st_module.warning(f"Arquivo não encontrado: {export_path}")

    st_module.caption(
        f"Reunião: {result['meeting_name']} | Gerado em: {result['timestamp']}"
    )


def render_streamlit_app(orchestrator: MeetingTranscriptionApp) -> None:
    """Initializes the Streamlit interface for real-time monitoring."""
    import streamlit as st

    ensure_output_dirs(orchestrator.config)
    st.set_page_config(
        page_title="Transcrição Inteligente de Reuniões", layout="wide"
    )
    st.title("Transcrição Inteligente de Reuniões")
    st.caption("Whisper + Sentence-BERT + T5 (pipeline modular)")

    meeting_name = st.text_input(
        "Nome da reunião", value=orchestrator.config.default_meeting_name
    )
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader(
            "Envie um arquivo de áudio (.wav, .mp3, .m4a)",
            type=["wav", "mp3", "m4a"],
        )
    with col2:
        duration = st.number_input(
            "Capturar áudio do microfone (segundos)",
            min_value=5,
            max_value=600,
            value=30,
            step=5,
        )
        capture_clicked = st.button("Capturar microfone agora")

    if capture_clicked:
        try:
            with st.spinner("Capturando áudio do microfone..."):
                result = orchestrator.capture_and_process(
                    duration, meeting_name=meeting_name
                )
            _render_streamlit_result(st, result)
        except Exception as exc:  # pragma: no cover - depende de hardware
            st.error(f"Falha durante a captura ao vivo: {exc}")

    if uploaded_file is not None:
        suffix = Path(uploaded_file.name or "upload.wav").suffix or ".wav"
        temp_path = (
            orchestrator.config.outputs_dir
            / f"streamlit_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}{suffix}"
        )
        temp_path.write_bytes(uploaded_file.getbuffer())
        with st.spinner("Processando arquivo enviado..."):
            result = orchestrator.process_audio_file(
                temp_path, meeting_name=meeting_name
            )
        _render_streamlit_result(st, result)
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)

    sample_audio = orchestrator.config.resolve_sample_audio()
    if sample_audio and sample_audio.exists():
        if st.button("Rodar pipeline com áudio de demonstração"):
            with st.spinner("Processando áudio de demonstração..."):
                result = orchestrator.process_audio_file(
                    sample_audio, meeting_name=f"{meeting_name}_demo"
                )
            _render_streamlit_result(st, result)


def parse_args() -> argparse.Namespace:
    """Parses CLI arguments when running directly via python app.py."""
    parser = argparse.ArgumentParser(
        description="Pipeline de transcrição e resumo de reuniões."
    )
    parser.add_argument(
        "--serve", action="store_true", help="Inicializa a API FastAPI com Uvicorn."
    )
    parser.add_argument(
        "--audio",
        type=str,
        help="Caminho para arquivo de áudio a ser processado.",
    )
    parser.add_argument(
        "--meeting-name", type=str, help="Nome amigável da reunião."
    )
    parser.add_argument(
        "--duration",
        type=float,
        help="Duração, em segundos, para captura de microfone.",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Desativa geração de PDFs e JSON.",
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host para o servidor FastAPI."
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Porta para o servidor FastAPI."
    )
    return parser.parse_args()


def _format_cli_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Filters the pipeline output for readable CLI printing."""
    return {
        "meeting_name": result["meeting_name"],
        "timestamp": result["timestamp"],
        "summary": result["summary"],
        "exports": result["exports"],
    }


def main_cli(orchestrator: MeetingTranscriptionApp) -> None:
    """Entry-point executed when running python app.py."""
    args = parse_args()
    meeting_label = args.meeting_name or orchestrator.config.default_meeting_name

    if args.serve:
        logging.info("Iniciando servidor FastAPI em %s:%s", args.host, args.port)
        uvicorn.run(API_APP, host=args.host, port=args.port, log_level="info")
        return

    export_results = not args.no_export

    if args.duration:
        result = orchestrator.capture_and_process(
            args.duration,
            meeting_name=meeting_label,
            export_results=export_results,
        )
        print(json.dumps(_format_cli_result(result), ensure_ascii=False, indent=2))
        return

    audio_path: Optional[Path] = None
    if args.audio:
        candidate = Path(args.audio).expanduser().resolve()
        if not candidate.exists():
            logging.error("Arquivo não encontrado: %s", candidate)
            return
        audio_path = candidate
    else:
        sample = orchestrator.config.resolve_sample_audio()
        if sample and sample.exists():
            logging.info("Utilizando áudio de demonstração em %s", sample)
            audio_path = sample

    if audio_path is None:
        logging.info(
            "Nenhum áudio informado. Use --audio <arquivo.wav> ou --duration <segundos>."
        )
        return

    result = orchestrator.process_audio_file(
        audio_path,
        meeting_name=meeting_label,
        export_results=export_results,
    )
    print(json.dumps(_format_cli_result(result), ensure_ascii=False, indent=2))


CONFIG = AppConfig()
ensure_output_dirs(CONFIG)
ORCHESTRATOR = MeetingTranscriptionApp(CONFIG)
API_APP = build_fastapi_app(ORCHESTRATOR)

if _running_with_streamlit():
    render_streamlit_app(ORCHESTRATOR)
elif __name__ == "__main__":
    main_cli(ORCHESTRATOR)
