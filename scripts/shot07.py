# shot07.py — Shot 7 (frames 1161-1302, day).
#
# "You see? The second group wanted eggs. The third group wanted
# chickens." Symmetrical comparison: green yard + egg basket (C shows
# eggs) — HARD CUT at f1246, just before "third" (f1257), to teal yard +
# flock (A presents chickens). Two cameras, one cut; the framing is
# mirrored so the symmetry (then the divergence) reads.
import characters as ch
import common as cm
import village as vil

FRAME_START, FRAME_END = 1161, 1302
CUT_FRAME = 1246

# green yard half (1161-1245)
CAM_KEYS_A = [
    (1161, (0.3, 2.2, 1.5), 32),
    (1245, (0.3, 1.9, 1.45), 34),
]
FOCUS_KEYS_A = [
    (1161, (0.5, -2.4, 1.0)),
    (1245, (0.6, -2.3, 1.0)),
]
# teal yard half (1246-1302) — mirrored framing
CAM_KEYS_B = [
    (1246, (9, 2.2, 1.5), 32),
    (1301, (9, 1.9, 1.45), 34),
]
FOCUS_KEYS_B = [
    (1246, (9, -2.6, 1.0)),
    (1301, (8.7, -2.4, 1.0)),
]


def build(ctx):
    chars = ctx["chars"]
    birds = ctx["chickens"]
    cam_a, focus_a = cm.build_shot_camera(
        "Cam07a", CAM_KEYS_A, FOCUS_KEYS_A, FRAME_START, CUT_FRAME - 1)
    cam_b, focus_b = cm.build_shot_camera(
        "Cam07b", CAM_KEYS_B, FOCUS_KEYS_B, CUT_FRAME, FRAME_END - 1)

    # ---- green half: C shows the eggs, family beside her
    C = chars["C"]
    cm.place(C, FRAME_START, (0.4, -2.6), -10)
    cm.hold(C, FRAME_START, CUT_FRAME - 1)
    ch.stand_still(C, FRAME_START, CUT_FRAME - 1)
    ch.idle_breath(C, FRAME_START, CUT_FRAME - 1)
    ch.arm_keys(C, "R", [(FRAME_START, 0, 5), (1175, 60, 45),
                         (CUT_FRAME - 1, 60, 45)])
    cm.set_interp_range(C["arms"]["R"]["shoulder"], 1161, 1245)
    cm.set_interp_range(C["arms"]["R"]["elbow"], 1161, 1245)
    ch.head_keys(C, [(FRAME_START, 0, 0), (CUT_FRAME - 1, 0, -6)])
    # an egg in C's raised hand sells "wanted eggs" (parented to the
    # hand, so it follows the arm; visible for the green half only)
    import bpy
    hand_egg = vil.egg("EggInHandC", (0, 0, -0.05),
                       parent=bpy.data.objects["FarmerC_handR"])
    cm.visible_span(hand_egg, FRAME_START, CUT_FRAME - 1)
    for key, pos, yaw in (("Chusband", (-1.0, -3.2), 5),
                          ("Cyouth", (1.4, -3.0), -25)):
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, yaw)
        cm.hold(rig, FRAME_START, CUT_FRAME - 1)
        ch.stand_still(rig, FRAME_START, CUT_FRAME - 1)
        ch.idle_breath(rig, FRAME_START, CUT_FRAME - 1)
    hen = birds["hen_g2"]
    cm.place(hen, FRAME_START, (0.2, -2.2), 30)
    cm.hold(hen, FRAME_START, CUT_FRAME - 1)
    ch.peck_cycle(hen, FRAME_START, CUT_FRAME - 1, period=30, phase=0.3)
    rooster = birds["rooster_g2"]
    cm.place(rooster, FRAME_START, (1.5, -2.8), -15)
    cm.hold(rooster, FRAME_START, CUT_FRAME - 1)
    ch.peck_cycle(rooster, FRAME_START, CUT_FRAME - 1, period=42,
                  depth=0.35, phase=2.0)

    # ---- teal half: A presents the chickens, family beside him
    A = chars["A"]
    cm.place(A, CUT_FRAME, (8.6, -2.6), 10)
    cm.hold(A, CUT_FRAME, FRAME_END - 1)
    ch.stand_still(A, CUT_FRAME, FRAME_END - 1)
    ch.idle_breath(A, CUT_FRAME, FRAME_END - 1)
    cm.arms_both(A, CUT_FRAME, 0, 5)
    cm.arms_both(A, 1260, 50, 10)
    cm.arms_both(A, FRAME_END - 1, 50, 10)
    for side in ("L", "R"):
        cm.set_interp_range(A["arms"][side]["shoulder"], 1246, 1301)
        cm.set_interp_range(A["arms"][side]["elbow"], 1246, 1301)
    ch.head_keys(A, [(CUT_FRAME, 0, 0), (FRAME_END - 1, 0, 0)])
    for key, pos, yaw in (("Awife", (9.9, -3.2), -5),
                          ("Ahand", (7.8, -3.0), 25)):
        rig = chars[key]
        cm.place(rig, CUT_FRAME, pos, yaw)
        cm.hold(rig, CUT_FRAME, FRAME_END - 1)
        ch.stand_still(rig, CUT_FRAME, FRAME_END - 1)
        ch.idle_breath(rig, CUT_FRAME, FRAME_END - 1)
    hen3 = birds["hen_g3"]
    cm.place(hen3, CUT_FRAME, (8.4, -2.0), -25)
    cm.hold(hen3, CUT_FRAME, FRAME_END - 1)
    ch.peck_cycle(hen3, CUT_FRAME, FRAME_END - 1, period=28, phase=1.4)
    rooster3 = birds["rooster_g3"]
    cm.place(rooster3, CUT_FRAME, (9.6, -2.4), 15)
    cm.hold(rooster3, CUT_FRAME, FRAME_END - 1)
    ch.peck_cycle(rooster3, CUT_FRAME, FRAME_END - 1, period=44,
                  depth=0.35, phase=0.9)

    return dict(cameras=[(FRAME_START, cam_a), (CUT_FRAME, cam_b)],
                camera=cam_a, focus=focus_a)
