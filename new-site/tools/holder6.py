#!/usr/bin/env python3
"""6-slot station WITH its clear acrylic table-tent holder + FULLIN explanation flyer on top.
  1. renders the flyer (1800x1270, HTML->PNG via node playwright, Heebo from tools/fonts) -> assets/retouched/holder6-flyer.png
  2. builds a perfectly straight landscape A5 acrylic holder around it, standing on the deck of assets/retouched/station-6.png
  -> assets/retouched/station-6-holder.png / .webp   (unit body stays at the bottom, original pixel size; extra canvas on top = holder)
tools/scene.py reads the extra height (H6PAD) from that file."""
import numpy as np, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter
import qrcode
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(root, *p)
FW, FH = 1800, 1270

def qr_svg(url, size, fg='#0f1a14'):
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(url); q.make(fit=True)
    m = q.get_matrix(); n = len(m); u = size / n
    cells = ''.join('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f"/>' % (x * u, y * u, u + .02, u + .02) for y, r in enumerate(m) for x, v in enumerate(r) if v)
    return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" shape-rendering="crispEdges" fill="%s">%s</svg>' % (size, size, size, size, fg, cells)

def logo_svg():
    return open(R('assets/logos/fullin-mark-dark.svg')).read()

def flyer_html():
    hand = 'file://' + R('assets/curated/cutouts/hand-powerbank-yellow-cables.webp')
    fonts = ''.join("@font-face{font-family:Heebo;font-weight:%s;src:url(file://%s)}" % (w, R('tools/fonts/Heebo-%s.ttf' % w)) for w in (500, 800, 900))
    G, GD, GL = '#2FC353', '#1c8f3c', '#7ddc92'
    return f'''<!doctype html><html lang="he" dir="rtl"><meta charset="utf-8"><style>{fonts}
*{{box-sizing:border-box;margin:0}}
html,body{{width:{FW}px;height:{FH}px;overflow:hidden}}
body{{font-family:Heebo,sans-serif;background:#f6f5ee;position:relative;color:#13201a}}
.bgsvg{{position:absolute;inset:0}}
.hand{{position:absolute;left:-30px;top:150px;height:880px;filter:drop-shadow(0 26px 30px rgba(10,50,25,.28))}}
.batt{{position:absolute;right:504px;top:34px;width:196px;height:93px}}
.head{{position:absolute;right:92px;top:136px;width:1060px;text-align:center}}
.h1{{font-weight:800;font-size:84px;line-height:1.05;color:#1a2a22}}
.h2{{font-weight:900;font-size:136px;line-height:1.0;color:{GD};margin-top:4px}}
.sub{{font-weight:500;font-size:44px;color:#3a4a42;margin-top:8px}}
.steps{{position:absolute;right:92px;top:484px;display:flex;gap:30px;flex-direction:row;direction:rtl}}
.step{{width:318px;height:330px;border-radius:44px;background:linear-gradient(160deg,#3bd05f,#1f9a41);color:#fff;text-align:center;padding:30px 20px;box-shadow:0 14px 26px rgba(20,90,40,.35), inset 0 2px 0 rgba(255,255,255,.35)}}
.num{{width:72px;height:72px;border-radius:50%;border:5px solid #fff;margin:0 auto;font-weight:900;font-size:44px;line-height:60px}}
.st{{font-weight:900;font-size:66px;margin-top:14px}}
.sd{{font-weight:500;font-size:37px;line-height:1.25;margin-top:10px;opacity:.97}}
.tiles{{position:absolute;right:92px;top:852px;display:flex;gap:30px;direction:rtl}}
.tile{{width:318px;height:228px;border-radius:44px;background:#fff;border:9px solid {G};display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;box-shadow:0 10px 22px rgba(20,90,40,.18)}}
.big{{font-weight:900;font-size:88px;line-height:1;color:{GD}}}
.mid{{font-weight:800;font-size:50px;line-height:1.05;color:#1a2a22;margin-top:6px}}
.small{{font-weight:500;font-size:34px;color:#3a4a42;margin-top:8px}}
.qr svg{{display:block}}.sh{{font-family:'DejaVu Sans',sans-serif;font-weight:700;font-size:78px;margin-inline-start:8px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:128px;background:#0b130f;color:#e9f3ec;display:flex;align-items:center;direction:rtl;padding:0 92px;gap:46px;font-weight:800;font-size:42px}}
.foot .it{{display:flex;align-items:center;gap:16px;white-space:nowrap}}
.foot .bolt{{width:44px;height:44px;border-radius:14px;background:{G};display:grid;place-items:center}}
.foot .lg{{margin-inline-start:auto;height:64px;display:flex;align-items:center}}
.foot .lg svg{{height:64px;width:auto;display:block}}
.pt{{font-family:'Space Grotesk',Heebo,sans-serif;letter-spacing:.32em;font-weight:500;color:#9fb3a8;font-size:30px}}
</style><body>
<svg class="bgsvg" viewBox="0 0 {FW} {FH}" xmlns="http://www.w3.org/2000/svg">
 <defs><linearGradient id="wv" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#46d56b"/><stop offset="1" stop-color="#1b8a3b"/></linearGradient></defs>
 <path d="M1800 120 C1690 160 1650 330 1740 470 C1810 580 1790 700 1700 790 L1800 790 Z" fill="url(#wv)" opacity=".95"/>
 <path d="M-20 700 C140 600 330 640 440 760 C520 850 600 980 560 1130 L-20 1130 Z" fill="url(#wv)" opacity=".9"/>
 <path d="M420 560 C700 520 860 640 1100 600" fill="none" stroke="{GL}" stroke-width="26" stroke-linecap="round" opacity=".55"/>
 <circle cx="1180" cy="40" r="260" fill="#e5efe2" opacity=".6"/>
</svg>
<img class="hand" src="{hand}">
<svg class="batt" viewBox="0 0 236 112"><rect x="5" y="5" width="200" height="102" rx="16" fill="#fff" stroke="#1a2a22" stroke-width="8"/><rect x="209" y="34" width="20" height="44" rx="8" fill="#1a2a22"/><rect x="16" y="16" width="34" height="80" rx="9" fill="#e5322d"/></svg>
<div class="head"><div class="h1">הסוללה נגמרת?</div><div class="h2">קחו מטען!</div></div>
<div class="steps">
 <div class="step"><div class="num">1</div><div class="st">משחררים</div><div class="sd">סורקים QR<br>ומקבלים מטען</div></div>
 <div class="step"><div class="num">2</div><div class="st">טוענים</div><div class="sd">ממשיכים<br>עם החיים</div></div>
 <div class="step"><div class="num">3</div><div class="st">מחזירים</div><div class="sd">בכל עמדת<br>FULLIN</div></div>
</div>
<div class="tiles">
 <div class="tile"><div class="mid">שעה ראשונה</div><div class="big">חינם!</div><div class="small">באפליקציה</div></div>
 <div class="tile qr" style="background:#fff;padding:0">{qr_svg('https://fullin.co.il', 150)}<div class="small" style="margin-top:6px;font-size:28px;font-weight:800">fullin.co.il</div></div>
 <div class="tile"><div class="big"><span class="sh">₪</span>12</div><div class="mid">לשעה</div></div>
</div>
<div class="foot"><div class="it"><span class="bolt"><svg width="24" height="28" viewBox="0 0 24 28"><path d="M14 0 3 16h7l-2 12L21 11h-7z" fill="#fff"/></svg></span>תמיד טעון, לא משנה איפה</div><div class="it"><span class="bolt"><svg width="24" height="28" viewBox="0 0 24 28"><path d="M14 0 3 16h7l-2 12L21 11h-7z" fill="#fff"/></svg></span>מתאים לאייפון ולאנדרואיד</div><div class="lg">{logo_svg()}</div></div>
</body></html>'''

def render_flyer():
    out = R('assets/retouched/holder6-flyer.png')
    d = tempfile.mkdtemp(); h = os.path.join(d, 'f.html'); open(h, 'w').write(flyer_html())
    js = os.path.join(d, 'r.js')
    open(js, 'w').write("const {chromium}=require('/opt/node-tools/node_modules/playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:%d,height:%d},deviceScaleFactor:1});await p.goto('file://%s');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);await p.screenshot({path:'%s'});await b.close()})()" % (FW, FH, h, out))
    subprocess.check_call(['node', js]); return Image.open(out).convert('RGB')

# ------------------------------------------------------------------ the acrylic holder
def build(flyer):
    base = Image.open(R('assets/retouched/station-6.png')).convert('RGBA'); bw, bh = base.size           # 1501 x 1576
    a = np.asarray(base.getchannel('A')) > 128
    ys, xs = np.where(a); top = int(ys.min())                                                          # top of the deck
    # holder: width ~0.73 of the unit (as in the real photo), A5 landscape ratio, seated 6px into the deck's top
    Hw = int(bw * .735) // 2 * 2; fw = Hw - 2 * 34; fh = int(fw * FH / FW); Hh = fh + 34 + 22           # frame margins: 34 side/top, front lip 22 below
    pad = Hh + 30                                                                                        # canvas added above the unit
    cx = (xs.min() + xs.max()) // 2
    row = np.where(a[top + 8])[0]; cx = int((row.min() + row.max()) // 2)
    x0 = cx - Hw // 2; y1 = pad + top + 14                                                               # bottom of the holder (slightly below the deck top edge line)
    y0 = y1 - Hh
    W, H = bw, bh + pad
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); L.alpha_composite(base, (0, pad))
    S = 2                                                                                                # supersample factor for the holder layer
    # --- soft contact reflection / shadow of the holder on the deck (drawn UNDER the holder, clipped to the unit alpha)
    sh = Image.new('L', (W, H), 0); d = ImageDraw.Draw(sh)
    d.rectangle((x0 + 18, y1 - 20, x0 + Hw - 10, y1 + 8), fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(10)); ua = np.asarray(L.getchannel('A')).astype('float32') / 255
    arr = np.asarray(L).astype('float32'); k = (np.asarray(sh).astype('float32') / 255 * ua * .55)[..., None]
    arr[..., :3] = arr[..., :3] * (1 - k) + np.array([20, 30, 25], 'float32') * k
    # a faint mirrored band of the flyer's bottom on the glossy-black deck cap (reflection)
    fl = flyer.resize((fw, fh), Image.LANCZOS)
    rf = np.asarray(fl.crop((0, fh - 46, fw, fh)).transpose(Image.FLIP_TOP_BOTTOM)).astype('float32')
    rh = rf.shape[0]; fade = (np.linspace(.26, 0, rh) ** 1.0)[:, None, None]
    ry0 = y1 + 2; fx0 = x0 + (Hw - fw) // 2
    reg = arr[ry0:ry0 + rh, fx0:fx0 + fw]; m = (ua[ry0:ry0 + rh, fx0:fx0 + fw] > .5)[..., None]
    reg[..., :3] = np.where(m, reg[..., :3] * (1 - fade) + rf * fade, reg[..., :3]); arr[ry0:ry0 + rh, fx0:fx0 + fw] = reg
    L = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGBA')
    # --- the holder layer (supersampled): back panel + flyer + front acrylic with thickness & edge highlights
    hl = Image.new('RGBA', (Hw * S, Hh * S), (0, 0, 0, 0)); dd = ImageDraw.Draw(hl)
    rad = 20 * S; full = (0, 0, Hw * S - 1, Hh * S - 1)
    # acrylic body: very light cool tint, mostly transparent
    dd.rounded_rectangle(full, radius=rad, fill=(225, 238, 240, 46))
    # flyer sits behind the front sheet, flush on the base lip
    fx, fy = (Hw - fw) // 2 * S, 34 * S
    hl.alpha_composite(flyer.resize((fw * S, fh * S), Image.LANCZOS).convert('RGBA'), (fx, fy))
    # thin darker inner line around the print (the paper edge inside the acrylic) + glass veil over the print
    dd.rectangle((fx - 1, fy - 1, fx + fw * S, fy + fh * S), outline=(40, 60, 50, 90), width=S)
    yy, xx = np.mgrid[0:Hh * S, 0:Hw * S].astype('float32'); u = xx / (Hw * S); v = yy / (Hh * S)
    dgl = u * .9 + v * .55
    veil = np.clip(1 - np.abs(dgl - .42) / .05, 0, 1) * .10 + np.clip(1 - np.abs(dgl - .56) / .018, 0, 1) * .10 + np.clip(1 - dgl / 1.2, 0, 1) ** 2.5 * .06
    ov = np.zeros((Hh * S, Hw * S, 4), 'float32'); ov[..., :3] = 255; ov[..., 3] = veil * 255
    mk = np.zeros((Hh * S, Hw * S), 'float32'); mk[fy:fy + fh * S, fx:fx + fw * S] = 1; ov[..., 3] *= mk
    # acrylic edge: bright outer rim + inner darker rim (thickness) + brighter top edge and bottom lip
    edge = Image.new('L', (Hw * S, Hh * S), 0); de = ImageDraw.Draw(edge)
    de.rounded_rectangle(full, radius=rad, outline=255, width=3 * S)
    rim = np.asarray(edge).astype('float32') / 255
    edge2 = Image.new('L', (Hw * S, Hh * S), 0); ImageDraw.Draw(edge2).rounded_rectangle((7 * S, 7 * S, Hw * S - 8 * S, Hh * S - 8 * S), radius=rad - 6 * S, outline=255, width=2 * S)
    rim2 = np.asarray(edge2).astype('float32') / 255
    ov[..., :3] = np.where(rim[..., None] > .01, 255, ov[..., :3]); ov[..., 3] = np.maximum(ov[..., 3], rim * (150 + 80 * (1 - v)))
    ov[..., :3] = np.where(rim2[..., None] > .01, 215, ov[..., :3]); ov[..., 3] = np.maximum(ov[..., 3], rim2 * 85)
    # front lip: a lit horizontal strip along the bottom (thickness of the base) + a bright line on the very top edge
    lip = ((yy > (Hh - 22) * S) & (yy < Hh * S)).astype('float32')
    ov[..., :3] = np.where(lip[..., None] > 0, np.array([232, 244, 244], 'float32'), ov[..., :3]); ov[..., 3] = np.maximum(ov[..., 3], lip * 120)
    topline = np.clip(1 - np.abs(yy - 1.5 * S) / (1.4 * S), 0, 1) * (np.abs(xx - Hw * S / 2) < Hw * S / 2 - rad)
    ov[..., :3] = np.where(topline[..., None] > 0, 255, ov[..., :3]); ov[..., 3] = np.maximum(ov[..., 3], topline * 235)
    ovi = Image.fromarray(np.clip(ov, 0, 255).astype('uint8'), 'RGBA'); hl.alpha_composite(ovi)
    hl = hl.resize((Hw, Hh), Image.LANCZOS)
    L.alpha_composite(hl, (x0, y0))
    return L, pad

if __name__ == '__main__':
    fl = render_flyer(); L, pad = build(fl)
    o = R('assets/retouched/station-6-holder')
    L.save(o + '.png', optimize=True); L.save(o + '.webp', quality=92, method=6)
    print('station-6-holder', L.size, 'pad', pad)
