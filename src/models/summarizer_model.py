from __future__ import annotations

import logging
from typing import Any, Dict, List

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from config import AppConfig


class _Seq2SeqPipeline:
    """Thin wrapper around a seq2seq model that mimics the pipeline() call interface."""

    def __init__(self, model_name: str) -> None:
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def __call__(
        self,
        text: str,
        max_length: int = 180,
        min_length: int = 30,
        do_sample: bool = False,
        **_: Any,
    ) -> List[Dict[str, str]]:
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        )
        output_ids = self._model.generate(
            **inputs,
            max_length=max_length,
            min_length=min_length,
            do_sample=do_sample,
        )
        summary = self._tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return [{"summary_text": summary}]


class SummarizerModelLoader:
    """Builds a seq2seq summarization pipeline for meeting summaries."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._pipeline: _Seq2SeqPipeline | None = None

    def load_pipeline(self) -> _Seq2SeqPipeline:
        """Returns a cached seq2seq pipeline."""
        if self._pipeline is None:
            logging.info(
                "Carregando pipeline de sumarização (%s)...",
                self.config.summarizer_model_name,
            )
            self._pipeline = _Seq2SeqPipeline(self.config.summarizer_model_name)
        return self._pipeline
