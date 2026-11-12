# Proof Notes — Milestone 1 (Shot 6, Blender chicken short)

**Status: PROVEN.** Technique 1 (flat-shaded 3D primitive characters with
inverted-hull outlines) works end to end. Shot 6 is built, animated, and
validated with stills in both Workbench (geometry/framing) and Cycles CPU
(colour/material). The full build should proceed on this technique.

## Deliverables (all under `~/workspace/blender_chicken/`)

- `scripts/characters.py` — farmer/chicken builders + animation helpers
  (IK walk, arm/head keys, breathing, peck cycle). Bible colours are
  constants (`FARMERS`, `CHICKENS`); heights/builds parametrised.
- `scripts/village.py` — ground, house, coop, stall, tree, fence, windmill,
  basket/egg/crate/sack/hay/flower props, hills + clouds.
- `scripts/shot06.py` — Shot 6 assembly: village, characters, lights,
  Catmull-Rom camera path + tracking focus, all animation, frames 954–1161.
- `scripts/build_proof.py` — master script; saves `scenes/proof_shot06.blend`.
- `scripts/render_stills.py` — validation stills (Workbench or Cycles).
- `scenes/proof_shot06.blend` — the built proof shot (Eevee set as engine).
- `out/stills/proof/` — validation stills (see Verdicts below).

## Technique chosen: 1 — flat-shaded primitives + inverted-hull outlines

**Why:** it is fully scriptable (no GUI modelling), robust in headless
Blender, Eevee-compatible (Principled BSDF only), and fast (49k polys for
the whole shot). Techniques 2 (textured cards) and 3 (Grease Pencil) were
not needed — technique 1 reads clearly as the brief's "2D illustrated
characters in a 3D village" once the outlines, flat colours, and
proportions are right. The stills below are the evidence.

**Outlines:** each part gets a duplicate shell mesh offset 9 mm along
vertex normals with flipped normals, parented to the part (so it follows
animation), in a dark-plum `#241726` material that mixes Principled with
Transparent via the Geometry node's Backfacing output, plus backface
culling. This renders the same rim in Cycles and Eevee/Workbench.
Outline shells cast no shadow (`visible_shadow = False`).
**Eevee caveat (must verify on Colab):** the outline material was validated
in Cycles + Workbench only. Eevee was never run locally (no GPU). The
backface-culling path should make the Transparent branch irrelevant in
Eevee, but the full build MUST render one Eevee test frame per shot on
Colab before the full render and check the rims. If Eevee shows black
shells, set the outline material's `blend_method` to `'HASHED'`/`'BLEND'`.

## What worked

- **Characters read clearly** with correct bible colours: A (straw hat,
  teal vest, cream shirt, dark trousers), B (ochre shirt, moustache), C
  (rust headscarf, green tunic, cream trousers). Heights differ visibly
  (A 1.78 > B 1.72 > C 1.66). Hen/rooster read (white-cream body, brown
  wing, red comb; rooster rust neck + green tail + big comb).
- **Planted-feet walk (verified numerically):** analytic 2-bone IK, stance
  feet fixed in world space. Foot-position audit at every 4th frame
  f1015–1098 shows stance feet EXACTLY still (0 cm slide, soles at
  z ≈ 0.00) and correct 0.375 m step spacing. Swing feet lift 9 cm with
  toe droop mid-swing. See "Bug 2" for what it took to get there.
- **Handshake lands on f1098** ("together"): A's right arm + C's left arm
  (both camera side) extend and meet mid-frame; two shake oscillations,
  release by f1150.
- **Camera:** Catmull-Rom path sampled every 3 frames, Track-To focus
  empty that follows A then the handshake point; lens 22→35 mm push.
  No static framing; the f954→f1030 arc is smooth in the stills.
- **Village dressing:** 3 houses (group trim colours), 3 coops, striped
  market stall with egg baskets, oak + 6 trees, fences with a stall-path
  gap, windmill (blades rotate), hills, clouds, flowers, sacks, hay bale.
- **Lighting:** warm key sun (SE, 3.0) + cool fill (NW, 0.35, no shadow)
  + sky-blue world (0.9). Day, warm, soft grounding shadows.
- **Scene is light:** 569 objects, 469 meshes, 49,389 polys, 48,102
  verts, 56 actions. Build takes ~13 s including Blender startup.

## Stills — verdicts

All at 540x960. Workbench = geometry/framing; Cycles (16 samples +
OpenImageDenoise) = colour/material.

| frame | what it shows | verdict |
|---|---|---|
| f0954 | down-the-street wide, A starts walking | GOOD. Street recedes, houses + stall + windmill + oak read, B visible far down the street (small ochre figure, ~25 px — meets "visible"), hen near A, blue sky + cloud. Black ground band from v1 is gone. |
| f1030 | mid-tracking, A walking | GOOD. 3/4 front-side view, natural stride, front foot planted flat, back foot lifted with toe droop, arm swing, face visible, hen pecking beside him. House/coop/hay/fence behind. |
| f1098 | handshake on "together" | GOOD. Hands meet mid-frame, both full-length, feet planted, correct outfits, rooster (bottom-left) + hen (bottom-right) in frame, striped awning overhead, egg baskets on the counter. |
| f1161 | end frame | GOOD. Arms lowered after the handshake, both standing facing each other, push-in held, hens still visible. Resolved meeting. |
| f0985 | (bonus) A looks up on "idea" | GOOD. Head pitch reads (hat tilts back), C + B + hens + windmill blades (rotated) visible; camera arc smooth. |
| f1058 | (bonus) C's welcome gesture | GOOD. A mid-walk past the stall; rooster reads well (rust wing, green tail fan, red comb); hen pecking (head down — peck cycle works). C is off-frame here (west of the stall); her gesture is keyed and visible in the f1098 approach. |

## Measured render times (this VM, 4 CPU cores)

- Build (`build_proof.py`): **11.9–13.8 s** total incl. Blender startup.
- Workbench still, 540x960: **1.2–2.9 s** (first frame ~2.6 s, later ~1.2 s).
- Cycles CPU still, 540x960, 16 samples + denoise: **f954 22.8 s,
  f1030 31.3 s, f1098 33.3 s, f1161 32.7 s** (4-frame run ≈ 2 min incl.
  startup). First run was near-identical (24.4 / 31.0 / 35.3 / 33.3 s).
- Eevee on Colab GPU is unmeasured — expect ~1–3 s/frame at 1080x1920;
  measure on the first Colab test frame.

## Bugs found and fixed (full-build agent: do not reintroduce these)

1. **Coplanar box tops render BLACK in Cycles.** The dirt path (top
   z=0.02) and yard patches (top z=0.02) overlapped; the overlap strip
   rendered as a pure-black band (proven by raycast: the same yard-patch
   face was black at y=-2.77 inside the overlap, sunlit at y=-4.52
   outside it). Fix in `village.ground()`: path top 0.045, yard tops
   0.015 — never let two large flat tops share a height. Check any new
   ground-level boxes the same way.
2. **Walk IK leg-reach failure → sliding + lifting feet.** First version
   had the body start each step directly over the stance foot, so the
   stance leg had to reach a full step behind the hip — beyond the leg's
   length — and the IK clamp dragged the foot (3–5 cm slide, feet rising
   9 cm). Fixed in `animate_walk()`: steps are centred on the stance
   plant (max |fwd| = S/2), hips crouch 4 cm during the walk with the bob
   phased high mid-step / low at boundaries, step length clamped to the
   leg's actual reach (`s_max`, computed), bob scaled by the crouch
   ease-in. A's walk is 2.25 m in 71 frames (6 steps × 0.375 m,
   ~2.5 steps/s). **Rule for the full build:** do not ask for steps
   longer than ~0.40 m for these proportions — shorten the distance or
   lengthen the time instead. Re-run the foot audit
   (`/tmp/footcheck.py` pattern: sample foot world positions) after any
   walk change.
3. **Fill sun shadow toggle:** `Light.use_shadow` exists in 4.2 and is
   set False on the fill — verified by diagnostic (fill `use_shadow:
   False`, key sun direction (-0.44,-0.62,-0.65) as designed).
4. **Stall awning posts:** front posts must be shorter than back posts
   (2.15 vs 2.6) or the tilted awning floats through them.
5. **Sash/belt torus:** size from the torso's elliptical cross-section
   at belt height (`waist_ring()`), not a fixed radius — fixed radii
   floated like hula hoops.
6. **Chimney colour:** brick `#a85a44`, not the house trim colour (a
   teal chimney read as wrong).
7. **`read_factory_settings(use_empty=True)` creates no World** —
   `build_lights()` creates one if missing.

## Known limits / polish for the full build

- **Eevee never validated locally** (no GPU here). One Eevee test frame
  per shot on Colab before the full render; check outlines, the
  backfacing-transparent mix, and the emission windows.
- Outlines are subtle at 9 mm in Cycles (visible rim, not a heavy toon
  line). If the full build wants a stronger comic outline, raise
  `OUTLINE_THICKNESS` to 0.012 and re-check a still.
- Handshake arms are near-straight (shoulder 66°, elbow 14°) — reads
  clearly but slightly stiff; a little more elbow bend (25°) would look
  more natural.
- Faces pointing west (A in the handshake) sit in partial shade; consider
  fill 0.35 → 0.5 for close-ups, or a soft frontal fill in shot 7.
- The vest's front opening is only visible from the front — verify in a
  front-facing shot (shot 7's comparison will show it).
- Hens' heads blend into their bodies from directly behind (white on
  white); comb/beak read from the side. Acceptable at this scale.
- The stall awning's far end reads slightly floaty from the east-side
  wide; check in full-build wides, add an end post if it bothers.
- B is ~25 px tall in the f954 wide — visible as required, but small.
  Shot 10 is B's shot, so no action needed here.
- Clouds are simple merged spheres — fine as stylised clouds.
- No walk cycles for hens (they peck in place in shot 6); the full build
  needs a hen walk if any shot moves the flock (shots 9/12).
- Supporting family (A-wife, B-wife, etc. from the bible) are NOT built
  — only the three leads + chickens exist. The full build adds them via
  `build_farmer()` variants (new `FARMERS` entries) if a shot needs them.
- **No fade-in/out baked into the scene** (per brief — fades are applied
  in ffmpeg at assembly). Do not add them in Blender.

## Colab notebook dependency (for the coordinator)

The Colab notebook must install the same system libs this VM needed:
`apt-get install -y libegl1 libgl1 libegl-mesa0` (or at minimum
`libegl1 libgl1`). Without libEGL, Workbench/Eevee abort headless
(exit 134, "Couldn't open libEGL.so.1"). Verified on this VM: the
coordinator's message said apt had finished, but `ldconfig -p` showed
no libEGL and no apt history existed — I installed it myself
(apt took ~20 min through the egress proxy; libEGL present afterwards,
Workbench stills then ran in ~1–2 s). Colab's Ubuntu usually has most
GL libs, but install explicitly to be safe.

## Handoff notes for the full-build agent

- Reuse `characters.build_farmer()` / `build_chicken()` and
  `village.*` as-is; add shots as `shotNN.py` modules following
  `shot06.py` (one `build()` per shot). Build the village ONCE per
  .blend and reuse it across shots — do not rebuild it 13 times.
- Camera pattern: `CAM_KEYS` + Catmull-Rom sampling every 3 frames +
  Track-To focus empty. Keep cameras out of the y ≥ 0.5 south corridor
  clear of trees/props.
- Shot timing comes from `../chicken_short/voice/words.json` (256 words)
  and `../chicken_short_v3/SHOT_TIMELINE.md` — never re-time by feel.
- `render_stills.py --engine workbench` is the fast loop (1–3 s/frame);
  use Cycles for a final colour check per shot. Always inspect the
  stills by reading the image files — do not trust a clean exit code.
- The `.blend` is saved with engine `BLENDER_EEVEE_NEXT`, 1080x1920,
  30 fps. Stills scripts override engine/resolution per run.
