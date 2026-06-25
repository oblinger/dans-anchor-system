#!/usr/bin/env python3
"""svg-jiggle — geometry-aware layout-repair pass for hand-authored SVG diagrams.

Detects label-over-box overlaps (the "hard" tier) in a hand-authored SVG and
clears each with the cheapest topological move (slide-along-edge, then
flip-across-edge), repeating until zero hard overlaps or an iteration budget.

It is NOT a layout engine — it is the repair pass that runs AFTER the generator.
Implements the R-svg-jiggle ruleset (severity tiers + two free moves) over a
geometry primitive layer (SVG bbox reader + intersection test + edge association).

CLI:
    svg-jiggle.py <in.svg> [-o <out.svg>] [--max-iter 20] [--report]

Only `<text>` x/y attributes are rewritten; the rest of the source file is left
byte-identical (string-level edit of the moved tags only).
"""

import re
import math
import argparse
import xml.etree.ElementTree as ET

# ---- geometry tuning constants ------------------------------------------------
WIDTH_FACTOR = 0.58     # text width  ~= len * font_size * WIDTH_FACTOR  (per spec)
TOP_FACTOR = 0.8        # baseline -> top  ~= y - TOP_FACTOR * font_size
NODE_COVERAGE = 0.70    # >= this fraction of the label inside ONE box => node label (exempt)
MIN_OVERLAP = 5.0       # an intersection counts as "hard" only if >= this in BOTH axes
MAXDIST = 110.0         # a moved label must stay within this of its associated edge
PERP_MAX = 160.0        # slide search: perpendicular reach
PERP_STEP = 4.0
PAR_PAD = 100.0         # slide search: parallel reach beyond half the edge length
PAR_STEP = 8.0


def localname(elem):
    return elem.tag.split('}')[-1]


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---- bounding-box helpers -----------------------------------------------------
def text_bbox(ax, ay, anchor, fs, content):
    """Return (left, top, w, h, cx, cy) for a single-line <text>."""
    w = max(len(content), 1) * fs * WIDTH_FACTOR
    if anchor == 'middle':
        left = ax - w / 2.0
    elif anchor == 'end':
        left = ax - w
    else:  # 'start' / default
        left = ax
    top = ay - TOP_FACTOR * fs
    h = fs
    return left, top, w, h, left + w / 2.0, top + h / 2.0


def overlap_axis(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def rect_overlap(r, s):
    """r,s = (left, top, w, h). Returns (ox, oy) overlap extents."""
    ox = overlap_axis(r[0], r[0] + r[2], s[0], s[0] + s[2])
    oy = overlap_axis(r[1], r[1] + r[3], s[1], s[1] + s[3])
    return ox, oy


def contained(inner, outer):
    return (inner[0] >= outer[0] and inner[1] >= outer[1] and
            inner[0] + inner[2] <= outer[0] + outer[2] and
            inner[1] + inner[3] <= outer[1] + outer[3])


def point_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def edge_dist(px, py, edge):
    return min(point_seg_dist(px, py, s[0][0], s[0][1], s[1][0], s[1][1]) for s in edge)


# ---- path parsing -------------------------------------------------------------
def cubic_points(p0, p1, p2, p3, n=10):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        x = (mt**3 * p0[0] + 3 * mt*mt*t * p1[0] + 3 * mt*t*t * p2[0] + t**3 * p3[0])
        y = (mt**3 * p0[1] + 3 * mt*mt*t * p1[1] + 3 * mt*t*t * p2[1] + t**3 * p3[1])
        pts.append((x, y))
    return pts


def parse_path(d):
    """Parse a path 'd' into a polyline (list of (x,y) points). Supports M/L/H/V/C/Z."""
    toks = re.findall(r'[MmLlHhVvCcZzSsQqTtAa]|-?\d*\.?\d+(?:e-?\d+)?', d)
    pts = []
    i = 0
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    cmd = None

    def take(k):
        nonlocal i
        vals = [float(x) for x in toks[i:i + k]]
        i += k
        return vals

    while i < len(toks):
        t = toks[i]
        if re.match(r'[A-Za-z]', t):
            cmd = t
            i += 1
            if cmd in 'Zz':
                pts.append(start)
                cur = start
            continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == 'M':
            x, y = take(2)
            cur = (cur[0] + x, cur[1] + y) if rel else (x, y)
            start = cur
            pts.append(cur)
            cmd = 'l' if rel else 'L'
        elif c == 'L':
            x, y = take(2)
            cur = (cur[0] + x, cur[1] + y) if rel else (x, y)
            pts.append(cur)
        elif c == 'H':
            x = take(1)[0]
            cur = (cur[0] + x, cur[1]) if rel else (x, cur[1])
            pts.append(cur)
        elif c == 'V':
            y = take(1)[0]
            cur = (cur[0], cur[1] + y) if rel else (cur[0], y)
            pts.append(cur)
        elif c == 'C':
            v = take(6)
            if rel:
                p1 = (cur[0] + v[0], cur[1] + v[1])
                p2 = (cur[0] + v[2], cur[1] + v[3])
                p3 = (cur[0] + v[4], cur[1] + v[5])
            else:
                p1, p2, p3 = (v[0], v[1]), (v[2], v[3]), (v[4], v[5])
            pts.extend(cubic_points(cur, p1, p2, p3))
            cur = p3
        else:
            # S/Q/T/A not expected in these diagrams — consume conservatively
            take(2)
    return pts


def polyline_segments(pts):
    return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


# ---- SVG model ----------------------------------------------------------------
class Label:
    __slots__ = ('elems', 'ox', 'oy', 'ax', 'ay', 'anchor', 'fs', 'content')

    def __init__(self, ox, oy, anchor, fs, content):
        self.elems = []
        self.ox, self.oy = ox, oy           # original attr coords (source-edit key)
        self.ax, self.ay = ox, oy           # current attr coords
        self.anchor, self.fs, self.content = anchor, fs, content

    def bbox(self):
        return text_bbox(self.ax, self.ay, self.anchor, self.fs, self.content)[:4]

    def center(self):
        b = text_bbox(self.ax, self.ay, self.anchor, self.fs, self.content)
        return b[4], b[5]


def parse_svg(src):
    root = ET.fromstring(src)
    vb = root.get('viewBox')
    if vb:
        parts = [float(x) for x in vb.replace(',', ' ').split()]
        canvas = (parts[2], parts[3])
    else:
        canvas = (fnum(root.get('width')) or 1000.0, fnum(root.get('height')) or 1000.0)
    carea = canvas[0] * canvas[1]

    boxes = []
    edges = []
    label_map = {}  # (round ox, round oy, content) -> Label
    labels = []

    def walk(elem, inh, in_defs):
        name = localname(elem)
        if name in ('defs', 'marker'):
            in_defs = True
        # inherited text attrs
        inh2 = dict(inh)
        for k in ('font-size', 'text-anchor'):
            if elem.get(k) is not None:
                inh2[k] = elem.get(k)

        if not in_defs:
            if name == 'rect':
                stroke = elem.get('stroke')
                x, y = fnum(elem.get('x')) or 0.0, fnum(elem.get('y')) or 0.0
                w, h = fnum(elem.get('width')) or 0.0, fnum(elem.get('height')) or 0.0
                area = w * h
                # A "box" is a stroked rect that is not the full-canvas background.
                # No-stroke rects (background fill, white label halos) are not boxes.
                if stroke and stroke != 'none' and area < 0.6 * carea and w > 0 and h > 0:
                    boxes.append((x, y, w, h))
            elif name == 'line':
                x1, y1 = fnum(elem.get('x1')) or 0.0, fnum(elem.get('y1')) or 0.0
                x2, y2 = fnum(elem.get('x2')) or 0.0, fnum(elem.get('y2')) or 0.0
                edges.append([((x1, y1), (x2, y2))])
            elif name == 'path':
                d = elem.get('d')
                if d:
                    segs = polyline_segments(parse_path(d))
                    if segs:
                        edges.append(segs)
            elif name == 'text':
                ax = fnum(elem.get('x'))
                ay = fnum(elem.get('y'))
                if ax is not None and ay is not None:
                    content = ''.join(elem.itertext()).strip()
                    fs = fnum(elem.get('font-size') or inh2.get('font-size')) or 16.0
                    anchor = elem.get('text-anchor') or inh2.get('text-anchor') or 'start'
                    key = (round(ax, 2), round(ay, 2), content)
                    lab = label_map.get(key)
                    if lab is None:
                        lab = Label(ax, ay, anchor, fs, content)
                        label_map[key] = lab
                        labels.append(lab)
                    lab.elems.append(elem)

        for child in elem:
            walk(child, inh2, in_defs)

    walk(root, {}, False)
    return canvas, boxes, edges, labels


# ---- classification -----------------------------------------------------------
def classify(label, boxes):
    """Return 'node' (exempt), 'hard' (label-over-box), or 'free'."""
    tb = label.bbox()
    area = tb[2] * tb[3]
    max_cov = 0.0
    hard = False
    for b in boxes:
        ox, oy = rect_overlap(tb, b)
        if ox > 0 and oy > 0:
            cov = (ox * oy) / area if area else 0.0
            max_cov = max(max_cov, cov)
            if ox >= MIN_OVERLAP and oy >= MIN_OVERLAP:
                hard = True
    if max_cov >= NODE_COVERAGE:
        return 'node'
    if hard:
        return 'hard'
    return 'free'


def box_box_overlaps(boxes):
    bad = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            bi, bj = boxes[i], boxes[j]
            ox, oy = rect_overlap(bi, bj)
            if ox >= MIN_OVERLAP and oy >= MIN_OVERLAP:
                if not contained(bi, bj) and not contained(bj, bi):
                    bad.append((i, j))
    return bad


def hard_labels(labels, boxes):
    return [l for l in labels if classify(l, boxes) == 'hard']


# ---- edge association ---------------------------------------------------------
def associate(label, edges):
    cx, cy = label.center()
    best = None
    best_d = float('inf')
    for edge in edges:
        for seg in edge:
            d = point_seg_dist(cx, cy, seg[0][0], seg[0][1], seg[1][0], seg[1][1])
            if d < best_d:
                best_d, best = d, (edge, seg)
    if best is None:
        return None, None, None
    return best[0], best[1], best_d


# ---- candidate evaluation -----------------------------------------------------
def clean_at(label, ax, ay, boxes, canvas, edge):
    """Is the label clean (no box intersection), inside canvas, and near its edge?"""
    tb = text_bbox(ax, ay, label.anchor, label.fs, label.content)
    box = tb[:4]
    if box[0] < 0 or box[1] < 0 or box[0] + box[2] > canvas[0] or box[1] + box[3] > canvas[1]:
        return False
    for b in boxes:
        ox, oy = rect_overlap(box, b)
        if ox > 0 and oy > 0:
            return False
    if edge is not None and edge_dist(tb[4], tb[5], edge) > MAXDIST:
        return False
    return True


def try_slide(label, edge, seg, boxes, canvas):
    (x1, y1), (x2, y2) = seg
    L = math.hypot(x2 - x1, y2 - y1)
    if L == 0:
        ux, uy = 1.0, 0.0
    else:
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    par_max = L / 2.0 + PAR_PAD

    perp = [0.0]
    s = PERP_STEP
    while s <= PERP_MAX:
        perp += [s, -s]
        s += PERP_STEP
    par = [0.0]
    t = PAR_STEP
    while t <= par_max:
        par += [t, -t]
        t += PAR_STEP

    best = None
    best_disp = float('inf')
    for s in perp:
        for t in par:
            ax2 = label.ax + t * ux + s * nx
            ay2 = label.ay + t * uy + s * ny
            disp = math.hypot(t, s)
            if disp >= best_disp:
                continue
            if clean_at(label, ax2, ay2, boxes, canvas, edge):
                best_disp = disp
                best = (ax2, ay2)
    return best


def try_flip(label, seg, boxes, canvas, edge):
    (x1, y1), (x2, y2) = seg
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return None
    cx, cy = label.center()
    t = ((cx - x1) * dx + (cy - y1) * dy) / L2
    fx, fy = x1 + t * dx, y1 + t * dy        # foot on the (infinite) edge line
    rx, ry = 2 * fx - cx, 2 * fy - cy        # reflected center
    ax2 = label.ax + (rx - cx)
    ay2 = label.ay + (ry - cy)
    if clean_at(label, ax2, ay2, boxes, canvas, edge):
        return (ax2, ay2)
    return None


# ---- main loop ----------------------------------------------------------------
def jiggle(src, max_iter=20, report=False):
    canvas, boxes, edges, labels = parse_svg(src)

    log = []
    bb = box_box_overlaps(boxes)
    hard0 = len(hard_labels(labels, boxes)) + len(bb)

    if report:
        log.append("== classification ==")
        for l in labels:
            c = classify(l, boxes)
            if c != 'free':
                log.append(f"  [{c}] {l.content!r} @ ({l.ax:g},{l.ay:g}) anchor={l.anchor} fs={l.fs:g}")
        if bb:
            log.append(f"  box-box overlaps: {bb}")

    unresolved = []
    for _ in range(max_iter):
        hard = hard_labels(labels, boxes)
        if not hard:
            break
        progressed = False
        for lab in hard:
            edge, seg, _ = associate(lab, edges)
            if edge is None:
                if lab not in unresolved:
                    unresolved.append(lab)
                continue
            res = try_slide(lab, edge, seg, boxes, canvas)
            move = 'slide-label-along-edge'
            if res is None:
                res = try_flip(lab, seg, boxes, canvas, edge)
                move = 'flip-label-across-edge'
            if res is None:
                if lab not in unresolved:
                    unresolved.append(lab)
                continue
            ox, oy = lab.ax, lab.ay
            lab.ax, lab.ay = res
            if lab in unresolved:
                unresolved.remove(lab)
            log.append(f"  {move}: {lab.content!r} ({ox:g},{oy:g}) -> ({res[0]:.0f},{res[1]:.0f})")
            progressed = True
        if not progressed:
            break

    hard1 = len(hard_labels(labels, boxes)) + len(box_box_overlaps(boxes))

    # collect moves for source rewrite
    moved = {}
    for l in labels:
        if abs(l.ax - l.ox) > 1e-6 or abs(l.ay - l.oy) > 1e-6:
            moved[(round(l.ox, 2), round(l.oy, 2))] = (l.ax, l.ay)

    out = rewrite_source(src, moved)
    return out, hard0, hard1, log, unresolved


def rewrite_source(src, moved):
    """Rewrite only the x/y attrs of moved <text> tags; rest byte-identical."""
    if not moved:
        return src
    pat = re.compile(r'<text\b([^>]*)>', re.DOTALL)
    edits = []
    for m in pat.finditer(src):
        attrs = m.group(1)
        xm = re.search(r'\bx="([^"]*)"', attrs)
        ym = re.search(r'\by="([^"]*)"', attrs)
        if not xm or not ym:
            continue
        try:
            key = (round(float(xm.group(1)), 2), round(float(ym.group(1)), 2))
        except ValueError:
            continue
        if key in moved:
            nx, ny = moved[key]
            new_attrs = re.sub(r'\bx="[^"]*"', f'x="{nx:g}"', attrs, count=1)
            new_attrs = re.sub(r'\by="[^"]*"', f'y="{ny:g}"', new_attrs, count=1)
            edits.append((m.start(1), m.end(1), new_attrs))
    for start, end, txt in reversed(edits):
        src = src[:start] + txt + src[end:]
    return src


def main():
    ap = argparse.ArgumentParser(description="Geometry-aware layout-repair pass for hand-authored SVG diagrams.")
    ap.add_argument('infile')
    ap.add_argument('-o', '--out', help="output path (default: <in>.jiggled.svg)")
    ap.add_argument('--max-iter', type=int, default=20)
    ap.add_argument('--report', action='store_true', help="verbose classification + per-move log")
    args = ap.parse_args()

    with open(args.infile, encoding='utf-8') as f:
        src = f.read()

    out, hard0, hard1, log, unresolved = jiggle(src, args.max_iter, args.report)

    outpath = args.out
    if not outpath:
        outpath = re.sub(r'\.svg$', '', args.infile) + '.jiggled.svg'
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(out)

    print(f"hard overlaps: before {hard0} -> after {hard1}")
    for line in log:
        print(line)
    if unresolved:
        print(f"UNRESOLVED ({len(unresolved)}) — slide/flip could not clear (cascading move needed):")
        for l in unresolved:
            print(f"  {l.content!r} @ ({l.ax:g},{l.ay:g})")
    print(f"wrote {outpath}")


if __name__ == '__main__':
    main()
