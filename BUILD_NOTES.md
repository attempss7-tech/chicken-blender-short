# BUILD NOTES — Blender version of the chicken short

Project: `~/workspace/blender_chicken/`
Script: "Why do the rich keep getting richer while the poor get poorer?
One chicken explains it." — the user's verbatim 253-word parable, same
script and voice as `~/workspace/chicken_short/` (v1) and
`~/workspace/chicken_short_v3/` (v3, Three.js). This is a NEW rebuild in
Blender, ordered 2026-11-12 ("build blender version in collab").
Do not touch v1/v2/v3.

## Deliverable

`scenes/chicken_blender.blend` — one scene, one 2280-frame timeline
(1080x1920, 30fps, frames 0–2279), 13 shots, 14 marker-bound cameras
(shot 7 has two setups), engine `BLENDER_EEVEE_NEXT`.

Final build (2026-11-12, build #5): **1751 objects (1418 meshes),
175,147 polys, 310 actions, 14 cameras**, 30,646,964 bytes. Build time
**163.9s** headless.

## Technique (proven in Milestone 1, the shot-6 proof)

Flat-shaded 3D primitive characters (spheres, capsules, cones — no
downloaded models, no web textures, everything bpy-scripted per the
user's own-build rule) with inverted-hull outlines: each visible mesh
gets a slightly larger (×1.04) backfacing copy in near-black
(`#1a1a1a`), which reads as a dark outline rim. See `PROOF_NOTES.md`
for the full technique and the bugs found during the proof (coplanar
tops, walk leg-reach, outline scale) — none of them were reintroduced.

Characters: 3 leads (A teal vest + straw hat, B ochre shirt, C green
dress + scarf) + 6 supporting family (B-wife, B-elder with walking
stick, C-husband, C-youth, A-wife, A-hand), all built by
`scripts/characters.py::build_farmer()` with the same builder and
outlines. Chickens: one shared pool of 28 birds (hero hen, 3 group
hens, 3 roosters, 4 chicks, 4 young hens, 13 extra hens), built once
by `build_all.py` and shared across shots; each shot only keyframes
what it shows.

Village: built ONCE by `shot06.build_village()` and shared — ground,
3 houses (ochre west, green centre, teal east), market stall, coop,
windmill, fences, trees, nests, sacks, crates, flower patches, plus
foreground dressing (see below).

## Timing

All timing comes from `assets/words.json` (copy of
`~/workspace/chicken_short/voice/words.json`, 256 words) — never
re-timed by feel. Verified word frames: "chicken" (shot 1) f122;
"gone" f309; "chicken" (gift) f483; "cook" f559; "best dinner" f622;
"last" f666; "eggs" f853; "rooster" f888; "together" f1098; "hatch"
f1350; "laying" f1427; "complain" f1711; "work" f2020, "paid" f2029,
"eggs" f2042–2055. Last word ends 75.75s = f2272.

Voice: Warm Pebble (avocado_v2:chip, speed 112), 75.984s.
Mix: `assets/mix.wav` (copy of `~/workspace/chicken_short_v3/audio/mix.wav`).

## Decisions

- **Hard cuts, no in-Blender crossfades.** The v3 timeline's 8-frame
  xfades are dropped in favour of hard cuts (the brief's own rule is
  hard cuts for story changes). 14 cameras bound to timeline markers
  at each shot's start frame (shot 7 has a second marker at f1246).
- **No fade-in/out baked into the scene.** Fade-in (f0–14) and
  fade-out (f2265–2279) are applied in ffmpeg at assembly.
- **No captions/text on screen.** (The channel's word-by-word captions
  are a separate overlay step, not part of this .blend.)
- **Hero-hen exception to the flock table.** Shot 1's visual explicitly
  requires the hero hen at the village heart (macro CU f122), so she
  exists ONLY in shot 1 (visible f0–149). The flock table's "no
  chickens before f483" applies to the group yards.
- **Visibility = root scale** (0.001 = hidden), never `hide_render`
  (hiding a parent empty does not hide children in a render). Always
  key BOTH sides of a visibility change. All chicken/egg visibility
  lives centrally in `build_all.py::schedule_flock()`; shots only
  place birds.
- **Characters may teleport between shots** (hard cuts hide 1-frame
  interpolation). Within a shot, every placed character gets a `hold`
  at both ends so nothing drifts.
- **Lighting keyframed per shot** at each shot's first AND last frame,
  so light holds steady inside a shot and only changes across the
  1-frame cut. Golden shots: 4, 9, 11, 13. DAY: sun 3.0,
  (1.0,0.96,0.88), loc (12,14,18), fill 0.35, world #8ab8e8 @0.9.
  GOLDEN: sun 2.6, (1.0,0.72,0.45), loc (16,10,9), fill 0.22, world
  #f0b070 @0.75.

## Per-shot notes

1. **0–150, day.** Drone wide → push to the hero hen; macro CU on
   "chicken" (f122) from the EAST so C's legs aren't behind the hen.
   Hero hen yaw −15° (profile to the east camera).
2. **150–330, day.** High wide, slow push. Coin piles, sacks and field
   crops scale away across "Gone" (f309–324); houses STAY standing;
   villagers' hands to faces.
3. **330–510, day.** Low dolly that LINGERS ~35f on each yard and
   moves quickly between them (the first version dollied at constant
   speed and spent a full second on the empty gap between yards).
   On "chicken" (f483) each lead receives one identical hen (scale-in
   over ~6f, arms open). Dolly ends on A.
4. **510–708, GOLDEN.** Group 1 around the cooking pot. B stirs with
   his RIGHT arm (camera-side when facing NW toward the pot), turns
   toward camera at f659–680 for the rueful beat. Pot macro CU with
   steam on "Best dinner" (f622). Hen gone from the yard.
5. **708–954, day.** Group 2 with hen + rooster. Nest macro CU with
   eggs on "eggs" (f853) from the south-east so no legs intrude;
   C reaches with her LEFT arm. Rooster head-high on "rooster" (f888).
6. **954–1161, day.** PROVEN in Milestone 1 (shot06.py reused, adapted
   to the master build). A walks to the stall, handshake f1098.
   Hand gap at f1098: 0.13 m (hands meet on screen).
7. **1161–1302, day.** Symmetrical comparison, HARD CUT at f1246:
   green yard + egg basket (C shows eggs — an egg is parented to her
   raised right hand) / teal yard + flock (A presents chickens).
8. **1302–1476, day.** Nest macro CU due south (background is the
   empty yard/fence — the rooster and hay bale stay out of frame);
   4 chicks scale in INSIDE the nest rim on "hatch" (f1350); G3
   clutch eggs hatch away 4→0 across f1350–1380; 24f pull-back at
   f1427–1450 then HOLD to f1475 (the first build's 48f pull-back
   never settled before the shot ended). Young hens laying; C and A
   react.
9. **1476–1572, GOLDEN.** Time-lapse: teal yard fills with hens
   (flock 6→18, one per ~10f from f1512), grain pours, G3 house
   extension scales in. Camera drifts east at the end to show the
   extension.
10. **1572–1750, day.** Slow dolly-back on the EMPTY ochre yard (no
    hens, empty pot, empty pouch CU); B throws arms up on "complain"
    (f1711), head shaking. B-elder has his walking stick from here on.
11. **1750–1854, GOLDEN.** Group 2 relaxed; C's hand rests on the full
    egg basket (the basket sits on a 0.7 m crate so its rim is at her
    hanging-hand height); hens pecking calmly; slow dolly-out.
12. **1854–2070, day.** Wide teal yard overflowing with hens; B stands
    among the flock (hired help); handover MS — basket of pay-eggs
    between A and B on "work paid in eggs" (f2019–2054). A offers
    with BOTH hands (his right arm alone is on the far side from the
    camera when he faces west).
13. **2070–2280, GOLDEN.** Crane-out over all three yards in one
    frame: poor (empty, ochre, bowed) / middle (eggs, green, content)
    / rich (flock, teal, presenting).

## Flock schedule (verified by `scripts/audit_flock.py`)

FLOCK AUDIT: PASS at all 15 check frames — f100: 1 hero; f300: 0;
f490: 5; f550: 5; f600: 4; f1000: 4; f1200: 4 + G3 eggs 4; f1360: 8 +
G3 eggs 3; f1400: 8 + G3 eggs 0; f1450: 8 + G3 new eggs 3; f1520: 9;
f1571: 15; f1700/1900/2200: 22. All 14 markers bound to the correct
cameras. Foot audit: min foot-origin z 0.025 m (sole ~0.000 —
planted); the walk code is the proof's verified code, unchanged.

## Bugs found and fixed during validation

- **Yaw drift across shots (critical).** `common.hold()` keyed only
  root LOCATION, not rotation, so a character's yaw interpolated from
  one shot's value to the next across the whole intervening shot. At
  f1098 A's yaw had drifted 90°→~50° and C's −90°→~−34°, so the
  handshake hands missed by 0.56 m and A walked sideways in shot 6.
  Fix: `hold()` now keyframes root rotation at both ends too; shot 6
  keys A's root rotation at f1160.
- **Walk arm-swing keys interleaved with handshake keys.** Shot 6's
  walk keys A's right shoulder/elbow to 0 at f1088–1098, interleaved
  with the handshake raise keys — the arm would flick down during the
  raise. Fix: `common.clear_keys_range()` deletes the walk's keys in
  f1088–1098 before the handshake keys are applied. (This interleaving
  exists in the proof code too; only f1098 was rendered there so it
  was invisible.)
- **Catmull-Rom camera overshoot.** `build_shot_camera()` samples a
  CR spline every 3f; a fast camera move after a hold pulls the camera
  off its hold position (shot 12's handover MS cut A off; shot 8's CU
  drifted 0.2 m during the hatch beat). Fix: gentler key spacing,
  plus duplicate hold keys (shot 8's f1400 key) to flatten the spline
  through a beat.
- **Foreground dressing geometry.** For a high camera looking down,
  the bottom edge of the 9:16 frame shows ground ~8 m north of the
  camera — trees at y 9–12 fall BELOW the bottom edge, and bushes
  wider than ~5 m fall outside the frame sides. The foreground
  dressing sits at y 5–8, x ±2–5 (in the lower frame); yard-edge
  bushes at y −1..0.
- **Chicks outside the macro CU.** The first chick spots (on the nest
  rim, 0.6 m spread) put 3 of 4 chicks outside the CU's 0.5 m frame
  (verified numerically with `world_to_camera_view`). Chicks now hatch
  inside the rim (0.3 m spread).
- **Frame left/right.** For a north-facing camera in Blender, EAST
  appears LEFT and WEST appears RIGHT in the render (camera local +X
  points west). Several placements were reasoned backwards from this
  before the chick diagnostic pinned it down.
- **Foreground bush hid A in the handshake.** BushFG2 at (6,-1.5)
  stood in shot 6's sightline: a 0.35-scale bush 2.7 m from the camera
  reads as big as a man 2.9 m away, and it covered A's whole body in
  the f1098 Cycles still (the Workbench f1098 from the earlier build
  had no bush there, so it was only caught by the colour check).
  Fix: moved to (3.5,-0.5), clear of the stall sightline. Lesson:
  re-render the key frames of EVERY shot after moving dressing, not
  just the shots the dressing was meant for.
- **A-wife/A-hand interpolating through shot 8.** A-wife drifted
  through the pull-back frame (she dominated the f1450 still).
  Fix: park off-frame characters explicitly in every shot they don't
  appear in (they teleport across the hard cut, invisibly).

## Validation stills

`out/stills/all/` — Workbench stills (540x960) at 2–3 key frames per
shot, inspected by reading the image files. Frames: 0, 90, 122, 200,
320, 400, 490, 560, 622, 680, 800, 853, 895, 1030, 1098, 1200, 1270,
1355, 1360, 1450, 1460, 1500, 1560, 1571, 1600, 1720, 1800, 1900,
2030, 2100, 2270. Plus 1 Cycles CPU colour-check still per shot
(16 samples + denoise) in `out/stills/cycles/`.

Per-shot verdicts (final build, all Workbench + Cycles stills inspected):

1. **Reads well.** Drone wide over the village (foreground trees frame
   the bottom); macro CU of the hero hen at f122 is clean — no legs
   behind her. Cycles: hen's white/brown/orange colours + outline
   rims read beautifully.
2. **Reads well.** High wide, coin piles visible then vanished on
   "Gone"; houses stand; hands to faces read. Foreground trees frame
   the bottom.
3. **Reads well.** Dolly lingers on each yard (C family at f400, bowed
   heads); gift at f490 — A arms open, hen + rooster read. Cycles:
   outfit colours (teal/cream/ochre) clean, rooster's green tail +
   red comb read.
4. **Reads well.** B stirs with his right arm, family clustered around
   the pot; pot CU at f622 with glowing flames + steam. Cycles:
   golden-hour light reads clearly (warm orange cast).
5. **Reads well.** Nest CU at f853 clean (nest + 3 eggs, no legs);
   rooster head-high at f895.
6. **Reads well.** A walks facing west (yaw fix verified); handshake
   at f1098 lands — hands meet mid-frame (gap 0.13 m). NOTE: the
   final build moved a foreground bush that had hidden A in the
   handshake frame; re-verified after the move.
7. **Reads well.** C holds an egg up in her raised hand (f1200);
   basket on the crate in frame; teal half symmetrical with A
   presenting.
8. **Reads well.** Hatch CU at f1360 — all 4 yellow chicks visible in
   the nest with 2 eggs + 1 half-hatched; pull-back at f1460 holds
   with A presenting, C in frame, young hens laying, nest at the
   edge.
9. **Reads well.** Flock fills the yard (7+ hens at f1560, 15 by
   f1571); grain pile + A-wife/A-hand read; golden light. The house
   extension is NOT a distinct read (see Known limits) — the flock
   growth carries the shot.
10. **Reads well.** Empty ochre yard, B arms thrown up at f1720,
    B-elder with grey hair + walking stick, B-wife bowed, flat empty
    pouch foreground, empty pot visible, no hens.
11. **Reads well.** C's hand rests on the full egg basket on the crate
    (f1800); golden light; hens pecking calmly.
12. **Reads well.** Wide teal yard overflowing (B in frame at the
    right edge); handover MS at f2030 — A and B both fully in frame,
    pay basket centered between them.
13. **Reads well.** Crane-out over all three yards in one frame:
    poor (empty, ochre, bowed) / middle (eggs, green, content) /
    rich (flock, teal, presenting). Foreground trees frame the
    bottom; outer houses partially cropped at the edges (see Known
    limits).

No shot is broken. The two weakest reads are shot 9's house extension
(background detail, not distinct) and shot 13's edge-cropped outer
houses (unavoidable in 9:16 without extreme wide-angle distortion).

## Measured timings (this VM, 2026-11-12)

- `build_all.py`: ~160s (shot 2 takes ~22s — wealth props via bpy.ops;
  other shots 0–2s).
- Workbench stills: 1.4–4.4s each when the VM is idle; up to ~90s each
  under contention (a 7-still batch took 12 min on a loaded VM).
- Cycles CPU colour checks (540x960, 16 samples + denoise): ~30s each.
- `audit_flock.py`: ~40s (mostly .blend load).

## Colab render — what to watch for

- **Eevee was never validated locally (no GPU).** Materials are
  Principled BSDF only, but the inverted-hull outlines (backfacing +
  transparent mix) and the emissive window/flame materials have only
  been rendered in Cycles and Workbench. **Render one Eevee test
  frame per shot on the Colab GPU before the full render** and check:
  outlines read as dark rims (not black shells), windows glow,
  flames glow, no missing/black objects. If Eevee shows black shells
  around characters, set the outline material's `blend_method` to
  'HASHED' or 'BLEND'.
- **Render in shards** (the plan is 4 frame shards) and save frames to
  Drive per shard — Colab sessions reset/disconnect.
- **Fade-in/out in ffmpeg at assembly** (not in the scene).
- **Captions are a separate overlay step** (not in this .blend).
- Scene weight: 175k polys, 1751 objects — light for a T4. If the
  Colab render is slow, simplify dressing before cutting characters.
- The windmill rotor spins f0–2279 (0→60 rad); the rotor is a single
  object with rotation keys — no per-frame Python needed at render.

## Known limits

- Hen legs are static during walks (the hen walk bobs the body and
  yaws the root; legs don't step). At 540p and the distances used,
  this doesn't read as wrong.
- Faces look dark in Workbench stills (Workbench STUDIO lighting
  ignores scene lights). Cycles colour checks confirm the real look.
- The outer houses (G1/G3) are partially cut at the edges of the
  widest wides (shots 1, 2, 13) — a 24 m-wide village can't fit a
  9:16 frame without extreme wide-angle distortion. All three yards
  and all three groups are in frame; only the houses' outer walls
  are cropped.
- The G3 house extension is a background detail in shot 9 (visible at
  the left edge of the end frame, partially behind the coop from some
  angles) — the flock growth is the shot's main read.
- The crate under the G2 egg basket is a plain cube (stylised
  dressing, no slat detail).
- Steam puffs are opaque pale spheres (stylised cartoon steam, not
  volumetrics — volumetrics would be too heavy for the Colab render).

## Files

- `scripts/characters.py` — farmers, chickens, walks, gestures.
- `scripts/village.py` — ground, houses, coop, stall, trees, props.
- `scripts/common.py` — shot helpers (place/hold/arms/camera paths).
- `scripts/shot01.py` … `scripts/shot13.py` — one `build(ctx)` each.
- `scripts/build_all.py` — master build; saves
  `scenes/chicken_blender.blend`.
- `scripts/render_stills.py` — still renderer (`--engine workbench |
  cycles`, `--frames`, `--out`, `--res`).
- `scripts/audit_flock.py` — flock counts, marker/camera check, foot
  audit.
- `scenes/chicken_blender.blend` — the deliverable.
  (`scenes/proof_shot06.blend` is the Milestone 1 proof — untouched.)
- `assets/words.json`, `assets/mix.wav` — timing + sound mix.
- `PROOF_NOTES.md` — Milestone 1 technique + bugs.
- `README.md` — build/run instructions.

## Rebuild

```
./tools/blender-4.2.23-linux-x64/blender --background --python scripts/build_all.py
./tools/blender-4.2.23-linux-x64/blender --background --python scripts/audit_flock.py
```
