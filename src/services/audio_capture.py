from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np

from config import AppConfig
from utils import audio_utils

try:
    import sounddevice as sd
except ImportError:  # pragma: no cover - optional dependency
    sd = None
    logging.warning(
        "sounddevice não está disponível; captura ao vivo ficará desativada."
    )


class AudioCaptureService:
    """Handles microphone capture and offline preprocessing workflow."""

    def __init__(self, config: AppConfig):
        self.config = config

    def capture_microphone(
        self, duration_seconds: float, samplerate: Optional[int] = None
    ) -> Path:
        """Captures audio from the default microphone for a given duration."""
        if sd is None:
            raise RuntimeError(
                "sounddevice não está instalado; não é possível capturar áudio ao vivo."
            )
        samplerate = samplerate or self.config.target_samplerate
        logging.info(
            "Capturando áudio do microfone por %.1f segundos...",
            duration_seconds,
        )
        recording = sd.rec(
            int(duration_seconds * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        audio_array = recording[:, 0]
        return self.preprocess_array(audio_array, samplerate)

    def preprocess_file(
        self, audio_path: Path, target_sr: Optional[int] = None
    ) -> Path:
        """Preprocesses an existing audio file and returns the normalized temp path."""
        logging.info("Pré-processando áudio em %s...", audio_path)
        samples, sr = audio_utils.load_audio(audio_path, target_sr=None)
        processed = self._post_process(
            samples, sr, target_sr or self.config.target_samplerate
        )
        output_path = self.config.audio_temp_path
        audio_utils.write_wav_file(
            output_path,
            processed,
            target_sr or self.config.target_samplerate,
        )
        logging.info("Áudio pré-processado disponível em %s", output_path)
        return output_path

    def preprocess_array(self, audio_array: np.ndarray, sr: int) -> Path:
        """Preprocesses an in-memory audio array and persists the normalized file."""
        processed = self._post_process(
            audio_array, sr, self.config.target_samplerate
        )
        output_path = self.config.audio_temp_path
        audio_utils.write_wav_file(
            output_path, processed, self.config.target_samplerate
        )
        logging.info("Áudio normalizado salvo em %s", output_path)
        return output_path

    def _post_process(
        self, audio_array: np.ndarray, sr: int, target_sr: int
    ) -> np.ndarray:
        """Runs trimming, normalization, noise reduction, and resampling."""
        trimmed = audio_utils.trim_silence(audio_array, sr)
        normalized = audio_utils.normalize_audio(trimmed)
        denoised = audio_utils.reduce_noise(normalized, sr)
        resampled, _ = audio_utils.resample_audio(denoised, sr, target_sr)
        return resampled
