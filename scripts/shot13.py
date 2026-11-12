# shot13.py — Shot 13 (frames 2070-2280, GOLDEN).
#
# "And just like that, a world where everyone started with the exact
# same chicken has split into the poor, the middle class, and the rich."
# Golden-hour crane-out over all three yards in one frame: poor (empty,
# ochre, bowed) / middle (eggs, green, content) / rich (flock, teal,
# presenting). (Fade-out is ffmpeg's job, not this scene's.)
import characters as ch
import common as cm

FRAME_START, FRAME_END = 2070, 2280

CAM_KEYS = [
    (2070, (0, 3.5, 2.6), 30),      # starts on the middle yard
    (2160, (0, 10, 7.5), 22),       # crane-out reveals all three
    (2279, (0, 20, 11), 20),        # full village in one frame
]
FOCUS_KEYS = [
    (2070, (0, -3.5, 1.0)),
    (2160, (0, -4, 1.2)),
    (2279, (0, -4, 1.5)),
]


def build(ctx):
    chars = ctx["chars"]
    birds = ctx["chickens"]
    spots = ctx["flock_spots"]
    cam, focus = cm.build_shot_camera("Cam13", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- poor (G1): empty yard, bowed heads
    for key, pos, yaw in (("B", (-9, -3), 0),
                          ("Bwife", (-9.9, -3.6), 10),
                          ("Belder", (-8.1, -3.7), -10)):
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, yaw)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1, amp=0.008,
                       period=150)
        ch.head_keys(rig, [(FRAME_START, 0, -20),
                           (FRAME_END - 1, 0, -20)])

    # ---- middle (G2): eggs, content — C's hand on the basket
    C = chars["C"]
    cm.place(C, FRAME_START, (0.9, -1.6), -10)
    cm.hold(C, FRAME_START, FRAME_END - 1)
    ch.stand_still(C, FRAME_START, FRAME_END - 1)
    ch.idle_breath(C, FRAME_START, FRAME_END - 1)
    ch.arm_keys(C, "R", [(FRAME_START, 12, 8),
                         (FRAME_END - 1, 12, 8)])
    ch.head_keys(C, [(FRAME_START, 0, -4), (FRAME_END - 1, 0, -4)])
    for key, pos, yaw in (("Chusband", (-0.9, -3.0), 5),
                          ("Cyouth", (0.6, -3.4), -15)):
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, yaw)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1)
        ch.head_keys(rig, [(FRAME_START, 0, 0),
                           (FRAME_END - 1, 0, 0)])
    hen = birds["hen_g2"]
    cm.place(hen, FRAME_START, (0.3, -2.2), 20)
    cm.hold(hen, FRAME_START, FRAME_END - 1)
    ch.peck_cycle(hen, FRAME_START, FRAME_END - 1, period=36, phase=0.2)
    rooster = birds["rooster_g2"]
    cm.place(rooster, FRAME_START, (2.4, -2.0), -30)
    cm.hold(rooster, FRAME_START, FRAME_END - 1)
    ch.peck_cycle(rooster, FRAME_START, FRAME_END - 1, period=48,
                  depth=0.3, phase=1.5)

    # ---- rich (G3): flock, presenting
    A = chars["A"]
    cm.place(A, FRAME_START, (9.0, -2.2), 0)
    cm.hold(A, FRAME_START, FRAME_END - 1)
    ch.stand_still(A, FRAME_START, FRAME_END - 1)
    ch.idle_breath(A, FRAME_START, FRAME_END - 1)
    cm.arms_both(A, FRAME_START, 50, 10)
    cm.arms_both(A, FRAME_END - 1, 50, 10)
    for key, pos, yaw in (("Awife", (10.2, -3.0), -15),
                          ("Ahand", (7.8, -3.4), 20)):
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, yaw)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1)
    flock = [birds["hen_g3"]] + birds["young"] + birds["extra"]
    for i, hen in enumerate(flock):
        cm.place(hen, FRAME_START, spots[i], -30 + (i * 37) % 60)
        cm.hold(hen, FRAME_START, FRAME_END - 1)
        ch.peck_cycle(hen, FRAME_START, FRAME_END - 1,
                      period=26 + (i % 5) * 2, phase=i * 0.9)
    for rooster, pos, yaw in ((birds["rooster_g3"], (8.0, -2.8), -20),
                              (birds["rooster_g3b"], (10.8, -3.3), 25)):
        cm.place(rooster, FRAME_START, pos, yaw)
        cm.hold(rooster, FRAME_START, FRAME_END - 1)
        ch.peck_cycle(rooster, FRAME_START, FRAME_END - 1, period=44,
                      depth=0.35, phase=1.0)

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
