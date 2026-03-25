# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Audio processing service.

Handles audio preprocessing (format conversion, noise reduction,
normalisation), quality analysis, and speech-to-text transcription via the
OpenAI Whisper model.

The Whisper model is loaded once at module import time on the available
device (CUDA if present, otherwise CPU).  This mirrors the original
behaviour and avoids reloading the model on every request.
"""

import logging
import os
import uuid
from typing import Any, Dict, Tuple

import librosa
import numpy as np
import noisereduce as nr
import soundfile as sf
import torch
import whisper
from pydub import AudioSegment

from app.config import UPLOAD_FOLDER, WHISPER_MODEL

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model initialisation (module-level singleton)
# ---------------------------------------------------------------------------

device: str = "cuda" if torch.cuda.is_available() else "cpu"
modelo = whisper.load_model(WHISPER_MODEL, device=device)

logger.info("Whisper model '%s' loaded on %s", WHISPER_MODEL, device)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def transcricao_pdf(audio_path: str) -> Dict[str, Any]:
    """Transcribe speech from *audio_path* using Whisper.

    Args:
        audio_path: Path to a WAV or compatible audio file.

    Returns:
        Whisper result dict (contains at least ``"text"``), or a dict with
        an ``"error"`` key on failure.
    """
    try:
        use_fp16 = device == "cuda"
        return modelo.transcribe(audio_path, fp16=use_fp16, language="pt")
    except Exception as e:
        return {"error": str(e)}


def calculate_snr_speech(audio_path: str) -> float:
    """Compute the Signal-to-Noise Ratio (dB) of a speech recording.

    Uses ``librosa.effects.split`` to separate voiced intervals from silence
    and estimates noise power from the gaps between intervals.

    Args:
        audio_path: Path to the audio file.

    Returns:
        SNR value in decibels.
    """
    y, sr = librosa.load(audio_path, sr=None)
    intervals = librosa.effects.split(y, top_db=20)
    signal_p = np.mean([np.mean(y[s:e] ** 2) for s, e in intervals])
    if len(intervals) > 1:
        noise = np.concatenate(
            [y[j1:i2] for (_, j1), (i2, _) in zip(intervals, intervals[1:])]
        )
        noise_p = np.mean(noise ** 2)
    else:
        noise_p = np.mean(y[-int(sr * 0.1):] ** 2)
    return 10 * np.log10(signal_p / noise_p)


def analyze_audio(audio_path: str) -> Tuple[float, float, float]:
    """Compute basic audio quality metrics.

    Args:
        audio_path: Path to the audio file.

    Returns:
        Tuple of ``(rms, pitch, spectral_centroid)`` as floats.
    """
    y, sr = librosa.load(audio_path, sr=None)
    rms = float(np.mean(librosa.feature.rms(y=y)))
    pitches, _ = librosa.core.piptrack(y=y, sr=sr)
    pitch = float(np.mean(pitches[pitches > 0]))
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    return rms, pitch, centroid


def preprocess_audio(
    input_path: str,
    output_path: str = "processed_audio.wav",
    target_sr: int = 16000,
    upload_folder: str = UPLOAD_FOLDER,
) -> str:
    """Convert, denoise, and normalise an audio file for transcription.

    Steps:
    1. If the file is already ``.wav``, return it unchanged.
    2. Convert to mono at *target_sr* Hz using pydub.
    3. Export a temporary WAV for librosa processing.
    4. Apply spectral noise reduction (noisereduce).
    5. Normalise amplitude to peak = 1.0.
    6. Save as 16-bit PCM WAV with a unique filename.
    7. Remove the intermediate temporary file.

    Args:
        input_path: Path to the raw input audio (any pydub-supported format).
        output_path: Base filename for the processed output (a UUID prefix is
            prepended to avoid collisions).
        target_sr: Target sample rate in Hz (default 16 000).
        upload_folder: Directory where temporary and output files are written.

    Returns:
        Path to the processed WAV file.
    """
    if ".wav" in input_path:
        return input_path

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(target_sr)

    temp_path = os.path.join(upload_folder, "temp.wav")
    audio.export(temp_path, format="wav")

    y, sr = librosa.load(temp_path, sr=target_sr)
    reduced_noise = nr.reduce_noise(y=y, sr=sr)

    peak = max(abs(reduced_noise))
    if peak > 0:
        reduced_noise = reduced_noise / peak

    final = os.path.join(upload_folder, f"{uuid.uuid4()}_{output_path}")
    sf.write(final, reduced_noise, sr, subtype="PCM_16")

    os.remove(temp_path)
    return final
