# SUENO LUCIDO - animaciones del sonador (Humanoid), generadas apuntando segmentos en espacio de armadura.
#
# Leccion de Esneider: escribir angulos locales a mano termina en signos invertidos. Aqui cada segmento se APUNTA
# a una direccion en espacio de armadura y la rotacion local se deduce; las piernas se resuelven con IK analitica
# de dos huesos hacia el tobillo, y la altura de la pelvis sale del alcance de los pies apoyados, asi que el pie
# de apoyo no patina por construccion. Clips en el sitio: Unity mueve el CharacterController.
# Convencion del rig (build_dreamer.py): Z arriba, mira a -Y, su izquierda es +X, pose A.
import bpy, math
from mathutils import Vector, Matrix, Quaternion

ARM = "SN_Armature"
FWD = Vector((0, -1, 0))
UP = Vector((0, 0, 1))
ORDER = ["Hips", "Spine", "Chest", "UpperChest", "Neck", "Head",
         "LeftShoulder", "LeftUpperArm", "LeftLowerArm", "LeftHand",
         "RightShoulder", "RightUpperArm", "RightLowerArm", "RightHand",
         "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "LeftToes",
         "RightUpperLeg", "RightLowerLeg", "RightFoot", "RightToes"]


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def bump(u, peak=0.5):
    if u <= 0 or u >= 1:
        return 0.0
    x = u / (2 * peak) if u < peak else 0.5 + (u - peak) / (2 * (1 - peak))
    return math.sin(math.pi * x)


def rot_about(axis, deg):
    return Matrix.Rotation(math.radians(deg), 3, Vector(axis))


class Poser:
    def __init__(self, arm):
        self.arm = arm
        self.pb = arm.pose.bones
        self.rest = {b.name: b.matrix_local.copy() for b in arm.data.bones}
        self.len = {b.name: b.length for b in arm.data.bones}
        self.head_rest = {b.name: b.head_local.copy() for b in arm.data.bones}
        self.reset()

    def reset(self):
        self.M = {}
        self.q = {}

    def rest_dir(self, name):
        return (self.rest[name].to_3x3() @ Vector((0, 1, 0))).normalized()

    def _base(self, name):
        b = self.arm.data.bones[name]
        if b.parent is None:
            return self.rest[name].copy()
        return self.M[b.parent.name] @ (self.rest[b.parent.name].inverted() @ self.rest[name])

    def set_hips(self, offset=Vector(), aim_dir=None, twist=0.0, tilt_side=0.0):
        base = self.rest["Hips"].copy()
        base.translation = base.translation + Vector(offset)
        d = Vector(aim_dir) if aim_dir is not None else self.rest_dir("Hips")
        self._finish("Hips", base, d.normalized(), twist, extra=rot_about(FWD, tilt_side))

    def aim(self, name, direction, twist=0.0):
        self._finish(name, self._base(name), Vector(direction).normalized(), twist)

    def keep(self, name):
        self.M[name] = self._base(name)
        self.q[name] = Quaternion()

    def _finish(self, name, base, d_arm, twist, extra=None):
        if extra is not None:
            d_arm = (extra @ d_arm).normalized()
        d_local = (base.to_3x3().inverted() @ d_arm).normalized()
        q = Vector((0, 1, 0)).rotation_difference(d_local)
        if twist:
            q = q @ Quaternion(Vector((0, 1, 0)), math.radians(twist))
        self.q[name] = q
        self.M[name] = base @ q.to_matrix().to_4x4()

    def leg(self, side, ankle_target, knee_dir=FWD, foot_pitch=0.0, toe_bend=0.0):
        up, lo, ft, to = side + "UpperLeg", side + "LowerLeg", side + "Foot", side + "Toes"
        hip = self._base(up).translation
        a, b = self.len[up], self.len[lo]
        d = Vector(ankle_target) - hip
        L = min(d.length, (a + b) * 0.9995)
        dn = d.normalized()
        cos_h = max(-1.0, min(1.0, (a * a + L * L - b * b) / (2 * a * L)))
        ang = math.acos(cos_h)
        kd = Vector(knee_dir)
        pole = (kd - dn * kd.dot(dn)).normalized()
        knee = hip + (dn * math.cos(ang) + pole * math.sin(ang)) * a
        self.aim(up, knee - hip)
        self.aim(lo, (hip + dn * L) - knee)
        fdir = (rot_about((1, 0, 0), -foot_pitch) @ Vector((0, -1, -0.55))).normalized()
        self.aim(ft, fdir)
        tdir = (rot_about((1, 0, 0), -foot_pitch - toe_bend) @ Vector((0, -1, -0.1))).normalized()
        self.aim(to, tdir)

    def arm_chain(self, side, upper_dir, lower_dir, hand_dir=None):
        self.keep(side + "Shoulder")
        self.aim(side + "UpperArm", upper_dir)
        self.aim(side + "LowerArm", lower_dir)
        self.aim(side + "Hand", hand_dir if hand_dir is not None else lower_dir)

    def apply(self, frame):
        for name in ORDER:
            pb = self.pb[name]
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = self.q.get(name, Quaternion())
            pb.keyframe_insert("rotation_quaternion", frame=frame)
        hips = self.pb["Hips"]
        base_rest = self.rest["Hips"]
        off = self.M["Hips"].translation - base_rest.translation
        hips.location = base_rest.to_3x3().inverted() @ off
        hips.keyframe_insert("location", frame=frame)


def hang(side, out_deg=7.0, swing_deg=0.0):
    sx = 1 if side == "Left" else -1
    d = Vector((sx * math.sin(math.radians(out_deg)), 0, -math.cos(math.radians(out_deg))))
    # Girar sobre +X un brazo que cuelga lleva la mano hacia +Y, que es ATRAS (el personaje mira a -Y).
    # Por eso el angulo va negado: swing positivo = mano adelante. Medido en la hoja de contactos v1, donde los
    # codos se doblaban hacia atras y el braceo iba en fase con la pierna del mismo lado.
    return (rot_about((1, 0, 0), -swing_deg) @ d).normalized()


def bend(upper, elbow_deg):
    """Flexion del codo: el antebrazo sube hacia delante."""
    return (rot_about((1, 0, 0), -elbow_deg) @ upper).normalized()


def spine_dir(lean_fwd=0.0, side_tilt=0.0):
    d = rot_about((1, 0, 0), lean_fwd) @ UP
    return (rot_about((0, 1, 0), side_tilt) @ d).normalized()


def torso(P, hips_off, lean, pelvis_twist=0.0, chest_twist=0.0, tilt=0.0, head_pitch=0.0, head_twist=0.0, side_bend=0.0):
    P.set_hips(offset=hips_off, aim_dir=spine_dir(lean * 0.4), twist=pelvis_twist, tilt_side=tilt)
    # la columna compensa la bascula de la cadera en tramos (cada vertebra un poco), como un cuerpo de verdad
    P.aim("Spine", spine_dir(lean * 0.7, side_bend * 0.4), twist=chest_twist * 0.35)
    P.aim("Chest", spine_dir(lean, side_bend * 0.8), twist=chest_twist)
    P.aim("UpperChest", spine_dir(lean * 0.8, side_bend), twist=chest_twist * 0.4)
    P.aim("Neck", spine_dir(lean * 0.3 - 4, -side_bend * 0.5))
    P.aim("Head", spine_dir(head_pitch, -side_bend * 0.4), twist=head_twist)


def locomotion(P, t, step_len, stance_frac, clear, lean, arm_swing, elbow, pelvis_twist, chest_twist,
               bob_extra=0.0, hip_drop=0.0, knee_reach=0.985, bob_keep=0.55, weight_shift=0.022, pelvis_tilt=4.0,
               arm_out=9.0, shoulder_roll=5.0):
    a = P.len["LeftUpperLeg"]; b = P.len["LeftLowerLeg"]
    R = (a + b) * knee_reach
    half = step_len / 2.0
    hip_rest_z = P.head_rest["LeftUpperLeg"].z
    ankle_rest_z = P.head_rest["LeftFoot"].z
    feet = {}
    for side, phase in (("Left", 0.0), ("Right", 0.5)):
        p = (t + phase) % 1.0
        if p < stance_frac:
            u = p / stance_frac
            y = -half + step_len * u
            pitch = 12 * (1 - smooth(u / 0.18)) - 28 * smooth((u - 0.7) / 0.3)
            toe = 28 * smooth((u - 0.72) / 0.28)
            feet[side] = dict(y=y, z=0.0, ground=True, pitch=pitch, toe=toe)
        else:
            u = (p - stance_frac) / (1 - stance_frac)
            e = 0.5 - 0.5 * math.cos(math.pi * u)
            feet[side] = dict(y=half - step_len * e, z=clear * bump(u, 0.42), ground=False,
                              pitch=-20 * (1 - smooth(u / 0.35)) + 10 * smooth((u - 0.6) / 0.4), toe=0.0)
    reach = [math.sqrt(max(R * R - f["y"] ** 2, 0.01)) for f in feet.values() if f["ground"]]
    h_contact = R * math.cos(math.asin(min(half / R, 0.99)))
    h = min(reach) if reach else h_contact + bob_extra
    # En una marcha real la rodilla se flexiona en el apoyo medio y la pelvis no sube todo lo que permitiria la
    # pierna recta: se comprime el rebote. La IK dobla la rodilla sola y el pie sigue clavado en el suelo.
    h = h_contact + bob_keep * (h - h_contact)
    dz = h + ankle_rest_z - hip_drop - hip_rest_z
    ph = 2 * math.pi * t
    # el peso se va sobre el pie de apoyo (el izquierdo esta en +X y apoya a mitad de su apoyo)
    wph = 2 * math.pi * (t - stance_frac / 2.0)
    shift = weight_shift * math.cos(wph)
    P.reset()
    torso(P, Vector((shift, 0, dz)), lean, pelvis_twist * math.cos(ph), -chest_twist * math.cos(ph),
          tilt=pelvis_tilt * math.cos(wph) + 1.5 * math.cos(2 * ph),
          head_pitch=-lean * 0.6 + 2 + 1.5 * math.cos(2 * ph),
          head_twist=chest_twist * 0.55 * math.cos(ph),                  # la cabeza mira al frente: contragira
          side_bend=-pelvis_tilt * 0.9 * math.cos(wph))
    for side in ("Left", "Right"):
        f = feet[side]
        sx = 1 if side == "Left" else -1
        hip_joint = P._base(side + "UpperLeg").translation
        ankle = Vector((hip_joint.x + sx * 0.004, f["y"], f["z"] + ankle_rest_z))
        P.leg(side, ankle, foot_pitch=f["pitch"], toe_bend=f["toe"])
    for side, phase in (("Left", 0.5), ("Right", 0.0)):
        a = 2 * math.pi * (t + phase)
        sw = arm_swing * math.cos(a)
        lag = arm_swing * math.cos(a - 0.6)                               # antebrazo y mano llegan un poco despues
        sx = 1 if side == "Left" else -1
        # el brazo que va adelante se cierra hacia el cuerpo; el de atras se abre
        up = (rot_about((0, 0, 1), sx * shoulder_roll * math.cos(a)) @ hang(side, arm_out - 2.5 * math.cos(a), sw)).normalized()
        low = bend(up, elbow + max(0.0, lag) * 0.95 + 4 * math.sin(a))
        hand = bend(low, 6 + 6 * math.sin(a - 0.9))
        P.arm_chain(side, up, low, hand)


def idle_pose(P, t):
    br = math.sin(2 * math.pi * t * 2)                                   # dos respiraciones por ciclo
    sway = math.sin(2 * math.pi * t)                                     # el peso va y vuelve de una pierna a otra
    look = math.sin(2 * math.pi * t + 0.8)
    P.reset()
    torso(P, Vector((0.022 * sway, 0, -0.014 + 0.004 * br)), 1.0 - 1.6 * br, tilt=3.0 * sway,
          chest_twist=3 * look, head_pitch=2 + 2.5 * br - 4 * math.sin(4 * math.pi * t + 1.3),
          head_twist=22 * look, side_bend=-2.4 * sway)
    for side in ("Left", "Right"):
        sx = 1 if side == "Left" else -1
        P.leg(side, Vector((sx * 0.105, 0.0, P.head_rest[side + "Foot"].z)))
        # hombros que suben con la respiracion; manos que se mecen apenas
        up = hang(side, 7 + 1.5 * br, 2 + 2.5 * br + 2 * sway * sx)
        low = bend(up, 10 + 3 * br + 3 * math.sin(2 * math.pi * t + sx))
        P.arm_chain(side, up, low, bend(low, 8 + 4 * math.sin(2 * math.pi * t * 2 + sx)))


def static_pose(P, hips_dz=0.0, lean=0.0, arm_out=8, arm_swing=0, elbow=12, legs_tuck=0.0, legs_y=0.0,
                head=0.0, foot_pitch=0.0):
    P.reset()
    torso(P, Vector((0, 0, hips_dz)), lean, head_pitch=head)
    for side in ("Left", "Right"):
        sx = 1 if side == "Left" else -1
        P.leg(side, Vector((sx * 0.105, legs_y, P.head_rest[side + "Foot"].z + legs_tuck)), foot_pitch=foot_pitch)
        up = hang(side, arm_out, arm_swing)
        P.arm_chain(side, up, bend(up, elbow))


def jump_start(P, t):
    c = smooth(t / 0.6) if t < 0.6 else 1.0 - 1.25 * smooth((t - 0.6) / 0.4)
    static_pose(P, hips_dz=-0.10 * max(c, 0), lean=8 * max(c, 0), arm_out=10, arm_swing=-25 * c + 30 * max(0, -c),
                elbow=20, foot_pitch=-8 * max(0, -c))


def fall_pose(P, t):
    w = math.sin(2 * math.pi * t)
    static_pose(P, lean=-4, arm_out=28 + 3 * w, arm_swing=12, elbow=25, legs_tuck=0.10 + 0.015 * w, legs_y=-0.04,
                foot_pitch=-12)


def land_pose(P, t):
    c = bump(t, 0.25)
    static_pose(P, hips_dz=-0.12 * c, lean=10 * c, arm_out=14, arm_swing=10 * c, elbow=20 + 15 * c)


def fly_pose(P, t):
    w = math.sin(2 * math.pi * t)
    P.reset()
    lean = 32 + 3 * w
    torso(P, Vector((0, 0, 0)), lean, head_pitch=lean * 0.1 - 6)
    for side, off in (("Left", 0.0), ("Right", 1.3)):
        sx = 1 if side == "Left" else -1
        trail = 0.26 + 0.03 * math.sin(2 * math.pi * t + off)
        P.leg(side, Vector((sx * 0.12, trail, P.head_rest[side + "Foot"].z + 0.10)), foot_pitch=-35)
        up = hang(side, 38 + 4 * w, -18)
        P.arm_chain(side, up, bend(up, 12))


def swim_pose(P, t):
    P.reset()
    torso(P, Vector((0, 0, 0.02 * math.sin(4 * math.pi * t))), 5, head_pitch=-12)
    for side, ph in (("Left", 0.0), ("Right", 0.5)):
        sx = 1 if side == "Left" else -1
        c = math.sin(2 * math.pi * (t + ph))
        P.leg(side, Vector((sx * 0.12, 0.10 * c, P.head_rest[side + "Foot"].z + 0.18 + 0.08 * math.cos(2 * math.pi * (t + ph)))),
              foot_pitch=-25)
        scull = 25 * math.sin(2 * math.pi * (t + ph * 0.5))
        up = (rot_about((0, 0, 1), sx * scull) @ hang(side, 55, 10)).normalized()
        P.arm_chain(side, up, bend(up, 30))


def pickup_pose(P, t):
    c = bump(t, 0.45)
    P.reset()
    P.set_hips(offset=Vector((0, 0.05 * c, -0.32 * c)), aim_dir=spine_dir(25 * c))
    P.aim("Spine", spine_dir(35 * c)); P.aim("Chest", spine_dir(42 * c)); P.aim("UpperChest", spine_dir(45 * c))
    P.aim("Neck", spine_dir(40 * c)); P.aim("Head", spine_dir(55 * c))
    for side in ("Left", "Right"):
        sx = 1 if side == "Left" else -1
        y = -0.12 * c if side == "Right" else 0.10 * c
        P.leg(side, Vector((sx * 0.11, y, P.head_rest[side + "Foot"].z)))
    upR = hang("Right", 6, 55 * c)
    P.arm_chain("Right", upR, bend(upR, 10))
    upL = hang("Left", 14, 10 * c)
    P.arm_chain("Left", upL, bend(upL, 25 * c + 8))



def peek_pose(P, t):
    # se acerca al hueco y asoma la cabeza: el torso se inclina, las manos se apoyan en el borde imaginario
    c = smooth(t / 0.55)
    sway = 0.03 * math.sin(2 * math.pi * t) * c
    P.reset()
    P.set_hips(offset=Vector((0, -0.04 * c, -0.06 * c)), aim_dir=spine_dir(12 * c))
    P.aim("Spine", spine_dir(22 * c)); P.aim("Chest", spine_dir(30 * c + 2 * sway)); P.aim("UpperChest", spine_dir(34 * c))
    P.aim("Neck", spine_dir(38 * c)); P.aim("Head", spine_dir(46 * c), twist=6 * math.sin(math.pi * t))
    for side in ("Left", "Right"):
        sx = 1 if side == "Left" else -1
        P.leg(side, Vector((sx * 0.11, (0.06 if side == "Left" else -0.08) * c, P.head_rest[side + "Foot"].z)))
        up = hang(side, 16 * c + 7, 48 * c)
        P.arm_chain(side, up, bend(up, 30 * c + 9))


def stumble_pose(P, t):
    # tropieza: el pie derecho se queda atras, el cuerpo se va hacia delante y los brazos buscan donde agarrarse
    c = smooth(t / 0.7)
    flail = math.sin(2 * math.pi * t * 2.2) * (1 - t)
    P.reset()
    P.set_hips(offset=Vector((0, 0.10 * c, -0.10 * c)), aim_dir=spine_dir(28 * c))
    P.aim("Spine", spine_dir(38 * c)); P.aim("Chest", spine_dir(48 * c), twist=8 * flail); P.aim("UpperChest", spine_dir(50 * c))
    P.aim("Neck", spine_dir(30 * c)); P.aim("Head", spine_dir(20 * c - 10 * flail))
    P.leg("Left", Vector((0.11, 0.18 * c, P.head_rest["LeftFoot"].z + 0.03 * bump(t, 0.3))))
    P.leg("Right", Vector((-0.11, -0.30 * c, P.head_rest["RightFoot"].z + 0.16 * c)), foot_pitch=-30 * c)
    for side, ph in (("Left", 0.0), ("Right", 0.5)):
        up = hang(side, 30 * c + 8, 70 * c + 25 * flail * (1 if side == "Left" else -1))
        P.arm_chain(side, up, bend(up, 15))


def emerge_pose(P, t):
    # sale del agua tomando aire: la cabeza se echa atras, el pecho sube y los brazos abren el agua
    gasp = bump(t, 0.3)
    settle = smooth((t - 0.45) / 0.55)
    P.reset()
    torso(P, Vector((0, 0, 0.10 * gasp)), -14 * gasp + 5 * settle, head_pitch=-30 * gasp - 8 * settle)
    for side in ("Left", "Right"):
        sx = 1 if side == "Left" else -1
        P.leg(side, Vector((sx * 0.12, 0.05, P.head_rest[side + "Foot"].z + 0.15)), foot_pitch=-25)
        up = (rot_about((0, 0, 1), sx * (35 * gasp + 15 * settle)) @ hang(side, 50 + 20 * gasp, 10)).normalized()
        P.arm_chain(side, up, bend(up, 25 + 15 * gasp))


CLIPS = [
    ("Idle", 181, idle_pose),
    # cadencia calibrada a la velocidad del juego: velocidad = paso / (fraccion de apoyo * ciclo)
    ("Walk", 27, lambda P, t: locomotion(P, t, 0.66, 0.60, 0.10, 4.0, 26, 14, 8, 11, bob_keep=0.62,
                                         weight_shift=0.024, pelvis_tilt=4.5, arm_out=9, shoulder_roll=6)),
    # trote relajado: cadera alta, rodilla casi recta en el apoyo (antes salia agazapado con hip_drop y 0.965)
    ("Jog", 30, lambda P, t: locomotion(P, t, 0.80, 0.40, 0.16, 7.0, 36, 78, 10, 15, bob_extra=0.035,
                                        hip_drop=0.0, knee_reach=0.982, bob_keep=0.8,
                                        weight_shift=0.018, pelvis_tilt=5.5, arm_out=11, shoulder_roll=9)),
    ("JumpStart", 9, jump_start),
    ("Fall", 31, fall_pose),
    ("Land", 13, land_pose),
    ("Fly", 61, fly_pose),
    ("Swim", 49, swim_pose),
    ("Pickup", 37, pickup_pose),
    ("Peek", 76, peek_pose),
    ("Stumble", 37, stumble_pose),
    ("Emerge", 61, emerge_pose),
]


def build_all():
    bpy.context.scene.render.fps = 30
    bpy.context.scene.render.fps_base = 1.0
    arm = bpy.data.objects[ARM]
    ad = arm.animation_data or arm.animation_data_create()
    for tr in list(ad.nla_tracks):
        ad.nla_tracks.remove(tr)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    P = Poser(arm)
    out = {}
    for name, frames, fn in CLIPS:
        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        ad.action = act
        for f in range(frames):
            fn(P, f / float(frames - 1))
            P.apply(f + 1)
        act.frame_range = (1, frames)
        ad.action = None
        tr = ad.nla_tracks.new(); tr.name = name
        tr.strips.new(name, 1, act)
        out[name] = frames
    ad.use_nla = True
    for pb in arm.pose.bones:
        pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = Quaternion(); pb.location = (0, 0, 0)
    return out


RESULT = build_all()
print("CLIPS", RESULT)
