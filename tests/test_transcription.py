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
    transcript_text = "Discussão sobre planejamento."
    path = service._save_transcript(transcript_text, "Sprint Planning", "20240101")
    assert path.exists()
    assert path.read_text(encoding="utf-8") == transcript_text
    assert path.parent == config.transcripts_dir
