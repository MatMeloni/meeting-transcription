import pytest

pytest.importorskip("faster_whisper")

from config import AppConfig, ensure_output_dirs
from services.transcription_service import TranscriptionService


def test_slugify_generates_safe_filename(tmp_path) -> None:
    config = AppConfig(outputs_dir=tmp_path / "outputs")
    ensure_output_dirs(config)
    service = TranscriptionService(config)
    assert service._slugify("Reunião @ Sprint #1!") == "reuniao_sprint_1"


def test_save_transcript_creates_file(tmp_path) -> None:
    config = AppConfig(outputs_dir=tmp_path / "outputs")
    ensure_output_dirs(config)
    service = TranscriptionService(config)
    transcript_text = "[00:00:00 --> 00:00:04] Discussão sobre planejamento."
    path = service._save_transcript(transcript_text, "Sprint Planning", "20240101")
    assert path.exists()
    assert path.read_text(encoding="utf-8") == transcript_text
    assert path.parent == config.transcripts_dir


def test_format_transcript_with_timestamps() -> None:
    segments = [
        {"start": 0.0, "end": 4.2, "text": "Olá equipe"},
        {"start": 65.0, "end": 70.5, "text": "Próximo ponto"},
    ]
    formatted = TranscriptionService.format_transcript_with_timestamps(segments)
    assert formatted == (
        "[00:00:00 --> 00:00:04] Olá equipe\n"
        "[00:01:05 --> 00:01:10] Próximo ponto"
    )
