from __future__ import annotations

import re
from typing import Iterable, List, Tuple

TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def clean_text(text: str) -> str:
    """Normalizes whitespace and strips trailing markers from transcriptions."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned


def tokenize_text(text: str) -> List[str]:
    """Tokenizes text using a regex that preserves punctuation."""
    return TOKEN_PATTERN.findall(text)


def detokenize(tokens: Iterable[str]) -> str:
    """Reconstructs text from tokens while handling spacing around punctuation."""
    text = " ".join(tokens)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    return text


def chunk_tokens(tokens: List[str], chunk_size: int, overlap: int) -> List[Tuple[int, List[str]]]:
    """Splits tokens into windows with defined overlap."""
    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser positivo")
    if overlap >= chunk_size:
        raise ValueError("overlap deve ser menor que chunk_size")
    step = chunk_size - overlap
    windows: List[Tuple[int, List[str]]] = []
    for start in range(0, len(tokens), step):
        end = min(start + chunk_size, len(tokens))
        window_tokens = tokens[start:end]
        if not window_tokens:
            continue
        windows.append((start, window_tokens))
        if end >= len(tokens):
            break
    return windows


def limit_tokens(tokens: List[str], max_tokens: int) -> List[str]:
    """Crops token list to the requested size."""
    if max_tokens <= 0:
        return []
    return tokens[:max_tokens]


def approximate_token_count(text: str) -> int:
    """Provides an approximate token count for logging and metrics."""
    return len(tokenize_text(text))
