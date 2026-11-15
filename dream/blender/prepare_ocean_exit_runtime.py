"""Attach explicit C++ material IDs and navigation to the active Blender scene.

Run in the live Blender MCP with DREAM_OceanExitWater active, then run
export_runtime.py in that same Blender session.
"""
import bpy
import json
from pathlib import Path

scene = bpy.context.scene
if scene.name != "DREAM_OceanExitWater":
    raise RuntimeError(f"Expected the isolated ocean-water candidate, got {scene.name}")

# Stable IDs are serialized in the DREAMM02 material table. The shader kinds
# are interpreted by the native OpenGL profile 5 without changing older scenes.
materials = {
    "cream_enamel": (0, 10),
    "exit_here": (1, 8),
    "exit_lamp": (2, 7),
    "frame": (3, 0),
    "interior_water": (4, 4),
    "ocean": (5, 4),
    "pink_ceramic": (6, 3),
    "pushbar": (7, 0),
    "submerged_bed": (8, 0),
}
used = {material.name: material for obj in scene.objects if obj.type == "MESH"
        for material in obj.data.materials}
if len(used) != len(materials):
    raise RuntimeError(f"Material inventory changed: {sorted(used)}")
for suffix, (material_id, kind) in materials.items():
    material = used[f"MAT-DREAM-oceanwater-{suffix}"]
    shader = next((node for node in material.node_tree.nodes
                   if node.type == "BSDF_PRINCIPLED"), None)
    if shader is None:
        raise RuntimeError(f"Missing Principled shader: {material.name}")
    material["dream_id"] = material_id
    material["kind"] = kind
    material["roughness"] = float(shader.inputs["Roughness"].default_value)
    material["metallic"] = float(shader.inputs["Metallic"].default_value)
    material["opacity"] = 0.0
    material["albedo_variant"] = 0.0

for suffix in ("interior_water", "ocean"):
    scene.objects[f"GEO-DREAM-oceanwater-{suffix}"]["dream_skip_ao"] = True

camera = scene.camera
plan = json.loads((Path(__file__).resolve().with_name("ocean_exit_plan.json")).read_text(encoding="utf8"))
camera_fit = plan["primary_camera"]
eye_height = camera.location.z - (-0.75)
# Blender's fitted principal point is 224.10 px at an 850 px render height.
camera_shift_ndc = 1.0 - 2.0 * 224.10021449508235 / 850.0
runtime = [
    f"camera {camera.location.x:.9f} {camera.location.y:.9f} {camera.location.z:.9f} {camera_fit['yaw_rad']:.12f} {camera_fit['pitch_rad']:.12f}",
    f"camera_roll {camera_fit['roll_rad']:.12f}",
    f"camera_shift_y {camera_shift_ndc:.12f}",
    "fov 0.85",
    "reflection 0.0",
    "far_clip 500",
    "environment 5",
    "exposure 0",
    f"eye_height {eye_height:.9f}",
    "step_limits 0.18 0.18",
    "bounds -1.55 1.55 -2.30 28.0",
    "surface -1.55 -2.30 1.55 28.0 -0.75",
    "capsule -0.90 -2.40 -0.90 1.70 0.26",
    "capsule 0.90 -2.40 0.90 1.70 0.26",
    "light 0.0 2.2 2.9 3.80 3.10 2.70 2.6 0",
    "light 0.0 -1.0 2.6 1.60 1.85 2.20 2.5 0",
    "light -0.4 6.5 1.8 3.00 0.12 1.20 1.2 0",
]
scene["dream_runtime_config"] = json.dumps(runtime)
print(json.dumps({"scene": scene.name, "materials": len(used),
                  "camera_shift_ndc": camera_shift_ndc,
                  "runtime_settings": len(runtime), "kind_counts": {
                      str(kind): sum(1 for _, value in materials.values() if value == kind)
                      for kind in sorted({value for _, value in materials.values()})
                  }}))
