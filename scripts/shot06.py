# shot06.py — builds Shot 6 (the proof shot) of the Blender chicken short.
#
# Frames 954-1161 (31.8-38.7 s). Narration: "The third group has a different
# idea. They go to the second group and say, let's put our hens and roosters
# together and we'll give you some of the eggs."
#
# Visual: low-angle tracking shot of Farmer A walking from his yard to the
# market stall (planted-feet IK walk), two-lead meeting at the stall with
# Farmer C, handshake on "together" (frame 1098). Farmer B visible in his own
# yard in the opening wide. Hens + rooster present. Day lighting, warm.
#
# Layout: v3 (x, z) -> Blender (x, y, z=height). Street along x at y=-2.2;
# houses face +Y at y=-9; stall at (5.5, -3). Camera stays south (y >= 0.5).
import math

import bpy
from mathutils import Vector

import characters as ch
import common as cm
import village as vil

FRAME_START, FRAME_END = 954, 1161
WALK_START, WALK_END, CLOSE_END = 1015, 1086, 1098
HANDSHAKE_FRAME = 1098
A_START = (8.2, -1.7)
A_END = (5.95, -1.7)          # 0.95 m from C -> handshake reach
C_POS = (5.0, -1.7)
B_POS = (-9.0, -3.0)
WALK_DIST = 2.25              # 6 steps of 0.375 m in 71 frames (~2.5/s)

# camera control points: (frame, location, lens_mm)
CAM_KEYS = [
    (954, (15.5, -1.0, 2.30), 22),    # down-the-street wide; B far west
    (990, (11.0, 0.2, 1.40), 27),     # swing south as A starts to move
    (1010, (8.6, 1.2, 1.35), 29),     # arc continues around A
    (1030, (6.4, 2.2, 1.30), 30),     # mid-tracking, low angle, ahead of A
    (1060, (5.6, 2.4, 1.35), 32),     # tracking, A mid-walk
    (1098, (5.45, 2.4, 1.75), 34),    # handshake two-shot, slightly high
    (1161, (5.45, 2.1, 1.72), 35),    # slow push-in to end
]


def _catmull_rom(p0, p1, p2, p3, u):
    return 0.5 * ((2 * p1) + (-p0 + p2) * u
                  + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u)


def _lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _focus_at(f):
    """Focus-empty position at frame f (tracks A, then the handshake)."""
    if f < WALK_START:
        t = ch._smootherstep((f - FRAME_START) / (WALK_START - FRAME_START))
        return _lerp((-1.0, -4.5, 1.0), (A_START[0], -1.7, 1.2), t)
    if f <= WALK_END:
        t = (f - WALK_START) / (WALK_END - WALK_START)
        x = A_START[0] - ch._ease_walk(t) * WALK_DIST
        return (x, -1.7, 1.2)
    if f < CLOSE_END:
        t = ch._smootherstep((f - WALK_END) / (CLOSE_END - WALK_END))
        return _lerp((A_END[0], -1.7, 1.2), (5.47, -1.6, 1.25), t)
    return (5.47, -1.6, 1.25)


def _set_interp_range(obj, f_min, f_max, interp="BEZIER"):
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if f_min <= kp.co.x <= f_max:
                    kp.interpolation = interp


def build_village():
    vil.ground()
    vil.hills_and_clouds()
    # houses (group colours per bible)
    vil.house("HouseG1", (-9, -9, 0), wall="#d8b878", trim="#a85a44")
    vil.house("HouseG2", (0, -9, 0), wall="#e8dcc0", trim="#2e6a3e")
    vil.house("HouseG3", (9, -9, 0), wall="#ece0c8", trim="#3a7a72")
    # coops
    vil.coop("CoopG1", (-11.5, -6, 0), yaw_deg=15)
    vil.coop("CoopG2", (-2.5, -6.5, 0), yaw_deg=-10)
    vil.coop("CoopG3", (11.5, -6, 0), yaw_deg=-15)
    # market stall between G2/G3
    vil.stall("Stall", (5.5, -3, 0))
    # trees: big oak centre-back + scattered; one small foreground tree
    vil.tree("Oak", (-4, -13, 0), scale=1.6, leaf="#4a7a34")
    vil.tree("TreeE1", (14, -7, 0), scale=1.0)
    vil.tree("TreeW1", (-14, -6, 0), scale=1.1, leaf="#6a9a4a")
    vil.tree("TreeC1", (2, -13.5, 0), scale=0.9)
    vil.tree("TreeW2", (-12, -12, 0), scale=1.2, leaf="#6a9a4a")
    vil.tree("TreeE2", (16, -12, 0), scale=1.0)
    vil.tree("TreeFG", (13.5, 2.5, 0), scale=0.7, leaf="#6a9a4a")
    # front fences with a gap at the stall path (x 4.2..6.8)
    vil.fence("FenceW", (-13, -5.5, 0), (4.2, -5.5, 0))
    vil.fence("FenceE", (6.8, -5.5, 0), (13, -5.5, 0))
    # windmill west
    _, rotor = vil.windmill("Windmill", (-20, -14, 0))
    # flowers / props
    vil.flower_patch("FlowersG1", (-7, -6.5, 0))
    vil.flower_patch("FlowersG2", (2, -6.5, 0))
    vil.flower_patch("FlowersG3", (7, -6.5, 0))
    vil.sack("Sack1", (4.2, -3.4, 0))
    vil.sack("Sack2", (6.9, -3.2, 0))
    # hay bale on the WEST side of the teal yard: at (10.5,-4.5) it loomed
    # in shot 8's nest CU background (it sits on the CU sightline)
    vil.hay_bale("Hay1", (6.8, -4.0, 0))
    vil.basket("BasketGround", (4.3, -1.2, 0), eggs=3)
    vil.crate("CrateG2", (1.5, -6.0, 0))
    # G2 nest with 3 eggs (flock table: G2 always has 3 after the gift)
    nest = ch.new_empty("NestG2", loc=(1.8, -1.8, 0))
    ch.add_torus("NestG2_rim", 0.28, 0.07, ch.flat_mat("nest", "#c8a86a"),
                 parent=nest, loc=(0, 0, 0.05), scale=(1, 1, 0.5))
    for i, dx in enumerate((-0.09, 0.09, 0.0)):
        vil.egg("NestG2_egg%d" % i, (dx, 0.02 * i, 0.09), parent=nest)
    return rotor


def build_lights():
    # sky
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*ch.hx("#8ab8e8"), 1.0)
    bg.inputs["Strength"].default_value = 0.9
    # warm key sun from the south-east (lights faces toward camera)
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.0
    sun_data.color = (1.0, 0.96, 0.88)
    sun_data.angle = math.radians(0.5)
    sun = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.location = (12, 14, 18)
    sun.rotation_euler = (Vector((0, -3, 0)) - sun.location).to_track_quat(
        "-Z", "Y").to_euler()
    # cool fill from the north-west (backs / rim), no shadow
    fill_data = bpy.data.lights.new("Fill", "SUN")
    fill_data.energy = 0.35
    fill_data.color = (0.75, 0.85, 1.0)
    try:
        fill_data.use_shadow = False
    except AttributeError:
        pass
    fill = bpy.data.objects.new("Fill", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = (-8, -10, 14)
    fill.rotation_euler = (Vector((0, -3, 0)) - fill.location).to_track_quat(
        "-Z", "Y").to_euler()
    return sun, fill


def build_camera(name="Camera", focus_name="Focus", set_active=True):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = 24
    cam_data.sensor_fit = "VERTICAL"
    cam_data.sensor_width = 36
    cam_data.clip_start = 0.1
    cam_data.clip_end = 250
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    if set_active:
        bpy.context.scene.camera = cam
    focus = ch.new_empty(focus_name, loc=(2.0, -2.6, 1.1))
    con = cam.constraints.new(type="TRACK_TO")
    con.target = focus
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"

    pts = [(f, Vector(loc), lens) for f, loc, lens in CAM_KEYS]
    # Catmull-Rom through control points, sampled every 3 frames
    for f in range(FRAME_START, FRAME_END + 1, 3):
        if f <= pts[0][0]:
            loc, lens = pts[0][1], pts[0][2]
        elif f >= pts[-1][0]:
            loc, lens = pts[-1][1], pts[-1][2]
        else:
            i = next(i for i in range(len(pts) - 1)
                     if pts[i][0] <= f < pts[i + 1][0])
            u = (f - pts[i][0]) / (pts[i + 1][0] - pts[i][0])
            p0 = pts[max(0, i - 1)][1]
            p1 = pts[i][1]
            p2 = pts[i + 1][1]
            p3 = pts[min(len(pts) - 1, i + 2)][1]
            loc = _catmull_rom(p0, p1, p2, p3, u)
            lens = pts[i][2] + (pts[i + 1][2] - pts[i][2]) * u
        cam.location = loc
        ch.kf(cam, f, "location")
        cam_data.lens = lens
        cam_data.keyframe_insert(data_path="lens", frame=f)
        focus.location = _focus_at(f)
        ch.kf(focus, f, "location")
    ch.set_linear(cam)
    ch.set_linear(focus)
    if cam_data.animation_data and cam_data.animation_data.action:
        for fc in cam_data.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    return cam, focus


def build(ctx=None):
    """Build the proof shot.

    Standalone (ctx=None): builds village, lights, characters, camera and
    scene settings exactly as the proof did.
    Master (ctx given): the village, lights and characters already exist
    (built once by build_all.py). Uses the shared rigs and the shared
    chicken pool — mapped to the proof's five bird slots, except the
    proof's extra background hen (HenG3) is dropped: the flock table has
    exactly 2 hens + 2 roosters in shot 6, and the G2 rooster takes the
    background-hen slot. Skips scene settings and the rotor keys (the
    master build owns the timeline and the rotor spin).
    Returns dict of key objects (camera included for marker binding).
    """
    master = ctx is not None
    if master:
        chars = ctx["chars"]
        birds = ctx["chickens"]
        A, B, C = chars["A"], chars["B"], chars["C"]
        # place the leads at the proof's positions (keys at shot start)
        cm.place(A, FRAME_START, A_START, 90)
        cm.place(B, FRAME_START, B_POS, -90)
        cm.place(C, FRAME_START, C_POS, -90)
        # pool birds -> proof slots
        hen1 = birds["hen_g2"]
        hen2 = birds["hen_g3"]
        rooster = birds["rooster_g3"]
        hen_g2 = birds["rooster_g2"]
        cm.place(hen1, FRAME_START, (4.75, -2.4), -30)
        cm.place(hen2, FRAME_START, (7.5, -2.3), 140)
        cm.place(rooster, FRAME_START, (6.2, -2.35), 70)
        cm.place(hen_g2, FRAME_START, (0.8, -4.2), 20)
        # hold the placements to the shot's last rendered frame
        # (NOT A: his walk keys own his root location after f1015)
        for rig in (B, C, hen1, hen2, rooster, hen_g2):
            cm.hold(rig, FRAME_START, FRAME_END - 1)
    else:
        rotor = build_village()
        build_lights()

        # ---- characters
        A = ch.build_farmer("A", "FarmerA", loc=(A_START[0], A_START[1], 0),
                            yaw_deg=90)    # faces west, walks to the stall
        B = ch.build_farmer("B", "FarmerB", loc=(B_POS[0], B_POS[1], 0),
                            yaw_deg=-90)   # faces east, in his yard
        C = ch.build_farmer("C", "FarmerC", loc=(C_POS[0], C_POS[1], 0),
                            yaw_deg=-90)   # faces east, at the stall
        # chickens: behind the handshake line (midground by the stall), NOT in
        # the central foreground — the first staging put the rooster 3.5 m from
        # the camera where it filled a third of the frame
        hen1 = ch.build_chicken("hen", "Hen1", loc=(4.75, -2.4, 0),
                                yaw_deg=-30)
        hen2 = ch.build_chicken("hen", "Hen2", loc=(7.5, -2.3, 0),
                                yaw_deg=140)
        rooster = ch.build_chicken("rooster", "Rooster1",
                                   loc=(6.2, -2.35, 0), yaw_deg=70)
        hen_g2 = ch.build_chicken("hen", "HenG2", loc=(0.8, -4.2, 0),
                                  yaw_deg=20)
        hen_g3 = ch.build_chicken("hen", "HenG3", loc=(10.2, -4.3, 0),
                                  yaw_deg=-70)

    if master:
        cam, focus = build_camera(name="Cam06", focus_name="Focus06",
                                  set_active=False)
    else:
        cam, focus = build_camera()

    # ---- animation
    # A: idle -> look up on "idea" (f978-987) -> walk -> close -> handshake
    ch.animate_walk(A, A_START, A_END, WALK_START, WALK_END, CLOSE_END)
    if master:
        # Hold A's yaw (90 deg, facing west) to the shot's end: without
        # this his yaw interpolates toward shot 7's value across shot 6
        # (he walked sideways and the handshake missed by 0.56 m).
        # The walk owns his root location, so only the rotation is keyed.
        A["root"].rotation_euler = (0, 0, math.radians(90))
        ch.kf(A["root"], FRAME_END - 1)
        # The walk's arm-swing keys (settling to 0) interleave with the
        # handshake keys on A's RIGHT arm in f1088-1098 and would make
        # the arm flick down between handshake keys — clear them first.
        cm.clear_keys_range(A["arms"]["R"]["shoulder"], 1088, 1098)
        cm.clear_keys_range(A["arms"]["R"]["elbow"], 1088, 1098)
    ch.head_keys(A, [(FRAME_START, 0, 0), (985, 0, 12), (1010, 0, 0),
                     (HANDSHAKE_FRAME, 0, 0)])
    # handshake: A's RIGHT arm (camera side for yaw +90) + C's LEFT arm
    ch.arm_keys(A, "R", [
        (1088, 0, 5), (1092, 25, 10), (1096, 50, 14),
        (1098, 66, 14), (1103, 60, 14), (1108, 66, 14),
        (1113, 60, 14), (1118, 66, 14), (1130, 40, 20), (1150, 0, 5),
    ])
    _set_interp_range(A["arms"]["R"]["shoulder"], 1088, 1150)
    _set_interp_range(A["arms"]["R"]["elbow"], 1088, 1150)
    # C: stands at the stall, welcomes, then shakes with LEFT arm
    ch.stand_still(C, FRAME_START, FRAME_END)
    ch.head_keys(C, [(FRAME_START, 0, -12), (1015, 0, 0), (1040, 8, 0),
                     (1075, -5, 0), (HANDSHAKE_FRAME, 0, 0),
                     (FRAME_END, 0, 0)])
    ch.arm_keys(C, "L", [
        (1044, 0, 5), (1058, 45, 25), (1075, 30, 20), (1090, 0, 5),
        (1092, 25, 10), (1096, 50, 14), (1098, 66, 14),
        (1103, 60, 14), (1108, 66, 14), (1113, 60, 14), (1118, 66, 14),
        (1130, 40, 20), (1150, 0, 5),
    ])
    _set_interp_range(C["arms"]["L"]["shoulder"], 1044, 1150)
    _set_interp_range(C["arms"]["L"]["elbow"], 1044, 1150)
    # B: idle in his yard, turns toward the street
    ch.stand_still(B, FRAME_START, FRAME_END)
    ch.head_keys(B, [(FRAME_START, 0, 0), (1030, 15, 0),
                     (FRAME_END, 10, 0)])
    # breathing for all three leads
    for rig in (A, B, C):
        ch.idle_breath(rig, FRAME_START, FRAME_END)
    # hens peck (different phases); rooster mostly alert, occasional peck
    ch.peck_cycle(hen1, FRAME_START, FRAME_END, period=28, phase=0.0)
    ch.peck_cycle(hen2, FRAME_START, FRAME_END, period=30, phase=2.1)
    ch.peck_cycle(hen_g2, FRAME_START, FRAME_END, period=26, phase=1.2)
    if not master:
        ch.peck_cycle(hen_g3, FRAME_START, FRAME_END, period=32, phase=4.0)
    ch.peck_cycle(rooster, FRAME_START, FRAME_END, period=44, depth=0.4,
                  phase=1.0)
    if not master:
        # windmill rotor: slow spin (master build owns the rotor keys)
        rotor.rotation_euler = (0, 0, 0)
        ch.kf(rotor, FRAME_START)
        rotor.rotation_euler = (0, 5.5, 0)
        ch.kf(rotor, FRAME_END)
        ch.set_linear(rotor)

        # ---- scene settings (final: 1080x1920, 30 fps, Eevee on Colab GPU)
        scene = bpy.context.scene
        scene.frame_start = FRAME_START
        scene.frame_end = FRAME_END
        scene.render.fps = 30
        scene.render.resolution_x = 1080
        scene.render.resolution_y = 1920
        scene.render.resolution_percentage = 100
        scene.render.engine = "BLENDER_EEVEE_NEXT"
        scene.render.image_settings.file_format = "PNG"
        return dict(A=A, B=B, C=C,
                    hens=[hen1, hen2, hen_g2, hen_g3],
                    rooster=rooster, camera=cam, focus=focus, rotor=rotor)
    return dict(A=A, B=B, C=C, hens=[hen1, hen2, hen_g2],
                rooster=rooster, camera=cam, focus=focus,
                cameras=[(FRAME_START, cam)])
