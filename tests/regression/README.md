# Regression harness

Locks generation outputs at frozen seed/prompt/resolution so we can prove
that an upstream-sync fix produces the expected delta and nothing else.

## What it captures

Three goldens (see `config.py`):

| ID            | Pipeline                | Covers                                |
|---------------|-------------------------|----------------------------------------|
| `g1_two_stage`| `generate --two-stage`  | DiT, VAE, Vocoder, BWE, Euler+CFG     |
| `g2_hq`       | `generate --hq`         | + res_2s sampler                       |
| `g3_keyframe` | `keyframe`              | `VideoConditionByKeyframeIndex` (Fix 2)|

Heavy artifacts (`.mp4`, `.wav`) are gitignored. Only `manifest.json`
(stats per tag) is committed.

## Per-fix workflow

```bash
# 0. Lock the current behaviour as baseline.
python -m tests.regression.capture_baseline --tag pre_fix_1

# 1. Apply the fix in a feature branch.
git switch -c fix/vocoder-fp32
# ... edit code ...

# 2. Capture the new behaviour.
python -m tests.regression.capture_baseline --tag post_fix_1

# 3. Diff.
python -m tests.regression.verify_no_regression \
    --against pre_fix_1 --tag post_fix_1
```

## Expected deltas per fix

| Fix | g1_two_stage video | g1 audio (L1, STFT) | g2_hq video | g2 audio | g3_keyframe video |
|-----|--------------------|----------------------|-------------|----------|--------------------|
| **1 — Vocoder fp32** | PSNR ~ inf (identical) | sample L1 >> 1e-2, STFT L1 >> 1e-2 | identical | same delta as g1 | identical |
| **2 — `num_pixel_frames`** | PSNR ~ inf | identical | PSNR ~ inf | identical | PSNR drops (real change) |
| **3 — Decoder dtype guard** | PSNR ~ inf | identical | PSNR ~ inf | identical | PSNR ~ inf |

If a column says "identical" but PSNR is < 60 dB, the fix has leaked into
unrelated paths — **stop and investigate**.

## A/B audio listening

`tests/regression/goldens/pre_fix_1__g1_two_stage.wav` vs
`post_fix_1__g1_two_stage.wav`. Upstream reports 40-90% spectral metric
gap; the fix should be audibly cleaner (less crunch on transients).

## Memory check

Run with `MLX_METAL_DEBUG=1` or capture peak memory in a wrapper —
post-fix peak must stay within +5% of baseline.
