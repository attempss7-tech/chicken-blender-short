# build_all.py — master build for the FULL Blender chicken short (Milestone 2).
#
# Builds all 13 shots in ONE scene on ONE 2280-frame timeline, with the
# village built once and shared, 13 marker-bound cameras (shot 7 has two
# setups, so 14 cameras / 14 markers), day/golden lighting keyframed per
# shot, and the flock table enforced centrally (see schedule_flock).
# Saves scenes/chicken_blender.blend (BLENDER_EEVEE_NEXT, 1080x1920,
# 30 fps, frames 0-2279).
#
# Run from ~/workspace/blender_chicken:
#   ./tools/blender-4.2.23-linux-x64/blender --background \
#       --python scripts/build_all.py
import os
import sys
import time

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import characters as ch  # noqa: E402
import common as cm  # noqa: E402
import village as vil  # noqa: E402
import shot01, shot02, shot03, shot04, shot05  # noqa: E402
import shot06, shot07, shot08, shot09, shot10  # noqa: E402
import shot11, shot12, shot13  # noqa: E402

SHOTS = [shot01, shot02, shot03, shot04, shot05, shot06, shot07,
         shot08, shot09, shot10, shot11, shot12, shot13]

# 18 fixed spots for the teal-yard flock (hen_g3 + 4 young + 13 extra),
# shared by shots 9/12/13. Kept clear of the coop (11.5,-6), stall
# (5.5,-3), fences (y=-5.5) and the grain pile (7.85,-4.8).
FLOCK_SPOTS = [
    (6.6, -2.0), (7.2, -3.2), (7.8, -2.1), (8.3, -4.0),
    (8.8, -2.4), (9.2, -3.6), (9.7, -2.0), (10.1, -4.4),
    (10.6, -2.7), (11.0, -3.8), (11.4, -2.2), (6.9, -4.6),
    (7.0, -5.1), (8.8, -5.1), (9.5, -4.8), (10.4, -5.0),
    (11.2, -4.9), (11.6, -3.1),
]

# farmer home positions (build-time defaults; shots re-place as needed)
FARMER_HOME = {
    "A": ((9, -3), 0), "B": ((-9, -3), 0), "C": ((0, -3), 0),
    "Bwife": ((-9.9, -3.6), 0), "Belder": ((-8.1, -3.7), 0),
    "Chusband": ((0.9, -3.6), 0), "Cyouth": ((-0.9, -3.5), 0),
    "Awife": ((9.9, -3.6), 0), "Ahand": ((8.1, -3.7), 0),
}

CHICK_SPOTS = [(10.72, -1.8), (11.28, -1.8), (10.7, -1.3), (11.3, -1.3)]
YOUNG_SPOTS = [(10.4, -2.6), (11.6, -2.4), (10.8, -3.4), (9.9, -2.2)]


def build_shared_props():
    """Props shared across shots (nests, pot, basket, house extension)."""
    # G3 nest with the clutch of 4 + 3 "new" eggs for after the laying
    nest_g3, eggs_g3 = vil.nest("NestG3", (11, -1.8, 0), eggs=4)
    new_eggs = []
    for i, (dx, dy) in enumerate(((-0.09, 0.0), (0.09, 0.03),
                                  (0.0, -0.08))):
        new_eggs.append(vil.egg("NestG3_newegg%d" % i, (dx, dy, 0.09),
                                parent=nest_g3))
    # G2 nest was built by shot06.build_village(); fetch its eggs by name
    nest_g2 = bpy.data.objects["NestG2"]
    eggs_g2 = [bpy.data.objects["NestG2_egg%d" % i] for i in range(3)]
    # G2 yard egg basket (shots 7/11/13) — on a 0.7 m crate so its rim
    # is at C's hanging-hand height for the "hand on the basket" beat
    vil.crate("CrateBasketG2", (1.0, -1.0, 0), size=0.7)
    basket_g2 = vil.basket("BasketG2Yard", (1.0, -1.0, 0.7), eggs=4)
    # G1 cooking pot (shot 4 lit, shot 10 cold and empty)
    pot = vil.cooking_pot("PotG1", (-10, -3.8, 0))
    # G3 house extension (appears in shot 9's time-lapse; hidden until
    # then — the group empty is scale-keyed, children ride along)
    ext = ch.new_empty("HouseG3Ext", loc=(12.7, -9, 0))
    ch.add_box("HouseG3Ext_walls", (2.4, 3.6, 2.4),
               ch.flat_mat("wall_HouseG3", "#ece0c8"), parent=ext,
               loc=(0, 0, 1.2))
    roof = ch.add_box("HouseG3Ext_roof", (2.8, 4.0, 0.15),
                      ch.flat_mat("roof_HouseG3", "#b85c38"), parent=ext,
                      loc=(0, 0, 2.55))
    roof.rotation_euler = (0, -0.3, 0)
    ch.add_box("HouseG3Ext_win", (0.7, 0.08, 0.7),
               ch.flat_mat("trim_HouseG3", "#3a7a72"), parent=ext,
               loc=(0, 1.82, 1.4))
    ch.add_box("HouseG3Ext_glass", (0.5, 0.1, 0.5),
               ch.flat_mat("window_glass", "#ffd98a"), parent=ext,
               loc=(0, 1.83, 1.4))
    cm.scale_at(ext, 0, cm.HIDDEN)
    return dict(nests={"g2": (nest_g2, eggs_g2),
                       "g3": (nest_g3, eggs_g3, new_eggs)},
                basket_g2=basket_g2, pot=pot, extension=[ext])


def _loc3(p):
    return (p[0], p[1], 0)


def build_characters():
    chars = {}
    for key, (pos, yaw) in FARMER_HOME.items():
        chars[key] = ch.build_farmer(key, "Farmer" + key, loc=_loc3(pos),
                                     yaw_deg=yaw)
    birds = {}
    birds["hero"] = ch.build_chicken("hen", "HeroHen", loc=(0, -1, 0),
                                     yaw_deg=30)
    birds["hen_g1"] = ch.build_chicken("hen", "HenG1", loc=(-9, -2.2, 0),
                                       yaw_deg=15)
    birds["hen_g2"] = ch.build_chicken("hen", "HenG2b", loc=(0, -2.2, 0),
                                       yaw_deg=-10)
    birds["rooster_g2"] = ch.build_chicken("rooster", "RoosterG2",
                                           loc=(0.8, -2.5, 0), yaw_deg=-35)
    birds["hen_g3"] = ch.build_chicken("hen", "HenG3b",
                                       loc=_loc3(FLOCK_SPOTS[0]),
                                       yaw_deg=20)
    birds["rooster_g3"] = ch.build_chicken("rooster", "RoosterG3",
                                           loc=(8.0, -2.8, 0),
                                           yaw_deg=-20)
    birds["rooster_g3b"] = ch.build_chicken("rooster", "RoosterG3b",
                                            loc=(10.8, -3.3, 0),
                                            yaw_deg=25)
    birds["chicks"] = [
        ch.build_chicken("chick", "Chick%d" % i, loc=_loc3(CHICK_SPOTS[i]),
                         yaw_deg=-20 + i * 15) for i in range(4)]
    birds["young"] = [
        ch.build_chicken("hen", "YoungHen%d" % i, loc=_loc3(YOUNG_SPOTS[i]),
                         yaw_deg=-25 + i * 18) for i in range(4)]
    birds["extra"] = [
        ch.build_chicken("hen", "FlockHen%02d" % i,
                         loc=_loc3(FLOCK_SPOTS[5 + i]),
                         yaw_deg=-30 + ((5 + i) * 37) % 60)
        for i in range(13)]
    return chars, birds


def schedule_flock(ctx):
    """Central flock-table enforcement (SHOT_TIMELINE.md `flockAt`).

    ALL chicken/egg visibility lives here — shots only place birds.
    Visibility is root scale (0.001 = hidden). Key beats, all from
    words.json: gift f483, "cook" f559, hatch f1350, laying f1427,
    flock growth from f1512 (one per ~10f).
    """
    birds = ctx["chickens"]
    # hero hen: shot 1 only (the symbol; gone by shot 2)
    cm.visible_span(birds["hero"]["root"], 0, 149)
    # G1: 1 hen f483-558, then 0 forever (taken to the pot f551-557)
    cm.visible_span(birds["hen_g1"]["root"], 483, 557, fade_in=6,
                    fade_out=6)
    # G2/G3: 1 hen + 1 rooster from the gift, forever
    for key in ("hen_g2", "rooster_g2", "hen_g3", "rooster_g3"):
        cm.visible_span(birds[key]["root"], 483, 2279, fade_in=6)
    # G3 chicks: scale in staggered over the hatch beat, gone at f1427
    for i, chick in enumerate(birds["chicks"]):
        cm.visible_span(chick["root"], 1350 + i * 2, 1426, fade_in=6)
    # young hens (smaller, scale 0.75) from the pull-back, forever
    for hen in birds["young"]:
        cm.visible_span(hen["root"], 1427, 2279, base=0.75, fade_in=6)
    # flock growth: 6 -> 18 hens, one per ~10f from f1512
    for i, hen in enumerate(birds["extra"]):
        cm.visible_span(hen["root"], 1512 + i * 10, 2279, fade_in=8)
    # G3's second rooster joins during the time-lapse
    cm.visible_span(birds["rooster_g3b"]["root"], 1560, 2279, fade_in=8)

    # ---- eggs
    # G2 nest: always 3 after the gift
    for egg in ctx["nests"]["g2"][1]:
        cm.visible_span(egg, 483, 2279)
    # G3 clutch of 4: visible from shot 7, hatches away egg by egg
    # across f1350-1380 (one every ~8f)
    for i, egg in enumerate(ctx["nests"]["g3"][1]):
        cm.scale_at(egg, 1160, cm.HIDDEN)
        cm.scale_at(egg, 1161, 1.0)
        cm.scale_at(egg, 1350 + i * 8, 1.0)
        cm.scale_at(egg, 1354 + i * 8, cm.HIDDEN)
    # G3's 3 new eggs after the young hens start laying
    for egg in ctx["nests"]["g3"][2]:
        cm.visible_span(egg, 1440, 2279, fade_in=10)
    # basket eggs (stall, ground, G2 yard): none before the gift
    for obj in bpy.data.objects:
        if "_egg" in obj.name and obj.name.startswith(
                ("Stall_basket", "BasketGround", "BasketG2Yard")):
            cm.visible_span(obj, 483, 2279)

    # ---- B-elder's walking stick appears in the late shots (from f1572)
    cm.visible_span(ctx["chars"]["Belder"]["stick"], 1572, 2279)


def key_lighting(sun, fill, world, frame, preset):
    """Keyframe the full lighting state (sun, fill, world) at one frame."""
    p = cm.LIGHTING[preset]
    sun.location = p["sun_loc"]
    sun.rotation_euler = (Vector((0, -3, 0)) - Vector(p["sun_loc"])
                          ).to_track_quat("-Z", "Y").to_euler()
    ch.kf(sun, frame, "location")
    ch.kf(sun, frame)
    sun.data.energy = p["sun_energy"]
    sun.data.keyframe_insert(data_path="energy", frame=frame)
    sun.data.color = p["sun_color"]
    sun.data.keyframe_insert(data_path="color", frame=frame)
    fill.data.energy = p["fill_energy"]
    fill.data.keyframe_insert(data_path="energy", frame=frame)
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*ch.hx(p["world_color"]), 1.0)
    bg.inputs["Color"].keyframe_insert(data_path="default_value",
                                       frame=frame)
    bg.inputs["Strength"].default_value = p["world_strength"]
    bg.inputs["Strength"].keyframe_insert(data_path="default_value",
                                          frame=frame)


def main():
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # ---- village + lights, built ONCE and shared by all 13 shots
    rotor = shot06.build_village()
    sun, fill = shot06.build_lights()
    world = bpy.context.scene.world
    # foreground dressing for the south grass (y 2..10): the first build's
    # high wides (shots 1/2/13) showed 35-40% empty grass at the bottom
    # of the 9:16 frame. GEOMETRY NOTE: for a high camera looking down,
    # the bottom edge of the frame shows ground ~8 m north of the camera
    # — objects closer than that (y 9-12) fall BELOW the bottom edge, and
    # objects wider than ~5 m fall outside the frame sides. So the
    # foreground dressing sits at y 5-8, x +/-2-5 (in the lower frame),
    # and the yard-edge bushes at y -1..0 (visible in the dolly shots).
    vil.tree("TreeFG2", (-14, 7, 0), scale=0.9, leaf="#6a9a4a")
    vil.tree("TreeFG3", (14, 6, 0), scale=1.0)
    vil.tree("TreeFG4", (-9, 9, 0), scale=0.8, leaf="#5a8a3e")
    vil.tree("TreeFG5", (10, 10, 0), scale=0.9, leaf="#6a9a4a")
    vil.tree("TreeFG6", (4.5, 6.5, 0), scale=0.8, leaf="#5a8a3e")
    vil.tree("TreeFG7", (-4.5, 7, 0), scale=0.75, leaf="#6a9a4a")
    vil.tree("BushFG1", (-6, -1, 0), scale=0.3, leaf="#5a8a3e")
    # BushFG2 sits at (3.5,-0.5), NOT near the stall: at (6,-1.5) it stood
    # in shot 6's sightline and hid A behind its canopy in the f1098
    # handshake frame (a 0.35-scale bush 2.7 m from the camera reads as
    # big as a man 2.9 m away)
    vil.tree("BushFG2", (3.5, -0.5, 0), scale=0.35, leaf="#6a9a4a")
    vil.tree("BushFG3", (-12, -2, 0), scale=0.3, leaf="#4a7a34")
    vil.tree("BushFG4", (13, -2, 0), scale=0.3, leaf="#5a8a3e")
    vil.tree("BushFG5", (2.5, 5.5, 0), scale=0.4, leaf="#5a8a3e")
    vil.tree("BushFG6", (-2.5, 6, 0), scale=0.35, leaf="#6a9a4a")
    vil.flower_patch("FlowersFG1", (-3, 6, 0), count=6)
    vil.flower_patch("FlowersFG2", (3, 5.5, 0), count=6)

    props = build_shared_props()
    chars, birds = build_characters()

    ctx = dict(chars=chars, chickens=birds, rotor=rotor, sun=sun,
               fill=fill, world=world, flock_spots=FLOCK_SPOTS, **props)

    schedule_flock(ctx)

    # ---- windmill rotor: slow spin across the whole timeline
    rotor.rotation_euler = (0, 0, 0)
    ch.kf(rotor, 0)
    rotor.rotation_euler = (0, 60, 0)
    ch.kf(rotor, 2279)
    ch.set_linear(rotor)

    # ---- lighting: key each shot's preset at its first AND last frame
    # so the light holds steady inside a shot and only changes across
    # the 1-frame hard cut between shots
    for _num, start, end, preset in cm.SHOTS:
        key_lighting(sun, fill, world, start, preset)
        key_lighting(sun, fill, world, end - 1, preset)

    # ---- the 13 shots, in timeline order
    cameras = []  # (marker frame, camera object)
    for i, mod in enumerate(SHOTS, start=1):
        ts = time.time()
        info = mod.build(ctx)
        cameras.extend(info["cameras"])
        print("  shot %02d built in %.1fs" % (i, time.time() - ts))

    # ---- markers + camera binding (hard cuts)
    scene = bpy.context.scene
    for frame, cam in sorted(cameras):
        m = scene.timeline_markers.new(name="Shot_%04d" % frame,
                                       frame=frame)
        m.camera = cam
    scene.camera = sorted(cameras)[0][1]

    # ---- scene settings (final: 1080x1920, 30 fps, Eevee on Colab GPU)
    scene.frame_start = 0
    scene.frame_end = 2279
    scene.render.fps = 30
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.normpath(os.path.join(here, "..", "scenes",
                                        "chicken_blender.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=out)

    n_mesh = sum(1 for o in scene.objects if o.type == "MESH")
    n_all = len(scene.objects)
    n_poly = sum(len(o.data.polygons) for o in scene.objects
                 if o.type == "MESH")
    n_actions = len(bpy.data.actions)
    print("BUILD ALL OK in %.1fs: %d objects (%d meshes), %d polys, "
          "%d actions, %d cameras, frames 0-2279"
          % (time.time() - t0, n_all, n_mesh, n_poly, n_actions,
             len(cameras)))
    print("saved:", out)


if __name__ == "__main__":
    main()
