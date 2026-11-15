# Mide Walk y Jog sobre los huesos del pie: despeje, velocidad y dispersion del pie apoyado, rebote de cadera.
import bpy
arm = bpy.data.objects["SN_Armature"]
ad = arm.animation_data
ad.use_nla = False
MEAS = {}
for clip in ("Walk", "Jog"):
    act = bpy.data.actions[clip]
    ad.action = act
    n = int(act.frame_range[1])
    rows = []
    for f in range(1, n + 1):
        bpy.context.scene.frame_set(f)
        L = arm.matrix_world @ arm.pose.bones["LeftFoot"].head
        R = arm.matrix_world @ arm.pose.bones["RightFoot"].head
        hz = (arm.matrix_world @ arm.pose.bones["Hips"].head).z
        rows.append((L.y, L.z, R.y, R.z, hz))
    zmin = min(min(r[1], r[3]) for r in rows)
    steps = [abs(rows[i + 1][0] - rows[i][0]) for i in range(n - 1)
             if rows[i][1] - zmin < 0.005 and rows[i + 1][1] - zmin < 0.005]
    mean = sum(steps) / len(steps) if steps else 0.0
    jit = max(abs(s - mean) for s in steps) / mean if steps and mean > 1e-6 else -1.0
    MEAS[clip] = dict(despeje_mm=round((max(r[1] for r in rows) - zmin) * 1000),
                      velocidad_pie_ms=round(mean * 30, 2), dispersion=round(jit, 2),
                      rebote_cadera_mm=round((max(r[4] for r in rows) - min(r[4] for r in rows)) * 1000),
                      frames=n)
ad.action = None
ad.use_nla = True
bpy.context.scene.frame_set(1)
