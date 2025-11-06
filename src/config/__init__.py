"""Configuration utilities and defaults for the AI core."""

from .settings import (  # noqa: F401
    AppConfig,
    EMBEDDING_MODEL,
    OUTPUT_DIR,
    SUMMARIZER_MODEL,
    WHISPER_MODEL,
    ensure_output_dirs,
    setup_logging,
)
