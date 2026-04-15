"""Testa o encadeamento do pipeline com serviços de IA dubados."""

from __future__ import annotations

import pytest

pytest.importorskip("librosa")
pytest.importorskip("faster_whisper")
pytest.importorskip("sentence_transformers")

from pathlib import Path

import numpy as np

from backend.controller.pipeline_controller import PipelineController
from config import AppConfig, ensure_output_dirs
from services.transcription_service import TranscriptionResult
from utils.audio_utils import write_wav_file


@pytest.fixture
def tiny_wav(tmp_path: Path) -> Path:
    wav = tmp_path / "tone.wav"
    sr = 16_000
    t = np.linspace(0.0, 0.25, int(0.25 * sr), endpoint=False)
    samples = 0.05 * np.sin(2 * np.pi * 440.0 * t).astype(np.float32)
    write_wav_file(wav, samples, sr)
    return wav


def test_process_audio_file_end_to_end_stubbed(tiny_wav: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = AppConfig(outputs_dir=tmp_path / "outputs")
    ensure_output_dirs(config)
    controller = PipelineController(config=config, configure_logging=False)
    pipeline = controller.pipeline

    transcript_path = tmp_path / "outputs" / "transcripts" / "stub.txt"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text("Discussão de teste.", encoding="utf-8")

    def fake_transcribe(self, audio_path: Path, meeting_name: str) -> TranscriptionResult:
        return TranscriptionResult(
            segments=[
                {"id": 1, "start": 0.0, "end": 2.0, "text": "Discussão de teste."},
            ],
            text="Discussão de teste.",
            transcript_path=transcript_path,
            metadata={
                "duration_seconds": 2.0,
                "language": "pt",
                "probability": 0.99,
                "timestamp": "20990101_120000",
                "meeting_name": meeting_name,
            },
        )

    monkeypatch.setattr(
        pipeline.transcription_service,
        "transcribe_audio",
        fake_transcribe,
    )

    from services.semantic_service import SemanticAnalyzer, SemanticCluster, SemanticChunk

    def fake_clusters(self, segments):
        return [
            SemanticCluster(
                label="Bloco 1",
                text="Discussão de teste.",
                chunks=[
                    SemanticChunk(
                        text="Discussão de teste.",
                        start_time=0.0,
                        end_time=2.0,
                        token_start=0,
                        token_end=4,
                        embedding=np.ones(4, dtype=float),
                    )
                ],
                start_time=0.0,
                end_time=2.0,
            )
        ]

    monkeypatch.setattr(SemanticAnalyzer, "build_semantic_clusters", fake_clusters)

    def fake_summary(self, transcript_text, semantic_clusters):
        return {
            "decisions": ["Aprovado o plano."],
            "pending": ["Aguardar revisão."],
            "next_steps": ["Enviar documento."],
            "overview": ["Reunião de teste executada com sucesso."],
        }

    monkeypatch.setattr(
        pipeline.summarization_service,
        "generate_structured_summary",
        fake_summary,
    )

    result = controller.process_audio_file(
        audio_file=tiny_wav,
        meeting_name="integracao",
        export_results=False,
    )

    assert result["meeting_name"] == "integracao"
    assert "Discussão" in result["transcript_text"]
    assert len(result["segments"]) == 1
    assert result["semantic_clusters"]
    assert result["summary"]["decisions"]
    assert "stage_timings" in result
    assert result["stage_timings"]["transcribe_seconds"] >= 0.0
    assert result["stage_timings"]["total_wall_seconds"] >= 0.0


def test_process_uploaded_bytes_invokes_pipeline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = AppConfig(outputs_dir=tmp_path / "outputs")
    ensure_output_dirs(config)
    controller = PipelineController(config=config, configure_logging=False)

    calls: list[str] = []

    def fake_process_audio_file(self, audio_file, meeting_name=None, export_results=True):
        calls.append(str(audio_file))
        return {
            "meeting_name": meeting_name or "x",
            "timestamp": "t",
            "transcript_text": "",
            "segments": [],
            "semantic_clusters": [],
            "summary": {"decisions": [], "pending": [], "next_steps": [], "overview": []},
            "exports": {},
            "stage_timings": {},
        }

    monkeypatch.setattr(
        controller.pipeline,
        "process_audio_file",
        fake_process_audio_file,
    )

    out = controller.process_uploaded_bytes(
        payload=b"fake",
        original_filename="clip.wav",
        meeting_name="up",
        export_results=False,
    )
    assert out["meeting_name"] == "up"
    assert len(calls) == 1
    assert "upload_" in Path(calls[0]).name
