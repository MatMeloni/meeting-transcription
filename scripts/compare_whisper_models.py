#!/usr/bin/env python3
"""Roda benchmark_pipeline.py em subprocessos com WHISPER_MODEL distintos (isolamento de cache)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    benchmark = root / "scripts" / "benchmark_pipeline.py"
    parser = argparse.ArgumentParser(description="Compara tempos do pipeline entre tamanhos Whisper.")
    parser.add_argument("--audio", type=Path, required=True, help="Áudio de entrada.")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["base", "small"],
        help="Valores de WHISPER_MODEL a comparar (ex.: tiny base small).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "docs" / "runs",
        help="Pasta para gravar Markdown por modelo.",
    )
    args = parser.parse_args()

    if not args.audio.expanduser().resolve().exists():
        print(f"Áudio não encontrado: {args.audio}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    env_base = os.environ.copy()
    py = sys.executable

    print("# Comparação A/B Whisper\n", flush=True)
    for model in args.models:
        out = args.output_dir / f"benchmark_whisper_{model}.md"
        env = {**env_base, "WHISPER_MODEL": model}
        cmd = [
            py,
            str(benchmark),
            "--audio",
            str(args.audio.expanduser().resolve()),
            "--meeting-prefix",
            f"ab_{model}",
            "--output",
            str(out),
            "--no-export",
        ]
        print(f"## WHISPER_MODEL={model}\n", flush=True)
        proc = subprocess.run(cmd, cwd=str(root), env=env)
        if proc.returncode != 0:
            return proc.returncode
        if out.exists():
            print(out.read_text(encoding="utf-8"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
