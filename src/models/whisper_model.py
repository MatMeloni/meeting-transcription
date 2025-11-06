from __future__ import annotations

import logging
from typing import Optional

from faster_whisper import WhisperModel

from utils.config import AppConfig


class WhisperModelLoader:
    """Loads and caches the Whisper ASR model using faster-whisper."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._model: Optional[WhisperModel] = None

    def load_model(self) -> WhisperModel:
        """Returns a memoized WhisperModel instance."""
        if self._model is None:
            logging.info(
                "Carregando modelo Whisper (%s) com compute_type=%s...",
                self.config.whisper_model_size,
                self.config.whisper_compute_type,
            )
            self._model = WhisperModel(
                model_size_or_path=self.config.whisper_model_size,
                device=self.config.whisper_device,
                compute_type=self.config.whisper_compute_type,
                download_root=str(self.config.models_dir),
            )
        return self._model
