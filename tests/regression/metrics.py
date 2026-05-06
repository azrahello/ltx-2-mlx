"""Lightweight metrics for goldens comparison. Pure numpy + ffmpeg subprocess."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np


def decode_video(path: str | Path) -> np.ndarray:
    """Decode a video file to (T, H, W, 3) uint8 via ffmpeg."""
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    info = json.loads(probe.stdout)["streams"][0]
    w, h = int(info["width"]), int(info["height"])
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, h, w, 3)


def decode_audio(path: str | Path, sr: int = 48000, channels: int = 2) -> np.ndarray:
    """Decode audio from any container to (C, T) float32 via ffmpeg."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ar", str(sr), "-ac", str(channels), "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, channels).T


def video_stats(frames: np.ndarray) -> dict:
    f = frames.astype(np.float32)
    return {
        "shape": list(frames.shape),
        "mean": float(f.mean()),
        "std": float(f.std()),
        "p01": float(np.percentile(f, 1)),
        "p50": float(np.percentile(f, 50)),
        "p99": float(np.percentile(f, 99)),
    }


def audio_stats(wave: np.ndarray) -> dict:
    return {
        "shape": list(wave.shape),
        "rms": float(np.sqrt((wave**2).mean())),
        "peak": float(np.max(np.abs(wave))),
        "mean_abs": float(np.mean(np.abs(wave))),
    }


def video_psnr(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        return float("nan")
    mse = ((a.astype(np.float32) - b.astype(np.float32)) ** 2).mean()
    if mse == 0:
        return float("inf")
    return float(20.0 * np.log10(255.0 / np.sqrt(mse)))


def audio_l1(a: np.ndarray, b: np.ndarray) -> float:
    n = min(a.shape[-1], b.shape[-1])
    return float(np.mean(np.abs(a[..., :n] - b[..., :n])))


def audio_stft_l1(a: np.ndarray, b: np.ndarray, n_fft: int = 1024, hop: int = 256) -> float:
    """Magnitude-STFT L1 — proxy for spectral distance, no librosa dependency."""
    n = min(a.shape[-1], b.shape[-1])
    a1 = a[..., :n].mean(axis=0) if a.ndim > 1 else a[..., :n]
    b1 = b[..., :n].mean(axis=0) if b.ndim > 1 else b[..., :n]
    win = np.hanning(n_fft).astype(np.float32)

    def stft_mag(x: np.ndarray) -> np.ndarray:
        steps = max(0, 1 + (len(x) - n_fft) // hop)
        out = np.empty((steps, n_fft // 2 + 1), dtype=np.float32)
        for i in range(steps):
            seg = x[i * hop : i * hop + n_fft] * win
            out[i] = np.abs(np.fft.rfft(seg)).astype(np.float32)
        return out

    return float(np.mean(np.abs(stft_mag(a1) - stft_mag(b1))))
