# Chicken short — Blender version

Same story, same voice as the Three.js versions (v1/v2/v3), rebuilt fully in
Blender with scripted geometry (bpy — no manual GUI modelling, no downloaded
models). Rendered with Eevee on a Colab GPU.

- Script (verbatim): `../chicken_short/SCRIPT.md` — 253 words, 3-group parable.
- Voice: Warm Pebble, exactly 75.984 s (`../chicken_short/voice/`).
- Sound mix: `../chicken_short_v3/audio/mix.wav` (75.984 s, -14.5 LUFS).
- Format: 1080x1920, 30 fps, 2,280 frames, h264+AAC, ~-14 LUFS.
- Visual target: `../shared/chicken_v3_visual_brief.md`,
  `../chicken_short_v3/CHARACTER_BIBLE.md`, `../chicken_short_v3/SHOT_TIMELINE.md`
  — 2D illustrated characters in a detailed 3D village, 13 shots timed to the
  real words.json. No captions/text on screen. Fade-in (f0–14) and fade-out
  (f2265–2279) required.

## Layout

- `scripts/` — bpy build scripts (one module per system + per shot) and the
  master build script `scripts/build_all.py` that produces the .blend.
- `scenes/` — the built `chicken_blender.blend` (generated, not hand-made),
  plus `proof_shot06.blend` (Milestone 1 proof — untouched).
- `assets/` — `words.json` (timing) and `mix.wav` (sound mix) for the repo
  + Colab notebook.
- `notebook/` — `chicken_blender_colab.ipynb`, the ready-to-run Colab
  notebook (GPU check, Blender install, Eevee test frames, 4 render shards,
  assembly + verification).
- `COLAB_RUN.md` — the exact Colab click-path + what to do if a session drops.
- `out/stills/all/` — Workbench validation stills (2–3 key frames per shot).
- `out/stills/cycles/` — Cycles CPU colour-check stills (1 per shot).
- `final/` — assembled `chicken_blender.mp4` (built after the Colab render).
- `tools/` — local Blender install (NOT committed; the notebook downloads it).
- `BUILD_NOTES.md` — technique, per-shot notes, decisions, measured timings,
  Colab render watch-list. `PROOF_NOTES.md` — Milestone 1 technique + bugs.

## Build locally

Run from the project root (`~/workspace/blender_chicken/`):

```
./tools/blender-4.2.23-linux-x64/blender --background --python scripts/build_all.py
./tools/blender-4.2.23-linux-x64/blender --background --python scripts/audit_flock.py
```

Validation stills:

```
./tools/blender-4.2.23-linux-x64/blender --background --python scripts/render_stills.py -- --engine workbench --frames 0,122,490,1098 --out out/stills/all --res 540
```

## Render (Colab GPU)

See `COLAB_RUN.md`. Frames render in
4 shards, each saved to Drive on completion, then assembled with ffmpeg and
muxed with `mix.wav`. **Eevee was never validated locally (no GPU) — render
one Eevee test frame per shot on Colab before the full render** (see
BUILD_NOTES.md).
