# audit_flock.py — mechanical verification of scenes/chicken_blender.blend.
#
# Opens the blend and checks, at a set of key frames:
#   * which chickens are visible (root scale > 0.5) and where they are
#   * nest egg counts (G2: 3 after f483; G3: 4 until the hatch, 0 during
#     f1380-1439, 3 new ones after f1440)
#   * marker -> camera binding (each marker frame's camera)
#   * A's walk feet (stance feet must not slide, soles at z ~ 0)
#
# Run from ~/workspace/blender_chicken:
#   ./tools/blender-4.2.23-linux-x64/blender --background \
#       --python scripts/audit_flock.py
import math
import os

import bpy
from mathutils import Vector

here = os.path.dirname(os.path.abspath(__file__))
proj = os.path.normpath(os.path.join(here, ".."))
bpy.ops.wm.open_mainfile(
    filepath=os.path.join(proj, "scenes", "chicken_blender.blend"))
scene = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

CHICKENS = (["HeroHen", "HenG1", "HenG2b", "RoosterG2", "HenG3b",
             "RoosterG3", "RoosterG3b"]
            + ["Chick%d" % i for i in range(4)]
            + ["YoungHen%d" % i for i in range(4)]
            + ["FlockHen%02d" % i for i in range(13)])
EGGS_G2 = ["NestG2_egg%d" % i for i in range(3)]
EGGS_G3 = ["NestG3_egg%d" % i for i in range(4)]
EGGS_G3_NEW = ["NestG3_newegg%d" % i for i in range(3)]

# expected visible-chicken counts per frame (from the flock table)
EXPECT = {
    100: 1,    # hero hen only
    300: 0,    # wealth taken, no chickens yet
    490: 5,    # G1 hen + G2 hen/rooster + G3 hen/rooster
    550: 5,    # G1 hen still there (vanishes f551-557)
    600: 4,    # G1 hen gone
    1000: 4,
    1200: 4,
    1360: 8,   # + 4 chicks
    1400: 8,
    1450: 8,   # 4 chicks -> 4 young hens (+ G2 pair + G3 pair)
    1520: 9,   # + 1 extra hen (f1512)
    1571: 15,  # + 7 extra hens (f1512..1562) + 2nd rooster (f1560)
    1700: 22,  # full flock: G2 pair + G3 18 hens + 2 roosters
    1900: 22,
    2200: 22,
}


def visible(name, frame):
    obj = bpy.data.objects.get(name)
    if obj is None:
        return None
    return obj.evaluated_get(dg).scale.x > 0.5


def eggs_visible(names):
    return sum(1 for n in names
               if bpy.data.objects[n].evaluated_get(dg).scale.x > 0.5)


print("== flock audit ==")
ok = True
for frame in sorted(EXPECT):
    scene.frame_set(frame)
    dg.update()
    vis = [n for n in CHICKENS if visible(n, frame)]
    n = len(vis)
    exp = EXPECT[frame]
    flag = "OK " if n == exp else "FAIL"
    if n != exp:
        ok = False
    print("f%04d %s visible=%2d expected=%2d | G2eggs=%d G3eggs=%d G3new=%d"
          % (frame, flag, n, exp, eggs_visible(EGGS_G2),
             eggs_visible(EGGS_G3), eggs_visible(EGGS_G3_NEW)))
    if n != exp:
        print("      visible:", ", ".join(vis))
print("FLOCK AUDIT:", "PASS" if ok else "FAIL")

print("== markers ==")
for m in sorted(scene.timeline_markers, key=lambda m: m.frame):
    print("  f%04d -> %s" % (m.frame, m.camera.name if m.camera else None))

print("== A walk foot audit (f1015-1098, every 4th frame) ==")
scene.frame_set(1015)
A_root = bpy.data.objects["FarmerA"]
foot_l = bpy.data.objects["FarmerA_footL"]
foot_r = bpy.data.objects["FarmerA_footR"]
prev = {}
max_slide = 0.0
min_z = 99.0
for f in range(1015, 1099, 4):
    scene.frame_set(f)
    dg.update()
    for name, foot in (("L", foot_l), ("R", foot_r)):
        w = foot.evaluated_get(dg).matrix_world.translation
        # foot mesh origin is ~2.5cm above the sole (loc z -0.025 in the
        # ankle frame, scaled sphere) — sole is ~w.z - 0.025
        min_z = min(min_z, w.z)
        if name in prev:
            d = (Vector((w.x, w.y)) - Vector(prev[name])).length
            # only stance feet should be still; swings move up to 0.4m
            # per 4 frames, so report the max *small* move as the slide
            # proxy: moves < 0.05m between samples while near the ground
            if w.z < 0.06 and d < 0.05:
                max_slide = max(max_slide, d)
        prev[name] = (w.x, w.y)
print("  min foot-origin z: %.3f m (sole ~ %.3f)" % (min_z, min_z - 0.025))
print("  max small-move near ground: %.3f m" % max_slide)

print("== scene stats ==")
n_mesh = sum(1 for o in scene.objects if o.type == "MESH")
n_poly = sum(len(o.data.polygons) for o in scene.objects
             if o.type == "MESH")
print("  objects=%d meshes=%d polys=%d actions=%d" % (
    len(scene.objects), n_mesh, n_poly, len(bpy.data.actions)))
print("  engine=%s res=%dx%d fps=%d frames=%d-%d" % (
    scene.render.engine, scene.render.resolution_x,
    scene.render.resolution_y, scene.render.fps,
    scene.frame_start, scene.frame_end))
print("AUDIT DONE")
