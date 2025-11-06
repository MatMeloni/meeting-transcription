from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

import uvicorn

from backend.controller.pipeline_controller import PipelineController
from backend.controller.streamlit_app import render_streamlit_app, running_inside_streamlit
from backend.api.app import create_app


def parse_args() -> argparse.Namespace:
    """Parses CLI arguments when running directly via python app.py."""
    parser = argparse.ArgumentParser(description="Controle da API e CLI para transcrição de reuniões.")
    parser.add_argument("--serve", action="store_true", help="Inicializa a API FastAPI com Uvicorn.")
    parser.add_argument("--audio", type=str, help="Caminho para arquivo de áudio a ser processado.")
    parser.add_argument("--meeting-name", type=str, help="Nome amigável da reunião.")
    parser.add_argument("--duration", type=float, help="Duração, em segundos, para captura de microfone.")
    parser.add_argument("--no-export", action="store_true", help="Desativa geração de PDFs e JSON.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host para o servidor FastAPI.")
    parser.add_argument("--port", type=int, default=8000, help="Porta para o servidor FastAPI.")
    args, _ = parser.parse_known_args()
    return args


def run_cli(controller: PipelineController) -> None:
    """Entry-point executed when running python app.py."""
    if running_inside_streamlit():
        render_streamlit_app(controller)
        return

    args = parse_args()
    meeting_label = args.meeting_name or controller.config.default_meeting_name

    if args.serve:
        app = create_app(controller)
        logging.info("Iniciando servidor FastAPI em %s:%s", args.host, args.port)
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return

    export_results = not args.no_export

    if args.duration:
        result = controller.capture_and_process(
            duration_seconds=args.duration,
            meeting_name=meeting_label,
            export_results=export_results,
        )
        _print_result(result)
        return

    audio_path: Optional[Path] = None
    if args.audio:
        candidate = Path(args.audio).expanduser().resolve()
        if not candidate.exists():
            logging.error("Arquivo não encontrado: %s", candidate)
            return
        audio_path = candidate
    else:
        sample = controller.resolve_sample_audio()
        if sample and sample.exists():
            logging.info("Utilizando áudio de demonstração em %s", sample)
            audio_path = sample

    if audio_path is None:
        logging.info("Nenhum áudio informado. Use --audio <arquivo.wav> ou --duration <segundos>.")
        return

    result = controller.process_audio_file(
        audio_file=audio_path,
        meeting_name=meeting_label,
        export_results=export_results,
    )
    _print_result(result)


def _print_result(result: dict) -> None:
    """Utility to print pipeline results in JSON format."""
    payload = {
        "meeting_name": result["meeting_name"],
        "timestamp": result["timestamp"],
        "summary": result["summary"],
        "exports": result["exports"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
