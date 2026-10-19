#!/usr/bin/env python3
"""Studio compositions of the real station cutouts on art-directed light backdrops -> assets/composed/*.webp"""
import numpy as np, os
from PIL import Image, ImageDraw, ImageFilter
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W,H=1000,1250
def grad(w,h,top,bot):
    t=np.linspace(0,1,h)[:,None,None]; a=np.array(top)[None,None,:]*(1-t)+np.array(bot)[None,None,:]*t
    return Image.fromarray(np.repeat(a,w,1).astype('uint8'),'RGB').convert('RGBA')
def radial(w,h,cx,cy,rx,ry,col,alpha):
    y,x=np.mgrid[0:h,0:w]; d=np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2); a=np.clip(1-d,0,1)**1.6*alpha
    im=np.zeros((h,w,4),'uint8'); im[...,:3]=col; im[...,3]=(a*255).astype('uint8'); return Image.fromarray(im,'RGBA')
def blur(im,r): return im.filter(ImageFilter.GaussianBlur(r))
def backdrop(warm=0.0,arch=True):
    bg=grad(W,H,(246,250,246),(222,240,227))
    # depth blobs
    for (cx,cy,r,c,a) in [(150,260,200,(120,220,160),.35),(880,200,170,(232,242,58),.38+warm*.2),(900,820,150,(120,220,160),.25)]:
        bg.alpha_composite(blur(radial(W,H,cx,cy,r,r,c,a),30))
    # arch panel
    if arch:
        pw,ph_=640,1010; x0=(W-pw)//2; y0=70
        m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m); d.rounded_rectangle((x0,y0,x0+pw,y0+ph_+300),radius=pw//2,fill=255)
        sh=Image.new('RGBA',(W,H),(14,60,30,0)); sh.putalpha(blur(m,28).point(lambda v:int(v*.18))); 
        sh=ImageChops_offset(sh,0,22); bg.alpha_composite(sh)
        panel=grad(W,H,(255,255,255),(226,244,231)); panel.putalpha(m); bg.alpha_composite(panel)
        ring=Image.new('L',(W,H),0); d=ImageDraw.Draw(ring); d.rounded_rectangle((x0,y0,x0+pw,y0+ph_+300),radius=pw//2,outline=255,width=3)
        r=Image.new('RGBA',(W,H),(47,195,83,0)); r.putalpha(ring.point(lambda v:int(v*.35))); bg.alpha_composite(r)
        # inner glow + beam (clipped to panel)
        g=Image.new('RGBA',(W,H),(0,0,0,0)); g.alpha_composite(blur(radial(W,H,W//2,640,380,470,(47,195,83),.55),20))
        beam=Image.new('L',(W,H),0); d=ImageDraw.Draw(beam); d.polygon([(W//2-60,0),(W//2+60,0),(W//2+330,1000),(W//2-330,1000)],fill=120)
        b=Image.new('RGBA',(W,H),(255,255,255,0)); b.putalpha(blur(beam,40)); g.alpha_composite(b)
        pm=m.copy(); ga=g.getchannel('A'); g.putalpha(Image.fromarray((np.array(ga)*(np.array(pm)/255)).astype('uint8')))
        bg.alpha_composite(g)
    # floor sweep
    fl=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(fl)
    d.ellipse((-300,H-330,W+300,H+330),fill=(255,255,255,235))
    bg.alpha_composite(blur(fl,2))
    ed=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ed); d.ellipse((-300,H-330,W+300,H+330),outline=(47,195,83,70),width=3); bg.alpha_composite(ed)
    bg.alpha_composite(blur(radial(W,H,W//2,H-250,420,70,(47,195,83),.35),12))
    return bg
def ImageChops_offset(im,dx,dy):
    o=Image.new('RGBA',im.size,(0,0,0,0)); o.paste(im,(dx,dy)); return o
def place(bg,cut,height,floor_y,cx=W//2,refl=.2):
    r=height/cut.height; c=cut.resize((int(cut.width*r),height),Image.LANCZOS)
    x=cx-c.width//2; y=floor_y-height
    # contact shadow (light from top-left -> shadow falls slightly right)
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(sh)
    d.ellipse((cx-c.width*.62+30,floor_y-22,cx+c.width*.62+30,floor_y+26),fill=(10,50,25,150))
    bg.alpha_composite(blur(sh,14))
    sh2=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(sh2); d.ellipse((cx-c.width*.5,floor_y-8,cx+c.width*.5,floor_y+10),fill=(5,30,15,200)); bg.alpha_composite(blur(sh2,5))
    # reflection
    rf=c.transpose(Image.FLIP_TOP_BOTTOM); rh=int(c.height*.22); rf=rf.crop((0,0,c.width,rh))
    a=np.array(rf.getchannel('A')).astype(float)*np.linspace(refl,0,rh)[:,None]; rf.putalpha(Image.fromarray(a.astype('uint8')))
    bg.alpha_composite(rf,(x,floor_y-4))
    # soft drop shadow of the object itself
    al=c.getchannel('A'); ds=Image.new('RGBA',c.size,(10,50,25,0)); ds.putalpha(blur(al,10).point(lambda v:int(v*.28)))
    bg.alpha_composite(ds,(x+14,y+16)); bg.alpha_composite(c,(x,y)); return bg
def finish(c):
    """premium finish: gentle sharpen, green bounce light from the floor glow, soft top-left key light"""
    c=c.convert('RGBA'); a=c.getchannel('A'); rgb=c.convert('RGB')
    rgb=rgb.filter(ImageFilter.UnsharpMask(radius=1.4,percent=55,threshold=2))
    arr=np.array(rgb).astype(float); h,w=arr.shape[:2]
    yy=np.linspace(0,1,h)[:,None]; xx=np.linspace(0,1,w)[None,:]
    bounce=np.clip((yy-.78)/.22,0,1)**1.5*.10            # green bounce at the foot
    key=np.clip(1-(xx*.8+yy*.5)*1.1,0,1)*.045             # soft white wash top-left
    g=np.array([47,195,83.])
    arr=arr*(1-bounce[...,None])+g*bounce[...,None]
    arr=arr+(255-arr)*key[...,None]
    out=Image.fromarray(np.clip(arr,0,255).astype('uint8')).convert('RGBA'); out.putalpha(a); return out
def real(n): return Image.open(os.path.join(root,'assets/real',n+'.webp')).convert('RGBA')
def counter(bg,top_y,x0=80,x1=W-80):
    """countertop slab for the countertop 6-slot (so it reads small, not floor-standing)"""
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(sh); d.rounded_rectangle((x0+10,top_y+20,x1+10,H+60),radius=26,fill=(10,50,25,120)); bg.alpha_composite(blur(sh,26))
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m); d.rounded_rectangle((x0,top_y,x1,H+60),radius=26,fill=255)
    p=grad(W,H,(252,254,252),(206,228,213)); p.putalpha(m); bg.alpha_composite(p)
    hl=Image.new('L',(W,H),0); d=ImageDraw.Draw(hl); d.rounded_rectangle((x0,top_y,x1,top_y+16),radius=10,fill=255)
    t=Image.new('RGBA',(W,H),(255,255,255,0)); t.putalpha(hl); bg.alpha_composite(t)
    ln=Image.new('L',(W,H),0); d=ImageDraw.Draw(ln); d.line((x0+20,top_y+17,x1-20,top_y+17),fill=255,width=2)
    l=Image.new('RGBA',(W,H),(47,195,83,0)); l.putalpha(ln.point(lambda v:int(v*.28))); bg.alpha_composite(l)
    return bg
def save(im,n):
    im=im.convert('RGB'); p=os.path.join(root,'assets/composed',n+'.webp'); im.save(p,quality=80,method=6); print(n,os.path.getsize(p)//1024,'KB')
def save_hero(im,n,h):
    im=im.resize((round(im.width*h/im.height),h),Image.LANCZOS); p=os.path.join(root,'assets/hero',n+'.webp'); im.save(p,quality=84,method=6,exact=True); print(n,im.size,os.path.getsize(p)//1024,'KB')

# ======================================================================
# Showroom scenes (hero A/B + network cards) -- see tools/scene.py
# ======================================================================
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as SC
import json

H48_D = 820          # tower-48 height (px) in the 1800x1200 reference scene
def outp(name, folder='assets/composed'): return os.path.join(root, folder, name)
def save_webp(im, path, q=78, target_kb=None):
    im = im.convert('RGB'); lo, hi = 40, 90; best = None
    for qq in ([q] if not target_kb else range(88, 38, -4)):
        im.save(path, quality=qq, method=6)
        if not target_kb or os.path.getsize(path) <= target_kb * 1024: break
    print(os.path.basename(path), im.size, os.path.getsize(path) // 1024, 'KB'); return path

def build_counter(s, with_items=True, items='slot+pb', w=420):
    """shared counter piece (white stone top, fluted light oak front). dims scale with s. Returns RGBA layer incl. headroom for items."""
    w = int(w * s); depth = int(66 * s); thick = int(32 * s); toe = int(22 * s)
    panel_h = int(320 * s); head = int(250 * s)
    C = SC.counter_layer(w, depth + thick + panel_h + toe, thick, panel_h, toe=toe, depth=depth, side=int(14 * s))
    L = Image.new('RGBA', (C.width, C.height + head), (0, 0, 0, 0)); L.alpha_composite(C, (0, head))
    if with_items:
        s6 = SC.grade(SC.defringe(SC.real('station-6')))
        h6 = int(205 * s); s6 = s6.resize((int(s6.width * h6 / s6.height), h6), Image.LANCZOS)
        SC.cutout_on(L, s6, cx=int(w * .34), base_y=head + int(depth * .58), lim=head + depth, lim0=head, strength=1.0)
        if items == 'slot+pb':
            pb = SC.lying(SC.real('powerbank-front-horizontal', 'assets/curated/cutouts'), int(104 * s))
            pb = pb.rotate(-6, expand=True, resample=Image.BICUBIC)
            SC.cutout_on(L, SC.grade(pb), cx=int(w * .74), base_y=head + int(depth * .80), lim=head + depth, lim0=head, strength=1.0)
    return L, head

def lineup(room, s, ox, base48, mirror=False, W=1800, with_pb=True):
    """48 tower + 24 tower on the floor, 6-slot on a bar counter, all on the shared floor. coordinates from the 1800 reference."""
    X = (lambda xd: W - (ox + xd * s)) if mirror else (lambda xd: ox + xd * s)
    out = {}
    t48 = SC.grade(SC.defringe(SC.real('station-48')))
    t24 = SC.grade(SC.defringe(SC.real('station-24')))
    h48 = int(H48_D * s); h24 = int(h48 * .85 * .965)
    # counter (front-most, slightly nearer than the towers)
    base_c = base48 + int(37 * s)
    Lc, head = build_counter(s, items='slot+pb' if with_pb else 'slot')
    cxc = X(260); cx = int(cxc - Lc.width / 2)
    ytop = base_c - Lc.height
    out['counter'] = (cx, ytop, Lc.width, Lc.height)
    # shadows of both towers fall right/back: draw far-to-near so nothing is covered wrongly: 24 (back) -> 48 -> counter
    r24 = h24 / t24.height; i24 = t24.resize((int(t24.width * r24), h24), Image.LANCZOS)
    b24 = base48 - int(23 * s); x24 = int(X(960) - i24.width / 2)
    r48 = h48 / t48.height; i48 = t48.resize((int(t48.width * r48), h48), Image.LANCZOS)
    x48 = int(X(700) - i48.width / 2)
    order = [('t24', i24, x24, b24), ('t48', i48, x48, base48)]
    if mirror: pass
    for n, im, x, b in order:
        pos = room.ground(im, x, b - im.height, b, strength=1.0, refl=.10, shadow_len=1.0)
        out[n] = (pos[0], pos[1], im.width, im.height)
    room.ground(Lc, cx, ytop, base_c, strength=1.05, refl=.07, shadow_len=.85)
    out['base'] = (base48, b24, base_c)
    return out

def hero_a(W=1800, H=1200, mirror=False, mobile=False):
    if mobile:
        W, H = 1000, 1010; s = .80; ox = 65; base48 = 885
    else:
        s = 1.0; ox = 30; base48 = 1035
    h48 = int(H48_D * s); cam = 1.4
    y_h = base48 - h48 * cam / 1.8
    wall_y = int(base48 - (base48 - y_h) * .62) if not mobile else int(base48 - (base48 - y_h) * .66)
    f = 1400 if not mobile else 1000
    gx = (ox + 700 * s) if not mirror else (W - (ox + 700 * s))
    room = SC.Room(W, H, wall_y, vp_x=gx + (80 if not mirror else -80), horizon_y=y_h, f=f, cam=cam, mirror=mirror,
                   glow_cx=gx, glow_cy=wall_y * .50, glow_rx=W * (.40 if not mobile else .55), seed=7 if not mirror else 8)
    lay = lineup(room, s, ox, base48, mirror=mirror, W=W)
    room.vignette(.05)
    lay.update(dict(W=W, H=H, wall_y=wall_y))
    return room.canvas, lay

def hero_b():
    """Cinematic venue: AI bar render (labelled 'הדמיה' in the page) with the REAL 48 cutout standing on the same wood floor, graded to the scene."""
    src = Image.open(os.path.join(root, 'assets/curated/venues-render/bar-tower-station.webp')).convert('RGBA')
    bg = src.copy()
    cut = SC.defringe(SC.real('station-48'))
    base_y, cx, hgt = 1506, 962, 1400
    r = hgt / cut.height; cut = cut.resize((int(cut.width * r), hgt), Image.LANCZOS)
    arr = np.array(cut).astype('float32'); h, w = arr.shape[:2]
    yy = np.linspace(0, 1, h)[:, None]; xx = np.linspace(0, 1, w)[None, :]
    screen = np.clip((0.40 - yy) / .05, 0, 1)                    # emissive screen area keeps its luminance
    k = screen * 1.0 + (1 - screen) * (0.80 - 0.10 * yy)         # body sits in the dim bar light, darker towards the floor
    warm = np.array([1.05, .975, .87], 'float32'); green = np.array([.93, 1.04, .95], 'float32')
    side = np.clip((xx - .55) / .45, 0, 1)[..., None]            # right flank catches the green neon / left flank the warm key
    tone = warm[None, None, :] * (1 - side) + green[None, None, :] * side
    body = (1 - screen)[..., None]
    arr[..., :3] = arr[..., :3] * (k[..., None] * (1 + (tone - 1) * body))
    arr[..., :3] += np.clip(1 - np.abs(xx - .12) * 9, 0, 1)[..., None] * (1 - screen)[..., None] * np.array([14, 8, 0])   # warm rim from the bar lights, left edge
    arr[..., :3] += side * (1 - screen)[..., None] * np.array([0, 10, 3]) * np.clip(yy * 2 - .2, 0, 1)[..., None]
    cut = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGBA')
    # screen glow onto the wall/floor around it (spill)
    W_, H_ = bg.size
    x = cx - cut.width // 2; y = base_y - hgt
    glow = SC.blur(SC.radial(W_, H_, cx, y + hgt * .2, 330, 400, SC.GREEN, .35, 1.4), 30); bg.alpha_composite(glow)
    # retire the render's own base plate: repaint dark glossy wood where it stood (the real unit stands there now)
    pt = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); ImageDraw.Draw(pt).ellipse((755, 1410, 1170, 1540), fill=(34, 22, 15, 255)); bg.alpha_composite(SC.blur(pt, 9))
    # floor: dark contact shadow + warm-wood reflection (wood floor is glossy in the render)
    sh = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    d.ellipse((cx - 250, base_y - 34, cx + 250, base_y + 40), fill=(0, 0, 0, 120)); sh = SC.blur(sh, 26); bg.alpha_composite(sh)
    # cast shadow right/back along the floor (same key light direction as scene A)
    al = cut.getchannel('A'); sx, sq = .30, .10
    cast = Image.new('L', (W_, H_), 0)
    cs = SC.Room._shear_shadow(None, al.crop((0, 0, cut.width, cut.height - 4)), sx, sq, cut.width + int(cut.height * sx) + 40, int(cut.height * sq) + 18)
    cast.paste(cs, (x, base_y - cs.height + 6)); cast = SC.blur(cast, 14)
    cm = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); cm.putalpha(cast.point(lambda v: int(v * .50))); bg.alpha_composite(cm)
    sh2 = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(sh2); d.ellipse((cx - 190, base_y - 12, cx + 190, base_y + 16), fill=(0, 0, 0, 200)); bg.alpha_composite(SC.blur(sh2, 7))
    rh = 380; fl = cut.crop((0, cut.height - rh, cut.width, cut.height)).transpose(Image.FLIP_TOP_BOTTOM)
    fa = np.array(fl.getchannel('A')).astype('float32') * (np.linspace(.30, 0, rh) ** 1.3 / .30 ** 1.3 * .30)[:, None]
    fl.putalpha(Image.fromarray(fa.astype('uint8'), 'L')); bg.alpha_composite(SC.blur(fl, 3), (x, base_y + 2))
    bg.alpha_composite(cut, (x, y))
    # crop 4:5 around the tower, split-tone grade (green shadows, warm highlights), gentle vignette
    cr = bg.crop((200, 40, 200 + 1248, 40 + 1560)).convert('RGB').resize((1000, 1250), Image.LANCZOS)
    a = np.array(cr).astype('float32'); lum = a.mean(2, keepdims=True) / 255
    a = a + (1 - lum) * np.array([-4, 5, 1]) * 1.0 + lum * np.array([5, 1, -5])
    yy2, xx2 = np.mgrid[0:1250, 0:1000]; dd = np.sqrt(((xx2 - 500) / 700) ** 2 + ((yy2 - 600) / 900) ** 2)
    a = a * (1 - np.clip(dd - .5, 0, 1)[..., None] * .22)
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'), 'RGB'), dict(cx=(cx - 200) / 1248 * 100, top=(y - 40) / 1560 * 100)

def render_scenes():
    res = {}
    for name, kw in (('hero-a', {}), ('hero-a-ltr', dict(mirror=True)), ('hero-a-m', dict(mobile=True))):
        im, lay = hero_a(**kw); res[name] = lay
        save_webp(im, outp(name + '.webp', 'assets/hero'), target_kb=170)
    im, lb = hero_b(); res['hero-b'] = lb
    save_webp(im, outp('hero-b.webp', 'assets/hero'), target_kb=175)
    json.dump(res, open(os.path.join(root, 'content', 'scene-layout.json'), 'w'), indent=1)
    def vars_(pref, L):
        o = []
        for k, sc in (('t48', .21), ('t24', .22)):
            x, y, w, h = L[k]; W, H = L['W'], L['H']
            o.append('--%s-%sx:%.2f%%;--%s-%sy:%.2f%%;--%s-%sw:%.2f%%;--%s-%sh:%.2f%%;' % (pref, k, (x + w / 2) / W * 100, pref, k, (y + h * sc) / H * 100, pref, k, w * 1.5 / W * 100, pref, k, h * .62 / H * 100))
        o.append('--%s-floory:%.2f%%;' % (pref, L['base'][0] / L['H'] * 100)); return ''.join(o)
    css = '/* generated by tools/compose.py scenes: screen-glow positions, percent of each hero scene image */\n:root{%s}\n:root[dir="ltr"]{%s}\n@media (max-width:959px){:root,:root[dir="ltr"]{%s}}\n' % (vars_('a', res['hero-a']), vars_('a', res['hero-a-ltr']), vars_('a', res['hero-a-m']))
    css += ':root{--b-cx:%.2f%%;--b-top:%.2f%%;}\n' % (res['hero-b']['cx'], res['hero-b']['top'])
    open(os.path.join(root, 'css', 'scene-pos.css'), 'w').write(css)

if __name__=='__main__' and 'scenes' in sys.argv:
    render_scenes(); sys.exit(0)

if __name__=='__main__':
    s6,s24,s48=[finish(real(n)) for n in ('station-6','station-24','station-48')]
    TOP6=H-400
    bg=counter(backdrop(),TOP6,x0=130,x1=W-130); save(place(bg,s6,640,TOP6+2,refl=0),'card-6')
    save(place(backdrop(),s24,865,H-175),'card-24')
    save(place(backdrop(warm=1),s48,1010,H-175),'card-48')
    save(backdrop(),'hero-backdrop')
    save_hero(s48,'real-48',1000); save_hero(s24,'real-24',900); save_hero(s6,'real-6',620)
