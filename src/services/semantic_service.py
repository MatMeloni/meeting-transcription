from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

import numpy as np

from models.embedding_model import EmbeddingModelLoader
from utils import text_utils
from utils.config import AppConfig


@dataclass
class SemanticChunk:
    """Represents a chunk of transcript text and its embedding vector."""

    text: str
    start_time: float
    end_time: float
    token_start: int
    token_end: int
    embedding: np.ndarray = field(repr=False)


@dataclass
class SemanticCluster:
    """Groups semantically similar chunks into a higher-level block."""

    label: str
    text: str
    chunks: List[SemanticChunk]
    start_time: float
    end_time: float


class SemanticAnalyzer:
    """Derives semantic structure from transcript text using embeddings."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.model_loader = EmbeddingModelLoader(config)

    def build_semantic_clusters(
        self, segments: List[Dict[str, Any]]
    ) -> List[SemanticCluster]:
        """Chunks the transcript, embeds each part, and clusters them semantically."""
        if not segments:
            logging.warning("Nenhum segmento disponível para análise semântica.")
            return []

        tokens_per_segment: List[int] = []
        token_cursor = 0
        segment_token_ranges: List[Dict[str, Any]] = []
        all_tokens: List[str] = []
        for segment in segments:
            segment_tokens = text_utils.tokenize_text(segment["text"])
            start_idx = token_cursor
            token_cursor += len(segment_tokens)
            tokens_per_segment.append(len(segment_tokens))
            segment_token_ranges.append(
                {
                    "start": start_idx,
                    "end": token_cursor,
                    "start_time": segment["start"],
                    "end_time": segment["end"],
                }
            )
            all_tokens.extend(segment_tokens)

        token_windows = text_utils.chunk_tokens(
            all_tokens, self.config.chunk_size, self.config.chunk_overlap
        )
        if not token_windows:
            logging.warning(
                "Transcrição insuficiente para formar chunks semânticos."
            )
            return []

        embedding_model = self.model_loader.load_model()
        logging.info("Gerando embeddings semânticos...")
        semantic_chunks: List[SemanticChunk] = []
        for window_index, (token_start, window_tokens) in enumerate(
            token_windows
        ):
            token_end = token_start + len(window_tokens)
            text = text_utils.detokenize(window_tokens)
            chunk_start_time, chunk_end_time = self._resolve_time_bounds(
                token_start, token_end, segment_token_ranges
            )
            embedding = embedding_model.encode(
                text, convert_to_numpy=True
            )
            embedding = self._normalize_vector(embedding)
            semantic_chunks.append(
                SemanticChunk(
                    text=text,
                    start_time=chunk_start_time,
                    end_time=chunk_end_time,
                    token_start=token_start,
                    token_end=token_end,
                    embedding=embedding,
                )
            )
            logging.debug(
                "Chunk %s tokens [%s, %s) mapeado para %.2f-%.2f s",
                window_index,
                token_start,
                token_end,
                chunk_start_time,
                chunk_end_time,
            )

        clusters = self._cluster_chunks(semantic_chunks)
        logging.info("Agrupamento semântico gerou %s blocos.", len(clusters))
        return clusters

    def _resolve_time_bounds(
        self,
        token_start: int,
        token_end: int,
        ranges: List[Dict[str, Any]],
    ) -> Tuple[float, float]:
        """Maps token spans back to approximate timeline seconds."""
        start_time = ranges[0]["start_time"]
        end_time = ranges[-1]["end_time"]
        for entry in ranges:
            if entry["end"] <= token_start:
                continue
            start_time = entry["start_time"]
            break
        for entry in reversed(ranges):
            if entry["start"] >= token_end:
                continue
            end_time = entry["end_time"]
            break
        return float(start_time), float(end_time)

    def _cluster_chunks(
        self, chunks: List[SemanticChunk]
    ) -> List[SemanticCluster]:
        """Clusters chunk embeddings by cosine similarity using a greedy strategy."""
        if not chunks:
            return []
        clusters: List[SemanticCluster] = []
        centroids: List[np.ndarray] = []
        threshold = self.config.similarity_threshold
        for chunk in chunks:
            assigned_index = None
            for idx, centroid in enumerate(centroids):
                similarity = float(np.dot(centroid, chunk.embedding))
                if similarity >= threshold:
                    assigned_index = idx
                    break
            if assigned_index is None:
                label = f"Bloco {len(clusters) + 1}"
                clusters.append(
                    SemanticCluster(
                        label=label,
                        text=chunk.text,
                        chunks=[chunk],
                        start_time=chunk.start_time,
                        end_time=chunk.end_time,
                    )
                )
                centroids.append(chunk.embedding.copy())
            else:
                cluster = clusters[assigned_index]
                cluster.chunks.append(chunk)
                cluster.text = " ".join([cluster.text, chunk.text]).strip()
                cluster.start_time = min(cluster.start_time, chunk.start_time)
                cluster.end_time = max(cluster.end_time, chunk.end_time)
                centroid = centroids[assigned_index]
                centroid = self._normalize_vector(centroid + chunk.embedding)
                centroids[assigned_index] = centroid
        return clusters

    @staticmethod
    def _normalize_vector(vector: np.ndarray) -> np.ndarray:
        """Normalizes embedding vectors to unit norm."""
        norm = np.linalg.norm(vector) or 1.0
        return vector / norm
