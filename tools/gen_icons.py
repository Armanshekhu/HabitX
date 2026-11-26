#!/usr/bin/env python3
"""Converts the SVG <symbol>s from the design into absolute M/L/C/Z path strings
and emits IconData.swift. Arcs, circles and rounded rects become cubic Béziers."""
import re, math, sys

def tokens(d):
    return re.findall(r'[MmLlHhVvCcAaZz]|-?(?:\d+\.?\d*|\.\d+)', d)

def arc_to_cubics(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    if rx == 0 or ry == 0:
        return [('L', [x2, y2])]
    phi = math.radians(phi)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p = cp * dx + sp * dy
    y1p = -sp * dx + cp * dy
    rx, ry = abs(rx), abs(ry)
    lam = (x1p**2) / (rx**2) + (y1p**2) / (ry**2)
    if lam > 1:
        s = math.sqrt(lam); rx *= s; ry *= s
    num = rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2
    den = rx**2 * y1p**2 + ry**2 * x1p**2
    co = math.sqrt(max(0, num / den)) if den else 0
    if fa == fs: co = -co
    cxp = co * rx * y1p / ry
    cyp = -co * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2
    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a
    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dth > 0: dth -= 2 * math.pi
    elif fs and dth < 0: dth += 2 * math.pi
    n = max(1, int(math.ceil(abs(dth) / (math.pi / 2) - 1e-9)))
    seg = dth / n
    out = []
    t = 4 / 3 * math.tan(seg / 4)
    a = th1
    for _ in range(n):
        b = a + seg
        def pt(th):
            return (cx + rx * math.cos(th) * cp - ry * math.sin(th) * sp,
                    cy + rx * math.cos(th) * sp + ry * math.sin(th) * cp)
        def dv(th):
            return (-rx * math.sin(th) * cp - ry * math.cos(th) * sp,
                    -rx * math.sin(th) * sp + ry * math.cos(th) * cp)
        p0, p1 = pt(a), pt(b)
        d0, d1 = dv(a), dv(b)
        out.append(('C', [p0[0] + t * d0[0], p0[1] + t * d0[1],
                          p1[0] - t * d1[0], p1[1] - t * d1[1], p1[0], p1[1]]))
        a = b
    return out

def parse_path(d):
    t = tokens(d); i = 0
    ops = []; cx = cy = sx = sy = 0.0; cmd = None
    def num():
        nonlocal i
        v = float(t[i]); i += 1; return v
    while i < len(t):
        if re.match(r'[A-Za-z]', t[i]):
            cmd = t[i]; i += 1
            if cmd in 'Zz':
                ops.append(('Z', [])); cx, cy = sx, sy
                continue
        rel = cmd.islower(); c = cmd.upper()
        if c == 'M':
            x, y = num(), num()
            if rel: x += cx; y += cy
            ops.append(('M', [x, y])); cx, cy = x, y; sx, sy = x, y
            cmd = 'l' if rel else 'L'
        elif c == 'L':
            x, y = num(), num()
            if rel: x += cx; y += cy
            ops.append(('L', [x, y])); cx, cy = x, y
        elif c == 'H':
            x = num()
            if rel: x += cx
            ops.append(('L', [x, cy])); cx = x
        elif c == 'V':
            y = num()
            if rel: y += cy
            ops.append(('L', [cx, y])); cy = y
        elif c == 'C':
            v = [num() for _ in range(6)]
            if rel:
                v = [v[0]+cx, v[1]+cy, v[2]+cx, v[3]+cy, v[4]+cx, v[5]+cy]
            ops.append(('C', v)); cx, cy = v[4], v[5]
        elif c == 'A':
            rx, ry, phi, fa, fs, x, y = [num() for _ in range(7)]
            if rel: x += cx; y += cy
            ops += arc_to_cubics(cx, cy, rx, ry, phi, int(fa), int(fs), x, y)
            cx, cy = x, y
        else:
            raise ValueError(cmd)
    return ops

def circle(cx, cy, r):
    k = 0.5522847498 * r
    return [('M', [cx + r, cy]),
            ('C', [cx + r, cy + k, cx + k, cy + r, cx, cy + r]),
            ('C', [cx - k, cy + r, cx - r, cy + k, cx - r, cy]),
            ('C', [cx - r, cy - k, cx - k, cy - r, cx, cy - r]),
            ('C', [cx + k, cy - r, cx + r, cy - k, cx + r, cy]), ('Z', [])]

def rrect(x, y, w, h, r):
    k = 0.5522847498 * r
    return [('M', [x + r, y]), ('L', [x + w - r, y]),
            ('C', [x + w - r + k, y, x + w, y + r - k, x + w, y + r]),
            ('L', [x + w, y + h - r]),
            ('C', [x + w, y + h - r + k, x + w - r + k, y + h, x + w - r, y + h]),
            ('L', [x + r, y + h]),
            ('C', [x + r - k, y + h, x, y + h - r + k, x, y + h - r]),
            ('L', [x, y + r]),
            ('C', [x, y + r - k, x + r - k, y, x + r, y]), ('Z', [])]

def fmt(v):
    s = f'{v:.3f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def to_string(ops):
    return ' '.join(op + ((' ' + ' '.join(fmt(v) for v in vals)) if vals else '') for op, vals in ops)

def symbol_ops(body):
    ops = []
    for m in re.finditer(r'<(path|circle|rect)\b([^>]*)>', body):
        tag, attrs = m.group(1), dict(re.findall(r'(\S+?)="([^"]*)"', m.group(2)))
        if tag == 'path': ops += parse_path(attrs['d'])
        elif tag == 'circle': ops += circle(float(attrs['cx']), float(attrs['cy']), float(attrs['r']))
        else: ops += rrect(float(attrs['x']), float(attrs['y']), float(attrs['width']),
                           float(attrs['height']), float(attrs.get('rx', 0)))
    return ops

if __name__ == '__main__':
    src = open('newhabit.tpl.html').read()
    icons = {}; filled = set()
    for m in re.finditer(r'<symbol id="(\w+)"[^>]*>(.*?)</symbol>', src, re.S):
        icons[m.group(1)] = symbol_ops(m.group(2))
        if 'fill="currentColor"' in m.group(2): filled.add(m.group(1))
    # lock icon is inline in the Statistics screen
    icons['lock'] = symbol_ops('<rect x="5" y="11" width="14" height="10" rx="2"></rect><path d="M8 11V8a4 4 0 0 1 8 0v3"></path>')
    names = list(icons)
    out = ['// Generated by tools/gen_icons.py from the design SVG symbols. Do not edit by hand.',
           '// Coordinates are in a 24x24 space; M/L/C/Z absolute commands.', '',
           'enum IconData {', '    static let filled: Set<String> = [' + ', '.join(f'"{n}"' for n in sorted(filled)) + ']', '',
           '    static let paths: [String: String] = [']
    for n in names:
        out.append(f'        "{n}": "{to_string(icons[n])}",')
    out += ['    ]', '}', '']
    open('../HabitTracker/IconData.swift', 'w').write('\n'.join(out))
    print(len(names), 'icons:', ', '.join(names), '| filled:', filled)
    import json; json.dump({n: to_string(o) for n, o in icons.items()}, open('icons.json', 'w'))
