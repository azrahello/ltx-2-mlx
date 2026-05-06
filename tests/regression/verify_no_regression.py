"""Compare two captured tags pairwise.

Both tags must already exist in ``manifest.json`` (run
``capture_baseline`` for each before invoking this script).

Usage:
    python -m tests.regression.verify_no_regression --against pre_fix_1 --tag post_fix_1
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tests.regression.config import GOLDENS
from tests.regression.metrics import (
    audio_l1,
    audio_stft_l1,
    decode_audio,
    decode_video,
    video_psnr,
)

ROOT = Path(__file__).parent
GOLDENS_DIR = ROOT / "goldens"
MANIFEST = ROOT / "manifest.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--against", required=True, help="Tag to compare against (baseline)")
    ap.add_argument("--tag", required=True, help="Tag whose artifacts to evaluate")
    ap.add_argument("--only", choices=list(GOLDENS))
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text())
    for t in (args.against, args.tag):
        if t not in manifest:
            raise SystemExit(f"missing tag in manifest: {t}")

    targets = [args.only] if args.only else list(GOLDENS)
    print(f"\nComparing {args.tag} (current) <-> {args.against} (baseline)\n")

    for name in targets:
        a_mp4 = GOLDENS_DIR / f"{args.against}__{name}.mp4"
        b_mp4 = GOLDENS_DIR / f"{args.tag}__{name}.mp4"
        if not (a_mp4.exists() and b_mp4.exists()):
            print(f"  {name}: SKIP (mp4 missing — {a_mp4.name} or {b_mp4.name})")
            continue

        psnr = video_psnr(decode_video(a_mp4), decode_video(b_mp4))
        a_wav, b_wav = decode_audio(a_mp4), decode_audio(b_mp4)
        wav_l1 = audio_l1(a_wav, b_wav)
        stft_l1 = audio_stft_l1(a_wav, b_wav)

        print(f"  {name}:")
        print(f"    video PSNR      = {psnr:7.2f} dB")
        print(f"    audio sample L1 = {wav_l1:.4e}")
        print(f"    audio STFT L1   = {stft_l1:.4e}")


if __name__ == "__main__":
    main()
