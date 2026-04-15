#!/usr/bin/env python3
"""Executa o pipeline sobre um ou mais áudios e gera tabela Markdown + JSON de métricas."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _bootstrap_paths() -> Path:
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root))
    return root


def main() -> int:
    _bootstrap_paths()

    from config import AppConfig, ensure_output_dirs, setup_logging
    from backend.controller.pipeline_controller import PipelineController

    parser = argparse.ArgumentParser(description="Benchmark do pipeline de transcrição.")
    parser.add_argument(
        "--audio",
        nargs="+",
        type=Path,
        required=True,
        help="Caminhos para arquivos de áudio.",
    )
    parser.add_argument("--meeting-prefix", default="bench", help="Prefixo do nome da reunião.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Arquivo Markdown de saída (opcional).",
    )
    parser.add_argument("--json-out", type=Path, help="Arquivo JSON com linhas brutas (opcional).")
    parser.add_argument("--no-export", action="store_true", help="Desativa PDF/JSON de exportação.")
    args = parser.parse_args()

    setup_logging()
    config = AppConfig()
    ensure_output_dirs(config)
    controller = PipelineController(config=config, configure_logging=False)

    rows: list[dict[str, object]] = []
    lines: list[str] = [
        "# Benchmark do pipeline",
        "",
        "| Arquivo | Duração (s) | total_wall | preprocess | transcribe | semantic | summarize | export | Segmentos | Clusters | Chars |",
        "|---------|------------|------------|------------|------------|----------|-----------|--------|-----------|----------|-------|",
    ]

    export_results = not args.no_export
    for idx, audio in enumerate(args.audio):
        path = audio.expanduser().resolve()
        if not path.exists():
            print(f"Arquivo não encontrado: {path}", file=sys.stderr)
            return 1
        label = f"{args.meeting_prefix}_{idx}_{path.stem}"
        result = controller.process_audio_file(
            audio_file=path,
            meeting_name=label,
            export_results=export_results,
        )
        timings = result.get("stage_timings", {})
        duration: float | None = None
        if result.get("segments"):
            last = result["segments"][-1]
            duration = float(last.get("end", 0.0))
        transcript_text = result.get("transcript_text", "")
        row = {
            "file": str(path),
            "meeting_name": result["meeting_name"],
            "duration_end_last_segment_s": duration,
            "chars": len(transcript_text),
            "segments": len(result.get("segments", [])),
            "clusters": len(result.get("semantic_clusters", [])),
            "stage_timings": timings,
        }
        rows.append(row)

        def t(key: str) -> str:
            v = timings.get(key)
            return f"{v:.3f}" if isinstance(v, (int, float)) else ""

        lines.append(
            f"| {path.name} | {duration or ''} | {t('total_wall_seconds')} | "
            f"{t('preprocess_seconds')} | {t('transcribe_seconds')} | {t('semantic_seconds')} | "
            f"{t('summarize_seconds')} | {t('export_seconds')} | {row['segments']} | {row['clusters']} | {row['chars']} |"
        )

    md = "\n".join(lines) + "\n"
    print(md)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
        print(f"Markdown escrito em {args.output}", file=sys.stderr)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON escrito em {args.json_out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
