# common.py — shared helpers for the full-build shot modules.
#
# Conventions (read before writing a shot module):
# - One scene, one 2280-frame timeline. Shots are HARD CUTS at the marker
#   frames in SHOTS (end is exclusive: shot N covers [start, end-1]).
# - Characters/chickens are built ONCE by build_all.py and shared. A shot
#   module only keyframes the things it shows: root location/yaw (place),
#   arms/head (characters.arm_keys / head_keys), breathing, peck cycles.
# - Because cuts are hard, a character may teleport between shots: key its
#   new pose at the shot's start frame and hold it at the shot's last
#   rendered frame (end-1). Interpolation across the 1-frame cut is
#   invisible. Characters a shot does not show are left wherever they are.
# - Visibility is done by ROOT SCALE (0.001 = hidden), never hide_render:
#   hiding a parent empty does NOT hide its children in a render, but
#   scaling the root scales the whole rig. Always key BOTH sides of a
#   visibility change (old value at F-1, new value at F) or the object
#   will visibly grow/shrink across the whole span between keys.
# - Timing comes from voice/words.json via SHOT_TIMELINE.md — never by feel.
import math

import bpy
from mathutils import Vector

import characters as ch

FRAME_END = 2280            # timeline is frames 0..2279
HIDDEN = 0.001              # root scale that reads as "not there"

# (shot number, start frame, end frame [exclusive], lighting preset)
SHOTS = [
    (1, 0, 150, "day"),
    (2, 150, 330, "day"),
    (3, 330, 510, "day"),
    (4, 510, 708, "golden"),
    (5, 708, 954, "day"),
    (6, 954, 1161, "day"),
    (7, 1161, 1302, "day"),
    (8, 1302, 1476, "day"),
    (9, 1476, 1572, "golden"),
    (10, 1572, 1750, "day"),
    (11, 1750, 1854, "golden"),
    (12, 1854, 2070, "day"),
    (13, 2070, 2280, "golden"),
]

# lighting presets (keyframed at every shot boundary by build_all.py)
DAY = dict(
    sun_energy=3.0, sun_color=(1.0, 0.96, 0.88),
    sun_loc=(12, 14, 18), fill_energy=0.35,
    world_color="#8ab8e8", world_strength=0.9,
)
GOLDEN = dict(
    sun_energy=2.6, sun_color=(1.0, 0.72, 0.45),
    sun_loc=(16, 10, 9), fill_energy=0.22,
    world_color="#f0b070", world_strength=0.75,
)
LIGHTING = {"day": DAY, "golden": GOLDEN}


# ---------------------------------------------------------------- placement

def yaw_to(from_xy, to_xy):
    """Yaw (degrees) for a character at from_xy to face to_xy.
    Local forward is +Y; yaw t gives forward (-sin t, cos t)."""
    dx = to_xy[0] - from_xy[0]
    dy = to_xy[1] - from_xy[1]
    return math.degrees(math.atan2(-dx, dy))


def place(rig, frame, loc, yaw_deg=None):
    """Keyframe a rig's root location (+ optional yaw) at one frame.
    Also updates rig['yaw'] so animate_walk's IK math matches the root."""
    root = rig["root"]
    root.location = (loc[0], loc[1], 0.0)
    ch.kf(root, frame, "location")
    if yaw_deg is not None:
        root.rotation_euler = (0, 0, math.radians(yaw_deg))
        ch.kf(root, frame)
        if "yaw" in rig:
            rig["yaw"] = math.radians(yaw_deg)


def hold(rig, f_start, f_end):
    """Keyframe the rig's CURRENT root location AND rotation at both ends
    of a range (holds it still across the shot).

    The rotation keys matter as much as the location: without them, the
    yaw interpolates from this shot's value to the next shot's value
    across the whole intervening shot — in the first full build this
    turned Farmer A 40 deg toward the camera mid-walk in shot 6 and
    broke the handshake (hands missed by 0.56 m)."""
    root = rig["root"]
    for f in (f_start, f_end):
        root.location = (root.location.x, root.location.y, 0.0)
        ch.kf(root, f, "location")
        ch.kf(root, f)


def clear_keys_range(obj, f_min, f_max, data_path=None):
    """Delete an object's keyframe points in [f_min, f_max] (all fcurves,
    or only those matching data_path). Used where two animation passes
    write the same channel in the same range — e.g. shot 6's walk keys
    interleaved with the handshake keys on A's right arm, which made the
    arm flick down to 0 deg between handshake keys."""
    if not (obj.animation_data and obj.animation_data.action):
        return
    for fc in obj.animation_data.action.fcurves:
        if data_path is not None and fc.data_path != data_path:
            continue
        doomed = [kp for kp in fc.keyframe_points
                  if f_min <= kp.co.x <= f_max]
        for kp in reversed(doomed):
            fc.keyframe_points.remove(kp)
        if doomed:
            fc.update()


def stand(rig, f_start, f_end, loc=None, yaw_deg=None):
    """place() + hold + neutral pose keys: the standard "character stands
    here for this shot" call. If loc is None, keeps the current location."""
    if loc is not None or yaw_deg is not None:
        place(rig, f_start, loc if loc is not None else
              (rig["root"].location.x, rig["root"].location.y), yaw_deg)
    ch.stand_still(rig, f_start, f_end)


# ---------------------------------------------------------------- visibility

def scale_at(obj, frame, s):
    """Keyframe an object's scale (uniform) at one frame."""
    obj.scale = (s, s, s)
    ch.kf(obj, frame, "scale")


def visible_span(obj, f_start, f_end, base=1.0, fade_in=0, fade_out=0):
    """Object visible (scale=base) between f_start and f_end inclusive,
    hidden (scale 0.001) outside. fade_in/fade_out grow/shrink it over
    that many frames at the span's edges. Keys both sides of every
    transition so nothing drifts between spans."""
    if f_start > 0:
        scale_at(obj, f_start - 1, HIDDEN)
    if fade_in > 0:
        scale_at(obj, f_start, HIDDEN)
        scale_at(obj, f_start + fade_in, base)
    else:
        scale_at(obj, f_start, base)
    if fade_out > 0:
        scale_at(obj, f_end - fade_out, base)
        scale_at(obj, f_end, HIDDEN)
    else:
        scale_at(obj, f_end, base)
    if f_end < FRAME_END - 1:
        scale_at(obj, f_end + 1, HIDDEN)


def hide_from(obj, frame, base=1.0):
    """Object visible from f0 until `frame`, hidden from frame+1 on.
    (For things that vanish once, e.g. the G1 hen, the wealth props.)"""
    scale_at(obj, 0, base)
    scale_at(obj, frame, base)
    scale_at(obj, frame + 1, HIDDEN)


# ---------------------------------------------------------------- gestures

def arms_both(rig, frame, sho_deg, elb_deg=5):
    """Keyframe both arms to the same shoulder/elbow pose at one frame."""
    for side in ("L", "R"):
        arm = rig["arms"][side]
        arm["shoulder"].rotation_euler = (math.radians(sho_deg), 0, 0)
        ch.kf(arm["shoulder"], frame)
        arm["elbow"].rotation_euler = (math.radians(elb_deg), 0, 0)
        ch.kf(arm["elbow"], frame)


def head_shake(rig, f_start, f_end, amp_deg=14, period=12):
    """Head yaw oscillation (e.g. B complaining). Keys every half period."""
    f = f_start
    while f <= f_end:
        ph = 2 * math.pi * (f - f_start) / period
        rig["head"].rotation_euler = (0, 0, math.radians(amp_deg)
                                      * math.sin(ph))
        ch.kf(rig["head"], f)
        f += max(2, period // 2)
    rig["head"].rotation_euler = (0, 0, 0)
    ch.kf(rig["head"], f_end)


def head_nod(rig, f_start, f_end, amp_deg=8, period=20):
    """Gentle head nod (pitch oscillation)."""
    f = f_start
    while f <= f_end:
        ph = 2 * math.pi * (f - f_start) / period
        rig["head"].rotation_euler = (math.radians(amp_deg) * math.sin(ph),
                                      0, 0)
        ch.kf(rig["head"], f)
        f += max(2, period // 2)
    rig["head"].rotation_euler = (0, 0, 0)
    ch.kf(rig["head"], f_end)


def set_interp_range(obj, f_min, f_max, interp="BEZIER"):
    """Set keyframe interpolation for one object's keys in a frame range."""
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if f_min <= kp.co.x <= f_max:
                    kp.interpolation = interp


# ---------------------------------------------------------------- camera

def _catmull_rom(p0, p1, p2, p3, u):
    return 0.5 * ((2 * p1) + (-p0 + p2) * u
                  + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u)


def _sample_keys(pts, f):
    """Catmull-Rom sample of [(frame, Vector, lens)] at frame f.
    Returns (Vector loc, lens)."""
    if f <= pts[0][0]:
        return pts[0][1], pts[0][2]
    if f >= pts[-1][0]:
        return pts[-1][1], pts[-1][2]
    i = next(i for i in range(len(pts) - 1)
             if pts[i][0] <= f < pts[i + 1][0])
    u = (f - pts[i][0]) / (pts[i + 1][0] - pts[i][0])
    p0 = pts[max(0, i - 1)][1]
    p1 = pts[i][1]
    p2 = pts[i + 1][1]
    p3 = pts[min(len(pts) - 1, i + 2)][1]
    loc = _catmull_rom(p0, p1, p2, p3, u)
    lens = pts[i][2] + (pts[i + 1][2] - pts[i][2]) * u
    return loc, lens


def build_shot_camera(name, cam_keys, focus_keys, f_start, f_end,
                      sample=3):
    """Build one marker-bound shot camera.

    cam_keys: [(frame, (x, y, z), lens_mm)] — Catmull-Rom path.
    focus_keys: [(frame, (x, y, z))] — Track-To focus path (same sampling).
    Keys cover [f_start, f_end]; build_all binds the camera to the marker
    at f_start. Returns (camera object, focus empty).
    """
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = cam_keys[0][2]
    cam_data.sensor_fit = "VERTICAL"
    cam_data.sensor_width = 36
    cam_data.clip_start = 0.1
    cam_data.clip_end = 250
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    focus = ch.new_empty(name + "_Focus", loc=focus_keys[0][1])
    con = cam.constraints.new(type="TRACK_TO")
    con.target = focus
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"

    pts = [(f, Vector(loc), lens) for f, loc, lens in cam_keys]
    fpts = [(f, Vector(loc), 0.0) for f, loc in focus_keys]
    for f in range(f_start, f_end + 1, sample):
        loc, lens = _sample_keys(pts, f)
        cam.location = loc
        ch.kf(cam, f, "location")
        cam_data.lens = lens
        cam_data.keyframe_insert(data_path="lens", frame=f)
        floc, _ = _sample_keys(fpts, f)
        focus.location = floc
        ch.kf(focus, f, "location")
    if (f_end - f_start) % sample:
        loc, lens = _sample_keys(pts, f_end)
        cam.location = loc
        ch.kf(cam, f_end, "location")
        cam_data.lens = lens
        cam_data.keyframe_insert(data_path="lens", frame=f_end)
        floc, _ = _sample_keys(fpts, f_end)
        focus.location = floc
        ch.kf(focus, f_end, "location")
    ch.set_linear(cam)
    ch.set_linear(focus)
    if cam_data.animation_data and cam_data.animation_data.action:
        for fc in cam_data.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    return cam, focus
