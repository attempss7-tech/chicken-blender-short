# shot08.py — Shot 8 (frames 1302-1476, day).
#
# "Three weeks later, the first chicks hatch. A few months after that,
# those chicks are laying eggs of their own." Nest-3 macro CU; 4 chicks
# scale in over the hatch beat on "hatch" (f1350) — two perched on the
# rim, two in front of the nest; the G3 clutch of 4 eggs hatches away
# egg by egg (4 -> 0 across f1350-1380); pull-back at f1427 to the young
# hens laying, C and A reacting. (Chick/egg scale keys live in
# build_all.py's flock schedule; positions and camera here.)
import characters as ch
import common as cm

FRAME_START, FRAME_END = 1302, 1476
NEST_POS = (11, -1.8)
HATCH_FRAME = 1350
PULLBACK_FRAME = 1427

CAM_KEYS = [
    (1302, (11, -0.5, 0.7), 40),    # nest macro CU, due south looking
    (1400, (11, -0.5, 0.7), 40),    # north — the background is the empty
    (1426, (11, -0.5, 0.75), 40),   # yard/fence, no rooster, no hay bale
    (1450, (9.0, 4.5, 2.8), 24),    # pull-back (24f) then HOLD — the
    (1475, (9.0, 4.5, 2.8), 24),    # first build's 48f pull-back never
]                                   # settled before the shot ended; the
FOCUS_KEYS = [                      # f1400 hold key kills the Catmull-Rom
    (1302, (11, -1.8, 0.15)),       # overshoot that pushed the CU camera
    (1400, (11, -1.8, 0.15)),       # 0.2 m off during the hatch beat
    (1426, (11, -1.8, 0.15)),
    (1450, (9.2, -2.6, 0.8)),
    (1475, (9.2, -2.6, 0.8)),
]

# chicks: two on the rim, two in front of the nest
# chicks hatch INSIDE the nest rim (0.28 m radius) so all four stay in
# the macro CU — the first spots (on the rim, 0.6 m spread) put three of
# them outside the CU's 0.5 m frame
CHICK_SPOTS = [(10.82, -1.7), (11.18, -1.7),
               (10.88, -1.95), (11.12, -1.95)]
# young hens (scale 0.75) after the pull-back
YOUNG_SPOTS = [(10.4, -2.6), (11.6, -2.4), (10.8, -3.4), (9.9, -2.2)]


def build(ctx):
    chars = ctx["chars"]
    birds = ctx["chickens"]
    cam, focus = cm.build_shot_camera("Cam08", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- the G3 hen + rooster wait AWAY from the nest during the CU
    # (in the first build they interpolated across the frame and the
    # rooster loomed in the CU's background); they take their pull-back
    # spots at f1427
    hen3 = birds["hen_g3"]
    cm.place(hen3, FRAME_START, (9.5, -3.5), 10)
    cm.hold(hen3, FRAME_START, PULLBACK_FRAME - 1)
    rooster3 = birds["rooster_g3"]
    cm.place(rooster3, FRAME_START, (12.6, -3.6), -30)
    cm.hold(rooster3, FRAME_START, PULLBACK_FRAME - 1)

    # ---- A-wife + A-hand are not in this shot — park them out of the
    # pull-back frame (they otherwise interpolate through it: A-wife
    # dominated the f1450 still in the first build)
    cm.place(chars["Awife"], FRAME_START, (12.8, -4.8), -15)
    cm.hold(chars["Awife"], FRAME_START, FRAME_END - 1)
    cm.place(chars["Ahand"], FRAME_START, (6.5, -4.5), 20)
    cm.hold(chars["Ahand"], FRAME_START, FRAME_END - 1)

    # ---- chicks scale in at the hatch (scale keys: build_all schedule)
    for i, chick in enumerate(birds["chicks"]):
        cm.place(chick, HATCH_FRAME, CHICK_SPOTS[i], -20 + i * 15)
        cm.hold(chick, HATCH_FRAME, PULLBACK_FRAME - 1)
        ch.peck_cycle(chick, HATCH_FRAME + 6, PULLBACK_FRAME - 1,
                      period=20, depth=0.5, phase=i * 1.3)

    # ---- after the pull-back: young hens laying (+ the G3 hen/rooster
    # move in from their waiting spots)
    for i, hen in enumerate(birds["young"]):
        cm.place(hen, PULLBACK_FRAME, YOUNG_SPOTS[i], -25 + i * 18)
        cm.hold(hen, PULLBACK_FRAME, FRAME_END - 1)
        ch.peck_cycle(hen, PULLBACK_FRAME, FRAME_END - 1, period=26,
                      phase=i * 1.7)
    cm.place(hen3, PULLBACK_FRAME, (10.6, -2.8), 10)
    cm.hold(hen3, PULLBACK_FRAME, FRAME_END - 1)
    ch.peck_cycle(hen3, PULLBACK_FRAME, FRAME_END - 1, period=28,
                  phase=0.4)
    cm.place(rooster3, PULLBACK_FRAME, (11.8, -3.0), -30)
    cm.hold(rooster3, PULLBACK_FRAME, FRAME_END - 1)
    ch.peck_cycle(rooster3, PULLBACK_FRAME, FRAME_END - 1, period=44,
                  depth=0.35, phase=2.2)

    # ---- A reacts with delight; C came over to see
    A = chars["A"]
    cm.place(A, PULLBACK_FRAME, (8.8, -2.4), -20)
    cm.hold(A, PULLBACK_FRAME, FRAME_END - 1)
    ch.stand_still(A, PULLBACK_FRAME, FRAME_END - 1)
    ch.idle_breath(A, PULLBACK_FRAME, FRAME_END - 1)
    cm.arms_both(A, PULLBACK_FRAME, 0, 5)
    cm.arms_both(A, 1440, 100, 15)
    cm.arms_both(A, FRAME_END - 1, 100, 15)
    for side in ("L", "R"):
        cm.set_interp_range(A["arms"][side]["shoulder"], 1427, 1475)
        cm.set_interp_range(A["arms"][side]["elbow"], 1427, 1475)
    cm.head_nod(A, 1440, 1470, amp_deg=8, period=20)
    C = chars["C"]
    cm.place(C, PULLBACK_FRAME, (7.6, -2.2), -40)
    cm.hold(C, PULLBACK_FRAME, FRAME_END - 1)
    ch.stand_still(C, PULLBACK_FRAME, FRAME_END - 1)
    ch.idle_breath(C, PULLBACK_FRAME, FRAME_END - 1)
    ch.arm_keys(C, "R", [(PULLBACK_FRAME, 0, 5), (1440, 45, 25),
                         (FRAME_END - 1, 45, 25)])
    cm.head_nod(C, 1440, 1470, amp_deg=8, period=20)

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
