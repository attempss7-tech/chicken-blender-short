# characters.py — reusable farmer / chicken builders for the Blender chicken short.
#
# Technique 1 (proof): flat-shaded 3D primitive characters (bean/sphere heads,
# capsule-ish bodies, cylinder limbs) with flat Principled materials in the
# CHARACTER_BIBLE.md colours, plus inverted-hull outlines (dark plum #241726).
# No armatures: parts are parented empties/meshes animated by keyframing
# object transforms. Walk cycles use analytic 2-bone IK so stance feet stay
# planted in world space.
#
# Local character frame: forward = +Y, up = +Z. Root empty sits on the ground;
# rotation.z (yaw) sets facing. arm_R / leg_R live at local +X, arm_L / leg_L
# at local -X.
#
# All materials are Principled BSDF only (Eevee-compatible, no Cycles-only
# nodes). Outline material uses a Backfacing -> Transparent mix so it renders
# correctly in both Cycles and Eevee.
import math

import bpy
from mathutils import Matrix, Vector

# ---------------------------------------------------------------- constants

OUTLINE_HEX = "#241726"          # dark plum outlines (v3 brief)
OUTLINE_THICKNESS = 0.009        # metres of outline shell offset

# Character bible constants (CHARACTER_BIBLE.md) — never per-shot.
FARMERS = {
    "A": dict(
        height=1.78, build=1.15, skin="#8a5a34", hair="#1a1210",
        hat=True, hat_col="#d8b25e", hat_band="#4a3a28",
        vest="#3a7a72", shirt="#f0e6cc", trousers="#2e3440", boots="#33261a",
        moustache=False, scarf=None, sash=None, belt=None,
    ),
    "B": dict(
        height=1.72, build=1.00, skin="#a06a42", hair="#241a12",
        hat=False, vest=None, shirt="#c09a4e", trousers="#6a4a2e",
        boots="#4a3220", moustache=True, scarf=None,
        sash="#a8823c", belt=None,
    ),
    "C": dict(
        height=1.66, build=0.90, skin="#b07a4e", hair="#241a12",
        hat=False, vest=None, shirt="#2e6a3e", trousers="#e8dcc0",
        boots="#5a3a24", moustache=False, scarf="#a84838",
        sash=None, belt="#5a3a24",
    ),
    # ---- supporting family (CHARACTER_BIBLE.md) — same builder, bible
    # colours/heights; simpler than the leads (fewer gesture keys).
    "Bwife": dict(
        height=1.60, build=0.95, skin="#96603a", hair="#241a12",
        hat=False, vest=None, shirt="#b08a44", trousers="#6a4a2e",
        boots="#4a3220", moustache=False, scarf=None,
        sash="#6a4a2e", belt=None,
        skirt="#b08a44", apron="#6a4a2e", bun=True,
    ),
    "Belder": dict(
        height=1.68, build=0.90, skin="#a87850", hair="#8a8078",
        hat=False, vest=None, shirt="#b8945a", trousers="#6a4a2e",
        boots="#4a3220", moustache=True, scarf=None,
        sash=None, belt=None, stick=True,
    ),
    "Chusband": dict(
        height=1.74, build=1.05, skin="#a87048", hair="#241a12",
        hat=False, vest=None, shirt="#357a46", trousers="#5a5248",
        boots="#5a3a24", moustache=False, scarf=None,
        sash=None, belt="#5a3a24", beard=True,
    ),
    "Cyouth": dict(
        height=1.58, build=0.85, skin="#b07a4e", hair="#1a1210",
        hat=False, vest=None, shirt="#4a8a58", trousers="#e8dcc0",
        boots="#5a3a24", moustache=False, scarf=None,
        sash=None, belt=None,
    ),
    "Awife": dict(
        height=1.64, build=0.95, skin="#8a5a34", hair="#1a1210",
        hat=False, vest=None, shirt="#f0e6cc", trousers="#f0e6cc",
        boots="#33261a", moustache=False, scarf=None,
        sash=None, belt=None,
        skirt="#f0e6cc", shawl="#3a7a72", bun=True, earrings=True,
    ),
    "Ahand": dict(
        height=1.74, build=1.05, skin="#8a5a34", hair="#1a1210",
        hat=True, hat_col="#d8b25e", hat_band="#4a3a28",
        vest=None, shirt="#3a7a72", trousers="#2e3440", boots="#33261a",
        moustache=False, scarf=None, sash=None, belt=None,
    ),
}

CHICKENS = {
    "hen": dict(
        scale=1.0, body="#f2ead8", wing="#b08a5e", neck="#f2ead8",
        tail="#b08a5e", comb="#c04030", beak="#e08a30", legs="#e08a30",
        comb_n=3, tail_n=1,
    ),
    "rooster": dict(
        scale=1.22, body="#f2ead8", wing="#b05030", neck="#b05030",
        tail="#2e6a4a", comb="#c04030", beak="#e08a30", legs="#e08a30",
        comb_n=5, tail_n=4,
    ),
    "chick": dict(
        scale=0.34, body="#f5d76a", wing="#e8c85a", neck="#f5d76a",
        tail="#f5d76a", comb="#e08a30", beak="#e08a30", legs="#e08a30",
        comb_n=0, tail_n=1,
    ),
}

# ---------------------------------------------------------------- colour

def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hx(hexcol):
    """'#rrggbb' -> linear RGB tuple for Blender colour inputs."""
    h = hexcol.lstrip("#")
    return tuple(_srgb_to_linear(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


# ---------------------------------------------------------------- materials

_mat_cache = {}


def flat_mat(name, hexcol, roughness=0.92):
    """Flat Principled material (Eevee + Cycles safe). Cached by name."""
    if name in _mat_cache:
        return _mat_cache[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*hx(hexcol), 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Specular IOR Level"].default_value = 0.3
    mat.diffuse_color = (*hx(hexcol), 1.0)  # Workbench MATERIAL colour mode
    _mat_cache[name] = mat
    return mat


def outline_material():
    """Dark plum inverted-hull material.

    The shell mesh has flipped normals, so the faces pointing at the camera
    are backfaces -> Transparent; the far-side faces are front faces -> dark
    plum. Renders the same in Cycles and Eevee. Backface culling is also on
    so Workbench (which ignores nodes) still shows the rim only.
    """
    if "Outline" in _mat_cache:
        return _mat_cache["Outline"]
    mat = bpy.data.materials.new("Outline")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*hx(OUTLINE_HEX), 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Backfacing"], mix.inputs["Fac"])
    nt.links.new(bsdf.outputs["BSDF"], mix.inputs[1])    # front-facing -> plum
    nt.links.new(transp.outputs["BSDF"], mix.inputs[2])  # back-facing -> clear
    nt.links.new(mix.outputs["Shader"],
                 nt.nodes["Material Output"].inputs["Surface"])
    mat.use_backface_culling = True
    mat.diffuse_color = (*hx(OUTLINE_HEX), 1.0)
    _mat_cache["Outline"] = mat
    return mat


# ---------------------------------------------------------------- mesh utils

def _link(obj):
    bpy.context.collection.objects.link(obj)
    return obj


def _mesh_transform(obj, matrix):
    obj.data.transform(matrix)
    obj.data.update()


def bake_scale(obj, sx, sy, sz):
    _mesh_transform(obj, Matrix.Diagonal(Vector((sx, sy, sz, 1.0))))


def translate_mesh(obj, dx, dy, dz):
    _mesh_transform(obj, Matrix.Translation(Vector((dx, dy, dz))))


def shade(obj, smooth=True):
    for p in obj.data.polygons:
        p.use_smooth = smooth


def new_empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "PLAIN_AXES"
    e.empty_display_size = 0.08
    _link(e)
    if parent is not None:
        e.parent = parent
    e.location = loc
    return e


def _finish(obj, mat, parent, loc, rot, outline, outline_t):
    if parent is not None:
        obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rot
    if mat is not None:
        obj.data.materials.append(mat)
    if outline:
        add_outline(obj, outline_t)
    return obj


def add_sphere(name, r, mat, parent=None, loc=(0, 0, 0), rot=(0, 0, 0),
               scale=(1, 1, 1), seg=20, rings=14, outline=False,
               outline_t=OUTLINE_THICKNESS, smooth_shade=True):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=seg, ring_count=rings, radius=r, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    bake_scale(obj, *scale)
    shade(obj, smooth_shade)
    return _finish(obj, mat, parent, loc, rot, outline, outline_t)


def add_cylinder(name, r, depth, mat, parent=None, loc=(0, 0, 0),
                 rot=(0, 0, 0), verts=16, outline=False,
                 outline_t=OUTLINE_THICKNESS, smooth_shade=True):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=r, depth=depth, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    shade(obj, smooth_shade)
    return _finish(obj, mat, parent, loc, rot, outline, outline_t)


def add_cone(name, r1, r2, depth, mat, parent=None, loc=(0, 0, 0),
             rot=(0, 0, 0), verts=16, outline=False,
             outline_t=OUTLINE_THICKNESS):
    bpy.ops.mesh.primitive_cone_add(
        vertices=verts, radius1=r1, radius2=r2, depth=depth,
        location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    shade(obj, True)
    return _finish(obj, mat, parent, loc, rot, outline, outline_t)


def add_box(name, dims, mat, parent=None, loc=(0, 0, 0), rot=(0, 0, 0),
            outline=False, outline_t=OUTLINE_THICKNESS):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    bake_scale(obj, dims[0], dims[1], dims[2])
    shade(obj, False)
    return _finish(obj, mat, parent, loc, rot, outline, outline_t)


def add_torus(name, major_r, minor_r, mat, parent=None, loc=(0, 0, 0),
              rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_r, minor_radius=minor_r,
        major_segments=24, minor_segments=10, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    bake_scale(obj, *scale)
    shade(obj, True)
    return _finish(obj, mat, parent, loc, rot, False, 0)


def add_outline(obj, thickness=OUTLINE_THICKNESS):
    """Inverted-hull outline shell: mesh offset along vertex normals,
    normals flipped, dark plum backfacing-transparent material. Parented to
    the part so it follows animation. Casts no shadow."""
    if obj.type != "MESH":
        return None
    mesh = obj.data.copy()
    mesh.update()
    for v in mesh.vertices:
        v.co += v.normal * thickness
    mesh.flip_normals()
    mesh.update()
    out = bpy.data.objects.new(obj.name + "_ol", mesh)
    _link(out)
    out.parent = obj
    out.location = (0, 0, 0)
    out.rotation_euler = (0, 0, 0)
    out.scale = (1, 1, 1)
    out.data.materials.append(outline_material())
    try:
        out.visible_shadow = False
    except AttributeError:
        pass
    return out


def sphere_cap_mesh(r, zmin_frac, sx=1.0, sy=1.0, sz=1.0,
                    segments=24, rings=16):
    """UV sphere with faces below zmin_frac*r removed (open cap for hair /
    headscarves). Scaled ellipsoid via the bmesh matrix."""
    import bmesh
    bm = bmesh.new()
    mat = Matrix.Diagonal(Vector((sx * r, sy * r, sz * r, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings,
                              radius=1.0, matrix=mat)
    zmin = zmin_frac * r * sz
    doomed = [f for f in bm.faces if f.calc_center_median().z < zmin]
    if doomed:
        bmesh.ops.delete(bm, geom=doomed, context="FACES")
    mesh = bpy.data.meshes.new("cap")
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def cap_object(name, mesh, mat, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    obj = bpy.data.objects.new(name, mesh)
    _link(obj)
    shade(obj, True)
    return _finish(obj, mat, parent, loc, rot, False, 0)


# ---------------------------------------------------------------- farmers

def build_farmer(key, name, loc=(0, 0, 0), yaw_deg=0.0):
    """Build one farmer from the bible constants. Returns a rig dict of the
    named parts plus proportions (used by the animation helpers)."""
    spec = FARMERS[key]
    H = spec["height"]
    build = spec["build"]
    skin = flat_mat("skin_" + key, spec["skin"])
    hair_m = flat_mat("hair_" + key, spec["hair"])
    shirt_m = flat_mat("shirt_" + key, spec["shirt"])
    trouser_m = flat_mat("trousers_" + key, spec["trousers"])
    boot_m = flat_mat("boots_" + key, spec["boots"])
    dark_m = flat_mat("dark", "#1a1210")

    # proportions (fractions of height)
    hip_z = 0.52 * H
    ankle_z = 0.05
    L1 = L2 = (hip_z - ankle_z) / 2.0
    shoulder_z = hip_z + 0.295 * H
    neck_z = shoulder_z + 0.055 * H
    head_r = 0.066 * H
    head_cz = neck_z + head_r * 1.15
    torso_cz = hip_z + 0.15 * H
    torso_rx, torso_ry, torso_rz = 0.11 * H * build, 0.072 * H * build, 0.15 * H
    upper_l, fore_l = 0.155 * H, 0.145 * H
    hip_dx = 0.062 * H
    sho_dx = 0.125 * H * build

    root = new_empty(name, loc=loc)
    root.rotation_euler = (0, 0, math.radians(yaw_deg))
    hips = new_empty(name + "_hips", parent=root, loc=(0, 0, hip_z))

    # ---- torso (bean) + vest / sash / belt
    torso = add_sphere(name + "_torso", 1.0, shirt_m, parent=hips,
                       loc=(0, 0, torso_cz - hip_z),
                       scale=(torso_rx, torso_ry, torso_rz), outline=True)
    if spec.get("vest"):
        vest_m = flat_mat("vest_" + key, spec["vest"])
        import bmesh
        bm = bmesh.new()
        mat = Matrix.Diagonal(Vector((torso_rx * 1.07, torso_ry * 1.10,
                                      torso_rz * 1.03, 1.0)))
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=20,
                                  radius=1.0, matrix=mat)
        # open front strip -> cream shirt shows through
        doomed = [f for f in bm.faces
                  if f.calc_center_median().y > 0.02
                  and abs(f.calc_center_median().x) < 0.085]
        if doomed:
            bmesh.ops.delete(bm, geom=doomed, context="FACES")
        mesh = bpy.data.meshes.new("vest")
        bm.to_mesh(mesh)
        bm.free()
        cap_object(name + "_vest", mesh, vest_m, parent=hips,
                   loc=(0, 0, torso_cz - hip_z))
        # cream collar ring at the neck
        add_torus(name + "_collar", 0.085, 0.022, shirt_m, parent=hips,
                  loc=(0, 0, neck_z - hip_z - 0.02), scale=(1, 1, 0.6))
    def waist_ring(z_rel):
        """Torus radii hugging the torso's elliptical cross-section at
        height z_rel (relative to hips). Returns (major_r, scale_x, scale_y)."""
        dz = z_rel - (torso_cz - hip_z)
        f = math.sqrt(max(0.05, 1.0 - (dz / torso_rz) ** 2))
        rx_at = torso_rx * f + 0.008
        ry_at = torso_ry * f + 0.008
        major = rx_at / 1.35
        return major, 1.35, ry_at / major

    if spec.get("sash"):
        sash_m = flat_mat("sash_" + key, spec["sash"])
        mj, sx, sy = waist_ring(0.06)
        add_torus(name + "_sash", mj, 0.030, sash_m, parent=hips,
                  loc=(0, 0, 0.06), scale=(sx, sy, 0.7))
    if spec.get("belt"):
        belt_m = flat_mat("belt_" + key, spec["belt"])
        mj, sx, sy = waist_ring(0.05)
        add_torus(name + "_belt", mj, 0.022, belt_m, parent=hips,
                  loc=(0, 0, 0.05), scale=(sx, sy, 0.6))
    # skirt (dress): cone from the waist to the ankles, hiding the legs.
    # Family members never walk, so the static legs underneath are fine.
    if spec.get("skirt"):
        skirt_m = flat_mat("skirt_" + key, spec["skirt"])
        skirt_h = hip_z - 0.02
        add_cone(name + "_skirt", 0.20 * H, 0.13 * H * build, skirt_h,
                 skirt_m, parent=hips, loc=(0, 0, -skirt_h / 2 + 0.04),
                 verts=20, outline=True)
    if spec.get("apron"):
        apron_m = flat_mat("apron_" + key, spec["apron"])
        add_box(name + "_apron", (0.20 * H, 0.02, 0.30 * H), apron_m,
                parent=hips, loc=(0, 0.075 * H, -0.16 * H))
    if spec.get("shawl"):
        shawl_m = flat_mat("shawl_" + key, spec["shawl"])
        add_sphere(name + "_shawl", 1.0, shawl_m, parent=hips,
                   loc=(0, 0, shoulder_z - hip_z - 0.03),
                   scale=(0.15 * H * build, 0.10 * H * build, 0.055 * H),
                   outline=True)

    # ---- head group
    head_g = new_empty(name + "_head", parent=hips,
                       loc=(0, 0, head_cz - hip_z))
    add_sphere(name + "_headmesh", head_r, skin, parent=head_g,
               scale=(1.0, 0.94, 1.06), outline=True)
    # eyes / nose / mouth
    er = 0.13 * head_r
    add_sphere(name + "_eyeL", er, dark_m, parent=head_g,
               loc=(-0.38 * head_r, 0.86 * head_r, 0.14 * head_r))
    add_sphere(name + "_eyeR", er, dark_m, parent=head_g,
               loc=(0.38 * head_r, 0.86 * head_r, 0.14 * head_r))
    add_sphere(name + "_nose", 0.10 * head_r, skin, parent=head_g,
               loc=(0, 0.95 * head_r, -0.06 * head_r))
    add_sphere(name + "_mouth", 1.0, flat_mat("mouth", "#4a2a20"),
               parent=head_g, loc=(0, 0.90 * head_r, -0.34 * head_r),
               scale=(0.24 * head_r, 0.07 * head_r, 0.055 * head_r))
    if spec.get("moustache"):
        for s in (-1, 1):
            add_sphere(name + "_moust%d" % s, 1.0, hair_m, parent=head_g,
                       loc=(s * 0.16 * head_r, 0.88 * head_r,
                            -0.24 * head_r),
                       scale=(0.22 * head_r, 0.08 * head_r, 0.07 * head_r),
                       rot=(0, 0, math.radians(-18 * s)))
    if spec.get("beard"):
        add_sphere(name + "_beard", 1.0, hair_m, parent=head_g,
                   loc=(0, 0.72 * head_r, -0.62 * head_r),
                   scale=(0.55 * head_r, 0.35 * head_r, 0.42 * head_r))
    if spec.get("bun"):
        add_sphere(name + "_bun", 0.34 * head_r, hair_m, parent=head_g,
                   loc=(0, -0.92 * head_r, 0.30 * head_r))
    if spec.get("earrings"):
        ear_m = flat_mat("gold", "#e8b83a")
        for s in (-1, 1):
            add_sphere(name + "_ear%d" % s, 0.10 * head_r, ear_m,
                       parent=head_g,
                       loc=(s * 0.95 * head_r, 0, -0.12 * head_r))
    # hair cap / headscarf / straw hat
    if spec.get("scarf"):
        scarf_m = flat_mat("scarf_" + key, spec["scarf"])
        cap_object(name + "_scarf",
                   sphere_cap_mesh(head_r * 1.08, -0.55, 1.0, 1.0, 1.0),
                   scarf_m, parent=head_g, loc=(0, -0.01, 0.01))
        add_sphere(name + "_scarfknot", 0.28 * head_r, scarf_m,
                   parent=head_g, loc=(0, -0.95 * head_r, -0.15 * head_r))
        for s in (-1, 1):
            add_box(name + "_scarfend%d" % s,
                    (0.07, 0.02, 0.14), scarf_m, parent=head_g,
                    loc=(s * 0.05, -1.0 * head_r, -0.40 * head_r),
                    rot=(math.radians(8), 0, math.radians(10 * s)))
    else:
        cap_object(name + "_hair",
                   sphere_cap_mesh(head_r * 1.05, -0.10, 1.0, 1.0, 1.0),
                   hair_m, parent=head_g, loc=(0, -0.005, 0.018))
    if spec.get("hat"):
        hat_m = flat_mat("hat_" + key, spec["hat_col"])
        band_m = flat_mat("hatband_" + key, spec["hat_band"])
        add_cylinder(name + "_hatbrim", 0.135 * H, 0.012 * H, hat_m,
                     parent=head_g, loc=(0, 0, 0.82 * head_r),
                     verts=24, outline=True, outline_t=0.006)
        add_sphere(name + "_hatdome", 0.075 * H, hat_m, parent=head_g,
                   loc=(0, 0, 0.92 * head_r), scale=(1, 1, 0.72),
                   outline=True, outline_t=0.006)
        add_cylinder(name + "_hatband", 0.078 * H, 0.028 * H, band_m,
                     parent=head_g, loc=(0, 0, 0.86 * head_r), verts=24)

    # ---- arms: shoulder pivot -> upper arm -> elbow pivot -> forearm + hand
    arms = {}
    for side, sx in (("L", -1), ("R", 1)):
        sho = new_empty(name + "_sho" + side, parent=hips,
                        loc=(sx * sho_dx, 0, shoulder_z - hip_z))
        ua = add_cylinder(name + "_upperarm" + side, 0.034 * H, upper_l,
                          shirt_m, parent=sho, outline=True)
        translate_mesh(ua, 0, 0, -upper_l / 2.0)
        add_sphere(name + "_shoulder" + side, 0.045 * H, shirt_m, parent=sho)
        elb = new_empty(name + "_elb" + side, parent=sho,
                        loc=(0, 0, -upper_l))
        fa = add_cylinder(name + "_forearm" + side, 0.030 * H, fore_l,
                          shirt_m, parent=elb, outline=True)
        translate_mesh(fa, 0, 0, -fore_l / 2.0)
        add_sphere(name + "_hand" + side, 0.030 * H, skin, parent=elb,
                   loc=(0, 0, -fore_l - 0.015))
        arms[side] = dict(shoulder=sho, elbow=elb)

    # ---- legs: hip pivot -> thigh -> knee pivot -> shin -> ankle -> foot
    legs = {}
    for side, sx in (("L", -1), ("R", 1)):
        hip = new_empty(name + "_hip" + side, parent=hips,
                        loc=(sx * hip_dx, 0, 0))
        th = add_cylinder(name + "_thigh" + side, 0.042 * H, L1,
                          trouser_m, parent=hip, outline=True)
        translate_mesh(th, 0, 0, -L1 / 2.0)
        knee = new_empty(name + "_knee" + side, parent=hip, loc=(0, 0, -L1))
        sh = add_cylinder(name + "_shin" + side, 0.036 * H, L2,
                          trouser_m, parent=knee, outline=True)
        translate_mesh(sh, 0, 0, -L2 / 2.0)
        ank = new_empty(name + "_ankle" + side, parent=knee, loc=(0, 0, -L2))
        add_sphere(name + "_foot" + side, 1.0, boot_m, parent=ank,
                   loc=(0, 0.045, -0.025),
                   scale=(0.050, 0.115, 0.025), outline=True,
                   outline_t=0.006)
        legs[side] = dict(hip=hip, knee=knee, ankle=ank)

    # walking stick (B-elder, late shots): parented to the root so it
    # stands beside him; hidden by scale until shot 10.
    stick = None
    if spec.get("stick"):
        stick_m = flat_mat("stick_wood", "#6a4a2e")
        stick = add_cylinder(name + "_stick", 0.018, 0.95, stick_m,
                             parent=root, loc=(0.24, 0.08, 0.475),
                             verts=8)
        add_sphere(name + "_stickknob", 0.03, stick_m, parent=root,
                   loc=(0.24, 0.08, 0.96), seg=10, rings=8)

    return dict(
        key=key, name=name, root=root, hips=hips, torso=torso,
        head=head_g, arms=arms, legs=legs, stick=stick,
        height=H, hip_z=hip_z, ankle_z=ankle_z, L1=L1, L2=L2,
        hip_dx=hip_dx, shoulder_z=shoulder_z, yaw=math.radians(yaw_deg),
    )


# ---------------------------------------------------------------- chickens

def build_chicken(kind, name, loc=(0, 0, 0), yaw_deg=0.0):
    """Hen / rooster / chick. Returns rig dict (root, body, head, tail)."""
    spec = CHICKENS[kind]
    s = spec["scale"]
    body_m = flat_mat("chicken_body_" + kind, spec["body"])
    wing_m = flat_mat("chicken_wing_" + kind, spec["wing"])
    neck_m = flat_mat("chicken_neck_" + kind, spec["neck"])
    tail_m = flat_mat("chicken_tail_" + kind, spec["tail"])
    comb_m = flat_mat("chicken_comb_" + kind, spec["comb"])
    beak_m = flat_mat("chicken_beak_" + kind, spec["beak"])
    leg_m = flat_mat("chicken_legs_" + kind, spec["legs"])
    dark_m = flat_mat("dark", "#1a1210")

    root = new_empty(name, loc=loc)
    root.rotation_euler = (0, 0, math.radians(yaw_deg))
    body_g = new_empty(name + "_body", parent=root, loc=(0, 0, 0.30 * s))

    add_sphere(name + "_belly", 1.0, body_m, parent=body_g,
               scale=(0.17 * s, 0.12 * s, 0.13 * s), outline=True)
    # wings (both sides)
    for sx in (-1, 1):
        add_sphere(name + "_wing%d" % sx, 1.0, wing_m, parent=body_g,
                   loc=(sx * 0.13 * s, -0.01, 0.01),
                   scale=(0.03 * s, 0.10 * s, 0.08 * s))
    # tail
    tail_g = new_empty(name + "_tail", parent=body_g, loc=(0, -0.15 * s, 0.06 * s))
    if spec["tail_n"] == 1:
        add_sphere(name + "_tail0", 1.0, tail_m, parent=tail_g,
                   loc=(0, -0.02, 0.05 * s),
                   scale=(0.05 * s, 0.09 * s, 0.09 * s),
                   rot=(math.radians(-35), 0, 0))
    else:
        # rooster tail: thin swept-back feathers (first version read as one
        # solid green fin)
        for i in range(spec["tail_n"]):
            ang = math.radians(-30 - i * 12)
            add_sphere(name + "_tail%d" % i, 1.0, tail_m, parent=tail_g,
                       loc=(0, -0.02 - i * 0.025, 0.05 * s + i * 0.018),
                       scale=(0.022 * s, 0.04 * s, 0.10 * s),
                       rot=(ang, 0, 0))
    # neck + head group (peck pivot)
    head_g = new_empty(name + "_head", parent=body_g,
                       loc=(0, 0.13 * s, 0.07 * s))
    add_cylinder(name + "_neck", 0.032 * s, 0.11 * s, neck_m, parent=head_g,
                 loc=(0, 0.01, 0.04 * s), rot=(math.radians(12), 0, 0))
    add_sphere(name + "_headmesh", 0.055 * s, body_m, parent=head_g,
               loc=(0, 0.03 * s, 0.105 * s), outline=True, outline_t=0.005)
    add_cone(name + "_beak", 0.018 * s, 0.002, 0.05 * s, beak_m,
             parent=head_g, loc=(0, 0.085 * s, 0.10 * s),
             rot=(math.radians(90), 0, 0))
    for i in range(spec["comb_n"]):
        add_sphere(name + "_comb%d" % i, 0.013 * s, comb_m, parent=head_g,
                   loc=(0, (0.005 + i * 0.016) * s, 0.155 * s))
    if kind == "rooster":
        add_sphere(name + "_wattle", 0.02 * s, comb_m, parent=head_g,
                   loc=(0, 0.06 * s, 0.065 * s),
                   scale=(1, 1, 1.4))
    for sx in (-1, 1):
        add_sphere(name + "_eye%d" % sx, 0.008 * s, dark_m, parent=head_g,
                   loc=(sx * 0.035 * s, 0.055 * s, 0.115 * s))
    # legs + feet (static; hens peck in place in shot 6)
    for sx in (-1, 1):
        add_cylinder(name + "_leg%d" % sx, 0.008 * s, 0.17 * s, leg_m,
                     parent=root, loc=(sx * 0.05 * s, 0, 0.085 * s))
        for j, ang in enumerate((-30, 0, 30)):
            add_box(name + "_toe%d_%d" % (sx, j),
                    (0.008 * s, 0.05 * s, 0.006 * s), leg_m, parent=root,
                    loc=(sx * 0.05 * s, 0.02 * s, 0.004),
                    rot=(0, 0, math.radians(ang)))
    return dict(kind=kind, name=name, root=root, body=body_g,
                head=head_g, tail=tail_g, scale=s)


# ---------------------------------------------------------------- keyframes

def kf(obj, frame, data_path="rotation_euler"):
    obj.keyframe_insert(data_path=data_path, frame=frame)


def set_linear(obj):
    """Make every keyframe point on the object's action LINEAR."""
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def set_linear_range(obj, f_min, f_max):
    """Make the keyframe points in [f_min, f_max] LINEAR (leaves keys
    from other shots untouched — the full build shares rigs across
    shots, so a blanket set_linear would re-linearize their eases)."""
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if f_min <= kp.co.x <= f_max:
                    kp.interpolation = "LINEAR"


def set_bezier(obj):
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"


def _smootherstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)


def _ease_walk(t):
    """Gentle accel/decel for the walk (feet still plant: foot motion is
    driven by eased distance, not by time)."""
    return 0.65 * t + 0.35 * _smootherstep(t)


def _solve_leg(fwd, down, L1, L2):
    """2-bone IK in the sagittal plane. fwd = foot forward of hip (m),
    down = foot below hip (m). Returns (thigh_rot_x, knee_rot_x, shin_rot_x)
    with the knee bending backward (human knee)."""
    d = math.hypot(fwd, down)
    d = max(0.05, min(d, L1 + L2 - 0.005))
    alpha = math.atan2(fwd, down)                       # hip->foot from vertical
    beta = math.acos(max(-1.0, min(1.0,
                                   (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    phi = math.pi - math.acos(max(-1.0, min(1.0,
                                            (L1 * L1 + L2 * L2 - d * d) /
                                            (2 * L1 * L2))))
    thigh = alpha + beta
    shin = thigh - phi
    return thigh, -phi, shin


def animate_walk(rig, start, end, f_start, f_end, f_close_end=None,
                 step_len=0.40, lift=0.09, key_every=2, crouch=0.04):
    """Planted-feet walk along a straight ground path.

    Gait model (fixed 2026-11-12 after a foot-slide audit found 3-5 cm of
    stance drift + feet lifting): steps are CENTRED on the stance foot's
    plant, so the body passes over the stance foot with |fwd| <= S/2
    (the first version had the body start each step directly over the
    stance foot, so the stance leg had to reach a full step behind the
    hip — beyond the leg's length — and the IK clamp dragged the foot).
    The hips also crouch ~4 cm during the walk (knees stay slightly bent,
    as in a real gait) with the bob phased high mid-step / low at the
    step boundaries, when the leg is most extended. Step length is
    clamped to what the leg can actually reach.
    Stance feet stay fixed in world space; the swing foot moves between
    plants as a function of eased body distance. Legs are solved with
    analytic 2-bone IK each keyframe. After f_end the swing foot plants
    beside the stance foot by f_close_end (default f_end + 12).
    Root yaw must already face along (end - start).
    """
    if f_close_end is None:
        f_close_end = f_end + 12
    start = Vector((start[0], start[1], 0.0))
    end = Vector((end[0], end[1], 0.0))
    dist = (end - start).length
    direction = (end - start).normalized()
    yaw = rig["yaw"]
    # world lateral vector for local +X (right side)
    lat = Vector((math.cos(yaw), math.sin(yaw), 0.0))
    L1, L2 = rig["L1"], rig["L2"]
    leg_len = L1 + L2
    hip_z, ankle_z, hip_dx = rig["hip_z"], rig["ankle_z"], rig["hip_dx"]
    bob_amp = 0.012
    hip_walk = hip_z - crouch
    # max step the leg can reach: at a step boundary the stance foot is
    # S/2 behind/ahead of the hip with the bob at zero
    down_bnd = hip_walk - ankle_z
    reach = math.sqrt(max(0.01, (leg_len - 0.015) ** 2 - down_bnd ** 2))
    s_max = 2.0 * reach
    s_use = min(step_len, s_max)
    n_steps = max(1, round(dist / s_use))
    S = dist / n_steps
    if S > s_max:  # keep the reach margin even if it means more steps
        n_steps = max(1, math.ceil(dist / s_max))
        S = dist / n_steps
    root, hips = rig["root"], rig["hips"]

    def foot_world(plant_d, side, lift_z=0.0):
        """World ankle position for a foot planted at distance plant_d."""
        sgn = 1.0 if side == "R" else -1.0
        return (start + direction * plant_d + lat * (sgn * hip_dx)
                + Vector((0, 0, ankle_z + lift_z)))

    def pose_at(f):
        """Compute and keyframe the full pose at frame f."""
        if f <= f_end:
            t = (f - f_start) / max(1, f_end - f_start)
            pD = _ease_walk(t) * dist
            # step k spans pD in [(k-0.5)S, (k+0.5)S], stance foot at kS;
            # k=0 is a half-step (pD 0 -> S/2, R swings 0 -> S)
            k = min(n_steps, int((pD + 0.5 * S) // S)) if S > 0 else 0
            if k == 0:
                u = min(1.0, pD / (0.5 * S)) if S > 0 else 0.0
                stance_side, swing_side = "L", "R"
                swing_from, swing_to = 0.0, S
                stance_d = 0.0
                bob = bob_amp * math.sin(math.pi * u)
            else:
                u = (pD - (k - 0.5) * S) / S if S > 0 else 0.0
                u = max(0.0, min(1.0, u))
                stance_side = "L" if k % 2 == 0 else "R"
                swing_side = "R" if stance_side == "L" else "L"
                swing_from, swing_to = (k - 1) * S, (k + 1) * S
                stance_d = k * S
                bob = bob_amp * math.sin(math.pi * u)
            su = _smootherstep(u)
            swing_d = swing_from + (swing_to - swing_from) * su
            swing_lift = math.sin(math.pi * u) * lift
            sway = 0.02 * (1.0 if stance_side == "R" else -1.0) * math.sin(math.pi * u)
            phase = math.pi * pD / S if S > 0 else 0.0
            # ease the crouch in over the first half-step, and scale the
            # bob by it: an un-crouched hip plus full bob puts the hip
            # ABOVE standing height, beyond the leg's reach (foot lifts)
            crouch_f = _smootherstep(min(1.0, pD / (0.5 * S))) if S > 0 else 1.0
            bob = bob * crouch_f
            hip_eff = hip_z - crouch * crouch_f
        else:
            # closing step: the swing foot plants beside the stance foot
            # (at pD=dist it is mid-swing, directly beside it, lifted)
            pD = dist
            u = (f - f_end) / max(1, f_close_end - f_end)
            su = _smootherstep(u)
            stance_side = "L" if n_steps % 2 == 0 else "R"
            swing_side = "R" if stance_side == "L" else "L"
            swing_d = n_steps * S
            swing_lift = lift * (1.0 - su)
            stance_d = n_steps * S
            bob = 0.0
            sway = 0.0
            phase = math.pi * n_steps
            hip_eff = hip_z - crouch * (1.0 - su)
        body_pos = start + direction * pD
        root.location = (body_pos.x, body_pos.y, 0.0)
        kf(root, f, "location")
        hips.location = (sway, 0.0, hip_eff + bob)
        kf(hips, f, "location")
        # legs via IK (in root-local frame)
        cos_y, sin_y = math.cos(-yaw), math.sin(-yaw)
        for side in ("L", "R"):
            if side == swing_side:
                fw = foot_world(swing_d, side, swing_lift)
            else:
                fw = foot_world(stance_d, side, 0.0)
            # to root-local: rotate by -yaw, subtract body pos
            rel = fw - Vector((body_pos.x, body_pos.y, 0.0))
            ly = rel.x * sin_y + rel.y * cos_y
            fwd = ly
            down = (hip_eff + bob) - fw.z
            thigh, knee, shin = _solve_leg(fwd, down, L1, L2)
            leg = rig["legs"][side]
            leg["hip"].rotation_euler = (thigh, 0, 0)
            kf(leg["hip"], f)
            leg["knee"].rotation_euler = (knee, 0, 0)
            kf(leg["knee"], f)
            # stance foot stays flat; swing foot droops its toe mid-swing
            # (natural plantarflex) and flattens again at plant
            if side == swing_side:
                droop = 0.55 * math.sin(math.pi * u)
                leg["ankle"].rotation_euler = (-shin * (1.0 - droop), 0, 0)
            else:
                leg["ankle"].rotation_euler = (-shin, 0, 0)
            kf(leg["ankle"], f)
        # arm swing (contralateral) + slight torso counter-rotation
        if f <= f_end:
            arm_amp = 0.28
        else:
            arm_amp = 0.28 * (1.0 - u)
        rig["arms"]["R"]["shoulder"].rotation_euler = (
            arm_amp * math.sin(phase), 0, 0)
        kf(rig["arms"]["R"]["shoulder"], f)
        rig["arms"]["L"]["shoulder"].rotation_euler = (
            -arm_amp * math.sin(phase), 0, 0)
        kf(rig["arms"]["L"]["shoulder"], f)
        for side in ("L", "R"):
            rig["arms"][side]["elbow"].rotation_euler = (0.12, 0, 0)
            kf(rig["arms"][side]["elbow"], f)
        rig["torso"].rotation_euler = (0, 0, 0.03 * math.sin(phase))
        kf(rig["torso"], f, "rotation_euler")

    f = f_start
    while f <= f_close_end:
        pose_at(f)
        f += key_every
    if (f_close_end - f_start) % key_every:
        pose_at(f_close_end)
    # settle to a neutral stand at the end of the close
    for side in ("L", "R"):
        leg = rig["legs"][side]
        leg["hip"].rotation_euler = (0, 0, 0)
        kf(leg["hip"], f_close_end)
        leg["knee"].rotation_euler = (0, 0, 0)
        kf(leg["knee"], f_close_end)
        leg["ankle"].rotation_euler = (0, 0, 0)
        kf(leg["ankle"], f_close_end)
        rig["arms"][side]["shoulder"].rotation_euler = (0, 0, 0)
        kf(rig["arms"][side]["shoulder"], f_close_end)
        rig["arms"][side]["elbow"].rotation_euler = (0.05, 0, 0)
        kf(rig["arms"][side]["elbow"], f_close_end)
    rig["torso"].rotation_euler = (0, 0, 0)
    kf(rig["torso"], f_close_end, "rotation_euler")
    hips.location = (0, 0, hip_z)
    kf(hips, f_close_end, "location")
    for obj in (root, hips, rig["torso"]):
        set_linear_range(obj, f_start, f_close_end)
    for side in ("L", "R"):
        for part in rig["legs"][side].values():
            set_linear_range(part, f_start, f_close_end)
        for part in rig["arms"][side].values():
            set_linear_range(part, f_start, f_close_end)
    return dict(n_steps=n_steps, step_len=S, s_max=s_max)


def stand_still(rig, f_start, f_end):
    """Keyframe a neutral standing pose (used before/after walks so the
    character does not drift between keyed ranges)."""
    for f in (f_start, f_end):
        rig["root"].location = (rig["root"].location.x,
                                rig["root"].location.y, 0.0)
        kf(rig["root"], f, "location")
        rig["hips"].location = (0, 0, rig["hip_z"])
        kf(rig["hips"], f, "location")
        for side in ("L", "R"):
            for part in rig["legs"][side].values():
                part.rotation_euler = (0, 0, 0)
                kf(part, f)
            rig["arms"][side]["shoulder"].rotation_euler = (0, 0, 0)
            kf(rig["arms"][side]["shoulder"], f)
            rig["arms"][side]["elbow"].rotation_euler = (0.05, 0, 0)
            kf(rig["arms"][side]["elbow"], f)
        rig["torso"].rotation_euler = (0, 0, 0)
        kf(rig["torso"], f, "rotation_euler")


def idle_breath(rig, f_start, f_end, amp=0.015, period=120):
    """Gentle torso breathing (scale) + tiny head sway. Keyframes every
    quarter period; Bezier interpolation keeps it smooth."""
    torso = rig["torso"]
    base = torso.scale
    f = f_start
    while f <= f_end:
        ph = 2 * math.pi * (f - f_start) / period
        s = 1.0 + amp * math.sin(ph)
        torso.scale = (base.x * (2.0 - s), base.y * (2.0 - s), base.z * s)
        kf(torso, f, "scale")
        rig["head"].rotation_euler = (0, 0, 0.02 * math.sin(ph + 0.6))
        kf(rig["head"], f)
        f += period // 4
    kf(torso, f_end, "scale")


def head_keys(rig, keys):
    """keys: list of (frame, yaw_deg, pitch_deg) for the head group."""
    for f, yaw, pitch in keys:
        rig["head"].rotation_euler = (math.radians(pitch), 0,
                                      math.radians(yaw))
        kf(rig["head"], f)


def arm_keys(rig, side, keys):
    """keys: list of (frame, shoulder_x_deg, elbow_x_deg).

    shoulder_x > 0 swings the arm forward (+Y local); elbow_x > 0 bends the
    forearm forward relative to the upper arm."""
    arm = rig["arms"][side]
    for f, sho, elb in keys:
        arm["shoulder"].rotation_euler = (math.radians(sho), 0, 0)
        kf(arm["shoulder"], f)
        arm["elbow"].rotation_euler = (math.radians(elb), 0, 0)
        kf(arm["elbow"], f)


def peck_cycle(rig, f_start, f_end, period=28, depth=0.65, phase=0.0):
    """Hen peck: head group pitches down (negative rotation.x) and back up
    on a smooth cycle, with a small body bob. Keyframes every ~quarter
    period."""
    head = rig["head"]
    body = rig["body"]
    step = max(2, period // 4)
    f = f_start
    while f <= f_end:
        ph = 2 * math.pi * ((f - f_start) / period) + phase
        # down fast, up slower: shape the sine
        v = math.sin(ph)
        pitch = -depth * max(0.0, v) ** 0.8
        head.rotation_euler = (pitch, 0, 0)
        kf(head, f)
        body.location = (0, 0, 0.30 * rig["scale"] - 0.012 * max(0.0, v))
        kf(body, f, "location")
        f += step
    kf(head, f_end)
    kf(body, f_end, "location")


def animate_hen_walk(rig, waypoints, f_start, f_end, bob=0.012,
                     bob_period=14, key_every=4):
    """Walk a hen along ground waypoints [(x, y), ...] between frames.

    Keyframes root location (linear between waypoints, time split by
    segment length), root yaw facing the travel direction, and a small
    body bob. Hens walk ~0.4 m/s — keep total distance modest for the
    frame range (a hen crossing 2 m needs ~150 frames). Legs are static
    (no per-leg cycle at 0.45 m scale); the bob + head sway sell the
    walk in wides. Returns the total distance walked.
    """
    if len(waypoints) < 2 or f_end <= f_start:
        return 0.0
    pts = [Vector((p[0], p[1], 0.0)) for p in waypoints]
    seg_len = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seg_len)
    if total < 0.01:
        return 0.0
    root, body = rig["root"], rig["body"]
    base_z = 0.30 * rig["scale"]

    def pose_at(f):
        t = (f - f_start) / (f_end - f_start)
        d = t * total
        acc = 0.0
        seg = 0
        for i, L in enumerate(seg_len):
            if d <= acc + L or i == len(seg_len) - 1:
                seg = i
                break
            acc += L
        u = (d - acc) / seg_len[seg] if seg_len[seg] > 0 else 0.0
        u = max(0.0, min(1.0, u))
        pos = pts[seg].lerp(pts[seg + 1], u)
        root.location = (pos.x, pos.y, 0.0)
        kf(root, f, "location")
        # yaw: local forward is +Y, so yaw = atan2(-dx, dy)
        dv = pts[seg + 1] - pts[seg]
        yaw = math.atan2(-dv.x, dv.y)
        root.rotation_euler = (0, 0, yaw)
        kf(root, f)
        ph = 2 * math.pi * (f - f_start) / bob_period
        body.location = (0, 0, base_z + bob * abs(math.sin(ph)))
        kf(body, f, "location")
        rig["head"].rotation_euler = (0.05 * math.sin(ph), 0, 0)
        kf(rig["head"], f)

    f = f_start
    while f <= f_end:
        pose_at(f)
        f += key_every
    if (f_end - f_start) % key_every:
        pose_at(f_end)
    set_linear(root)
    set_linear(body)
    return total
