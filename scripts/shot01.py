# shot01.py — Shot 1 (frames 0-150, day).
#
# "Why do the rich keep getting richer while the poor get poorer? One
# chicken explains it." Drone wide over the village, push to the hero hen
# at the village heart; macro CU on "chicken" (f122). All three leads look
# toward her. (Fade-in is ffmpeg's job, not this scene's.)
#
# The hero hen is the shot's symbol — she exists ONLY in this shot
# (visible_span 0-149 in build_all.py); the flock table's "no chickens
# before f483" applies to the group yards, and she is gone by shot 2.
import characters as ch
import common as cm

FRAME_START, FRAME_END = 0, 150
HEN_POS = (0, -1)

CAM_KEYS = [
    (0, (0, 16, 12), 22),       # drone wide over the whole village
    (50, (-3, 10, 8), 24),      # sweeping down
    (90, (-1, 4.5, 3.2), 28),   # descending toward the village heart
    (122, (1.4, 0.2, 0.6), 40),  # macro CU on "chicken" (from the east,
    (149, (1.45, 0.15, 0.55), 42),  # so C's legs aren't behind the hen)
]
FOCUS_KEYS = [
    (0, (0, -5, 1.5)),
    (50, (0, -3, 0.8)),
    (90, (0, -1.5, 0.5)),
    (122, (0, -1, 0.3)),
    (149, (0, -1, 0.3)),
]

# (key, position) — everyone faces the hero hen at (0, -1)
STAGING = [
    ("A", (9, -3)), ("B", (-9, -3)), ("C", (0, -3)),
    ("Bwife", (-9.9, -3.6)), ("Belder", (-8.1, -3.7)),
    ("Chusband", (0.9, -3.6)), ("Cyouth", (-0.9, -3.5)),
    ("Awife", (9.9, -3.6)), ("Ahand", (8.1, -3.7)),
]


def build(ctx):
    chars = ctx["chars"]
    hero = ctx["chickens"]["hero"]
    cam, focus = cm.build_shot_camera("Cam01", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    for key, pos in STAGING:
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, cm.yaw_to(pos, HEN_POS))
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        # look down toward the hen; a small lift as the camera arrives
        ch.head_keys(rig, [(FRAME_START, 0, -8), (110, 0, -8),
                           (122, 0, -4), (FRAME_END - 1, 0, -4)])
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1)

    cm.place(hero, FRAME_START, HEN_POS, -15)
    cm.hold(hero, FRAME_START, FRAME_END - 1)
    ch.peck_cycle(hero, FRAME_START, FRAME_END - 1, period=26, phase=0.5)

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
