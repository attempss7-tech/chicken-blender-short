# build_proof.py — master script for Milestone 1 (proof shot).
#
# Builds Shot 6 end to end and saves scenes/proof_shot06.blend.
# Run from ~/workspace/blender_chicken:
#   ./tools/blender-4.2.23-linux-x64/blender --background \
#       --python scripts/build_proof.py
import os
import sys
import time

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

t0 = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)

import shot06  # noqa: E402

info = shot06.build()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "scenes", "proof_shot06.blend")
out = os.path.normpath(out)
bpy.ops.wm.save_as_mainfile(filepath=out)

n_mesh = sum(1 for o in bpy.context.scene.objects if o.type == "MESH")
n_all = len(bpy.context.scene.objects)
print("PROOF BUILD OK in %.1fs: %d objects (%d meshes), frames %d-%d"
      % (time.time() - t0, n_all, n_mesh,
         bpy.context.scene.frame_start, bpy.context.scene.frame_end))
print("saved:", out)
