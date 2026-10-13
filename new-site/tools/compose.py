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
def load(n): return Image.open(os.path.join(root,'assets/hero',n+'.webp')).convert('RGBA')
def save(im,n):
    im=im.convert('RGB'); p=os.path.join(root,'assets/composed',n+'.webp'); im.save(p,quality=82,method=6); print(n,os.path.getsize(p)//1024,'KB')
if __name__=='__main__':
    save(place(backdrop(),load('station6'),600,H-210),'card-6')
    save(place(backdrop(),load('tower24s'),930,H-210),'card-24')
    save(place(backdrop(warm=1),load('tower24'),960,H-210),'card-48')
    save(backdrop(),'hero-backdrop')
