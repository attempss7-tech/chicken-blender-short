# shot10.py — Shot 10 (frames 1572-1750, day).
#
# "Meanwhile, the first group has nothing left to eat. So they do the
# only thing they can do — they complain." Slow dolly-back on the EMPTY
# ochre yard (no hens, empty pot, empty pouch CU); B throws his arms up
# on "complain" (f1711), head shaking. B-elder's walking stick appears
# from this shot on (scale key in build_all.py's schedule).
import characters as ch
import common as cm
import village as vil

FRAME_START, FRAME_END = 1572, 1750
COMPLAIN_FRAME = 1711
POUCH_POS = (-8.2, -1.6)

CAM_KEYS = [
    (1572, (-9, 1.2, 1.3), 35),     # close on the empty yard + pouch
    (1660, (-9, 3.0, 1.8), 32),     # slow dolly-back
    (1749, (-9, 4.5, 2.3), 30),
]
FOCUS_KEYS = [
    (1572, (-9, -3, 1.0)),
    (1660, (-9, -3, 1.0)),
    (1749, (-9, -3, 1.0)),
]


def build(ctx):
    chars = ctx["chars"]
    cam, focus = cm.build_shot_camera("Cam10", CAM_KEYS, FOCUS_KEYS,
                                      FRAME_START, FRAME_END - 1)

    # ---- empty pouch (flat sack) in the foreground, this shot only.
    # Flatten the sack BODY mesh (not the group: visible_span keys the
    # group's scale uniformly) and shrink the tied top — an empty pouch
    # lies flat.
    import bpy
    pouch = vil.sack("EmptyPouch", (POUCH_POS[0], POUCH_POS[1], 0))
    bpy.data.objects["EmptyPouch_body"].scale = (1.3, 1.3, 0.4)
    bpy.data.objects["EmptyPouch_top"].scale = (0.5, 0.5, 0.3)
    bpy.data.objects["EmptyPouch_top"].location = (0, 0, 0.28)
    cm.visible_span(pouch, FRAME_START, FRAME_END - 1)

    # ---- B: bowed and empty-handed, then throws his arms up on "complain"
    B = chars["B"]
    cm.place(B, FRAME_START, (-9, -3), 0)
    cm.hold(B, FRAME_START, FRAME_END - 1)
    ch.stand_still(B, FRAME_START, FRAME_END - 1)
    ch.idle_breath(B, FRAME_START, FRAME_END - 1, amp=0.008, period=150)
    cm.arms_both(B, 1700, 0, 5)
    cm.arms_both(B, COMPLAIN_FRAME, 150, 10)
    cm.arms_both(B, 1730, 150, 10)
    cm.arms_both(B, 1742, 30, 10)
    cm.arms_both(B, FRAME_END - 1, 30, 10)
    for side in ("L", "R"):
        cm.set_interp_range(B["arms"][side]["shoulder"], 1700, 1749)
        cm.set_interp_range(B["arms"][side]["elbow"], 1700, 1749)
    ch.head_keys(B, [(FRAME_START, 0, -15), (1700, 0, -15),
                     (COMPLAIN_FRAME, 0, 0)])
    cm.head_shake(B, COMPLAIN_FRAME, 1740, amp_deg=14, period=12)
    ch.head_keys(B, [(1749, 0, -10)])

    # ---- B-wife + B-elder (with his stick) bowed beside him
    for key, pos, yaw in (("Bwife", (-9.9, -3.6), 10),
                          ("Belder", (-8.1, -3.7), -10)):
        rig = chars[key]
        cm.place(rig, FRAME_START, pos, yaw)
        cm.hold(rig, FRAME_START, FRAME_END - 1)
        ch.stand_still(rig, FRAME_START, FRAME_END - 1)
        ch.idle_breath(rig, FRAME_START, FRAME_END - 1, amp=0.008,
                       period=150)
        ch.head_keys(rig, [(FRAME_START, 0, -18),
                           (FRAME_END - 1, 0, -18)])

    return dict(cameras=[(FRAME_START, cam)], camera=cam, focus=focus)
