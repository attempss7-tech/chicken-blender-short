# village.py — reusable village builders for the Blender chicken short.
#
# Everything is scripted primitives with flat Principled materials (Eevee
# compatible). Layout follows SHOT_TIMELINE.md: v3 (x, z) maps to Blender
# (x, y, z=height); houses face +Y (toward the street/camera). Ground is z=0.
import math

import bpy
from mathutils import Matrix, Vector

from characters import (add_box, add_cone, add_cylinder, add_sphere,
                        add_torus, cap_object, flat_mat, new_empty, shade)


def _mesh_from_pydata(name, verts, faces, mat, parent=None, loc=(0, 0, 0),
                      rot=(0, 0, 0), smooth=False, mats=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    shade(obj, smooth)
    if mats:
        for m in mats:
            obj.data.materials.append(m)
    elif mat is not None:
        obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rot
    return obj


# ---------------------------------------------------------------- ground

def ground():
    grass_m = flat_mat("grass", "#7fae5a")
    dirt_m = flat_mat("dirt", "#c8a878")
    yard_m = flat_mat("yardgrass", "#93ac62")
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
    g = bpy.context.active_object
    g.name = "Ground"
    g.scale = (110, 80, 1)
    bpy.context.view_layer.objects.active = g
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    g.data.materials.append(grass_m)
    # street / dirt path along the walk line y = -2.2.
    # NOTE: tops must NOT be coplanar with the yard patches: coplanar box
    # tops in the overlap strip rendered pure black in Cycles (proven
    # 2026-11-12 via raycast: YardPatch9 top at y=-2.77 was black while the
    # same face at y=-4.52 was sunlit). Path top 0.045, yard tops 0.015.
    add_box("Path", (34, 2.8, 0.05), dirt_m, loc=(0, -2.2, 0.02))
    # worn yard patches in front of each house
    for x in (-9, 0, 9):
        add_box("YardPatch%d" % x, (6.5, 5.5, 0.02), yard_m,
                loc=(x, -5.0, 0.005))
    return g


def hills_and_clouds():
    hill_m1 = flat_mat("hill1", "#7a9a6a")
    hill_m2 = flat_mat("hill2", "#8aa87a")
    cloud_m = flat_mat("cloud", "#f5f8ff")
    for i, (x, y, sx, sz, m) in enumerate((
            (-28, -38, 22, 6, hill_m1), (0, -42, 26, 7, hill_m2),
            (28, -38, 20, 5, hill_m1))):
        add_sphere("Hill%d" % i, 1.0, m, loc=(x, y, -0.5),
                   scale=(sx, 8, sz), seg=24, rings=12)
    for i, (x, y, z, s) in enumerate((
            (-14, -18, 16, 1.6), (4, -24, 19, 2.2), (20, -16, 15, 1.3))):
        grp = new_empty("Cloud%d" % i, loc=(x, y, z))
        for j, (dx, dy, dz, r) in enumerate((
                (0, 0, 0, 1.0), (1.1, 0.2, -0.15, 0.7),
                (-1.05, -0.1, -0.1, 0.75))):
            add_sphere("Cloud%d_%d" % (i, j), r * s, cloud_m, parent=grp,
                       loc=(dx * s, dy * s, dz * s),
                       scale=(1.4, 1.0, 0.55), seg=16, rings=10)


# ---------------------------------------------------------------- buildings

def house(name, loc, wall="#e8dcc0", trim="#b85c38", roof="#b85c38",
          w=5.0, d=4.0, wall_h=2.8, roof_h=1.6, yaw_deg=0.0):
    """Gabled house facing +Y. Walls box + prism roof (slopes roof colour,
    gable triangles wall colour) + door, windows, chimney, porch."""
    wall_m = flat_mat("wall_" + name, wall)
    roof_m = flat_mat("roof_" + name, roof)
    trim_m = flat_mat("trim_" + name, trim)
    wood_m = flat_mat("wood_dark", "#5a3a24")
    glass_m = flat_mat("window_glass", "#ffd98a")
    glass_m.node_tree.nodes["Principled BSDF"].inputs[
        "Emission Color"].default_value = (1.0, 0.85, 0.5, 1.0)
    glass_m.node_tree.nodes["Principled BSDF"].inputs[
        "Emission Strength"].default_value = 0.25

    grp = new_empty(name, loc=loc)
    grp.rotation_euler = (0, 0, math.radians(yaw_deg))
    add_box(name + "_walls", (w, d, wall_h), wall_m, parent=grp,
            loc=(0, 0, wall_h / 2))
    # roof prism: slopes overhang, gable triangles flush with walls
    rw, rd = w + 0.6, d + 0.7
    wh, rh = wall_h, wall_h + roof_h
    verts = [
        (-rw / 2, -rd / 2, wh), (rw / 2, -rd / 2, wh),   # 0,1 back eaves
        (rw / 2, rd / 2, wh), (-rw / 2, rd / 2, wh),     # 2,3 front eaves
        (-rw / 2, 0, rh), (rw / 2, 0, rh),               # 4,5 ridge
        (-w / 2, -d / 2, wh), (-w / 2, d / 2, wh), (-w / 2, 0, rh),  # 6,7,8
        (w / 2, -d / 2, wh), (w / 2, d / 2, wh), (w / 2, 0, rh),     # 9,10,11
    ]
    faces = [(0, 1, 5, 4), (3, 2, 5, 4), (6, 7, 8), (9, 11, 10)]
    roof = _mesh_from_pydata(name + "_roof", verts, faces, None, parent=grp,
                             mats=[roof_m, wall_m])
    for i, poly in enumerate(roof.data.polygons):
        poly.material_index = 0 if i < 2 else 1
    # door + porch (front, +Y side)
    add_box(name + "_door", (0.95, 0.1, 1.95), wood_m, parent=grp,
            loc=(0, d / 2 + 0.03, 0.98))
    add_sphere(name + "_knob", 0.05, flat_mat("brass", "#e8b83a"),
               parent=grp, loc=(0.32, d / 2 + 0.1, 1.0))
    porch = add_box(name + "_porch", (1.6, 0.9, 0.06), roof_m, parent=grp,
                    loc=(0, d / 2 + 0.45, 2.25), )
    porch.rotation_euler = (math.radians(-18), 0, 0)
    for sx in (-1, 1):
        add_cylinder(name + "_porchpost%d" % sx, 0.05, 2.25, wood_m,
                     parent=grp, loc=(sx * 0.7, d / 2 + 0.8, 1.12))
    # windows: front pair + one each side
    for sx in (-1, 1):
        add_box(name + "_winF%d" % sx, (0.85, 0.08, 0.85), trim_m,
                parent=grp, loc=(sx * 1.6, d / 2 + 0.02, 1.7))
        add_box(name + "_glassF%d" % sx, (0.65, 0.1, 0.65), glass_m,
                parent=grp, loc=(sx * 1.6, d / 2 + 0.03, 1.7))
    # chimney (brick, not trim colour — trim teal read as a teal chimney)
    add_box(name + "_chimney", (0.45, 0.45, 1.5),
            flat_mat("brick", "#a85a44"), parent=grp,
            loc=(w / 2 - 0.7, -0.6, wall_h + roof_h - 0.4))
    return grp


def coop(name, loc, yaw_deg=0.0):
    """Wooden A-frame coop with terracotta roof cap."""
    wood_m = flat_mat("coop_wood", "#8a6a42")
    dark_m = flat_mat("coop_dark", "#3a2a1a")
    cap_m = flat_mat("coop_cap", "#b85c38")
    grp = new_empty(name, loc=loc)
    grp.rotation_euler = (0, 0, math.radians(yaw_deg))
    for sx in (-1, 1):
        add_cylinder(name + "_leg%d" % sx, 0.05, 0.25, dark_m, parent=grp,
                     loc=(sx * 0.55, 0, 0.12))
    # A-frame slopes
    for s in (-1, 1):
        slope = add_box(name + "_slope%d" % s, (1.5, 0.06, 1.25), wood_m,
                        parent=grp, loc=(0, s * 0.42, 0.85))
        slope.rotation_euler = (math.radians(38 * s), 0, 0)
    # triangle end caps
    for sx in (-1, 1):
        verts = [(sx * 0.75, -0.72, 0.25), (sx * 0.75, 0.72, 0.25),
                 (sx * 0.75, 0, 1.42)]
        _mesh_from_pydata(name + "_end%d" % sx, verts, [(0, 1, 2)],
                          wood_m, parent=grp)
    # roof cap along the ridge
    add_box(name + "_cap", (1.6, 0.22, 0.08), cap_m, parent=grp,
            loc=(0, 0, 1.45))
    # dark doorway on the front (+Y) slope
    add_box(name + "_door", (0.34, 0.06, 0.4), dark_m, parent=grp,
            loc=(0, 0.62, 0.55), rot=(math.radians(38), 0, 0))
    return grp


def stall(name, loc, yaw_deg=0.0):
    """Market stall: posts, counter, striped awning, baskets + crates."""
    wood_m = flat_mat("stall_wood", "#7a5a34")
    awn1 = flat_mat("awning_cream", "#f0e6cc")
    awn2 = flat_mat("awning_rust", "#a84838")
    grp = new_empty(name, loc=loc)
    grp.rotation_euler = (0, 0, math.radians(yaw_deg))
    # counter
    add_box(name + "_counter", (2.4, 1.0, 0.85), wood_m, parent=grp,
            loc=(0, 0, 0.43))
    add_box(name + "_countertop", (2.55, 1.15, 0.07),
            flat_mat("stall_top", "#a8823c"), parent=grp, loc=(0, 0, 0.89))
    # posts: front (south, +Y) shorter than back so the tilted awning meets
    # the post tops instead of floating above / through them
    for sx in (-1, 1):
        add_cylinder(name + "_postF%d" % sx, 0.05, 2.15, wood_m,
                     parent=grp, loc=(sx * 1.15, 0.55, 1.075))
        add_cylinder(name + "_postB%d" % sx, 0.05, 2.6, wood_m,
                     parent=grp, loc=(sx * 1.15, -0.55, 1.3))
    for i in range(8):
        x = -1.05 + i * 0.3
        m = awn1 if i % 2 == 0 else awn2
        stripe = add_box(name + "_awn%d" % i, (0.3, 1.7, 0.03), m,
                         parent=grp, loc=(x, 0.1, 2.4))
        stripe.rotation_euler = (math.radians(-14), 0, 0)
    # baskets of eggs on the counter
    basket(name + "_basket1", (-0.7, 0, 0.93), parent=grp, eggs=3)
    basket(name + "_basket2", (0.65, 0.1, 0.93), parent=grp, eggs=4)
    # crates beside the stall
    crate(name + "_crate1", (1.6, 0.3, 0), parent=grp)
    crate(name + "_crate2", (1.55, -0.5, 0), parent=grp, size=0.45)
    return grp


# ---------------------------------------------------------------- props

def egg(name, loc, parent=None, scale=1.0):
    egg_m = flat_mat("egg", "#f5e6c8")
    return add_sphere(name, 1.0, egg_m, parent=parent, loc=loc,
                      scale=(0.045 * scale, 0.045 * scale, 0.06 * scale),
                      seg=14, rings=10)


def basket(name, loc, parent=None, eggs=3):
    """Woven basket with eggs peeking out. loc = ground point."""
    weave_m = flat_mat("basket_weave", "#8a6a42")
    grp = new_empty(name, parent=parent, loc=loc)
    add_cylinder(name + "_body", 0.22, 0.16, weave_m, parent=grp,
                 loc=(0, 0, 0.08), verts=18)
    add_torus(name + "_rim", 0.21, 0.025, weave_m, parent=grp,
              loc=(0, 0, 0.16))
    for i in range(eggs):
        ang = math.radians(i * (360.0 / max(1, eggs)) + 20)
        egg(name + "_egg%d" % i,
            (0.08 * math.cos(ang), 0.08 * math.sin(ang), 0.16),
            parent=grp)
    return grp


def nest(name, loc, eggs=3, parent=None):
    """Ground nest: woven torus rim + eggs. Returns (group, [egg objs]) so
    the master build can keyframe egg visibility (flock table)."""
    grp = new_empty(name, parent=parent, loc=loc)
    add_torus(name + "_rim", 0.28, 0.07, flat_mat("nest", "#c8a86a"),
              parent=grp, loc=(0, 0, 0.05), scale=(1, 1, 0.5))
    egg_objs = []
    for i in range(eggs):
        ang = math.radians(i * (360.0 / max(1, eggs)) + 30)
        egg_objs.append(egg(name + "_egg%d" % i,
                            (0.09 * math.cos(ang), 0.09 * math.sin(ang),
                             0.09),
                            parent=grp))
    return grp, egg_objs


def cooking_pot(name, loc, parent=None):
    """Dark iron pot on a tripod over a fire, with steam puffs.

    Returns dict(pot=group, flames=[...], steam=[...]) — the flames and
    steam are scale-keyed by the shots that use them (shot 4 lit, shot 10
    cold and empty); the pot itself is always visible once built."""
    iron_m = flat_mat("pot_iron", "#3a3a40")
    grp = new_empty(name, parent=parent, loc=loc)
    add_cylinder(name + "_pot", 0.34, 0.30, iron_m, parent=grp,
                 loc=(0, 0, 0.42), verts=20)
    add_torus(name + "_rim", 0.33, 0.03, iron_m, parent=grp,
              loc=(0, 0, 0.57))
    # tripod legs
    for i in range(3):
        ang = math.radians(i * 120)
        leg = add_cylinder(name + "_leg%d" % i, 0.025, 0.55,
                           flat_mat("wood_dark", "#5a3a24"), parent=grp,
                           loc=(0.22 * math.cos(ang), 0.22 * math.sin(ang),
                                0.26), verts=8)
        leg.rotation_euler = (math.radians(14) * math.sin(ang),
                              math.radians(-14) * math.cos(ang), 0)
    # flames: emissive cones (lit only in shot 4)
    flame_m = flat_mat("flame", "#e86a20")
    flame_m.node_tree.nodes["Principled BSDF"].inputs[
        "Emission Color"].default_value = (1.0, 0.45, 0.1, 1.0)
    flame_m.node_tree.nodes["Principled BSDF"].inputs[
        "Emission Strength"].default_value = 1.5
    flames = []
    for i, (dx, dy, s) in enumerate(((0, 0, 1.0), (0.12, 0.06, 0.7),
                                     (-0.11, -0.05, 0.75))):
        flames.append(add_cone(name + "_flame%d" % i, 0.09 * s, 0.005,
                               0.28 * s, flame_m, parent=grp,
                               loc=(dx, dy, 0.14)))
    # steam puffs: small pale spheres that rise (shot 4 only). Kept
    # small and staggered in x so they read as wisps, not a snowman
    # stack (the first version's 0.09-0.13 m balls stacked in a column).
    steam_m = flat_mat("steam", "#e8e8e8")
    steam = []
    for i, dx in enumerate((0.0, 0.08, -0.06)):
        steam.append(add_sphere(name + "_steam%d" % i, 0.07 + 0.015 * i,
                                steam_m, parent=grp,
                                loc=(dx, -0.01 * i, 0.75 + 0.12 * i),
                                seg=12, rings=8))
    return dict(pot=grp, flames=flames, steam=steam)


def crate(name, loc, parent=None, size=0.55):
    wood_m = flat_mat("crate_wood", "#a8823c")
    grp = new_empty(name, parent=parent, loc=loc)
    add_box(name + "_box", (size, size, size), wood_m, parent=grp,
            loc=(0, 0, size / 2))
    return grp


def sack(name, loc, parent=None):
    sack_m = flat_mat("sack", "#c8a86a")
    grp = new_empty(name, parent=parent, loc=loc)
    add_sphere(name + "_body", 1.0, sack_m, parent=grp, loc=(0, 0, 0.28),
               scale=(0.26, 0.26, 0.32))
    add_cone(name + "_top", 0.10, 0.03, 0.18, sack_m, parent=grp,
             loc=(0, 0, 0.62))
    return grp


def hay_bale(name, loc, parent=None):
    hay_m = flat_mat("hay", "#d8b25e")
    bale = add_cylinder(name, 0.42, 0.8, hay_m, parent=parent, loc=loc,
                        rot=(0, math.radians(90), 0), verts=20)
    bale.location = (loc[0], loc[1], 0.42)
    return bale


def tree(name, loc, scale=1.0, leaf="#5a8a3e"):
    trunk_m = flat_mat("trunk", "#6a4a2e")
    leaf_m = flat_mat("leaf_" + name, leaf)
    grp = new_empty(name, loc=loc)
    add_cylinder(name + "_trunk", 0.16 * scale, 2.4 * scale, trunk_m,
                 parent=grp, loc=(0, 0, 1.2 * scale), verts=10)
    blobs = [(0, 0, 3.0, 1.5), (0.9, 0.3, 2.5, 1.0), (-0.85, -0.2, 2.6, 1.05),
             (0.2, -0.7, 3.4, 0.9), (-0.3, 0.7, 3.5, 0.85)]
    for i, (x, y, z, r) in enumerate(blobs):
        b = add_sphere(name + "_leaf%d" % i, r * scale, leaf_m, parent=grp,
                       loc=(x * scale, y * scale, z * scale),
                       seg=10, rings=8, smooth_shade=False)
    return grp


def fence(name, start, end, parent=None):
    """Post-and-two-rail fence along a straight ground line."""
    wood_m = flat_mat("fence_wood", "#8a6a42")
    start = Vector(start)
    end = Vector(end)
    length = (end - start).length
    direction = (end - start).normalized()
    yaw = math.atan2(direction.y, direction.x)
    grp = new_empty(name, parent=parent, loc=((start + end) / 2).to_tuple())
    grp.rotation_euler = (0, 0, yaw)
    n_posts = max(2, int(length / 1.3) + 1)
    for i in range(n_posts):
        x = -length / 2 + i * (length / (n_posts - 1))
        add_box(name + "_post%d" % i, (0.09, 0.09, 0.95), wood_m,
                parent=grp, loc=(x, 0, 0.47))
    for z in (0.35, 0.72):
        add_box(name + "_rail%d" % int(z * 100), (length, 0.05, 0.09),
                wood_m, parent=grp, loc=(0, 0, z))
    return grp


def windmill(name, loc):
    """Stone tower + 4-blade rotor. Returns (group, rotor) — rotate the
    rotor about its local Y to spin the blades."""
    stone_m = flat_mat("mill_stone", "#c8b898")
    roof_m = flat_mat("mill_roof", "#b85c38")
    blade_m = flat_mat("mill_blade", "#f0e6cc")
    grp = new_empty(name, loc=loc)
    add_cone(name + "_tower", 1.7, 1.15, 6.0, stone_m, parent=grp,
             loc=(0, 0, 3.0), verts=12)
    add_cone(name + "_cap", 1.35, 0.1, 1.4, roof_m, parent=grp,
             loc=(0, 0, 6.6), verts=12)
    add_box(name + "_door", (0.8, 0.1, 1.7),
            flat_mat("wood_dark", "#5a3a24"), parent=grp,
            loc=(0, 1.62, 0.85))
    rotor = new_empty(name + "_rotor", parent=grp, loc=(0, 1.35, 5.6))
    add_sphere(name + "_hub", 0.22, blade_m, parent=rotor)
    for i in range(4):
        arm = new_empty(name + "_arm%d" % i, parent=rotor,
                        loc=(0, 0, 0))
        arm.rotation_euler = (0, math.radians(i * 90), 0)
        blade = add_box(name + "_blade%d" % i, (0.55, 0.06, 3.1), blade_m,
                        parent=arm, loc=(0, 0, 1.75))
        blade.rotation_euler = (math.radians(12), 0, 0)
    return grp, rotor


def flower_patch(name, loc, count=8, spread=1.5):
    """A few simple stem flowers for colour near houses."""
    stem_m = flat_mat("flower_stem", "#3e7a34")
    cols = ["#e86a8a", "#f5d76a", "#ffffff", "#c86ae8"]
    import random
    rnd = random.Random(hash(name) & 0xFFFF)
    grp = new_empty(name, loc=loc)
    for i in range(count):
        x = (rnd.random() - 0.5) * spread * 2
        y = (rnd.random() - 0.5) * spread
        h = 0.22 + rnd.random() * 0.12
        add_cylinder(name + "_stem%d" % i, 0.008, h, stem_m, parent=grp,
                     loc=(x, y, h / 2), verts=6)
        add_sphere(name + "_head%d" % i, 0.035,
                   flat_mat("flower_" + cols[i % len(cols)],
                            cols[i % len(cols)]),
                   parent=grp, loc=(x, y, h), seg=10, rings=8)
    return grp
