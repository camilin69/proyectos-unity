"""Diagrama de estados del Animator de SUENO LUCIDO, generado desde la misma spec que construye el controller.

El taller exige que el diagrama coincida con el Animator Controller. Dibujarlo a mano invita a que se separen;
aqui los dos salen del mismo archivo, y AnimatorMatchesSpecTests comprueba en Unity que el .controller real es
identico a la spec. Uso:

    python animator_diagram.py <spec.json> <salida_sin_extension> [titulo]

Escribe <salida>.png (Pillow) y <salida>.mmd (Mermaid stateDiagram-v2).
"""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont

ROSA = (234, 165, 188)
MENTA = (143, 190, 176)
LAVANDA = (145, 174, 220)
CREMA = (238, 230, 216)
TINTA = (52, 48, 64)
GRIS = (110, 106, 124)
FONDO = (250, 246, 242)

CELL_W, CELL_H = 340, 230
BOX_W, BOX_H = 170, 64
MARGIN_X, MARGIN_Y = 120, 170


def font(size, bold=False):
    for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def cond_text(c):
    m = c["mode"]
    if m == "If":
        return c["param"]
    if m == "IfNot":
        return "!" + c["param"]
    sym = {"Greater": ">", "Less": "<", "Equals": "==", "NotEqual": "!="}[m]
    return "%s %s %s" % (c["param"], sym, ("%g" % c.get("threshold", 0)))


def label_of(t):
    parts = [cond_text(c) for c in t.get("conditions", [])]
    if t.get("hasExitTime"):
        parts.append("exit %.0f%%" % (100 * t.get("exitTime", 1.0)))
    return " && ".join(parts) if parts else "(fin del clip)"


def color_of(state):
    n = state["name"]
    if n in ("Idle", "Walk", "Jog"):
        return ROSA
    if n in ("JumpStart", "Fall", "Land"):
        return LAVANDA
    if n in ("Fly", "Swim"):
        return MENTA
    return CREMA


def draw(spec, out_base, title):
    states = {s["name"]: s for s in spec["states"]}
    xs = [s["layout"][0] for s in spec["states"]]
    ys = [s["layout"][1] for s in spec["states"]]
    min_x, min_y = min(xs), min(ys)
    cols, rows = max(xs) - min_x + 1, max(ys) - min_y + 1
    W = MARGIN_X * 2 + cols * CELL_W + 560
    H = max(MARGIN_Y + rows * CELL_H + 120, MARGIN_Y + 300 + 25 * len(spec['transitions']) + 120)
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)

    def centre(name):
        lx, ly = states[name]["layout"]
        return (MARGIN_X + (lx - min_x) * CELL_W + CELL_W / 2, MARGIN_Y + (ly - min_y) * CELL_H + CELL_H / 2)

    def inside(px, py, cx, cy):
        return abs(px - cx) <= BOX_W / 2 + 4 and abs(py - cy) <= BOX_H / 2 + 4

    d.text((MARGIN_X, 40), title, fill=TINTA, font=font(34, True))
    d.text((MARGIN_X, 88), "Animator Controller \"%s\" - generado desde PlayerAnimatorSpec.json, la misma fuente que construye el .controller" % spec["name"],
           fill=GRIS, font=font(17))

    pairs = {(t["from"], t["to"]) for t in spec["transitions"]}
    f_lab = font(13)
    labels = []
    for t in spec["transitions"]:
        (x1, y1), (x2, y2) = centre(t["from"]), centre(t["to"])
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        off = 14 if (t["to"], t["from"]) in pairs else 0
        ax, ay, bx, by = x1 + nx * off, y1 + ny * off, x2 + nx * off, y2 + ny * off
        s = 0.0
        while s < 1 and inside(ax + (bx - ax) * s, ay + (by - ay) * s, x1, y1):
            s += 0.005
        e = 1.0
        while e > 0 and inside(ax + (bx - ax) * e, ay + (by - ay) * e, x2, y2):
            e -= 0.005
        sx, sy = ax + (bx - ax) * s, ay + (by - ay) * s
        ex, ey = ax + (bx - ax) * e, ay + (by - ay) * e
        d.line([(sx, sy), (ex, ey)], fill=GRIS, width=2)
        ah = 11
        d.polygon([(ex, ey), (ex - ux * ah + nx * ah * 0.5, ey - uy * ah + ny * ah * 0.5),
                   (ex - ux * ah - nx * ah * 0.5, ey - uy * ah - ny * ah * 0.5)], fill=GRIS)
        labels.append((sx + (ex - sx) * 0.42, sy + (ey - sy) * 0.42))
    # Cada flecha lleva un numero que remite a la tabla: con 26 transiciones, escribir la condicion sobre la
    # flecha las encima unas sobre otras y el diagrama deja de leerse.
    f_num = font(12, True)
    for i, (mx, my) in enumerate(labels, 1):
        d.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=TINTA)
        txt = str(i)
        tw = d.textlength(txt, font=f_num)
        d.text((mx - tw / 2, my - 8), txt, fill=FONDO, font=f_num)

    f_box = font(19, True)
    f_small = font(12)
    for s in spec["states"]:
        cx, cy = centre(s["name"])
        d.rounded_rectangle([cx - BOX_W / 2, cy - BOX_H / 2, cx + BOX_W / 2, cy + BOX_H / 2], radius=18,
                            fill=color_of(s), outline=TINTA, width=4 if s["name"] == spec["defaultState"] else 2)
        tw = d.textlength(s["name"], font=f_box)
        d.text((cx - tw / 2, cy - 22), s["name"], fill=TINTA, font=f_box)
        sub = "clip %s%s" % (s["clip"], " - loop" if s["loop"] else "")
        tw = d.textlength(sub, font=f_small)
        d.text((cx - tw / 2, cy + 6), sub, fill=TINTA, font=f_small)

    lx = MARGIN_X + cols * CELL_W + 40
    d.text((lx, MARGIN_Y), "Parametros", fill=TINTA, font=font(20, True))
    yy = MARGIN_Y + 36
    for p in spec["parameters"]:
        dv = "" if p["type"] == "Trigger" else " = %s" % str(p["default"]).lower()
        d.text((lx, yy), "%s : %s%s" % (p["name"], p["type"], dv), fill=TINTA, font=font(15))
        yy += 26
    yy += 20
    d.text((lx, yy), "Estado por defecto: %s (borde grueso)" % spec["defaultState"], fill=GRIS, font=font(14))
    yy += 24
    d.text((lx, yy), "%d estados, %d transiciones" % (len(spec["states"]), len(spec["transitions"])), fill=GRIS, font=font(14))
    yy += 40
    d.text((lx, yy), "Transiciones", fill=TINTA, font=font(20, True))
    yy += 34
    f_row = font(14)
    for i, tr in enumerate(spec["transitions"], 1):
        d.ellipse([lx, yy + 1, lx + 20, yy + 21], fill=TINTA)
        num = str(i)
        d.text((lx + 10 - d.textlength(num, font=f_num) / 2, yy + 3), num, fill=FONDO, font=f_num)
        d.text((lx + 30, yy + 1), "%s -> %s" % (tr["from"], tr["to"]), fill=TINTA, font=font(14, True))
        d.text((lx + 200, yy + 1), label_of(tr), fill=TINTA, font=f_row)
        yy += 25
    img = img.crop((0, 0, W, max(H, yy + 40)))
    img.save(out_base + ".png")

    lines = ["stateDiagram-v2", "    [*] --> %s" % spec["defaultState"]]
    for t in spec["transitions"]:
        lines.append("    %s --> %s : %s" % (t["from"], t["to"], label_of(t).replace(":", "")))
    with open(out_base + ".mmd", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return out_base + ".png"


if __name__ == "__main__":
    spec_path, out = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "SUENO LUCIDO - diagrama de animacion"
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    names = {s["name"] for s in spec["states"]}
    for t in spec["transitions"]:
        assert t["from"] in names and t["to"] in names, "transicion a un estado inexistente: %r" % t
    assert spec["defaultState"] in names
    print(draw(spec, out, title))
