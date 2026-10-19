#!/usr/bin/env python3
"""FULLIN showroom scene engine: one shared floor plane + wall + light, physically grounded products.
Used by tools/compose.py to render hero variant A (desktop he / ltr mirror / mobile), variant B and the network cards.

Camera model (pinhole, level): horizon y_h, focal f (px), camera height CAM (m). A floor point at depth Z (m) projects to
y = y_h + f*CAM/Z.  Key light: soft box up-left-front -> cast shadows fall RIGHT and slightly BACK on the floor.
"""
import numpy as np, os
from PIL import Image, ImageDraw, ImageFilter, ImageChops
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG_PAGE = (246, 248, 244)  # --bg
GREEN = (47, 195, 83); LIME = (232, 242, 58)


# ---------------------------------------------------------------- helpers
def blur(im, r): return im.filter(ImageFilter.GaussianBlur(r)) if r > 0 else im
def lerp(a, b, t): return a + (b - a) * t
def noise(w, h, sx, sy=None, seed=1):
    sy = sy or sx
    rng = np.random.default_rng(seed)
    n = rng.random((h // sy + 2, w // sx + 2)).astype('float32')
    im = Image.fromarray((n * 255).astype('uint8')).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255
def grain(w, h, seed=3):
    return np.random.default_rng(seed).normal(0, 1, (h, w)).astype('float32')
def rgba(arr_rgb, alpha):
    a = np.dstack([np.clip(arr_rgb, 0, 255), np.clip(alpha, 0, 255)]).astype('uint8'); return Image.fromarray(a, 'RGBA')
def radial(w, h, cx, cy, rx, ry, col, alpha, power=1.6):
    y, x = np.mgrid[0:h, 0:w]; d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    a = np.clip(1 - d, 0, 1) ** power * alpha
    im = np.zeros((h, w, 4), 'uint8'); im[..., :3] = col; im[..., 3] = (a * 255).astype('uint8'); return Image.fromarray(im, 'RGBA')
def vgrad(w, h, stops):
    """stops [(t,(r,g,b)),...] vertical gradient RGB image"""
    t = np.linspace(0, 1, h); out = np.zeros((h, 3))
    ts = [s[0] for s in stops]
    for c in range(3): out[:, c] = np.interp(t, ts, [s[1][c] for s in stops])
    return Image.fromarray(np.repeat(out[:, None, :], w, 1).astype('uint8'), 'RGB').convert('RGBA')
def real(n, folder='assets/real'): return Image.open(os.path.join(root, folder, n + '.webp')).convert('RGBA')
def defringe(c):
    """pull the alpha in 1px and soften: kills light/green halo of the matting"""
    a = c.getchannel('A'); a2 = a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.6))
    c = c.copy(); c.putalpha(a2); return c


def grade(c, amount=1.0, warm=0.0):
    """integrate a cutout into the scene: sharpen a touch, soft key from upper-left, green floor bounce at the foot,
    gentle contact darkening at the very bottom. Light direction identical for every object."""
    c = c.convert('RGBA'); a = c.getchannel('A'); rgb = c.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1.2, percent=45, threshold=2))
    arr = np.array(rgb).astype('float32'); h, w = arr.shape[:2]
    yy = np.linspace(0, 1, h)[:, None]; xx = np.linspace(0, 1, w)[None, :]
    key = np.clip(1 - (xx * .9 + yy * .35) * 1.15, 0, 1) * .05 * amount      # white wash upper-left
    shade = np.clip((xx - .55) / .45, 0, 1) * .045 * amount                   # falloff on the far (right) side
    bounce = np.clip((yy - .80) / .20, 0, 1) ** 1.6 * .09 * amount            # green floor bounce
    ao = np.clip((yy - .965) / .035, 0, 1) * .10 * amount                     # darkening at contact
    g = np.array(GREEN, 'float32')
    arr = arr * (1 - bounce[..., None]) + g * bounce[..., None]
    arr = arr + (255 - arr) * key[..., None]
    arr = arr * (1 - shade[..., None] - ao[..., None])
    if warm: arr = arr * np.array([1 + .03 * warm, 1.0, 1 - .05 * warm], 'float32')
    out = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).convert('RGBA'); out.putalpha(a); return out


# ---------------------------------------------------------------- the room
class Room:
    def __init__(self, W, H, wall_y, vp_x, horizon_y, f, cam=1.55, seed=7, mirror=False, floor_tone=0, bokeh=True, glow_cx=None, glow_cy=None, glow_rx=None, wash=1.0):
        self.W, self.H, self.wall_y, self.vp_x, self.y_h, self.f, self.cam = W, H, wall_y, vp_x, horizon_y, f, cam
        self.mirror = mirror
        self.glow = (glow_cx if glow_cx is not None else W * .42, glow_cy if glow_cy is not None else wall_y * .55, glow_rx if glow_rx is not None else W * .42)
        self.wash = wash
        self.canvas = Image.new('RGBA', (W, H), (255, 255, 255, 255))
        self.seed = seed
        self._wall(bokeh); self._floor()

    # --- back wall: pale mint plaster, green light wash from behind the products, lime accent, bokeh
    def _wall(self, bokeh):
        W, H, wy = self.W, self.H, self.wall_y
        wall = vgrad(W, wy, [(0, (243, 249, 244)), (.6, (233, 245, 236)), (1, (222, 240, 228))])
        gx, gy, grx = self.glow
        arr = np.array(wall).astype('float32')
        # plaster micro-texture + very soft large mottling
        arr[..., :3] += (grain(W, wy, 5)[..., None] * 1.1) + ((noise(W, wy, 140, 90, 11) - .5) * 5)[..., None]
        wall = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGBA')
        L = Image.new('RGBA', (W, wy), (0, 0, 0, 0))
        L.alpha_composite(blur(radial(W, wy, gx, gy, grx * 1.25, wy * 1.0, GREEN, .46 * self.wash, 1.5), 40))        # main green wash
        L.alpha_composite(blur(radial(W, wy, gx, gy + wy * .08, grx * .62, wy * .62, (120, 226, 150), .5 * self.wash, 1.4), 30))
        side = -1 if self.mirror else 1
        L.alpha_composite(blur(radial(W, wy, W * (.5 - side * .46), -wy * .04, W * .34, wy * .62, LIME, .5 * self.wash, 1.5), 40))  # lime accent, top far corner
        # vertical light column behind the main tower (soft box spill)
        col = Image.new('L', (W, wy), 0); d = ImageDraw.Draw(col)
        d.polygon([(gx - grx * .22, 0), (gx + grx * .22, 0), (gx + grx * .5, wy), (gx - grx * .5, wy)], fill=int(95 * self.wash))
        c2 = Image.new('RGBA', (W, wy), (255, 255, 255, 0)); c2.putalpha(blur(col, 46)); L.alpha_composite(c2)
        wall.alpha_composite(L)
        # cove light: soft lime-green glow where wall meets floor
        cove = Image.new('RGBA', (W, wy), (0, 0, 0, 0))
        cove.alpha_composite(blur(radial(W, wy, W // 2, wy - 4, W * .62, 70, GREEN, .38 * self.wash, 1.2), 18))
        wall.alpha_composite(cove)
        self.canvas.paste(wall, (0, 0))
        if bokeh: self._bokeh()
        # hairline baseboard shadow + cove line
        d = ImageDraw.Draw(self.canvas, 'RGBA')
        for i, (a, col) in enumerate([(170, (255, 255, 235)), (70, (47, 195, 83))]):
            pass
        line = Image.new('RGBA', (W, 8), (0, 0, 0, 0)); ld = ImageDraw.Draw(line)
        ld.rectangle((0, 3, W, 4), fill=(250, 255, 225, 120)); self.canvas.alpha_composite(blur(line, 2.2), (0, wy - 5))

    def _bokeh(self):
        """out-of-focus light discs and soft hex shapes: depth cue on the wall, brand colours"""
        W, wy = self.W, self.wall_y; rng = np.random.default_rng(self.seed)
        layer = Image.new('RGBA', (W, wy), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        sc = W / 1800
        for _ in range(26):
            x = rng.uniform(0, W); y = rng.uniform(wy * .06, wy * .94); r = rng.uniform(26, 90) * sc
            col = [GREEN, LIME, (255, 255, 255), (120, 226, 150)][rng.integers(0, 4)]
            a = int(rng.uniform(14, 40))
            if False:
                n = 6; ang = rng.uniform(0, 6.28); pts = [(x + r * np.cos(ang + i * 6.2832 / n), y + r * np.sin(ang + i * 6.2832 / n)) for i in range(n)]
                d.polygon(pts, fill=col + (a,))
            else: d.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,))
        layer = blur(layer, 14 * sc + 2)
        # ring edge on some discs is implicit through overlap; add faint fine layer
        self.canvas.alpha_composite(layer, (0, 0))
        # keep centre of the wash clean enough for the towers' silhouettes
        # (towers are opaque, so no masking needed)

    # --- floor: polished light concrete, reflected wall glow, perspective expansion joints, grain
    def _floor(self):
        W, H, wy, yh, f, cam = self.W, self.H, self.wall_y, self.y_h, self.f, self.cam
        fh = H - wy
        floor = vgrad(W, fh, [(0, (226, 236, 229)), (.35, (236, 241, 237)), (1, (BG_PAGE))])
        arr = np.array(floor).astype('float32')
        mott = (noise(W, fh, 220, 60, 21) - .5) * 9 + (noise(W, fh, 40, 14, 22) - .5) * 4
        arr[..., :3] += mott[..., None] + grain(W, fh, 4)[..., None] * 1.3
        floor = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGBA')
        # mirror the wall (glow, bokeh, cove) into the polished floor: faint, fading with distance
        n = min(fh, wy)
        refl = self.canvas.crop((0, wy - n, W, wy)).transpose(Image.FLIP_TOP_BOTTOM)
        refl = blur(refl, 3).resize((W, n), Image.BILINEAR)
        ra = np.linspace(.50, 0, n) ** 1.3 * .50
        r = np.array(refl).copy(); r[..., 3] = (ra[:, None] * 255).astype('uint8');
        base = floor.crop((0, 0, W, n)); base.alpha_composite(Image.fromarray(r, 'RGBA')); floor.paste(base, (0, 0))
        # perspective expansion joints (2x supersampled)
        S = 2; seam = Image.new('RGBA', (W * S, fh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(seam)
        Zw = f * cam / (wy - yh); step = 1.5
        Z = Zw
        while True:
            y = yh + f * cam / Z
            if y > H + 5: break
            yy = (y - wy) * S;
            t = min(1, (y - wy) / 300)
            d.line((0, yy, W * S, yy), fill=(40, 70, 52, int(14 + 10 * t)), width=2)
            d.line((0, yy + 2, W * S, yy + 2), fill=(255, 255, 255, int(40 * t + 10)), width=2)
            Z -= step
            if Z < .2: break
        for k in range(-14, 15):
            X = k * step
            x_top = self.vp_x + X * (wy - yh) / cam; x_bot = self.vp_x + X * (H - yh) / cam
            d.line((x_top * S, 0, x_bot * S, fh * S), fill=(40, 70, 52, 20), width=2)
            d.line((x_top * S + 3, 0, x_bot * S + 3, fh * S), fill=(255, 255, 255, 40), width=2)
        seam = seam.resize((W, fh), Image.LANCZOS)
        # seams fade near the wall (hazy) and are subtle overall
        sa = np.array(seam).copy(); sa[..., 3] = (sa[..., 3] * np.clip(np.linspace(.5, 1, fh), 0, 1)[:, None]).astype('uint8')
        floor.alpha_composite(Image.fromarray(sa, 'RGBA'))
        # green light pool from the wash spilling on the floor
        gx = self.glow[0]
        pool = blur(radial(W, fh, gx, 30, W * .5, fh * .62, GREEN, .26 * self.wash, 1.3), 25); floor.alpha_composite(pool)
        self.canvas.paste(floor, (0, wy))

    # ------------------------------------------------------------ grounding
    def _key_shear(self): return .24, .13     # shadow shear (right) and depth squash (back) per unit height

    def ground(self, layer, x, y, base_y, foot=None, strength=1.0, refl=.13, shadow_len=1.0, ao_wide=1.0, floor_surface=True):
        """paste RGBA `layer` with top-left at (x,y). base_y = y of the contact line on the floor (absolute).
        Casts: wide AO, tight contact AO from the base plate, directional cast shadow (one key light), faint floor reflection."""
        W, H = self.W, self.H
        al = layer.getchannel('A'); lw, lh = layer.size
        a = np.array(al)
        rows = np.where((a > 128).any(1))[0]; bot = rows[-1]                         # lowest opaque row (layer coords)
        fp_h = max(4, int(lh * .05))
        foot_mask = np.zeros_like(a); foot_mask[max(0, bot - fp_h):bot + 1] = a[max(0, bot - fp_h):bot + 1]
        dy = base_y - (y + bot)                                                       # shift so lowest row sits on base_y
        by = y + dy                                                                   # adjusted top y for the layer
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        # --- cast shadow: silhouette sheared right / squashed back, blurred progressively with distance
        sx, sq = self._key_shear(); sx *= shadow_len; sq *= shadow_len
        cast_h = int(lh * sq) + 6
        out_w = lw + int(lh * sx) + 40; out_h = cast_h + 12
        cast = self._shear_shadow(al.crop((0, 0, lw, bot + 1)), sx, sq, out_w, out_h)
        near = blur(cast, 3); far = blur(cast, 16)
        ramp = np.linspace(1, 0, out_h)[:, None] ** 1.0          # 1 at base (row out_h-6) ... go: top rows are far
        # row index 0 = farthest (top), rows near bottom = near base
        t = np.linspace(0, 1, out_h)[:, None]                    # 0 far -> 1 near
        na, fa = np.array(near).astype('float32'), np.array(far).astype('float32')
        ca = (na * t + fa * (1 - t)) * (t ** .6) * .62 * strength
        cs = Image.fromarray(np.clip(ca, 0, 255).astype('uint8'), 'L')
        col = Image.new('RGBA', cs.size, (18, 46, 30, 0)); col.putalpha(cs)
        sh.alpha_composite(col, (int(x), int(base_y - out_h + 6)))
        # --- wide soft AO beneath (large radius, centred on footprint)
        fm = Image.fromarray(foot_mask, 'L')
        big = Image.new('L', (W, H), 0); big.paste(fm, (int(x), int(by)))
        # squash footprint into a flat ellipse-like pad
        fx0, fx1 = np.where(foot_mask.any(0))[0][[0, -1]]
        cxp = x + (fx0 + fx1) / 2; wfp = (fx1 - fx0)
        ao1 = Image.new('L', (W, H), 0); d = ImageDraw.Draw(ao1)
        d.ellipse((cxp - wfp * .66, base_y - 26 * ao_wide, cxp + wfp * .66, base_y + 30 * ao_wide), fill=120)
        ao1 = blur(ao1, 20 * ao_wide)
        ao2 = Image.new('L', (W, H), 0); d = ImageDraw.Draw(ao2)
        d.ellipse((cxp - wfp * .54, base_y - 9, cxp + wfp * .54, base_y + 11), fill=190)
        ao2 = blur(ao2, 6)
        # tight contact: the plate silhouette itself, pushed 2px down, blurred 2px
        ao3 = Image.new('L', (W, H), 0); ao3.paste(fm.point(lambda v: int(v * .85)), (int(x), int(by) + 3)); ao3 = blur(ao3, 2.5)
        for m, c, k in ((ao1, (16, 44, 28), .70), (ao2, (10, 30, 20), .75), (ao3, (6, 20, 12), .80)):
            L = Image.new('RGBA', (W, H), c + (0,)); L.putalpha(m.point(lambda v, k=k: int(v * k * strength))); sh.alpha_composite(L)
        self.canvas.alpha_composite(sh)
        # --- reflection in polished floor (flip about contact line, fades fast)
        if refl > 0:
            rh = int(lh * .20); fl = layer.crop((0, max(0, bot - rh), lw, bot + 1)).transpose(Image.FLIP_TOP_BOTTOM)
            fa = np.array(fl.getchannel('A')).astype('float32') * (np.linspace(refl, 0, fl.height) ** 1.2)[:, None] / (refl ** 1.2 if refl else 1)
            fl.putalpha(Image.fromarray(fa.astype('uint8'), 'L')); fl = blur(fl, 1.6)
            self.canvas.alpha_composite(fl, (int(x), int(base_y + 3)))
        self.canvas.alpha_composite(layer, (int(x), int(by)))
        return (int(x), int(by))

    def _shear_shadow(self, silh, sx, sq, out_w, out_h):
        """project silhouette (L, height lh, lowest row = base) onto the floor: squash vertically by sq, shear right by sx per px of height."""
        lw, lh = silh.size
        sm = silh.resize((lw, max(2, int(lh * sq))), Image.BILINEAR)           # squashed height
        hh = sm.height
        # shear: row r (0 = top / farthest) is shifted right by (hh - r)/sq*sx
        out = Image.new('L', (out_w, out_h), 0)
        arr = np.array(sm); res = np.zeros((out_h, out_w), 'uint8')
        for r in range(hh):
            shift = int(round((hh - 1 - r) / sq * sx))
            row = arr[r];
            xs0 = shift; xe = min(out_w, shift + lw)
            yv = out_h - 6 - (hh - 1 - r) - 1
            if 0 <= yv < out_h and xe > xs0: res[yv, xs0:xe] = np.maximum(res[yv, xs0:xe], row[:xe - xs0])
        return Image.fromarray(res, 'L')

    def vignette(self, amt=.06):
        W, H = self.W, self.H; y, x = np.mgrid[0:H, 0:W]
        d = np.sqrt(((x - W / 2) / (W * .75)) ** 2 + ((y - H * .45) / (H * .85)) ** 2)
        a = (np.clip(d - .55, 0, 1) ** 1.5 * amt * 255).astype('uint8')
        L = Image.new('RGBA', (W, H), (20, 50, 35, 0)); L.putalpha(Image.fromarray(a)); self.canvas.alpha_composite(L)


# ---------------------------------------------------------------- the bar counter piece (shared material: white stone top, light fluted oak front)
def counter_layer(w, top_h, thick, panel_h, toe=26, depth=60, seed=5, side=0):
    """returns RGBA layer: top surface (depth px, seen from above), stone front edge (thick), oak fluted panel (panel_h), toe-kick recess.
    layer height = depth + thick + panel_h + toe ; top surface starts at y=0. `side` = width of the visible right side sliver."""
    H = depth + thick + panel_h + toe; W = w + side
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    rng = np.random.default_rng(seed)
    # ---- stone top surface (lit, slightly receding): subtle veining + soft reflection of the lit wall at the far edge
    top = np.zeros((depth, w, 3), 'float32'); top[:] = np.array([247, 247, 244])
    gy = np.linspace(0, 1, depth)[:, None, None]
    top = top * (1 - .05 * gy) + np.array([232, 244, 236]) * .0
    vein = noise(w, depth, 90, 6, seed + 1); v = np.clip(1 - np.abs(vein - .5) * 14, 0, 1) ** 2
    vein2 = noise(w, depth, 200, 14, seed + 2); v2 = np.clip(1 - np.abs(vein2 - .55) * 9, 0, 1) ** 2
    top = top - (v[..., None] * 9 + v2[..., None] * 6) + grain(w, depth, seed)[..., None] * .8
    far = np.clip(1 - np.linspace(0, 1, depth) * 6, 0, 1)[:, None, None] * 7      # far edge catches the green wash
    top = top + far * np.array([-.4, .35, -.2])
    Lt = Image.fromarray(np.clip(top, 0, 255).astype('uint8'), 'RGB').convert('RGBA')
    L.alpha_composite(Lt, (0, 0))
    # ---- stone front edge (vertical face, slightly in shade) with bright top bevel and darker bottom lip
    fe = np.zeros((thick, w, 3), 'float32'); fe[:] = np.array([232, 234, 231])
    ty = np.linspace(0, 1, thick)[:, None, None]
    fe = fe * (1 - .07 * ty) + (noise(w, thick, 120, 4, seed + 3)[..., None] - .5) * 6 + grain(w, thick, seed + 4)[..., None] * .8
    # soft left-to-right falloff: key light is on the left
    fe = fe * (1 - np.linspace(0, .045, w)[None, :, None])
    Le = Image.fromarray(np.clip(fe, 0, 255).astype('uint8'), 'RGB').convert('RGBA'); L.alpha_composite(Le, (0, depth))
    d = ImageDraw.Draw(L, 'RGBA')
    d.line((0, depth, w, depth), fill=(255, 255, 255, 255), width=2)                    # bevel highlight
    d.line((0, depth + 2, w, depth + 2), fill=(214, 220, 214, 140), width=1)
    d.line((0, depth + thick - 1, w, depth + thick - 1), fill=(120, 130, 120, 120), width=2)  # lower arris
    # ---- fluted oak panel, set back under the overhang (shadowed under the slab)
    ph = panel_h
    wood = np.zeros((ph, w, 3), 'float32'); wood[:] = np.array([232, 211, 178])
    xs = np.arange(w)[None, :]; pitch = 16.0
    ph_ = (xs % pitch) / pitch
    flute = (np.cos(ph_ * 2 * np.pi) * .5 + .5)                                          # 1 at flute crown, 0 in groove
    shade = (flute ** .8 - .5) * 20 - np.where(ph_ > .5, (ph_ - .5) * 14, 0)             # lit left, shadowed right of each rib
    grain_v = (noise(w, ph, 3, 90, seed + 5) - .5) * 14 + (noise(w, ph, 1, 40, seed + 6) - .5) * 5
    wood = wood + (shade[..., None] if shade.ndim == 3 else shade[:, :, None]) * np.array([1, 1, 1.05]) + grain_v[..., None] * np.array([1, .9, .7])
    py = np.linspace(0, 1, ph)[:, None, None]
    wood = wood * (1 - .22 * np.clip(1 - py * 7, 0, 1) - .10 * py)                       # overhang shadow at top, floor falloff below
    wood = wood * (1 - np.linspace(0, .06, w)[None, :, None])
    Lw = Image.fromarray(np.clip(wood, 0, 255).astype('uint8'), 'RGB').convert('RGBA'); L.alpha_composite(Lw, (0, depth + thick))
    # slab shadow cast onto the panel (soft)
    sdw = Image.new('L', (w, ph), 0); ImageDraw.Draw(sdw).rectangle((0, 0, w, 6), fill=150); sdw = blur(sdw, 7)
    Ls = Image.new('RGBA', (w, ph), (60, 40, 20, 0)); Ls.putalpha(sdw.point(lambda v: int(v * .55))); L.alpha_composite(Ls, (0, depth + thick))
    # ---- toe-kick recess: dark gap (shadowed) so the cabinet reads as standing, not floating
    tk = Image.new('RGBA', (w, toe), (52, 44, 36, 255)); ta = np.linspace(.0, 1, toe);
    tk_arr = np.array(tk).astype('float32'); tk_arr[..., :3] *= np.linspace(1.15, .75, toe)[:, None, None]; tk_arr[..., :3] += grain(w, toe, seed + 9)[..., None] * .8
    L.alpha_composite(Image.fromarray(np.clip(tk_arr, 0, 255).astype('uint8'), 'RGBA'), (0, depth + thick + ph))
    d.line((0, depth + thick + ph, w, depth + thick + ph), fill=(30, 24, 18, 170), width=2)
    # ---- right-hand side sliver (receding face, in shade) keeps the object solid
    if side:
        sl = Image.new('RGBA', (side, H - depth * 0), (0, 0, 0, 0)); sd = ImageDraw.Draw(sl)
        sd.polygon([(0, depth), (side, depth - int(depth * .3)), (side, H - toe - int(toe * .3)), (0, H)], fill=(168, 150, 124, 255))
        sd.polygon([(0, depth), (side, depth - int(depth * .3)), (side, depth - int(depth * .3) + thick), (0, depth + thick)], fill=(205, 208, 204, 255))
        L.alpha_composite(sl, (w, 0))
    return L


def lying(c, scale_w):
    """product lying on the counter top: cutout scaled to a given width, cropped to its alpha bbox"""
    c = c.crop(c.getchannel('A').getbbox()); r = scale_w / c.width
    return c.resize((scale_w, max(1, int(c.height * r))), Image.LANCZOS)


def cutout_on(top_layer, item, cx, base_y, shadow=(8, 22, 14), strength=1.0, key=(.55, .22), lim=None, lim0=0):
    """stand/lay a cutout on the top surface of a counter layer: contact + short cast shadow (same key light), then the item."""
    item = item.convert('RGBA'); iw, ih = item.size
    al = item.getchannel('A'); a = np.array(al)
    rows = np.where((a > 128).any(1))[0]; bot = rows[-1]
    x = int(cx - iw / 2); y = int(base_y - bot)
    L = top_layer; Wt, Ht = L.size
    sh = Image.new('L', (Wt, Ht), 0)
    # cast: sheared right + slightly back
    sx, sq = key; hh = max(2, int(ih * .20)); sm = al.crop((0, 0, iw, bot + 1)).resize((iw, hh), Image.BILINEAR)
    arr = np.array(sm); res = Image.new('L', (iw + int(ih * sx * .5) + 20, hh + 4), 0); ra = np.array(res)
    for r in range(hh):
        shift = int(round((hh - 1 - r) / .2 * sx * .5)); row = arr[r]
        ra[r + 2, shift:shift + iw] = np.maximum(ra[r + 2, shift:shift + iw], row)
    sh.paste(Image.fromarray(ra, 'L'), (x, int(base_y - hh - 1)))
    sh = blur(sh, 3.5)
    # contact pad
    pad = Image.new('L', (Wt, Ht), 0); fx = np.where(a[max(0, bot - 6):bot + 1].any(0))[0]
    if len(fx):
        ImageDraw.Draw(pad).ellipse((x + fx[0] - 4, base_y - 5, x + fx[-1] + 4, base_y + 5), fill=210)
    pad = blur(pad, 3)
    m = np.maximum(np.array(sh) * .62, np.array(pad) * .8) * strength
    if lim is not None: m[int(lim):] = 0
    m[:int(lim0)] = 0
    Ls = Image.new('RGBA', (Wt, Ht), shadow + (0,)); Ls.putalpha(Image.fromarray(np.clip(m, 0, 255).astype('uint8')))
    # keep shadow on the surface only: caller passes layer where top surface is rows [0..depth+thick); clip handled by caller
    L.alpha_composite(Ls)
    # faint reflection in the polished stone
    rh = int(ih * .10); fl = item.crop((0, max(0, bot - rh), iw, bot + 1)).transpose(Image.FLIP_TOP_BOTTOM)
    fa = np.array(fl.getchannel('A')).astype('float32') * (np.linspace(.12, 0, fl.height) ** 1.1)[:, None] / .12 * .12
    if lim is not None: fa[max(0, int(lim - base_y - 2)):] = 0
    # (reflection starts below base_y so lim0 not needed)
    fl.putalpha(Image.fromarray(fa.astype('uint8'), 'L')); fl = blur(fl, 1.2)
    L.alpha_composite(fl, (x, int(base_y + 2)))
    L.alpha_composite(item, (x, y))
