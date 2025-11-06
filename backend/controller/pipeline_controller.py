from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from config import AppConfig, ensure_output_dirs, setup_logging
from src import TranscriptionPipeline, build_pipeline


class PipelineController:
    """Coordinates interactions between API/front-end layers and the AI pipeline."""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        configure_logging: bool = True,
    ):
        self.config = config or AppConfig()
        if configure_logging:
            setup_logging()
        ensure_output_dirs(self.config)
        self.pipeline: TranscriptionPipeline = build_pipeline(self.config)

    def process_audio_file(
        self,
        audio_path: Path | str,
        meeting_name: Optional[str] = None,
        export_results: bool = True,
    ) -> Dict[str, Any]:
        """Processes an audio file present on disk."""
        return self.pipeline.process_audio_file(
            audio_file=audio_path,
            meeting_name=meeting_name,
            export_results=export_results,
        )

    def capture_and_process(
        self,
        duration_seconds: float,
        meeting_name: Optional[str] = None,
        export_results: bool = True,
    ) -> Dict[str, Any]:
        """Captures audio from microphone and processes it."""
        return self.pipeline.capture_and_process(
            duration_seconds=duration_seconds,
            meeting_name=meeting_name,
            export_results=export_results,
        )

    def process_uploaded_bytes(
        self,
        payload: bytes,
        original_filename: str,
        meeting_name: Optional[str] = None,
        export_results: bool = True,
    ) -> Dict[str, Any]:
        """Persists uploaded bytes temporarily before invoking the pipeline."""
        suffix = Path(original_filename or "upload.wav").suffix or ".wav"
        temp_name = f"upload_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}{suffix}"
        temp_path = self.config.outputs_dir / temp_name
        temp_path.write_bytes(payload)
        try:
            return self.pipeline.process_audio_file(
                audio_file=temp_path,
                meeting_name=meeting_name,
                export_results=export_results,
            )
        finally:
            temp_path.unlink(missing_ok=True)

    def resolve_sample_audio(self) -> Optional[Path]:
        """Returns a sample audio file if configured for demos."""
        sample = self.config.resolve_sample_audio()
        return sample if sample and sample.exists() else None
