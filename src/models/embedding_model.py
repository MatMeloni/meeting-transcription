from __future__ import annotations

import logging
from typing import Optional

from sentence_transformers import SentenceTransformer

from config import AppConfig


class EmbeddingModelLoader:
    """Instantiates the SentenceTransformer model used for semantic embeddings."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._model: Optional[SentenceTransformer] = None

    def load_model(self) -> SentenceTransformer:
        """Returns a cached instance of the embedding model."""
        if self._model is None:
            logging.info(
                "Carregando modelo de embeddings %s...",
                self.config.embedding_model_name,
            )
            self._model = SentenceTransformer(
                self.config.embedding_model_name,
                cache_folder=str(self.config.models_dir),
            )
        return self._model
