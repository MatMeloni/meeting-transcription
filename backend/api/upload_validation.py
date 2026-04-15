from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from config import AppConfig


def validate_audio_upload(filename: str | None, payload_size: int, config: AppConfig) -> None:
    """Raises HTTPException if upload exceeds limits or has disallowed extension."""
    if payload_size > config.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Arquivo excede o limite de {config.max_upload_bytes} bytes "
                f"({config.max_upload_bytes // (1024 * 1024)} MiB). "
                "Ajuste MAX_UPLOAD_BYTES se necessário."
            ),
        )
    suffix = Path(filename or "").suffix.lower()
    if not suffix or suffix not in config.allowed_audio_extensions:
        allowed = ", ".join(sorted(config.allowed_audio_extensions))
        raise HTTPException(
            status_code=400,
            detail=(
                f"Extensão obrigatória e permitida: {allowed}. "
                f"Recebido: '{suffix or '(sem extensão)'}'."
            ),
        )
