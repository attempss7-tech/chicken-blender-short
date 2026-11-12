# Running the Blender chicken short on Colab

The project is built and validated locally. The Colab GPU does the Eevee
render only. The notebook is `notebook/chicken_blender_colab.ipynb`.

## Click-path

1. Open https://colab.research.google.com.
2. **File > Open notebook > GitHub tab** — paste
   `attempss7-tech/chicken-blender-short`, open
   `notebook/chicken_blender_colab.ipynb`. (Or upload the `.ipynb` file
   directly: File > Upload notebook.)
3. **Runtime > Change runtime type > T4 GPU > Save.** The notebook fails
   fast with a clear message if no GPU is attached — do not render on CPU
   (Eevee falls back to software rendering, far too slow).
4. Run the cells **top to bottom, in order**. Do not use "Run all" blindly:
   you must STOP after the Eevee test-frames cell and inspect the 13 frames
   before running any shard cell.
5. The first cell mounts Google Drive — click through the auth prompt.
   Frames go to `MyDrive/chicken_blender/frames/`, test frames to
   `MyDrive/chicken_blender/test_frames/`, the final video to
   `MyDrive/chicken_blender/final/`.

## The mandatory stop: Eevee test frames

Eevee was never validated locally (no GPU there). The test-frames cell
renders 13 frames, one per shot, and displays them inline. Check every one:

- Outlines read as **dark rims** around characters/props — NOT solid black
  shells.
- Windows glow, pot flames glow, no black or missing objects.
- Outfit colours right: teal vest + straw hat = Farmer A (Group 3);
  ochre shirt = Farmer B (Group 1); green tunic + rust scarf = Farmer C
  (Group 2).

**If characters have black shells:** run the FIX cell (sets the Outline
material to HASHED blending), then re-run the test-frames cell.
**If all 13 look right:** skip the fix cell and run the 4 shard cells.

## Shards (frames 0–2279 in 4 × 570)

- Shard 1: 0–569 · Shard 2: 570–1139 · Shard 3: 1140–1709 · Shard 4: 1710–2279.
- Each shard renders in 6 batches of 95 frames and copies each batch to
  Drive immediately. Per-frame timings print as it goes; each shard ends
  with a count check against Drive.
- Expected speed is unmeasured until the first test frame — budget roughly
  1–3 s/frame on a T4 (10–30 min per shard) and re-estimate from the
  test-frames timings.

## If a session drops mid-shard

Colab sessions reset/disconnect (12 h cap, ~90 min idle, GPU preemption).
Nothing is lost beyond the in-progress batch (~5 min of rendering):

1. Reopen the notebook (same file, same account).
2. Re-run the setup cells in order: mount Drive + GPU check, install
   Blender + libs, clone repo (or pull).
3. Re-run the interrupted shard cell. It first syncs that shard's finished
   frames from Drive back to local disk, then renders only the missing
   frames, batch by batch.
4. Continue with the remaining shard cells, then assembly.

Do NOT re-run the test-frames cell unless you changed something — the test
frames are already on Drive.

## Assembly + verification

The assembly cell checks all 2,280 frames are on Drive (and stops, listing
any missing frames, if not), then runs ffmpeg: PNG sequence → h264 mp4
(crf 17), fade-in 0.5 s + fade-out 0.5 s from 75.5 s, muxed with the sound
mix (`assets/mix.wav`, already −14.5 LUFS). The verification cell prints
ffprobe details + an ebur128 loudness reading.

Expected final: `chicken_blender.mp4`, ~75.98 s, 1080x1920, 30 fps,
h264 + AAC, ~−14.5 LUFS.

## If the committed .blend fails

The last markdown cell has the rebuild command: it re-runs
`scripts/build_all.py` in Colab (~3 min) to regenerate
`scenes/chicken_blender.blend` from the scripts, then re-run the
test-frames cell.

## Known limits (from BUILD_NOTES.md)

- Hen legs are static during walks (body bobs + yaws; doesn't read wrong
  at render distance).
- Outer houses are partially cropped at the edges of the widest wides
  (shots 1, 2, 13) — a 24 m village can't fit 9:16 otherwise.
- Shot 9's house extension is a background detail, not a distinct read.
- Steam puffs are opaque stylised spheres, not volumetrics.
- No captions/text are baked in — captions are a separate overlay step.
