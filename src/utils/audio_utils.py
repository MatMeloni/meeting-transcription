from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import librosa
import numpy as np
import soundfile as sf


def load_audio(audio_path: Path, target_sr: int | None = None) -> Tuple[np.ndarray, int]:
    """Loads an audio file in mono and optionally resamples it."""
    if not audio_path.exists():
        raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")
    samples, sr = librosa.load(audio_path, sr=None, mono=True)
    logging.debug("Áudio carregado de %s com taxa %s Hz", audio_path, sr)
    if target_sr:
        samples, sr = resample_audio(samples, sr, target_sr)
    return samples, sr


def trim_silence(audio: np.ndarray, sr: int, top_db: float = 25.0) -> np.ndarray:
    """Removes leading and trailing silence from the audio signal."""
    trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
    logging.debug("Áudio trimado de %s amostras para %s", len(audio), len(trimmed))
    return trimmed


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Applies peak normalization to prevent clipping and balance gain."""
    peak = np.max(np.abs(audio)) or 1.0
    normalized = audio / peak
    logging.debug("Áudio normalizado com pico original %s", peak)
    return normalized


def reduce_noise(audio: np.ndarray, sr: int) -> np.ndarray:
    """Performs a lightweight spectral subtraction noise reduction."""
    stft = librosa.stft(audio)
    magnitude, phase = librosa.magphase(stft)
    noise_profile = np.mean(
        magnitude[:, : min(10, magnitude.shape[1])], axis=1, keepdims=True
    )
    cleaned_magnitude = np.maximum(magnitude - noise_profile, 0.0)
    cleaned_audio = librosa.istft(cleaned_magnitude * phase)
    cleaned_audio = librosa.util.fix_length(cleaned_audio, len(audio))
    logging.debug("Ruído atenuado por subtração espectral simples")
    return cleaned_audio


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> Tuple[np.ndarray, int]:
    """Resamples audio to the target sample-rate if needed."""
    if orig_sr == target_sr:
        return audio, target_sr
    resampled = librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)
    logging.debug("Áudio reamostrado de %s Hz para %s Hz", orig_sr, target_sr)
    return resampled, target_sr


def write_wav_file(path: Path, audio: np.ndarray, sr: int) -> None:
    """Writes audio samples to disk as a WAV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio, sr)
    logging.debug("Áudio persistido em %s", path)
