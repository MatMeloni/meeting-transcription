from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

from backend.api.upload_validation import validate_audio_upload
from config import AppConfig, ensure_output_dirs


def test_validate_rejects_large_payload(tmp_path: Path) -> None:
    config = AppConfig(outputs_dir=tmp_path / "out")
    ensure_output_dirs(config)
    config.max_upload_bytes = 10
    with pytest.raises(HTTPException) as exc:
        validate_audio_upload("a.wav", 100, config)
    assert exc.value.status_code == 413


def test_validate_rejects_wrong_extension(tmp_path: Path) -> None:
    config = AppConfig(outputs_dir=tmp_path / "out")
    ensure_output_dirs(config)
    with pytest.raises(HTTPException) as exc:
        validate_audio_upload("file.bin", 5, config)
    assert exc.value.status_code == 400


def test_validate_accepts_allowed_extension(tmp_path: Path) -> None:
    config = AppConfig(outputs_dir=tmp_path / "out")
    ensure_output_dirs(config)
    validate_audio_upload("rec.mp3", 5, config)
