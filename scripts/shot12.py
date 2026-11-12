# shot12.py — Shot 12 (frames 1854-2070, day).
#
# "But the third group now has so many chickens, they can't look after
# them all. So they go to the first group and offer them work paid in
# eggs." Wide teal yard overflowing with hens (all 18 + 2 roosters); B
# stands among the flock (hired help); MS of the handover — basket of
# pay-eggs between A and B on "work paid in eggs" (f2019-2054).
import characters as ch
import common as cm
import village as vil

FRAME_START, FRAME_END = 1854, 2070
HANDOVER_START = 2019
HANDOVER_END = 2054

CAM_KEYS = [
    (1854, (9, 6.5, 3.8), 24),      # wide teal yard overflowing (B in
    (1980, (8.6, 3.2, 2.1), 30),    # frame at the right edge)
    (2019, (7.9, 2.3, 1.6), 35),    # handover MS
    (2069, (7.8, 2.2, 1.6), 35),
]
FOCUS_KEYS = [
    (1854, (8.5, -2.8, 0.7)),
    (1980, (8.2, -2.6, 0.9)),
    (2019, (7.6, -2.3, 0.9)),
    (2069, (7.6, -2.3, 0.9)),
]

A_POS = (8.2, -2.2)
B_POS = (7.0, -2.4)
PAY_BASKET_POS = (7.6, -2.3)


def build(ctx):
    chars = ctx["chars"]
    birds = ctx["chickens"]
    spots = ctx["flock_spots"]
    cam, focus = cm.build_shot_camera("Cam12", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- the full flock at its yard spots (18 hens + 2 roosters)
    flock = [birds["hen_g3"]] + birds["young"] + birds["extra"]
    walkers = {2, 7}  # flock indices that walk this shot
    for i, hen in enumerate(flock):
        cm.place(hen, FRAME_START, spots[i], -30 + (i * 37) % 60)
        if i not in walkers:
            cm.hold(hen, FRAME_START, FRAME_END - 1)
        if i not in walkers:
            ch.peck_cycle(hen, FRAME_START, FRAME_END - 1,
                          period=26 + (i % 5) * 2, phase=i * 0.9)
    for rooster, pos, yaw in ((birds["rooster_g3"], (8.0, -2.8), -20),
                              (birds["rooster_g3b"], (10.8, -3.3), 25)):
        cm.place(rooster, FRAME_START, pos, yaw)
        cm.hold(rooster, FRAME_START, FRAME_END - 1)
        ch.peck_cycle(rooster, FRAME_START, FRAME_END - 1, period=44,
                      depth=0.35, phase=1.0)
    # two hens wander through the flock
    ch.animate_hen_walk(flock[2], [spots[2], (8.8, -3.0), (9.6, -2.4)],
                        1860, 2000)
    cm.place(flock[2], FRAME_END - 1, (9.6, -2.4))
    ch.animate_hen_walk(flock[7], [spots[7], (10.2, -4.0), (9.0, -4.6)],
                        1880, 2020)
    cm.place(flock[7], FRAME_END - 1, (9.0, -4.6))

    # ---- basket of pay-eggs between A and B, this shot only
    vil.basket("PayBasket", (PAY_BASKET_POS[0], PAY_BASKET_POS[1], 0),
               eggs=4)
    import bpy
    pay = bpy.data.objects["PayBasket"]
    cm.visible_span(pay, FRAME_START, FRAME_END - 1)

    # ---- A offers the work; B (hired help) stands among the flock
    A = chars["A"]
    cm.place(A, FRAME_START, A_POS, cm.yaw_to(A_POS, B_POS))
    cm.hold(A, FRAME_START, FRAME_END - 1)
    ch.stand_still(A, FRAME_START, FRAME_END - 1)
    ch.idle_breath(A, FRAME_START, FRAME_END - 1)
    # A offers with BOTH hands (his right arm alone is on the far side
    # from the camera when he faces west)
    ch.arm_keys(A, "R", [(FRAME_START, 0, 5), (2000, 0, 5),
                         (HANDOVER_START, 55, 20),
                         (HANDOVER_END, 55, 20),
                         (FRAME_END - 1, 20, 10)])
    ch.arm_keys(A, "L", [(FRAME_START, 0, 5), (2000, 0, 5),
                         (HANDOVER_START, 50, 20),
                         (HANDOVER_END, 50, 20),
                         (FRAME_END - 1, 20, 10)])
    for side in ("L", "R"):
        cm.set_interp_range(A["arms"][side]["shoulder"], 2000, 2069)
        cm.set_interp_range(A["arms"][side]["elbow"], 2000, 2069)
    ch.head_keys(A, [(FRAME_START, 0, 0), (FRAME_END - 1, 0, -4)])

    B = chars["B"]
    cm.place(B, FRAME_START, B_POS, cm.yaw_to(B_POS, A_POS))
    cm.hold(B, FRAME_START, FRAME_END - 1)
    ch.stand_still(B, FRAME_START, FRAME_END - 1)
    ch.idle_breath(B, FRAME_START, FRAME_END - 1)
    cm.arms_both(B, 2000, 0, 5)
    cm.arms_both(B, HANDOVER_START, 50, 20)
    cm.arms_both(B, HANDOVER_END, 50, 20)
    cm.arms_both(B, FRAME_END - 1, 20, 10)
    for side in ("L", "R"):
        cm.set_interp_range(B["arms"][side]["shoulder"], 2000, 2069)
        cm.set_interp_range(B["arms"][side]["elbow"], 2000, 2069)
    ch.head_keys(B, [(FRAME_START, 0, -6), (HANDOVER_START, 0, -12),
                     (FRAME_END - 1, 0, -6)])

    # ---- A-wife + A-hand in the yard
    for key, pos, yaw in (("Awife", (9.8, -3.0), -10),
                          ("Ahand", (8.9, -3.6), 15)):
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, yaw)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1)

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
