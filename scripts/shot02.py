# shot02.py — Shot 2 (frames 150-330, day).
#
# "One day, God takes away everyone's wealth. Every coin, every house,
# every field. Gone." High wide, slow push. Coin piles, sacks and field
# crops shrink away across "Gone" (f309-324); villagers' hands go to
# their faces. Houses STAY standing (same staging as v2/v3 — only
# coins/sacks/crops vanish).
#
# The wealth props are built here but visible from f0 (the village is
# wealthy in shot 1's drone wide too) and vanish once, here.
import math

import characters as ch
import common as cm
import village as vil

FRAME_START, FRAME_END = 150, 330
GONE_START, GONE_END = 309, 324

CAM_KEYS = [
    (150, (0, 15, 11), 22),     # high wide over all three yards
    (240, (0, 12.5, 9.5), 23),  # slow push
    (309, (0, 12, 8.5), 24),    # slight dip on "Gone" (impact kick)
    (329, (0, 10.5, 8), 24),    # push holds
]
FOCUS_KEYS = [
    (150, (0, -5, 1.5)),
    (329, (0, -5, 1.5)),
]

STAGING = [
    ("A", (9, -3)), ("B", (-9, -3)), ("C", (0, -3)),
    ("Bwife", (-9.9, -3.6)), ("Belder", (-8.1, -3.7)),
    ("Chusband", (0.9, -3.6)), ("Cyouth", (-0.9, -3.5)),
    ("Awife", (9.9, -3.6)), ("Ahand", (8.1, -3.7)),
]


def coin_pile(name, loc):
    """A small pile of gold coins (stack + scattered discs)."""
    gold_m = ch.flat_mat("coin_gold", "#e8b83a")
    grp = ch.new_empty(name, loc=loc)
    for i, (r, z) in enumerate(((0.17, 0.03), (0.14, 0.08),
                                (0.11, 0.13))):
        ch.add_cylinder(name + "_disc%d" % i, r, 0.05, gold_m, parent=grp,
                        loc=(0, 0, z), verts=18)
    for i, (dx, dy) in enumerate(((0.22, 0.1), (-0.2, 0.14),
                                  (0.1, -0.22), (-0.14, -0.18))):
        ch.add_cylinder(name + "_loose%d" % i, 0.06, 0.02, gold_m,
                        parent=grp, loc=(dx, dy, 0.012), verts=14)
    return grp


def crop_row(name, loc, n=6, spacing=0.7):
    """A row of small green crop cones."""
    crop_m = ch.flat_mat("crop", "#4a8a34")
    grp = ch.new_empty(name, loc=loc)
    for i in range(n):
        ch.add_cone(name + "_plant%d" % i, 0.13, 0.02, 0.42, crop_m,
                    parent=grp, loc=(i * spacing, 0, 0.21), verts=8)
    return grp


def _shrink(obj, f_start, f_end):
    """Visible from f0, scale to 0 across [f_start, f_end], gone after."""
    cm.scale_at(obj, 0, 1.0)
    cm.scale_at(obj, f_start, 1.0)
    cm.scale_at(obj, f_end, cm.HIDDEN)


def build(ctx):
    chars = ctx["chars"]
    cam, focus = cm.build_shot_camera("Cam02", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- wealth props (visible from f0, vanish on "Gone", staggered
    # yard by yard so the loss sweeps west -> east)
    vanishing = []
    for gx, g in ((-9, "G1"), (0, "G2"), (9, "G3")):
        vanishing.append((coin_pile("Coins%sA" % g, (gx - 1.6, -2.4, 0)),
                          GONE_START, GONE_START + 7))
        vanishing.append((coin_pile("Coins%sB" % g, (gx + 1.5, -4.6, 0)),
                          GONE_START + 2, GONE_START + 9))
        vanishing.append((vil.sack("WealthSack%s" % g,
                                   (gx + 2.0, -2.6, 0)),
                          GONE_START + 1, GONE_START + 8))
    # field crops behind the houses, east and west fields
    for fx, g in ((-15, "W"), (15, "E")):
        for r in range(3):
            vanishing.append((crop_row("Crops%s%d" % (g, r),
                                       (fx - 1.5, -13.5 - r * 1.2, 0)),
                              GONE_START, GONE_END))
    for obj, fs, fe in vanishing:
        _shrink(obj, fs, fe)

    # ---- villagers: standing, then hands to faces on "Gone"
    for key, pos in STAGING:
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, 0)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1)
        # arms: neutral -> hands to face across f300-318, hold to the end
        cm.arms_both(rig, 300, 0, 5)
        cm.arms_both(rig, 318, 130, 110)
        cm.arms_both(rig, FRAME_END - 1, 130, 110)
        cm.set_interp_range(rig["arms"]["L"]["shoulder"], 300, 329)
        cm.set_interp_range(rig["arms"]["R"]["shoulder"], 300, 329)
        cm.set_interp_range(rig["arms"]["L"]["elbow"], 300, 329)
        cm.set_interp_range(rig["arms"]["R"]["elbow"], 300, 329)
        ch.head_keys(rig, [(FRAME_START, 0, 0), (300, 0, -4),
                           (318, 0, -18), (FRAME_END - 1, 0, -18)])

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
