from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from config import AppConfig
from models.whisper_model import WhisperModelLoader
from utils.text_utils import clean_text


@dataclass
class TranscriptionResult:
    """Structured container for transcription outputs."""

    segments: List[Dict[str, Any]]
    text: str
    transcript_path: Path
    metadata: Dict[str, Any]


class TranscriptionService:
    """Coordinates audio transcription using faster-whisper."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.model_loader = WhisperModelLoader(config)

    def transcribe_audio(self, audio_path: Path, meeting_name: str) -> TranscriptionResult:
        """Transcribes the provided audio file and persists the raw transcript."""
        model = self.model_loader.load_model()
        logging.info("Iniciando transcrição com Whisper...")
        segments_iter, info = model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=True,
            language="pt",
        )
        segments: List[Dict[str, Any]] = []
        for idx, segment in enumerate(segments_iter, start=1):
            cleaned_text = clean_text(segment.text)
            segments.append(
                {
                    "id": idx,
                    "start": float(segment.start),
                    "end": float(segment.end),
                    "text": cleaned_text,
                }
            )
        transcript_text = " ".join(
            segment["text"] for segment in segments
        ).strip()
        timestamp = datetime.utcnow().strftime(
            self.config.transcripts_timestamp_format
        )
        transcript_path = self._save_transcript(
            transcript_text, meeting_name, timestamp
        )
        metadata = {
            "duration_seconds": getattr(info, "duration", None),
            "language": getattr(info, "language", "pt"),
            "probability": getattr(info, "language_probability", None),
            "timestamp": timestamp,
            "meeting_name": meeting_name,
        }
        logging.info(
            "Transcrição concluída: %s tokens (~%s segmentos)",
            len(transcript_text.split()),
            len(segments),
        )
        return TranscriptionResult(
            segments=segments,
            text=transcript_text,
            transcript_path=transcript_path,
            metadata=metadata,
        )

    def _save_transcript(self, text: str, meeting_name: str, timestamp: str) -> Path:
        """Saves the raw transcript to disk and returns the path."""
        safe_name = self._slugify(meeting_name)
        filename = f"{safe_name}_{timestamp}.txt"
        destination = self.config.transcripts_dir / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        logging.info("Transcrição salva em %s", destination)
        return destination

    @staticmethod
    def _slugify(value: str) -> str:
        """Builds a filesystem-safe identifier from user input."""
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_").lower()
        return slug or "reuniao"
