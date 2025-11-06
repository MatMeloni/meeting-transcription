from __future__ import annotations

import logging

from transformers import pipeline

from utils.config import AppConfig


class SummarizerModelLoader:
    """Builds a transformers summarization pipeline for meeting summaries."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._pipeline = None

    def load_pipeline(self):
        """Returns a cached transformers pipeline."""
        if self._pipeline is None:
            logging.info(
                "Carregando pipeline de sumarização (%s)...",
                self.config.summarizer_model_name,
            )
            self._pipeline = pipeline(
                task="summarization",
                model=self.config.summarizer_model_name,
            )
        return self._pipeline
