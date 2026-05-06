"""Frozen configuration for regression goldens.

Do not modify the SEED / PROMPT / MODEL / resolution constants without
re-capturing the baseline (manifest.json becomes meaningless if inputs
drift).
"""

from __future__ import annotations

SEED = 9803402

PROMPT = (
    "A young woman with long auburn hair walks slowly along a sunlit "
    "cobblestone street in Lisbon at golden hour, her white linen dress "
    "gently swaying with each step. The camera tracks beside her at eye "
    "level, then slowly pulls back to reveal pastel-colored buildings and "
    "a yellow tram passing in the background. Warm afternoon light filters "
    "through jacaranda trees, casting dappled shadows across the ground. "
    "Shallow depth of field, soft 35mm film grain, cinematic natural "
    "color grading."
)

NEG_PROMPT = ""
MODEL = "dgrauet/ltx-2.3-mlx-q8"
FPS = 24

GEN_HEIGHT, GEN_WIDTH, GEN_FRAMES = 480, 704, 33

KF_HEIGHT, KF_WIDTH, KF_FRAMES = 480, 480, 33
KF_START = "tests/fixtures/lisbon_woman_start.png"
KF_END = "tests/fixtures/lisbon_woman_end.png"

GOLDENS: dict[str, dict] = {
    "g1_two_stage": {
        "cli_args": [
            "generate",
            "--prompt",
            PROMPT,
            "--two-stage",
            "--seed",
            str(SEED),
            "-H",
            str(GEN_HEIGHT),
            "-W",
            str(GEN_WIDTH),
            "-f",
            str(GEN_FRAMES),
        ],
    },
    "g2_hq": {
        "cli_args": [
            "generate",
            "--prompt",
            PROMPT,
            "--hq",
            "--seed",
            str(SEED),
            "-H",
            str(GEN_HEIGHT),
            "-W",
            str(GEN_WIDTH),
            "-f",
            str(GEN_FRAMES),
        ],
    },
    "g3_keyframe": {
        # Keyframe interpolation requires the dev model + distilled LoRA;
        # the distilled-only model hallucinates during interpolation.
        "cli_args": [
            "keyframe",
            "--prompt",
            PROMPT,
            "--start",
            KF_START,
            "--end",
            KF_END,
            "--seed",
            str(SEED),
            "-H",
            str(KF_HEIGHT),
            "-W",
            str(KF_WIDTH),
            "-f",
            str(KF_FRAMES),
            "--dev-transformer",
            "transformer-dev.safetensors",
            "--distilled-lora",
            "ltx-2.3-22b-distilled-lora-384.safetensors",
        ],
    },
}
