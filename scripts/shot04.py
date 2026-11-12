# shot04.py — Shot 4 (frames 510-708, GOLDEN dusk).
#
# "The first group is so hungry, they cook their chicken that same night.
# Best dinner in three days. Last dinner, too." MS of Group 1 around the
# cooking pot, B stirring; pot macro CU with steam on "Best dinner"
# (f622); the hen is gone from the yard (she vanished f551-557, just
# before "cook" f559); rueful faces on "Last dinner, too" (f666) — B
# turns from the pot toward the camera.
import characters as ch
import common as cm

FRAME_START, FRAME_END = 510, 708
POT_POS = (-10, -3.8)
CU_FRAME = 622          # "Best dinner" — pot macro CU with steam
RUE_FRAME = 666         # "Last dinner, too" — rueful faces

CAM_KEYS = [
    (510, (-9, 3.2, 1.9), 30),      # MS of Group 1 around the pot
    (580, (-9.5, 1.6, 1.4), 34),    # pushing toward the pot
    (622, (-9.8, -1.4, 0.9), 45),   # pot macro CU with steam
    (660, (-9.4, 0.8, 1.3), 38),    # pulling back to faces
    (707, (-9, 2.4, 1.8), 34),      # rueful group shot
]
FOCUS_KEYS = [
    (510, (-9.5, -3.3, 1.0)),
    (580, (-9.8, -3.5, 0.8)),
    (622, (-10, -3.8, 0.6)),
    (660, (-9.3, -3.2, 1.0)),
    (707, (-9, -3, 1.1)),
]


def _stir(rig, side, f_start, f_end, period=12):
    """Stirring arm: shoulder oscillates 40-55 deg, elbow bent 55."""
    arm = rig["arms"][side]
    f = f_start
    while f <= f_end:
        import math
        ph = 2 * math.pi * (f - f_start) / period
        sho = 47 + 8 * (1 if (f // (period // 2)) % 2 == 0 else -1)
        arm["shoulder"].rotation_euler = (sho * math.pi / 180.0, 0, 0)
        ch.kf(arm["shoulder"], f)
        arm["elbow"].rotation_euler = (55 * math.pi / 180.0, 0, 0)
        ch.kf(arm["elbow"], f)
        f += period // 2


def build(ctx):
    chars = ctx["chars"]
    birds = ctx["chickens"]
    pot = ctx["pot"]
    cam, focus = cm.build_shot_camera("Cam04", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- fire lit + steam rising for this shot only
    for flame in pot["flames"]:
        cm.visible_span(flame, FRAME_START, FRAME_END - 1)
    for i, puff in enumerate(pot["steam"]):
        s0 = 560 + i * 15
        s1 = s0 + 100
        cm.scale_at(puff, 0, cm.HIDDEN)
        cm.scale_at(puff, s0 - 1, cm.HIDDEN)
        cm.scale_at(puff, s0, 0.5)
        cm.scale_at(puff, s0 + 50, 1.2)
        cm.scale_at(puff, s1, cm.HIDDEN)
        cm.scale_at(puff, s1 + 1, cm.HIDDEN)
        # slow rise while visible
        puff.location = (puff.location.x, puff.location.y, 0.75)
        ch.kf(puff, s0, "location")
        puff.location = (puff.location.x + 0.06, puff.location.y, 1.55)
        ch.kf(puff, s1, "location")

    # ---- B stirs (south of the pot, facing northwest toward it — his
    # front-left 3/4 is to the camera, and his RIGHT arm is camera-side)
    B = chars["B"]
    cm.place(B, FRAME_START, (-9.4, -3.1), 139)
    ch.stand_still(B, FRAME_START, FRAME_END - 1)
    ch.idle_breath(B, FRAME_START, FRAME_END - 1)
    _stir(B, "R", 520, 650)
    # B turns from the pot toward the camera for the rueful beat — the
    # f659 key holds his 139 deg yaw until the turn starts (without it
    # he would slowly rotate through the whole shot)
    cm.place(B, 659, (-9.4, -3.1), 139)
    cm.place(B, 680, (-9.4, -3.1), 25)
    cm.place(B, FRAME_END - 1, (-9.4, -3.1), 25)
    ch.arm_keys(B, "R", [(650, 47, 55), (670, 20, 20), (690, 0, 5),
                         (FRAME_END - 1, 0, 5)])
    ch.head_keys(B, [(FRAME_START, 0, -12), (650, 0, -12),
                     (RUE_FRAME, 0, -16), (FRAME_END - 1, 0, -16)])

    # ---- B-wife + B-elder cluster around the pot, rueful at f666
    for key, pos, yaw in (("Bwife", (-9.0, -3.0), 60),
                          ("Belder", (-10.4, -3.0), -60)):
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, yaw)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1)
        ch.head_keys(rig, [(FRAME_START, 0, -8), (650, 0, -8),
                           (RUE_FRAME, 0, -20), (FRAME_END - 1, 0, -20)])

    # ---- the G1 hen, still in the yard until she is cooked (vanishes
    # f551-557 per the flock schedule)
    hen = birds["hen_g1"]
    cm.place(hen, FRAME_START, (-8.6, -2.6), -20)
    cm.hold(hen, FRAME_START, 557)
    ch.peck_cycle(hen, FRAME_START, 557, period=28, phase=1.0)

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
