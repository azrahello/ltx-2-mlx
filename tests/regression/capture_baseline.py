"""Capture or refresh regression goldens for a tagged checkpoint.

Each tag (e.g. ``pre_fix_1``, ``post_fix_1``) writes mp4+wav files into
``tests/regression/goldens/`` and a stats block under that tag in
``manifest.json``. Heavy artifacts are gitignored; the manifest is
committed so deltas between tags are reviewable in the diff.

Usage:
    python -m tests.regression.capture_baseline --tag pre_fix_1
    python -m tests.regression.capture_baseline --tag pre_fix_1 --only g1_two_stage
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from tests.regression.config import GOLDENS
from tests.regression.metrics import (
    audio_stats,
    decode_audio,
    decode_video,
    video_stats,
)

ROOT = Path(__file__).parent
GOLDENS_DIR = ROOT / "goldens"
MANIFEST = ROOT / "manifest.json"


def _git_rev() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except subprocess.CalledProcessError:
        return "unknown"


def _run_one(name: str, cli_args: list[str], out_mp4: Path) -> dict:
    cmd = ["uv", "run", "ltx-2-mlx", *cli_args, "-o", str(out_mp4)]
    print(f"\n=== {name} ===")
    print(" ".join(cmd))
    t0 = time.time()
    subprocess.run(cmd, check=True)
    wall = time.time() - t0

    wav = out_mp4.with_suffix(".wav")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(out_mp4),
            "-vn",
            "-acodec",
            "pcm_f32le",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(wav),
        ],
        check=True,
    )

    return {
        "wall_seconds": round(wall, 1),
        "video": video_stats(decode_video(out_mp4)),
        "audio": audio_stats(decode_audio(out_mp4)),
        "mp4": out_mp4.name,
        "wav": wav.name,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="Manifest section name (e.g. pre_fix_1)")
    ap.add_argument("--only", choices=list(GOLDENS), help="Capture only one golden")
    args = ap.parse_args()

    GOLDENS_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    section = manifest.setdefault(args.tag, {})
    section["git_rev"] = _git_rev()

    targets = [args.only] if args.only else list(GOLDENS)
    for name in targets:
        out_mp4 = GOLDENS_DIR / f"{args.tag}__{name}.mp4"
        section[name] = _run_one(name, GOLDENS[name]["cli_args"], out_mp4)

    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"\nWrote {MANIFEST.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
