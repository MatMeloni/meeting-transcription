from __future__ import annotations

import pytest

pytest.importorskip("librosa")
pytest.importorskip("faster_whisper")
pytest.importorskip("sentence_transformers")

from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.app import create_app
from backend.controller.pipeline_controller import PipelineController
from config import AppConfig, ensure_output_dirs


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    config = AppConfig(outputs_dir=tmp_path / "outputs")
    ensure_output_dirs(config)
    config.max_upload_bytes = 500
    controller = PipelineController(config=config, configure_logging=False)

    def fake_process_uploaded_bytes(**kwargs):
        return {
            "meeting_name": kwargs.get("meeting_name", "x"),
            "timestamp": "20990101_000000",
            "transcript_text": "ok",
            "segments": [{"id": 1, "start": 0.0, "end": 1.0, "text": "ok"}],
            "semantic_clusters": [],
            "summary": {
                "decisions": [],
                "pending": [],
                "next_steps": [],
                "overview": ["teste"],
            },
            "exports": {},
            "stage_timings": {"total_wall_seconds": 0.1},
        }

    monkeypatch.setattr(controller, "process_uploaded_bytes", fake_process_uploaded_bytes)
    return TestClient(create_app(controller))


def test_transcribe_rejects_oversized_file(client: TestClient) -> None:
    body = b"x" * 600
    response = client.post(
        "/transcribe",
        files={"file": ("big.wav", body, "audio/wav")},
    )
    assert response.status_code == 413


def test_transcribe_rejects_bad_extension(client: TestClient) -> None:
    response = client.post(
        "/transcribe",
        files={"file": ("mal.exe", b"abcd", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_transcribe_rejects_empty_file(client: TestClient) -> None:
    response = client.post(
        "/transcribe",
        files={"file": ("empty.wav", b"", "audio/wav")},
    )
    assert response.status_code == 400


def test_transcribe_accepts_small_wav(client: TestClient) -> None:
    response = client.post(
        "/transcribe",
        files={"file": ("ok.wav", b"12345", "audio/wav")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meeting_name"]
    assert "stage_timings" in data
    assert data["transcript_text"] == "ok"
