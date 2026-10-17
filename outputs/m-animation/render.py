from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np
import subprocess
from pathlib import Path
base=Path(__file__).resolve().parent
W,H=540,960
rng=np.random.default_rng(27)
photo=ImageOps.fit(Image.open(base/'github-photo.png').convert('RGB'),(400,400))
a=np.array(photo)
# Omit the white background so the portrait floats in the darkness.
mask=(a.min(axis=2)<222)
luma=(a@np.array([.2126,.7152,.0722]))/255
edge=np.abs(np.gradient(luma)[0])+np.abs(np.gradient(luma)[1])
y,x=np.mgrid[0:400:3,0:400:3]
x=x.ravel(); y=y.ravel(); keep=mask[y,x]
x=x[keep]; y=y[keep]
px=x+70; py=y+265
colors=np.clip(a[y,x]*.7+np.array([105,88,53]),0,255).astype(np.uint8)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',380)
m=Image.new('L',(W,H)); d=ImageDraw.Draw(m); d.text((W/2,470),'M',font=font,fill=255,anchor='mm',stroke_width=1)
my,mx=np.where(np.array(m)>100)
n=len(px); sel=rng.integers(0,len(mx),n); mx=mx[sel]; my=my[sel]
sx=rng.uniform(-200,W+200,n); sy=rng.uniform(-250,H+250,n)
phase=rng.uniform(0,6.28,n); delay=rng.uniform(0,.45,n)
noise=rng.uniform(-1,1,(n,2)); stars=rng.uniform([0,0],[W,H],(110,2))
def ease(v):
 v=np.clip(v,0,1); return v*v*(3-2*v)
proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','24','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(base/'M-portrait-animation.mp4')],stdin=subprocess.PIPE)
for f in range(240):
 t=f/24
 im=Image.new('RGB',(W,H),(3,7,12)); dr=ImageDraw.Draw(im)
 for j,(xx,yy) in enumerate(stars):
  b=int(25+20*np.sin(t+j)); dr.point((xx,yy),fill=(b,b,int(b*.8)))
 if t<3.6:
  u=ease((t-delay)/2.3); xx=sx+(mx-sx)*u; yy=sy+(my-sy)*u
  cc=np.tile([242,212,142],(n,1))
 else:
  u=ease((t-3.6-delay)/2.8); xx=mx+(px-mx)*u; yy=my+(py-my)*u
  cc=np.array([242,212,142])*(1-u[:,None])+colors*u[:,None]
 shimmer=.72+.28*np.sin(t*3+phase)
 xx=xx+np.sin(phase+t*1.4)*1.1; yy=yy+np.cos(phase+t)*1.1
 particles=Image.new('RGB',(W,H)); pd=ImageDraw.Draw(particles)
 for j in range(n):
  col=tuple((cc[j]*shimmer[j]).astype(int)); xi=float(xx[j]); yi=float(yy[j])
  pd.point((xi,yi),fill=col)
  if j%9==0: pd.line((xi-1,yi,xi+1,yi),fill=col)
 glow=particles.filter(ImageFilter.GaussianBlur(3))
 from PIL import ImageChops
 im=ImageChops.add(im,glow); im=ImageChops.add(im,particles)
 # Fade into and out of the sequence.
 fade=min(1,t/.65,(10-t)/.7)
 if fade<1: im=Image.blend(Image.new('RGB',(W,H)),im,max(0,fade))
 proc.stdin.write(im.tobytes())
 if f in (72,200): im.save(base/f'preview-{f}.jpg')
proc.stdin.close()
if proc.wait(): raise SystemExit('Video encoding failed')
print(base/'M-portrait-animation.mp4')
