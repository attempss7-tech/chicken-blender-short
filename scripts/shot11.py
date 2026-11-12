# shot11.py — Shot 11 (frames 1750-1854, GOLDEN).
#
# "The second group has enough eggs to get by and lives comfortably."
# Golden MS: Group 2 relaxed, C's hand on the full egg basket, hens
# pecking calmly; slow dolly-out.
import characters as ch
import common as cm

FRAME_START, FRAME_END = 1750, 1854
BASKET_POS = (1.0, -1.0)   # on the 0.7 m crate (build_all.py)

CAM_KEYS = [
    (1750, (0, 1.5, 1.4), 35),      # close on C + the full basket
    (1853, (0, 3.5, 2.1), 30),      # slow dolly-out
]
FOCUS_KEYS = [
    (1750, (1.0, -1.5, 0.8)),
    (1853, (0.8, -2.0, 0.9)),
]


def build(ctx):
    chars = ctx["chars"]
    birds = ctx["chickens"]
    cam, focus = cm.build_shot_camera("Cam11", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- C, hand resting on the full egg basket (the basket sits on a
    # 0.7 m crate so its rim is at her hanging-hand height)
    C = chars["C"]
    cm.place(C, FRAME_START, (0.9, -1.6), -10)
    cm.hold(C, FRAME_START, FRAME_END - 1)
    ch.stand_still(C, FRAME_START, FRAME_END - 1)
    ch.idle_breath(C, FRAME_START, FRAME_END - 1)
    ch.arm_keys(C, "R", [(FRAME_START, 12, 8),
                         (FRAME_END - 1, 12, 8)])
    ch.head_keys(C, [(FRAME_START, 0, -4), (FRAME_END - 1, 0, -4)])

    # ---- C-husband + C-youth relaxed
    for key, pos, yaw in (("Chusband", (-0.9, -3.0), 5),
                          ("Cyouth", (0.6, -3.4), -15)):
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, yaw)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1)
        ch.head_keys(rig, [(FRAME_START, 0, 0),
                           (FRAME_END - 1, 0, 0)])

    # ---- hens pecking calmly
    hen = birds["hen_g2"]
    cm.place(hen, FRAME_START, (0.3, -2.2), 20)
    cm.hold(hen, FRAME_START, FRAME_END - 1)
    ch.peck_cycle(hen, FRAME_START, FRAME_END - 1, period=36, phase=0.2)
    rooster = birds["rooster_g2"]
    cm.place(rooster, FRAME_START, (2.4, -2.0), -30)
    cm.hold(rooster, FRAME_START, FRAME_END - 1)
    ch.peck_cycle(rooster, FRAME_START, FRAME_END - 1, period=48,
                  depth=0.3, phase=1.5)

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
