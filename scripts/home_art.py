"""Fig. 1 on the homepage: hand-drafted inline SVG line art. Decorative and aria-hidden; the data stays in the HTML."""
from __future__ import annotations

COS = 0.866


def _pt(cx, cy, x, y, z=0):
    return round(cx + (x - y) * COS, 1), round(cy + (x + y) * 0.5 - z, 1)


def _poly(pts, cls=''):
    d = ' '.join(f'{a},{b}' for a, b in pts)
    return f'<polygon points="{d}"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}/>'


def _line(a, b, cls=''):
    return f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}/>'


def _plate(cx, cy, half, z, thick, cls='p'):
    """An isometric plate: top face plus the two visible side faces, painted opaque so it hides what sits behind it."""
    tl, tr, br, bl = (_pt(cx, cy, -half, -half, z), _pt(cx, cy, half, -half, z), _pt(cx, cy, half, half, z), _pt(cx, cy, -half, half, z))
    low = lambda p: (p[0], round(p[1] + thick, 1))
    return (_poly([bl, br, low(br), low(bl)], cls) + _poly([br, tr, low(tr), low(br)], cls) + _poly([tl, tr, br, bl], cls))


def exploded_view(lang='en'):
    """Fig. 1: a chip package pulled apart along its axis, lid to solder balls, with leaders and a dimension line."""
    cx, cy, half = 124, 266, 46
    gap = 54
    z = [0, gap, gap * 2, gap * 3, gap * 4]  # balls, substrate, wires, die, lid
    out = []
    # explosion axis: three corners and the centre of the stack, dashed, drawn first so the plates hide them
    for corner in ((-half, half), (half, half), (half, -half), (0, 0)):
        out.append(_line(_pt(cx, cy, *corner, z[0]), _pt(cx, cy, *corner, z[4]), 'dash'))
    # E: solder balls
    for i in range(5):
        for j in range(5):
            x, y = -half + 8 + i * 19, -half + 8 + j * 19
            a, b = _pt(cx, cy, x, y, z[0])
            out.append(f'<ellipse cx="{a}" cy="{b}" rx="4" ry="2.5" class="p"/>')
    # D: substrate with routed traces
    out.append(_plate(cx, cy, half, z[1], 6))
    for k in (-26, -9, 9, 26):
        for sign in (-1, 1):
            a, b, c = _pt(cx, cy, k, sign * (half - 5), z[1]), _pt(cx, cy, k, sign * 22, z[1]), _pt(cx, cy, k * .45, sign * 8, z[1])
            out.append(f'<polyline points="{a[0]},{a[1]} {b[0]},{b[1]} {c[0]},{c[1]}" class="thin"/>')
    # C: lead frame ring and bond wires, three to a side
    out.append(_plate(cx, cy, half, z[2], 2))
    out.append(_poly([_pt(cx, cy, -20, -20, z[2]), _pt(cx, cy, 20, -20, z[2]), _pt(cx, cy, 20, 20, z[2]), _pt(cx, cy, -20, 20, z[2])], 'thin'))
    for side in range(4):
        for k in (-11, 0, 11):
            inner = {0: (k, -20), 1: (20, k), 2: (k, 20), 3: (-20, k)}[side]
            outer = {0: (k * 1.6, -half + 5), 1: (half - 5, k * 1.6), 2: (k * 1.6, half - 5), 3: (-half + 5, k * 1.6)}[side]
            a, b = _pt(cx, cy, *inner, z[2]), _pt(cx, cy, *outer, z[2])
            out.append(f'<path d="M{a[0]} {a[1]}Q{(a[0] + b[0]) / 2:.1f} {min(a[1], b[1]) - 11:.1f} {b[0]} {b[1]}" class="thin"/>')
    # B: the die, the one rose element
    out.append(_plate(cx, cy, 24, z[3], 4, 'a'))
    for k in (-12, 0, 12):
        out.append(_line(_pt(cx, cy, k, -24, z[3]), _pt(cx, cy, k, 24, z[3]), 'thin ink'))
        out.append(_line(_pt(cx, cy, -24, k, z[3]), _pt(cx, cy, 24, k, z[3]), 'thin ink'))
    # A: lid with a pin-1 mark
    out.append(_plate(cx, cy, half, z[4], 5))
    a, b = _pt(cx, cy, -half + 11, -half + 11, z[4])
    out.append(f'<ellipse cx="{a}" cy="{b}" rx="4.2" ry="2.5" class="a"/>')
    # leaders and callouts
    names = ('封盖', '晶粒', '键合线', '基板', '焊球') if lang == 'zh' else ('LID', 'DIE', 'BOND WIRES', 'SUBSTRATE', 'SOLDER BALLS')
    labels = [('A', names[0], z[4], half), ('B', names[1], z[3], 24), ('C', names[2], z[2], half), ('D', names[3], z[1], half), ('E', names[4], z[0], half)]
    for letter, name, zz, h in labels:
        s = _pt(cx, cy, h, -h, zz)
        y = s[1] - 7
        out.append(f'<polyline points="{s[0]},{s[1]} {s[0] + 10:.1f},{y} 262,{y}" class="thin"/>')
        out.append(f'<circle cx="{s[0]}" cy="{s[1]}" r="1.7" class="dot"/>')
        out.append(f'<text x="267" y="{y + 3.6:.1f}"><tspan class="b">{letter}</tspan> {name}</text>')
    # dimension line on the left, lid to balls
    lx = _pt(cx, cy, -half, half, 0)[0]
    top, bot = _pt(cx, cy, -half, half, z[4])[1], _pt(cx, cy, -half, half, z[0])[1]
    xd = 14
    out.append(_line((xd, top), (xd, bot), 'thin'))
    for yy, tip in ((top, 5), (bot, -5)):
        out.append(f'<polyline points="{xd - 3},{yy + tip} {xd},{yy} {xd + 3},{yy + tip}" class="thin"/>')
        out.append(_line((xd - 5, yy), (lx - 4, yy), 'thin'))
    return ('<svg class="art xv-art" viewBox="0 0 380 340" aria-hidden="true" focusable="false">' + ''.join(out)
            + f'<text x="14" y="336" class="cap">{"图 1  芯片封装爆炸图" if lang == "zh" else "FIG. 1  CHIP PACKAGE, EXPLODED"}</text></svg>')
