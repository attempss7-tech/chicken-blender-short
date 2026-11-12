# shot03.py — Shot 3 (frames 330-510, day).
#
# "Everyone is poor. Everyone is hungry. Three days later, he gives each
# person one chicken." Low dolly along the street past the hungry
# villagers (bowed heads); on "chicken" (f483) each lead receives ONE
# identical hen — scale-in over ~6f in front of each lead, arms open.
# The dolly ends on A, so his gift is the one seen close; the other two
# hens scale in at the same beat (verified by the flock audit, and seen
# in shots 4/5/6). The roosters arrive with the hens (flock table:
# G2/G3 have hen + rooster from f483).
import characters as ch
import common as cm

FRAME_START, FRAME_END = 330, 510
GIFT_FRAME = 483

# Low dolly that LINGERS on each yard (~35f each) and moves quickly
# between them — the first version dollied at constant speed and spent
# a full second on the empty gap (coop + fence, no villagers) between
# yards. Ends on A before the gift (f483).
CAM_KEYS = [
    (330, (-9, 2.0, 1.1), 30),  # on B's yard
    (365, (-9, 2.0, 1.1), 30),
    (400, (0, 2.0, 1.1), 30),   # quick move to C's yard
    (435, (0, 2.0, 1.1), 30),
    (470, (8.5, 2.0, 1.1), 30),  # quick move to A's yard
    (509, (9, 2.0, 1.1), 30),
]
FOCUS_KEYS = [
    (330, (-9, -3, 1.0)),
    (365, (-9, -3, 1.0)),
    (400, (0, -3, 1.0)),
    (435, (0, -3, 1.0)),
    (470, (8.5, -3, 1.0)),
    (509, (9, -3, 1.0)),
]

STAGING = [
    ("A", (9, -3)), ("B", (-9, -3)), ("C", (0, -3)),
    ("Bwife", (-9.9, -3.6)), ("Belder", (-8.1, -3.7)),
    ("Chusband", (0.9, -3.6)), ("Cyouth", (-0.9, -3.5)),
    ("Awife", (9.9, -3.6)), ("Ahand", (8.1, -3.7)),
]


def build(ctx):
    chars = ctx["chars"]
    birds = ctx["chickens"]
    cam, focus = cm.build_shot_camera("Cam03", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- villagers: bowed heads, then arms open to receive at f483
    for key, pos in STAGING:
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, 0)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1, amp=0.008,
                       period=150)
        ch.head_keys(rig, [(FRAME_START, 0, -20), (470, 0, -20),
                           (GIFT_FRAME, 0, -26), (FRAME_END - 1, 0, -26)])
        # arms open to receive the hen (leads reach out; family too)
        cm.arms_both(rig, 470, 0, 5)
        cm.arms_both(rig, GIFT_FRAME + 6, 55, 15)
        cm.arms_both(rig, FRAME_END - 1, 55, 15)
        for side in ("L", "R"):
            cm.set_interp_range(rig["arms"][side]["shoulder"], 470, 509)
            cm.set_interp_range(rig["arms"][side]["elbow"], 470, 509)

    # ---- the gift: one hen in front of each lead (+ roosters for G2/G3).
    # Scale-in keys live in build_all.py's flock schedule; positions here.
    gifts = [
        (birds["hen_g1"], (-9, -2.2), 15),
        (birds["hen_g2"], (0, -2.2), -10),
        (birds["hen_g3"], (9, -2.2), 20),
        (birds["rooster_g2"], (0.8, -2.5), -35),
        (birds["rooster_g3"], (9.8, -2.5), 40),
    ]
    for rig, pos, yaw in gifts:
        cm.place(rig, GIFT_FRAME, pos, yaw)
        cm.hold(rig, GIFT_FRAME, FRAME_END - 1)
        ch.peck_cycle(rig, GIFT_FRAME + 8, FRAME_END - 1, period=28,
                      phase=pos[0])

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
