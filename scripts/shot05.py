# shot05.py — Shot 5 (frames 708-954, day).
#
# "The second group is just as hungry, but they keep their chickens
# alive. If it's a hen, they eat her eggs. If it's a rooster, they keep
# him for breeding." MS of Group 2 with hen + rooster; nest macro CU
# with eggs on "eggs" (f853); rooster head-high on "rooster" (f888).
import math

import characters as ch
import common as cm

FRAME_START, FRAME_END = 708, 954
NEST_POS = (1.8, -1.8)
EGGS_FRAME = 853
ROOSTER_FRAME = 888

CAM_KEYS = [
    (708, (0, 2.4, 1.6), 32),       # MS of Group 2
    (800, (0.8, 2.0, 1.4), 34),     # drift toward the nest
    (853, (2.6, -0.2, 0.5), 45),    # nest macro CU with eggs (from the
    (888, (0.6, 0.6, 1.1), 36),     # south-east, so no legs intrude)
    (953, (0.5, 2.4, 1.6), 32),     # settle on the group
]
FOCUS_KEYS = [
    (708, (0.5, -2.5, 1.0)),
    (800, (1.0, -2.2, 0.8)),
    (853, (1.8, -1.8, 0.25)),
    (888, (0.2, -3.4, 0.4)),
    (953, (0.5, -2.5, 1.0)),
]


def build(ctx):
    chars = ctx["chars"]
    birds = ctx["chickens"]
    cam, focus = cm.build_shot_camera("Cam05", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- C reaches toward the nest to gather eggs (visible in the MS
    # before the CU; she stands west of the nest so her legs stay out of
    # the CU's sightline, and reaches with her LEFT arm, camera-side)
    C = chars["C"]
    cm.place(C, FRAME_START, (-0.6, -2.8), -63)
    cm.hold(C, FRAME_START, FRAME_END - 1)
    ch.stand_still(C, FRAME_START, FRAME_END - 1)
    ch.idle_breath(C, FRAME_START, FRAME_END - 1)
    ch.arm_keys(C, "L", [(FRAME_START, 0, 5), (800, 0, 5),
                         (820, 65, 35), (880, 65, 35), (910, 0, 5),
                         (FRAME_END - 1, 0, 5)])
    cm.set_interp_range(C["arms"]["L"]["shoulder"], 800, 910)
    cm.set_interp_range(C["arms"]["L"]["elbow"], 800, 910)
    ch.head_keys(C, [(FRAME_START, 0, -6), (810, 0, -22),
                     (880, 0, -22), (910, 0, -6),
                     (FRAME_END - 1, 0, -6)])

    # ---- C-husband + C-youth stand by, calm (west, out of the CU)
    for key, pos, yaw in (("Chusband", (-1.6, -3.0), 10),
                          ("Cyouth", (-1.8, -2.6), -20)):
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, yaw)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1)
        ch.head_keys(rig, [(FRAME_START, 0, -4), (850, 0, -10),
                           (FRAME_END - 1, 0, -4)])

    # ---- hen pecks near C; rooster head-high on "rooster" (f888)
    hen = birds["hen_g2"]
    cm.place(hen, FRAME_START, (0.2, -2.4), 25)
    cm.hold(hen, FRAME_START, FRAME_END - 1)
    ch.peck_cycle(hen, FRAME_START, FRAME_END - 1, period=28, phase=0.7)

    rooster = birds["rooster_g2"]
    cm.place(rooster, FRAME_START, (0.2, -3.4), -20)
    cm.hold(rooster, FRAME_START, FRAME_END - 1)
    # peck in two halves with a head-high pause in the middle
    ch.peck_cycle(rooster, FRAME_START, 880, period=40, depth=0.35,
                  phase=1.0)
    ch.peck_cycle(rooster, 920, FRAME_END - 1, period=40, depth=0.35,
                  phase=1.0)
    for f, pitch in ((880, 0.0), (888, 0.18), (910, 0.18), (920, 0.0)):
        rooster["head"].rotation_euler = (pitch, 0, 0)
        ch.kf(rooster["head"], f)
    # body stays upright through the head-high beat
    for f in (880, 920):
        rooster["body"].location = (0, 0, 0.30 * rooster["scale"])
        ch.kf(rooster["body"], f, "location")

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
