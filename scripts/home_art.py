"""Homepage drawings: hand-drafted inline SVG line art. Decorative and aria-hidden; the data stays in the HTML."""
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


def _rows(rows, x, y0, dy):
    return ''.join(f'<text x="{x}" y="{y0 + i * dy}">{r}</text>' for i, r in enumerate(rows))


VIGNETTES = {
    # The first bytes of a real ELF header, magic number marked.
    'hex': ('<rect x="28" y="16" width="68" height="14" class="a"/>'
            '<line x1="24" y1="10" x2="24" y2="84" class="thin"/>'
            + _rows(['00', '04', '08', '10', '14'], 8, 26, 14).replace('<text', '<text class="m"')
            + '<text x="30" y="26" class="i">7F 45 4C 46</text>' + _rows(['02 01 01 00', '00 00 00 00', '03 00 3E 00', '01 00 00 00'], 30, 40, 14)),
    # A process tree with an injected agent marked.
    'tree': ('<rect x="6" y="38" width="30" height="18"/><rect x="50" y="10" width="40" height="18"/><rect x="50" y="38" width="40" height="18" class="a"/><rect x="50" y="66" width="40" height="18"/>'
             '<polyline points="36,47 43,47 43,19 50,19" class="thin"/><line x1="36" y1="47" x2="50" y2="47" class="thin"/><polyline points="43,47 43,75 50,75" class="thin"/>'
             '<polyline points="90,47 100,47 100,30 112,30" class="thin dash"/><circle cx="112" cy="30" r="2" class="dot"/>'
             '<text x="10" y="50">pid1</text><text x="55" y="22">libc</text><text x="55" y="50" class="i">hook</text><text x="55" y="78">app</text>'),
    # A cartridge from the front: label, grip and edge connector.
    'cart': ('<path d="M26 8h68v8h4v62h-6v10H28V78h-6V16h4z" class="p"/>'
             '<rect x="34" y="16" width="52" height="34" class="a"/>'
             '<line x1="40" y1="25" x2="80" y2="25" class="thin ink"/><line x1="40" y1="32" x2="80" y2="32" class="thin ink"/><line x1="40" y1="39" x2="66" y2="39" class="thin ink"/>'
             '<line x1="34" y1="58" x2="86" y2="58" class="thin"/><line x1="34" y1="63" x2="86" y2="63" class="thin"/>'
             + ''.join(f'<line x1="{x}" y1="74" x2="{x}" y2="88" class="thin"/>' for x in range(34, 90, 6))),
    # A plug about to meet a socket: the agent side and the tool side of an MCP connection.
    'plug': ('<path d="M4 47h14" class="thin"/><rect x="18" y="32" width="30" height="30" class="p"/>'
             '<line x1="48" y1="39" x2="60" y2="39"/><line x1="48" y1="55" x2="60" y2="55"/>'
             '<line x1="64" y1="30" x2="64" y2="64" class="thin dash"/>'
             '<rect x="70" y="26" width="30" height="42" class="a"/>'
             '<rect x="70" y="35" width="10" height="7" class="p"/><rect x="70" y="52" width="10" height="7" class="p"/><line x1="100" y1="47" x2="116" y2="47" class="thin"/>'
             '<text x="22" y="50">MCP</text>'),
    # A chip pinout with debug pins marked.
    'pins': ('<rect x="40" y="10" width="40" height="76" class="p"/><path d="M53 10a7 7 0 0 0 14 0" class="thin"/>'
             + ''.join(f'<line x1="32" y1="{y}" x2="40" y2="{y}"/><line x1="80" y1="{y}" x2="88" y2="{y}"/>' for y in (24, 40, 56, 72))
             + '<rect x="4" y="33" width="26" height="30" class="a"/>'
             + '<text x="8" y="27">VCC</text><text x="8" y="43" class="i">TX</text><text x="8" y="59" class="i">RX</text><text x="8" y="75">GND</text>' + _rows(['SWD', 'CLK', 'RST', 'NC'], 92, 27, 16)),
    # A logic-analyser capture: clock and data, one bit window marked.
    'trace': ('<rect x="58" y="6" width="22" height="84" class="a"/>'
              '<polyline points="26,28 26,14 36,14 36,28 46,28 46,14 56,14 56,28 66,28 66,14 76,14 76,28 86,28 86,14 96,14 96,28 106,28 106,14 116,14"/>'
              '<polyline points="26,50 46,50 46,36 66,36 66,50 76,50 76,36 96,36 96,50 116,50"/>'
              '<polyline points="26,72 36,72 36,58 76,58 76,72 96,72 96,58 116,58" class="thin"/>'
              '<text x="4" y="26">CLK</text><text x="4" y="48">TX</text><text x="4" y="70">RX</text>'
              + ''.join(f'<line x1="{x}" y1="80" x2="{x}" y2="84" class="thin"/>' for x in range(26, 118, 10))),
}


def vignette(kind):
    return f'<span class="guide-art"><svg class="art" viewBox="0 0 120 96" aria-hidden="true" focusable="false">{VIGNETTES[kind]}</svg></span>'
