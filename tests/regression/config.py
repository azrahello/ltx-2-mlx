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

# G3 (keyframe interpolation) is intentionally absent: the keyframe
# pipeline currently produces a hold-cut-decay pattern instead of smooth
# interpolation on hedgehog (validated config), Lisbon (480x480) and
# 591a3d8 alike. Bug predates the upstream-sync work. Will be revisited
# alongside Fix 2 (num_pixel_frames) since it touches keyframe positions.

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
}
