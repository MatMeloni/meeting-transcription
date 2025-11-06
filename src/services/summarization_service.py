from __future__ import annotations

import logging
import re
from typing import Dict, List

from config import AppConfig
from models.summarizer_model import SummarizerModelLoader
from services.semantic_service import SemanticCluster
from utils import text_utils


class SummarizationService:
    """Builds structured meeting summaries from semantic clusters."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.model_loader = SummarizerModelLoader(config)

    def generate_structured_summary(
        self, transcript_text: str, semantic_clusters: List[SemanticCluster]
    ) -> Dict[str, List[str]]:
        """Produces bullet-point summaries for decisões, pendências e próximos passos."""
        summarizer = self.model_loader.load_pipeline()
        logging.info("Gerando resumo estruturado...")
        sections = {
            "decisions": "liste as principais decisões tomadas na reunião",
            "pending": "aponte pendências, bloqueios ou itens dependentes",
            "next_steps": "liste próximos passos ou encaminhamentos acordados",
        }

        results: Dict[str, List[str]] = {key: [] for key in sections}
        if not semantic_clusters:
            logging.warning(
                "Nenhum cluster semântico disponível; resumo pode ficar limitado."
            )

        for key, instruction in sections.items():
            section_context = self._compose_section_context(
                semantic_clusters, instruction
            )
            prompt_tokens = text_utils.tokenize_text(section_context)
            prompt_tokens = text_utils.limit_tokens(
                prompt_tokens, self.config.summary_max_tokens
            )
            prompt_text = text_utils.detokenize(prompt_tokens)
            try:
                summary_output = summarizer(
                    prompt_text,
                    max_length=180,
                    min_length=30,
                    do_sample=False,
                )
                summary_text = summary_output[0]["summary_text"].strip()
            except Exception as exc:  # pragma: no cover - defensive branch
                logging.exception(
                    "Falha ao resumir seção %s: %s", key, exc
                )
                summary_text = "Resumo indisponível no momento."
            bullet_points = [
                fragment.strip(" -•")
                for fragment in re.split(r"[.;]\s+", summary_text)
                if fragment.strip()
            ]
            results[key].extend(bullet_points)

        results["overview"] = self._generate_overall_summary(
            summarizer, transcript_text
        )
        logging.info("Resumo estruturado concluído.")
        return results

    def _compose_section_context(
        self, clusters: List[SemanticCluster], instruction: str
    ) -> str:
        """Builds input text for a summary section with guidance for the model."""
        if not clusters:
            return f"summarize: {instruction}."
        ordered_clusters = sorted(
            clusters, key=lambda cluster: cluster.start_time
        )
        cluster_text = " ".join(
            f"[{cluster.label}] {cluster.text}" for cluster in ordered_clusters
        )
        return f"summarize: {instruction}. Contexto: {cluster_text}"

    def _generate_overall_summary(self, summarizer, transcript_text: str) -> List[str]:
        """Creates a compact overview paragraph."""
        tokens = text_utils.tokenize_text(transcript_text)
        tokens = text_utils.limit_tokens(tokens, self.config.summary_max_tokens)
        if not tokens:
            return ["Transcrição indisponível para gerar visão geral."]
        prompt = text_utils.detokenize(tokens)
        try:
            output = summarizer(
                prompt, max_length=200, min_length=60, do_sample=False
            )
            overview = output[0]["summary_text"].strip()
        except Exception as exc:  # pragma: no cover - defensive branch
            logging.exception("Falha ao gerar visão geral: %s", exc)
            overview = "Não foi possível gerar o resumo geral."
        return [overview]
