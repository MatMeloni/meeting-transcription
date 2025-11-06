from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """Holds runtime configuration for the meeting transcription pipeline."""

    base_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "MEETING_APP_BASE_DIR",
                Path(__file__).resolve().parents[2],
            )
        )
    )
    outputs_dir: Path = field(init=False)
    transcripts_dir: Path = field(init=False)
    summaries_dir: Path = field(init=False)
    models_dir: Path = field(init=False)

    audio_temp_filename: str = os.getenv("AUDIO_TEMP_FILENAME", "audio_temp.wav")
    target_samplerate: int = int(os.getenv("TARGET_SAMPLERATE", "16000"))

    whisper_model_size: str = os.getenv("WHISPER_MODEL_SIZE", "medium")
    whisper_device: str = os.getenv("WHISPER_DEVICE", "auto")
    whisper_compute_type: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

    embedding_model_name: str = os.getenv(
        "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
    )
    summarizer_model_name: str = os.getenv("SUMMARIZER_MODEL_NAME", "t5-small")

    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    similarity_threshold: float = float(
        os.getenv("SIMILARITY_THRESHOLD", "0.78")
    )

    summary_max_tokens: int = int(os.getenv("SUMMARY_MAX_TOKENS", "300"))
    summary_temperature: float = float(
        os.getenv("SUMMARY_TEMPERATURE", "0.8")
    )

    transcripts_timestamp_format: str = os.getenv(
        "TRANSCRIPT_TS_FORMAT", "%Y%m%d_%H%M%S"
    )
    default_meeting_name: str = os.getenv("DEFAULT_MEETING_NAME", "reuniao")

    streamlit_poll_interval: float = float(
        os.getenv("STREAMLIT_POLL_INTERVAL", "0.5")
    )

    sample_audio_relative_path: Optional[str] = os.getenv(
        "SAMPLE_AUDIO_RELATIVE_PATH"
    )

    def __post_init__(self) -> None:
        """Derives dependent paths once base directory is known."""
        self.outputs_dir = (self.base_dir / "outputs").resolve()
        self.transcripts_dir = (self.outputs_dir / "transcripts").resolve()
        self.summaries_dir = (self.outputs_dir / "summaries").resolve()
        self.models_dir = (self.base_dir / "models_cache").resolve()

    @property
    def audio_temp_path(self) -> Path:
        """Returns absolute path for temporary processed audio."""
        return self.outputs_dir / self.audio_temp_filename

    def resolve_sample_audio(self) -> Optional[Path]:
        """Returns optional Path for packaged sample audio if configured."""
        if not self.sample_audio_relative_path:
            return None
        return (self.base_dir / self.sample_audio_relative_path).resolve()


def ensure_output_dirs(config: AppConfig) -> None:
    """Creates output directories if they do not exist."""
    for directory in (
        config.outputs_dir,
        config.transcripts_dir,
        config.summaries_dir,
        config.models_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def setup_logging() -> None:
    """Configures basic console logging for the application."""
    logging_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
