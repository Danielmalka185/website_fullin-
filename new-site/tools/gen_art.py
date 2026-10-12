#!/usr/bin/env python3
"""Generates the code-drawn FULLIN art (vector, no raster):
  _partials/hero.html (between art markers)  inline SVG for the hero stage (animated, parallax layers)
  assets/art/scene-beach.svg   venue illustration (beach, 6-slot station)
  assets/art/scene-mall.svg    venue illustration (mall corridor, 24-slot tower)
  assets/art/kiosk-24.svg / station-6.svg   standalone product renders (cards)
Run: python3 tools/gen_art.py  (then python3 tools/assemble.py)"""
import os, re, random
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- logo (from the real mark, recoloured) ----------
def logo_symbol(sid, dark_letters):
    s = open(os.path.join(root, 'assets/logos/fullin-mark-dark.svg'), encoding='utf8').read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    paths = re.findall(r'<path class="(\w)" d="([^"]+)"', s)
    L = '#0e1215' if dark_letters else '#ffffff'
    fills = {'a': L, 'b': '#48b754', 'c': '#8b9a93'}
    body = ''.join('<path fill="%s" d="%s"/>' % (fills[c], d) for c, d in paths)
    return '<symbol id="%s" viewBox="%s">%s</symbol>' % (sid, vb, body)

def qr(x, y, size, fg='#0e1215', seed=7):
    n = 9; c = size / n; r = random.Random(seed); out = []
    def finder(ox, oy):
        out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (x+ox*c, y+oy*c, 3*c, 3*c, fg))
        out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="#fff"/>' % (x+(ox+.5)*c, y+(oy+.5)*c, 2*c, 2*c))
        out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (x+(ox+1)*c, y+(oy+1)*c, c, c, fg))
    finder(0, 0); finder(n-3, 0); finder(0, n-3)
    for i in range(n):
        for j in range(n):
            if (i < 4 and j < 4) or (i > n-5 and j < 4) or (i < 4 and j > n-5): continue
            if r.random() > .5:
                out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (x+i*c, y+j*c, c*.92, c*.92, fg))
    return ''.join(out)

CREAM_A, CREAM_B = '#e9e2cd', '#cfc5a8'

def defs(p, animated=True):
    """shared gradients; p = id prefix so several SVGs can live on one page"""
    return f'''
<linearGradient id="{p}body" x1="0" x2="1"><stop offset="0" stop-color="#f1ebd9"/><stop offset=".55" stop-color="{CREAM_A}"/><stop offset="1" stop-color="#cdc3a6"/></linearGradient>
<linearGradient id="{p}side" x1="0" x2="1"><stop offset="0" stop-color="#b9ae92"/><stop offset="1" stop-color="#8d846c"/></linearGradient>
<linearGradient id="{p}top" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#d9d0b6"/><stop offset="1" stop-color="#fbf7ea"/></linearGradient>
<linearGradient id="{p}glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c2a17"/><stop offset=".55" stop-color="#06180d"/><stop offset="1" stop-color="#030b06"/></linearGradient>
<radialGradient id="{p}scr" cx=".5" cy=".42" r=".7"><stop offset="0" stop-color="#2FC353" stop-opacity=".55"/><stop offset="1" stop-color="#2FC353" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}sheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="{p}slot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#1b1d1e"/></linearGradient>
<linearGradient id="{p}bank" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b3236"/><stop offset=".5" stop-color="#14181a"/><stop offset="1" stop-color="#0a0c0d"/></linearGradient>
<linearGradient id="{p}yel" x1="0" x2="1"><stop offset="0" stop-color="#cbd62a"/><stop offset=".5" stop-color="#f4ff55"/><stop offset="1" stop-color="#b9c322"/></linearGradient>
<filter id="{p}blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="{p}blur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
'''

def refl_mask(mid, y0, y1, a=.45):
    return (f'<linearGradient id="{mid}g" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y1}"><stop offset="0" stop-color="#fff" stop-opacity="{a}"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-300" y="{y0-20}" width="900" height="{(y1-y0)+60}"><rect x="-300" y="{y0-20}" width="900" height="{(y1-y0)+60}" fill="url(#{mid}g)"/></mask>')

def led(x, y, w, i, p, n_total=24, cls='led'):
    """slot LED: glow + core strip; animation delay in sequence"""
    d = (i * 0.14)
    return (f'<g class="{cls}" style="--d:{d:.2f}s">'
            f'<rect x="{x:.1f}" y="{y-1.2:.1f}" width="{w:.1f}" height="4.8" rx="2.4" fill="#2FC353" opacity=".55" filter="url(#{p}blur)"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="2.4" rx="1.2" fill="#7dff9e"/></g>')

def kiosk(p, logo_id, cols=2, W=132, slot_w=40, screen_h=252, rows=12, dk_id=None):
    """tower kiosk; local coords x0..W, y0..H. 24-slot: cols=2 rows=12; 48-slot: cols=4 rows=12. Returns (svg, H)."""
    dk = dk_id or ('%sdk' % p)
    o = []
    sy = screen_h - 252          # vertical shift of everything below the screen
    H = 600 + sy
    cx = W / 2
    iw = W - 26                   # glass inner width
    o.append('<ellipse cx="%g" cy="%g" rx="%g" ry="12" fill="#000" opacity=".5" filter="url(#%sblur8)"/>' % (cx, H + 17, W * .82, p))
    o.append('<path d="M-22 %g H%g L%g %g H-14 Z" fill="url(#%sside)"/>' % (H + 4, W + 22, W + 14, H + 18, p))
    o.append('<rect x="-22" y="%g" width="%g" height="9" rx="4" fill="url(#%sbody)"/>' % (H - 2, W + 44, p))
    o.append('<rect x="-22" y="%g" width="%g" height="1.6" rx=".8" fill="#fff" opacity=".6"/>' % (H - 2, W + 44))
    o.append('<path d="M%g 8 L%g -2 L%g %g L%g %g Z" fill="url(#%sside)"/>' % (W, W + 20, W + 20, H - 8, W, H, p))
    o.append('<path d="M10 0 H%g Q%g 0 %g 10 L%g -2 Q%g -8 %g -8 H26 Q16 -8 10 0 Z" fill="url(#%stop)" opacity=".95"/>' % (W - 10, W, W, W + 20, W + 18, W + 8, p))
    o.append('<path d="M0 10 Q0 0 10 0 H%g Q%g 0 %g 10 V%g H0 Z" fill="url(#%sbody)"/>' % (W - 10, W, W, H, p))
    o.append('<path d="M1 10 Q1 1 10 1 H%g Q%g 1 %g 10" fill="none" stroke="#fff" stroke-opacity=".7"/>' % (W - 10, W - 1, W - 1))
    o.append('<rect x="0" y="0" width="12" height="%g" fill="#fff" opacity=".18"/>' % H)
    o.append('<rect x="8" y="12" width="%g" height="%g" rx="9" fill="#0a0d0e"/>' % (W - 16, screen_h + 12))
    o.append('<rect x="8.5" y="12.5" width="%g" height="%g" rx="8.5" fill="none" stroke="#fff" stroke-opacity=".14"/>' % (W - 17, screen_h + 11))
    o.append('<rect x="13" y="17" width="%g" height="%g" rx="5" fill="url(#%sglass)"/>' % (iw - 0, screen_h - 10, p))
    o.append('<rect x="13" y="17" width="%g" height="%g" rx="5" fill="url(#%sscr)"/>' % (iw, screen_h - 10, p))
    ly = 32
    o.append('<use href="#%s" x="%g" y="%g" width="70" height="36"/>' % (logo_id, cx - 35, ly))
    ry = 132 + sy * .45
    o.append('<circle cx="%g" cy="%g" r="31" fill="none" stroke="#2FC353" stroke-opacity=".35" stroke-width="1.5"/>' % (cx, ry))
    o.append('<circle class="ring" cx="%g" cy="%g" r="31" fill="none" stroke="#7dff9e" stroke-width="2.5" stroke-linecap="round" pathLength="100" stroke-dasharray="100" transform="rotate(-90 %g %g)"/>' % (cx, ry, cx, ry))
    o.append('<path d="M%g %g L%g %g H%g L%g %g L%g %g H%g Z" fill="#E8F23A"/>' % (cx + 4, ry - 18, cx - 10, ry + 3, cx - 1, cx - 5, ry + 19, cx + 10, ry - 3, cx + .5))
    by = 182 + sy * .8
    bw = min(iw - 34, 120)
    o.append('<rect x="%g" y="%g" width="%g" height="5" rx="2.5" fill="#fff" opacity=".12"/><rect class="bar" x="%g" y="%g" width="%g" height="5" rx="2.5" fill="#2FC353"/>' % (cx - bw / 2, by, bw, cx - bw / 2, by, bw))
    o.append('<rect x="%g" y="%g" width="46" height="4" rx="2" fill="#fff" opacity=".22"/><rect x="%g" y="%g" width="30" height="4" rx="2" fill="#fff" opacity=".12"/>' % (cx - bw / 2, by + 16, cx - bw / 2, by + 26))
    qy = screen_h - 32
    o.append('<g transform="translate(%g %g)"><rect width="20" height="20" rx="3" fill="#fff"/>%s</g>' % (cx + bw / 2 - 20, qy, qr(0, 0, 20, '#06180d', 3)))
    o.append('<path d="M13 17 H%g L13 %g Z" fill="#fff" opacity=".055"/>' % (13 + iw, 17 + screen_h * .55))
    o.append('<rect x="8" y="12" width="%g" height="%g" rx="9" fill="url(#%ssheen)" opacity=".5"/>' % (W - 16, screen_h + 12, p))
    o.append('<use href="#%s" x="%g" y="%g" width="52" height="27"/>' % (dk, cx - 26, 276 + sy))
    gap = (W - cols * slot_w) / (cols + 1)
    for r in range(rows):
        y = 322 + sy + r * 19
        for c in range(cols):
            x = gap + c * (slot_w + gap)
            o.append('<rect x="%g" y="%d" width="%g" height="9" rx="4.5" fill="url(#%sslot)"/>' % (x, y, slot_w, p))
            o.append('<rect x="%g" y="%d" width="%g" height="9" rx="4.5" fill="none" stroke="#000" stroke-opacity=".25"/>' % (x, y, slot_w))
            o.append('<rect x="%g" y="%.1f" width="%g" height="1.4" rx=".7" fill="#fff" opacity=".35"/>' % (x, y + 9.4, slot_w))
            o.append(led(x + slot_w * .27, y + 3.3, slot_w * .46, (r * cols + c), p))
    for gx in (14, W / 2 + 6):
        for r in range(4):
            for c in range(9 if W < 200 else 18):
                o.append('<circle cx="%g" cy="%g" r="1.4" fill="#8f866d" opacity=".75"/>' % (gx + 4 + c * 5.2, 568 + sy + r * 6.5))
    return ''.join(o), H

def kiosk24(p, logo_id):
    return kiosk(p, logo_id)[0]

def station6(p, logo_id, with_scan=True):
    """6-slot countertop station, local coords x0..250, y0..190 (body), screen on top."""
    o = []
    o.append('<ellipse cx="125" cy="192" rx="150" ry="14" fill="#000" opacity=".5" filter="url(#%sblur8)"/>' % p)
    # side + top
    o.append('<path d="M250 26 L272 14 Q274 118 272 160 Q270 176 256 184 L250 188 Z" fill="url(#%sside)"/>' % p)
    o.append('<path d="M18 12 H234 Q250 12 250 28 L272 14 Q268 4 252 4 H36 Q24 4 18 12 Z" fill="url(#%stop)"/>' % p)
    o.append('<path d="M0 30 Q0 12 18 12 H232 Q250 12 250 30 V170 Q250 190 230 190 H20 Q0 190 0 170 Z" fill="url(#%sbody)"/>' % p)
    o.append('<path d="M1.500 30 Q1.500 13.500 18 13.500 H232 Q248.500 13.500 248.500 30" fill="none" stroke="#fff" stroke-opacity=".75"/>')
    o.append('<rect x="0" y="12" width="12" height="178" rx="6" fill="#fff" opacity=".16"/>')
    # raised display bezel
    o.append('<rect x="10" y="-26" width="230" height="64" rx="12" fill="#0a0d0e"/>')
    o.append('<rect x="10.500" y="-25.500" width="229" height="63" rx="11.500" fill="none" stroke="#fff" stroke-opacity=".16"/>')
    o.append('<rect x="16" y="-20" width="218" height="52" rx="8" fill="url(#%sglass)"/>' % p)
    o.append('<rect x="16" y="-20" width="218" height="52" rx="8" fill="url(#%sscr)"/>' % p)
    o.append('<use href="#%s" x="30" y="-12" width="86" height="44"/>' % logo_id)
    o.append('<g transform="translate(176 -15)"><rect width="42" height="42" rx="5" fill="#fff"/>%s</g>' % qr(0, 0, 42, '#06180d', 11))
    if with_scan:
        o.append('<g clip-path="url(#%sscanClip)"><rect class="scan" x="172" y="-17" width="50" height="9" fill="#7dff9e" opacity=".0"/></g>' % p)
        o.append('<g class="unlock"><rect x="16" y="-20" width="218" height="52" rx="8" fill="#052a12" opacity=".98"/><circle cx="125" cy="6" r="15" fill="none" stroke="#2FC353" stroke-opacity=".4" stroke-width="2"/>'
                 '<circle cx="125" cy="6" r="15" fill="none" stroke="#7dff9e" stroke-width="3" stroke-linecap="round" pathLength="100" stroke-dasharray="100" transform="rotate(-90 125 6)" class="ucirc"/>'
                 '<path d="M117 6.500 L123 12.500 L134 0" fill="none" stroke="#E8F23A" stroke-width="3.400" stroke-linecap="round" stroke-linejoin="round" pathLength="100" stroke-dasharray="100" class="utick"/></g>')
    o.append('<rect x="10" y="-26" width="230" height="64" rx="12" fill="url(#%ssheen)" opacity=".35"/>' % p)
    # slots 2x3
    i = 0
    for r in range(3):
        y = 62 + r * 40
        for c, x in enumerate((24, 138)):
            o.append('<rect x="%d" y="%d" width="88" height="20" rx="10" fill="url(#%sslot)"/>' % (x, y, p))
            o.append('<rect x="%d" y="%d" width="88" height="20" rx="10" fill="none" stroke="#000" stroke-opacity=".3"/>' % (x, y))
            o.append('<rect x="%d" y="%.1f" width="88" height="1.6" rx=".8" fill="#fff" opacity=".4"/>' % (x + 4, y + 20.6))
            o.append(led(x + 26, y + 8.4, 36, 2 * r + c + (0 if True else 0), p, cls='led led6'))
            i += 1
    o.append('<path d="M0 190 H250" stroke="#fff" stroke-opacity=".5"/>')
    return ''.join(o)

def powerbank(p, logo_id):
    """power bank back (portrait): 62x118, with 3 yellow cables in a recess"""
    o = []
    o.append('<rect x="0" y="0" width="62" height="118" rx="11" fill="url(#%sbank)"/>' % p)
    o.append('<rect x=".5" y=".5" width="61" height="117" rx="10.500" fill="none" stroke="#fff" stroke-opacity=".22"/>')
    o.append('<rect x="0" y="0" width="62" height="118" rx="11" fill="url(#%ssheen)" opacity=".7"/>' % p)
    o.append('<use href="#%s" x="14" y="14" width="34" height="18"/>' % logo_id)
    o.append('<rect x="9" y="58" width="44" height="52" rx="7" fill="#050607"/>')
    for k, x in enumerate((16, 27, 38)):
        o.append('<g class="cab" style="--c:%d"><rect x="%d" y="66" width="8" height="58" rx="4" fill="url(#%syel)"/><rect x="%d" y="120" width="8" height="9" rx="2.200" fill="#d9dde0"/><rect x="%d" y="127" width="8" height="5" rx="1.500" fill="#8e969b"/></g>' % (k, x, p, x, x))
    return ''.join(o)

# ---------------------------------------------------------------- HERO
def hero_svg():
    p = 'h'
    sym = logo_symbol('hlw', False) + logo_symbol('hdk', True)
    k24 = kiosk24(p, 'hlw').replace('#%sdk' % p, '#hdk')
    s6 = station6(p, 'hlw')
    bank = powerbank(p, 'hlw')
    svg = f'''<svg class="hart" viewBox="0 0 640 720" role="presentation" focusable="false" aria-hidden="true">
<defs>{sym}{defs(p)}
<radialGradient id="hfloor" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#2FC353" stop-opacity=".6"/><stop offset=".55" stop-color="#2FC353" stop-opacity=".12"/><stop offset="1" stop-color="#2FC353" stop-opacity="0"/></radialGradient>
<radialGradient id="hhalo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#2FC353" stop-opacity=".42"/><stop offset="1" stop-color="#2FC353" stop-opacity="0"/></radialGradient>
<linearGradient id="hbeam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7dff9e" stop-opacity="0"/><stop offset="1" stop-color="#7dff9e" stop-opacity=".9"/></linearGradient>
<clipPath id="{p}scanClip"><rect x="172" y="-17" width="50" height="46" rx="4"/></clipPath>
{refl_mask("hm24",608,900)}{refl_mask("hm6",184,330)}
<g id="hk24">{k24}</g>
<g id="hs6">{s6}</g>
<g id="hpb">{bank}</g>
</defs>
<!-- atmosphere -->
<g class="px" data-depth="6">
 <ellipse class="halo" cx="330" cy="330" rx="300" ry="300" fill="url(#hhalo)"/>
 <ellipse class="floor" cx="330" cy="650" rx="310" ry="62" fill="url(#hfloor)"/>
 <ellipse cx="330" cy="650" rx="250" ry="44" fill="none" stroke="#2FC353" stroke-opacity=".35"/>
 <ellipse class="orbit" cx="330" cy="650" rx="300" ry="58" fill="none" stroke="#E8F23A" stroke-opacity=".22" stroke-dasharray="3 9"/>
 <ellipse cx="330" cy="650" rx="190" ry="32" fill="none" stroke="#fff" stroke-opacity=".08"/>
</g>
<!-- 24-slot tower + reflection -->
<g class="px" data-depth="14">
 <g transform="translate(118 36)">
  <use href="#hk24" transform="translate(0 1226) scale(1 -1)" mask="url(#hm24)"/>
  <use href="#hk24"/>
 </g>
</g>
<!-- 6-slot station -->
<g class="px" data-depth="22">
 <g transform="translate(300 470)">
  <use href="#hs6" transform="translate(0 378) scale(1 -1)" mask="url(#hm6)"/>
  <use href="#hs6"/>
 </g>
</g>
<!-- power bank sliding out -->
<g class="px" data-depth="34">
 <g class="bankwrap" transform="translate(372 168)">
  <g class="bankmove"><g class="bankfloat">
   <ellipse class="bglow" cx="52" cy="112" rx="110" ry="130" fill="url(#hhalo)"/>
   <g transform="scale(1.7) rotate(-9 31 59)"><use href="#hpb"/></g>
  </g></g>
 </g>
</g>
<g class="px" data-depth="40">
 <circle class="sp" cx="96" cy="190" r="3" fill="#E8F23A"/><circle class="sp" style="--sd:-1s" cx="560" cy="250" r="2.500" fill="#2FC353"/><circle class="sp" style="--sd:-2s" cx="520" cy="420" r="2" fill="#E8F23A"/><circle class="sp" style="--sd:-.5s" cx="70" cy="470" r="2.500" fill="#2FC353"/>
</g>
</svg>'''
    return svg

SA_CSS = ("<style>.led{animation:lw 3.6s ease-in-out infinite;animation-delay:var(--d,0s)}.led6{animation-duration:4.4s}"
          "@keyframes lw{0%,100%{opacity:.16}10%{opacity:1}26%{opacity:.42}40%{opacity:.16}}"
          ".ring{stroke-dashoffset:0}"
          ".bar{transform-box:fill-box;transform-origin:left center;animation:bf 7s ease-in-out infinite}@keyframes bf{0%{transform:scaleX(.04)}62%,100%{transform:scaleX(.97)}}"
          "@media (prefers-reduced-motion:reduce){*{animation:none!important}.led{opacity:.85}}</style>")

def standalone(vb, body, p, extra_defs=''):
    sym = logo_symbol('%slw' % p, False) + logo_symbol('%sdk' % p, True)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{SA_CSS}<defs>{sym}{defs(p)}{extra_defs}</defs>{body}</svg>'

def product_svgs():
    out = {}
    # 24
    p = 'a'
    k, H = kiosk(p, 'alw')
    ex = refl_mask('am', H, H + 300, .4) + '<g id="ak">%s</g>' % k
    body = '<use href="#ak" transform="translate(0 %g) scale(1 -1)" mask="url(#am)"/><use href="#ak"/>' % (2 * (H + 14))
    out['kiosk-24'] = standalone('-50 -30 252 %g' % (H + 150), body, p, ex)
    # 48
    p = 'b'
    k, H = kiosk(p, 'blw', cols=4, W=224, slot_w=36, screen_h=318)
    ex = refl_mask('bm', H, H + 300, .4) + '<g id="bk">%s</g>' % k
    body = '<use href="#bk" transform="translate(0 %g) scale(1 -1)" mask="url(#bm)"/><use href="#bk"/>' % (2 * (H + 14))
    out['kiosk-48'] = standalone('-50 -30 324 %g' % (H + 150), body, p, ex)
    # 6
    p = 'c'
    s6 = station6(p, 'clw', with_scan=False)
    ex = refl_mask('cm', 184, 330, .5) + '<g id="cs">%s</g>' % s6
    body = '<use href="#cs" transform="translate(0 378) scale(1 -1)" mask="url(#cm)"/><use href="#cs"/>'
    out['station-6'] = standalone('-50 -56 372 380', body, p, ex)
    return out

def scene_beach():
    p = 'e'
    s6 = station6(p, 'elw', with_scan=False)
    lights = ''.join('<circle cx="%d" cy="%d" r="%g" fill="#ffd9a0"/><circle cx="%d" cy="%d" r="9" fill="#ffb25a" opacity=".35" filter="url(#eblur)"/>' % (x, 70 + 46 * (1 - ((x - 600) / 640) ** 2) * -1 + 46, 3.2, x, 70 + 46 * (1 - ((x - 600) / 640) ** 2) * -1 + 46) for x in range(-20, 1240, 60))
    streaks = ''.join('<rect x="%d" y="%d" width="%d" height="3" rx="1.5" fill="#ffd9a0" opacity="%.2f"/>' % (940 - w / 2 + o, y, w, a) for y, w, o, a in [(536, 150, 0, .55), (550, 210, 30, .4), (566, 120, -50, .45), (582, 260, 10, .3), (600, 170, -20, .35), (618, 300, 40, .22), (624, 120, -80, .3)])
    palm = ''.join('<path d="M%d 560 Q%d %d %d %d" fill="none" stroke="#10061f" stroke-width="%d" stroke-linecap="round"/>' % (x, x + dx * .4, 560 - h * .6, x + dx, 560 - h, w) for x, dx, h, w in [(1070, -50, 360, 9)])
    fronds = ''
    for ang, ln in [(-160, 150), (-125, 140), (-90, 90), (-50, 140), (-15, 150), (20, 120), (170, 120)]:
        import math
        cx, cy = 1020, 200
        ex_, ey = cx + ln * math.cos(math.radians(ang)), cy + ln * math.sin(math.radians(ang)) + ln * .35
        mx, my = cx + ln * .5 * math.cos(math.radians(ang)), cy + ln * .5 * math.sin(math.radians(ang)) - 30
        fronds += '<path d="M%d %d Q%d %d %d %d Q%d %d %d %d Z" fill="#10061f"/>' % (cx, cy, mx, my - 10, ex_, ey, mx, my + 14, cx, cy + 6)
    body = f"""
<defs><linearGradient id="esky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#150b3a"/><stop offset=".38" stop-color="#5a2470"/><stop offset=".68" stop-color="#e5603f"/><stop offset="1" stop-color="#ffc26b"/></linearGradient>
<linearGradient id="esea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3a6a"/><stop offset="1" stop-color="#0c1830"/></linearGradient>
<linearGradient id="esand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b98f66"/><stop offset="1" stop-color="#4a3a2c"/></linearGradient>
<linearGradient id="ewood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a8703c"/><stop offset=".08" stop-color="#7a4a26"/><stop offset="1" stop-color="#2a1a0e"/></linearGradient>
<radialGradient id="esun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff2c4"/><stop offset=".3" stop-color="#ffc26b" stop-opacity=".8"/><stop offset="1" stop-color="#ff7a3a" stop-opacity="0"/></radialGradient>
<radialGradient id="evig" cx=".5" cy=".5" r=".7"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#05030c" stop-opacity=".7"/></radialGradient>
<clipPath id="eseaClip"><rect x="0" y="520" width="1200" height="130"/></clipPath>
<mask id="ehorizon" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="900"><rect width="1200" height="520" fill="#fff"/></mask></defs>
<rect width="1200" height="900" fill="url(#esky)"/>
<g opacity=".5">{''.join('<circle cx="%d" cy="%d" r="1.3" fill="#fff"/>' % (x, y) for x, y in [(80, 60), (210, 120), (420, 40), (560, 90), (700, 30), (940, 80), (1100, 150), (320, 170), (1030, 40), (840, 160)])}</g>
<circle cx="940" cy="520" r="230" fill="url(#esun)"/>
<g mask="url(#ehorizon)"><circle cx="940" cy="520" r="64" fill="#fff0bf"/></g>
<rect y="520" width="1200" height="130" fill="url(#esea)"/>
<g clip-path="url(#eseaClip)">{streaks}</g>
<rect y="520" width="1200" height="2" fill="#ffd9a0" opacity=".6"/>
<path d="M0 640 Q300 618 620 636 T1200 628 V900 H0Z" fill="url(#esand)"/>
<g opacity=".95">{palm}{fronds}</g>
<path d="M-20 100 Q600 210 1220 100" fill="none" stroke="#2a1a0e" stroke-opacity=".7" stroke-width="2"/>
<g transform="translate(0 -5)">{lights}</g>
<rect x="-10" y="700" width="1220" height="22" fill="url(#ewood)"/>
<rect x="-10" y="700" width="1220" height="3" fill="#e8b57a" opacity=".6"/>
<rect x="-10" y="722" width="1220" height="190" fill="#1a0f08"/>
{''.join('<rect x="%d" y="722" width="2" height="190" fill="#000" opacity=".35"/>' % x for x in range(40, 1200, 96))}
<g transform="translate(250 700) scale(1.5)"><g transform="translate(0 -190)"><use href="#es"/></g></g>
<ellipse cx="450" cy="704" rx="360" ry="16" fill="#ff9a4a" opacity=".16" filter="url(#eblur8)"/>
<rect width="1200" height="900" fill="url(#evig)"/>"""
    sym = logo_symbol('elw', False)
    d = defs(p) + '<g id="es">%s</g>' % s6
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" preserveAspectRatio="xMidYMid slice">{SA_CSS}<defs>{sym}{d}</defs>{body}</svg>'

def scene_mall():
    p = 'f'
    k, H = kiosk(p, 'flw')
    VX, VY = 600, 440
    def lerp(a, b, t): return a + (b - a) * t
    stops = [0, .30, .52, .68, .80, .88, .94, 1.0]
    pal = ['#ffd9a0', '#7fe0ff', '#ff8fd0', '#ffe27a', '#9bffb4', '#ffb27a', '#b9a6ff']
    walls = ''
    for side in (-1, 1):
        for i in range(len(stops) - 1):
            t1, t2 = stops[i], stops[i + 1]
            def pt(t, yy):  # yy 0=top 1=bottom of wall
                x = lerp(0, 470, t) if side < 0 else lerp(1200, 730, t)
                top = lerp(-40, 330, t); bot = lerp(940, 540, t)
                return (x, lerp(top, bot, yy))
            def poly(y1, y2, a=0, b=1):
                tt1 = lerp(t1, t2, a); tt2 = lerp(t1, t2, b)
                P = [pt(tt1, y1), pt(tt2, y1), pt(tt2, y2), pt(tt1, y2)]
                return ' '.join('%.1f,%.1f' % q for q in P)
            col = pal[(i * 2 + (0 if side < 0 else 3)) % len(pal)]
            walls += '<polygon points="%s" fill="#0d1218"/>' % poly(0, 1)
            walls += '<polygon points="%s" fill="%s" opacity="1"/>' % (poly(.30, .88, .08, .92), col)
            walls += '<polygon points="%s" fill="%s" opacity=".35" filter="url(#fblur8)"/>' % (poly(.30, .88, .08, .92), col)
            walls += '<polygon points="%s" fill="#0d1218" opacity=".22"/>' % poly(.30, .88, .08, .92)
            walls += '<polygon points="%s" fill="#ffffff" opacity=".07"/>' % poly(.30, .88, .08, .45)
            walls += '<polygon points="%s" fill="%s" opacity=".9"/>' % (poly(.12, .16, .08, .92), col)
    floor_lines = ''.join('<line x1="%d" y1="900" x2="%g" y2="540" stroke="#fff" stroke-opacity=".05"/>' % (x, lerp(470, 730, (x + 600) / 2400)) for x in range(-600, 1800, 150))
    ceil = ''.join('<line x1="%d" y1="-40" x2="%g" y2="330" stroke="#ffe8c0" stroke-opacity=".5" stroke-width="3"/>' % (x, lerp(470, 730, (x - 300) / 600)) for x in (420, 600, 780))
    body = f"""
<defs><radialGradient id="fvp" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6dc"/><stop offset=".25" stop-color="#ffd9a0" stop-opacity=".7"/><stop offset="1" stop-color="#ffb27a" stop-opacity="0"/></radialGradient>
<linearGradient id="ffloor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2d36"/><stop offset="1" stop-color="#07090b"/></linearGradient>
<linearGradient id="fceil" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#2b303a"/><stop offset="1" stop-color="#07090b"/></linearGradient>
<radialGradient id="fvig" cx=".5" cy=".5" r=".72"><stop offset=".5" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#03050a" stop-opacity=".75"/></radialGradient></defs>
<rect width="1200" height="900" fill="#0a0c10"/>
<polygon points="0,-40 1200,-40 730,330 470,330" fill="url(#fceil)"/>
<polygon points="0,940 1200,940 730,540 470,540" fill="url(#ffloor)"/>
{floor_lines}{ceil}
<rect x="480" y="340" width="240" height="190" fill="#ffe9c4" filter="url(#fblur8)"/>
<circle cx="600" cy="440" r="230" fill="url(#fvp)"/>
{walls}
<g transform="translate(0 0)"><polygon points="0,940 1200,940 730,540 470,540" fill="#fff" opacity=".02"/></g>
<ellipse cx="900" cy="880" rx="230" ry="22" fill="#000" opacity=".5" filter="url(#fblur8)"/>
<g transform="translate(780 190) scale(1.1)"><use href="#fk" transform="translate(0 {2*(H+14)}) scale(1 -1)" mask="url(#fm)"/><use href="#fk"/></g>
<rect width="1200" height="900" fill="url(#fvig)"/>"""
    sym = logo_symbol('flw', False) + logo_symbol('fdk', True)
    d = defs(p) + refl_mask('fm', H, H + 300, .4) + '<g id="fk">%s</g>' % k
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" preserveAspectRatio="xMidYMid slice">{SA_CSS}<defs>{sym}{d}</defs>{body}</svg>'

if __name__ == '__main__':
    os.makedirs(os.path.join(root, 'assets/art'), exist_ok=True)
    hp = os.path.join(root, '_partials/hero.html')
    h = open(hp, encoding='utf8').read()
    h = re.sub(r'<!--art:start-->.*?<!--art:end-->', lambda m: '<!--art:start-->\n' + hero_svg() + '\n      <!--art:end-->', h, flags=re.S)
    open(hp, 'w', encoding='utf8').write(h)
    print('hero-art', len(hero_svg()))
    for n, v in product_svgs().items():
        open(os.path.join(root, 'assets/art/%s.svg' % n), 'w', encoding='utf8').write(v); print(n, len(v))
    open(os.path.join(root, 'assets/art/scene-beach.svg'), 'w', encoding='utf8').write(scene_beach())
    open(os.path.join(root, 'assets/art/scene-mall.svg'), 'w', encoding='utf8').write(scene_mall())
