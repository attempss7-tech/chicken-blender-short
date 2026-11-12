# shot09.py — Shot 9 (frames 1476-1572, GOLDEN time-lapse).
#
# "Over time, the third group raises more and more chickens." Warm
# golden time-lapse: the teal yard fills with hens (flock grows 6 -> 18,
# one per ~10f from f1512 — the appearance keys live in build_all.py's
# flock schedule; 7 have appeared by this shot's end, the rest during
# shots 10-11, off-frame), grain pours, the G3 house extension appears.
# Hens walk here (animate_hen_walk), they don't just peck in place.
import characters as ch
import common as cm

FRAME_START, FRAME_END = 1476, 1572
GRAIN_POS = (7.5, -4.8)

CAM_KEYS = [
    (1476, (9, 4.5, 3.6), 26),      # wide on the teal yard
    (1520, (9, 3.5, 2.6), 28),      # closer on the growing flock
    (1571, (12, 3.5, 2.4), 28),     # drift east: the new house extension
]                                   # (x 11.5+) comes into frame left,
FOCUS_KEYS = [                      # clear of the coop
    (1476, (9, -3, 0.8)),
    (1520, (9, -3, 0.6)),
    (1571, (10.8, -3, 0.6)),
]


def _grain_pour():
    """Tipped sack + grain stream + growing pile at GRAIN_POS.
    The pile stays after this shot (yard dressing); the stream runs
    f1500-1560 only."""
    sack_m = ch.flat_mat("sack", "#c8a86a")
    grain_m = ch.flat_mat("grain", "#e8c85a")
    grp = ch.new_empty("GrainPour", loc=(GRAIN_POS[0], GRAIN_POS[1], 0))
    # the whole pour is hidden until shot 9 (the pile/stream have their
    # own keys inside that window)
    cm.visible_span(grp, 1476, 2279)
    # tipped sack, mouth pointing down-right
    sack = ch.add_sphere("GrainPour_sack", 1.0, sack_m, parent=grp,
                         loc=(0, 0, 0.42), scale=(0.26, 0.26, 0.32),
                         rot=(1.0, 0, 0.3))
    # grain stream: thin cylinder from the sack mouth to the pile
    stream = ch.add_cylinder("GrainPour_stream", 0.03, 0.5, grain_m,
                             parent=grp, loc=(0.25, 0, 0.22),
                             rot=(0, 0.5, 0), verts=8)
    # pile: cone that grows f1500-1560 and stays
    pile = ch.add_cone("GrainPour_pile", 0.45, 0.05, 0.35, grain_m,
                       parent=grp, loc=(0.35, 0, 0.17), verts=16)
    cm.visible_span(stream, 1500, 1560)
    cm.scale_at(pile, 0, cm.HIDDEN)
    cm.scale_at(pile, 1499, cm.HIDDEN)
    cm.scale_at(pile, 1560, 1.0)
    cm.scale_at(pile, 2279, 1.0)
    return grp


def build(ctx):
    chars = ctx["chars"]
    birds = ctx["chickens"]
    spots = ctx["flock_spots"]
    cam, focus = cm.build_shot_camera("Cam09", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- the flock takes its yard spots (18 hens + 2 roosters).
    # Appearance (scale) keys are in the flock schedule; positions here.
    flock = [birds["hen_g3"]] + birds["young"] + birds["extra"]
    walkers = {0, 1, 3}  # flock indices that walk this shot (see below)
    for i, hen in enumerate(flock):
        cm.place(hen, FRAME_START, spots[i], -30 + (i * 37) % 60)
        if i not in walkers:
            cm.hold(hen, FRAME_START, FRAME_END - 1)
    # hens that are already visible peck — EXCEPT the walkers (peck_cycle
    # and animate_hen_walk both key body location; the walkers get their
    # motion from the walk itself)
    for i, hen in enumerate(flock[:5]):
        if i in walkers:
            continue
        ch.peck_cycle(hen, FRAME_START, FRAME_END - 1, period=26 + i * 2,
                      phase=i * 1.1)
    rooster3 = birds["rooster_g3"]
    cm.place(rooster3, FRAME_START, (8.0, -2.8), -20)
    cm.hold(rooster3, FRAME_START, FRAME_END - 1)
    ch.peck_cycle(rooster3, FRAME_START, FRAME_END - 1, period=44,
                  depth=0.35, phase=0.5)
    rooster3b = birds["rooster_g3b"]
    cm.place(rooster3b, FRAME_START, (10.8, -3.3), 25)
    cm.hold(rooster3b, FRAME_START, FRAME_END - 1)

    # ---- a few hens actually walk (the flock must feel alive).
    # After each walk, hold the hen at its END spot (not the start spot).
    ch.animate_hen_walk(birds["young"][0],
                        [spots[1], (9.0, -3.8), (8.2, -2.6)],
                        1480, 1560)
    cm.place(birds["young"][0], FRAME_END - 1, (8.2, -2.6))
    ch.animate_hen_walk(birds["hen_g3"],
                        [spots[0], (7.0, -2.6), (7.6, -3.4)],
                        1490, 1570)
    cm.place(birds["hen_g3"], FRAME_END - 1, (7.6, -3.4))
    ch.animate_hen_walk(birds["young"][2],
                        [spots[3], (10.0, -4.2), (9.4, -4.8)],
                        1500, 1565)
    cm.place(birds["young"][2], FRAME_END - 1, (9.4, -4.8))

    # ---- grain pours + house extension appears (time-lapse)
    _grain_pour()
    for obj in ctx["extension"]:
        cm.scale_at(obj, 1499, cm.HIDDEN)
        cm.scale_at(obj, 1540, 1.0)
        cm.scale_at(obj, 2279, 1.0)

    # ---- A presents; A-wife + A-hand scatter grain
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
        # scattering: right arm swings down-forward repeatedly
        keys = []
        f = FRAME_START
        up = True
        while f <= FRAME_END - 1:
            keys.append((f, 55 if up else 20, 25))
            up = not up
            f += 12
        ch.arm_keys(rig, "R", keys)

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
