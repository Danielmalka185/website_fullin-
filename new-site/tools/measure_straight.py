#!/usr/bin/env python3
"""Straightness check on the FINAL composed images: for every unit, fit lines to its left/right silhouette edges (sub-pixel
gradient peaks searched around the expected edge) and to its top edge; report deviation from vertical / horizontal in degrees."""
import numpy as np, json, os, sys
from PIL import Image
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def lum(p): return np.asarray(Image.open(os.path.join(root, p)).convert('RGB')).astype('float32') @ np.array([.299, .587, .114], 'float32')
def alpha(n):
    """mask of the dark bezel / cap pixels of the source unit (black screen frame = the highest-contrast long verticals)"""
    im = Image.open(os.path.join(root, 'assets/retouched', n + '.png')); a = np.asarray(im.getchannel('A')) > 128
    l = np.asarray(im.convert('RGB')).astype('float32') @ np.array([.299, .587, .114], 'float32')
    return (a & (l < 70)).astype('float32')
def peak(g, c, R):
    lo = max(1, int(round(c)) - R); hi = min(len(g) - 2, int(round(c)) + R)
    if hi <= lo: return None
    seg = np.abs(g[lo:hi + 1]); k = int(seg.argmax()) + lo
    if seg.max() < 6: return None
    a, b, d = np.abs(g[k - 1]), np.abs(g[k]), np.abs(g[k + 1]); den = a - 2 * b + d
    return k + (.5 * (a - d) / den if den else 0), seg.max()
def fit(ts, vs):
    ts, vs = np.array(ts), np.array(vs)
    for _ in range(3):
        A = np.polyfit(ts, vs, 1); r = vs - np.polyval(A, ts); m = np.abs(r) < max(.6, 2.5 * r.std())
        if m.sum() < 8: break
        ts, vs = ts[m], vs[m]
    A = np.polyfit(ts, vs, 1); return np.degrees(np.arctan(A[0])), len(ts), float((vs - np.polyval(A, ts)).std())
ROWS = {'station-48': (.05, .50), 'station-24': (.04, .28), 'station-6': (.10, .34)}   # screen / bezel region = highest-contrast long vertical edges
def unit_report(img, n, box):
    y0, y1 = ROWS[n]
    L = lum(img); A = alpha(n); x, y, w, h = box; r = w / A.shape[1]
    res = {}
    for side in ('left', 'right'):
        ys, xs = [], []
        for row in range(int(y + h * y0), int(y + h * y1)):
            sr = int((row - y) / r); sr = min(sr, A.shape[0] - 1)
            cols = np.where(A[sr] > .5)[0]
            if not len(cols): continue
            ex = x + (cols[0] if side == 'left' else cols[-1] + 1) * r
            g = np.gradient(L[row]); p = peak(g, ex, 4)
            if p: ys.append(row); xs.append(p[0])
        if len(ys) > 40: res[side] = fit(ys, xs)
    # top edge (horizontal): columns across the middle of the top
    xs_, ys_ = [], []
    for col in range(int(x + w * .2), int(x + w * .8)):
        sc = min(int((col - x) / r), A.shape[1] - 1); rows = np.where(A[:, sc] > .5)[0]
        if not len(rows): continue
        g = np.gradient(L[:, col]); p = peak(g, y + rows[0] * r, 4)
        if p: xs_.append(col); ys_.append(p[0])
    if len(xs_) > 40: res['top'] = fit(xs_, ys_)
    return res
def six_report(img, box):
    """station-6: slot-end verticals (3 stacked slots, left & right column) and left-vs-right slot top edges (horizontal tilt)"""
    im = Image.open(os.path.join(root, 'assets/retouched/station-6.png')); l = np.asarray(im.convert('RGB')).astype('float32') @ np.array([.299, .587, .114], 'float32')
    a = np.asarray(im.getchannel('A')) > 128; dark = a & (l < 60); H, W = dark.shape
    x0, y0, w, h = box; r = w / W; L = lum(img); res = {}
    hp = Image.open(os.path.join(root, 'assets/retouched/station-6-holder.png')).height - H if os.path.exists(os.path.join(root, 'assets/retouched/station-6-holder.png')) else 0
    sy = h / (H + hp); y0 += hp * sy    # the composed unit carries the holder canvas above the body (own y scale: width rounding)
    rows = dark[int(H * .5):int(H * .95)].any(1); idx = np.where(rows)[0] + int(H * .5)
    bands = np.split(idx, np.where(np.diff(idx) > 5)[0] + 1)
    lx, rx, ly, ry, ys, tilt = [], [], [], [], [], []
    for b in bands:
        if len(b) < 40: continue
        mid = int(b.mean()); cols = np.where(dark[mid])[0]; left = cols[cols < W / 2]; right = cols[cols > W / 2]
        pl = peak(np.gradient(L[int(y0 + mid * sy)]), x0 + left[0] * r, 3); pr = peak(np.gradient(L[int(y0 + mid * sy)]), x0 + (right[-1] + 1) * r, 3)
        cl, cr = int((left[0] + left[-1]) / 2), int((right[0] + right[-1]) / 2)
        tl = peak(np.gradient(L[:, int(x0 + cl * r)]), y0 + b[0] * sy, 3); tr = peak(np.gradient(L[:, int(x0 + cr * r)]), y0 + b[0] * sy, 3)
        if pl and pr and tl and tr:
            ys.append(y0 + mid * sy); lx.append(pl[0]); rx.append(pr[0]); tilt.append(np.degrees(np.arctan((tr[0] - tl[0]) / ((cr - cl) * r))))
    if len(ys) >= 3:
        for nme, v in (('slot-left-vertical', lx), ('slot-right-vertical', rx)):
            A = np.polyfit(ys, v, 1); res[nme] = (np.degrees(np.arctan(A[0])), len(ys), float(np.std(np.array(v) - np.polyval(A, ys))))
        res['slot-top-horizontal'] = (float(np.mean(tilt)), len(tilt), float(np.std(tilt)))
    return res
def rect_report(img, box):
    """counter slab: left/right vertical sides + top edge"""
    L = lum(img); x, y, w, h = box; res = {}
    for side, ex in (('left', x), ('right', x + w)):
        ys, xs = [], []
        for row in range(int(y + h * .3), int(y + h * .8)):
            p = peak(np.gradient(L[row]), ex, 4)
            if p: ys.append(row); xs.append(p[0])
        if len(ys) > 40: res[side] = fit(ys, xs)
    return res
if __name__ == '__main__':
    lay = json.load(open(os.path.join(root, 'content/scene-layout.json'))); cl = json.load(open(os.path.join(root, 'content/card-layout.json')))
    jobs = []
    for k, img in (('hero-a', 'assets/hero/hero-a.webp'), ('hero-a-ltr', 'assets/hero/hero-a-ltr.webp'), ('hero-a-m', 'assets/hero/hero-a-m.webp')):
        for u, n in (('t48', 'station-48'), ('t24', 'station-24'), ('s6', 'station-6')): jobs.append((k + ' ' + n, img, n, lay[k][u]))
        jobs.append((k + ' counter', img, None, lay[k]['counter']))
    jobs.append(('card-48', 'assets/composed/card-48.webp', 'station-48', cl['48']['unit']))
    jobs.append(('card-24', 'assets/composed/card-24.webp', 'station-24', cl['24']['unit']))
    jobs.append(('card-6', 'assets/composed/card-6.webp', 'station-6', cl['6']['s6']))
    jobs.append(('card-6 counter', 'assets/composed/card-6.webp', None, cl['6']['counter']))
    r = 1400 / 2700; bw = int(804 * r); k = 1000 / 1248
    jobs.append(('hero-b station-48', 'assets/hero/hero-b.webp', 'station-48', [(962 - bw // 2 - 200) * k, (1506 - 1400 - 40) * k, bw * k, 1400 * k]))
    worst = 0
    for name, img, n, box in jobs:
        res = (six_report(img, box) if n == 'station-6' else unit_report(img, n, box)) if n else rect_report(img, box)
        s = ' | '.join('%s %.3f° (n=%d, rms %.2fpx)' % (e, v[0], v[1], v[2]) for e, v in res.items())
        for v in res.values(): worst = max(worst, abs(v[0]))
        print('%-24s %s' % (name, s))
    print('WORST |deviation| = %.3f°' % worst)
