from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import AppConfig, ensure_output_dirs
from services.audio_capture import AudioCaptureService
from services.export_service import ExportService
from services.semantic_service import SemanticAnalyzer, SemanticCluster
from services.summarization_service import SummarizationService
from services.transcription_service import TranscriptionService

__all__ = ["TranscriptionPipeline", "build_pipeline"]


class TranscriptionPipeline:
    """Core AI pipeline used for audio transcription and summarization."""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        ensure_output_dirs(self.config)

        self.audio_service = AudioCaptureService(self.config)
        self.transcription_service = TranscriptionService(self.config)
        self.semantic_service = SemanticAnalyzer(self.config)
        self.summarization_service = SummarizationService(self.config)
        self.export_service = ExportService(self.config)

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
        stage_timings: Dict[str, float] = {}
        run_started = time.perf_counter()

        t0 = time.perf_counter()
        processed_path = self.audio_service.preprocess_file(audio_path)
        stage_timings["preprocess_seconds"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        transcription = self.transcription_service.transcribe_audio(processed_path, meeting_label)
        stage_timings["transcribe_seconds"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        clusters = self.semantic_service.build_semantic_clusters(transcription.segments)
        stage_timings["semantic_seconds"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        summary = self.summarization_service.generate_structured_summary(transcription.text, clusters)
        stage_timings["summarize_seconds"] = time.perf_counter() - t0

        exports: Dict[str, Dict[str, str]] = {}
        stage_timings["export_seconds"] = 0.0
        if export_results:
            t0 = time.perf_counter()
            timed_transcript = TranscriptionService.format_transcript_with_timestamps(
                transcription.segments
            )
            transcript_exports = self.export_service.export_transcript(
                timed_transcript,
                transcription.transcript_path,
                transcription.metadata,
            )
            summary_exports = self.export_service.export_summary(summary, transcription.metadata)
            exports = {
                "transcript": {fmt: str(path) for fmt, path in transcript_exports.items()},
                "summary": {fmt: str(path) for fmt, path in summary_exports.items()},
            }
            stage_timings["export_seconds"] = time.perf_counter() - t0

        stage_timings["total_wall_seconds"] = time.perf_counter() - run_started

        return {
            "meeting_name": transcription.metadata["meeting_name"],
            "timestamp": transcription.metadata["timestamp"],
            "transcript_text": transcription.text,
            "segments": transcription.segments,
            "semantic_clusters": self._serialize_clusters(clusters),
            "summary": summary,
            "exports": exports,
            "stage_timings": stage_timings,
        }

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

    def _serialize_clusters(self, clusters: List[SemanticCluster]) -> List[Dict[str, Any]]:
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


def build_pipeline(config: Optional[AppConfig] = None) -> TranscriptionPipeline:
    """Convenience factory for building a pipeline instance."""
    return TranscriptionPipeline(config=config)
