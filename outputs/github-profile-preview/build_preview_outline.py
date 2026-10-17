from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageChops
B=Path(__file__).resolve().parent
rng=np.random.default_rng(42); W,H=600,640
src=Image.open('/Users/mani/Documents/Github/source-prepped.png').convert('L')
a=np.array(src); yy,xx=np.where(a<235)
src=src.crop((max(0,int(xx.min())-12),max(0,int(yy.min())-12),min(src.width,int(xx.max())+12),min(src.height,int(yy.max())+12)))
src=ImageOps.contain(src,(176,176),Image.Resampling.LANCZOS)
a=np.asarray(src.filter(ImageFilter.GaussianBlur(.8)),dtype=float)/255
vy,vx=np.gradient(a); edge=np.hypot(vx,vy)
y,x=np.where(edge>.065)
# Retain contour brightness while omitting low-contrast texture.
strength=np.clip(edge[y,x]/.24,.25,1)
step=2.95
p=np.column_stack(((x-src.width/2)*step+300,y*step+70))
n=len(p)
phase=rng.uniform(0,math.tau,n); rad=np.sqrt(rng.uniform(0,1,n))
cloud=np.column_stack((300+np.cos(phase)*rad*360,330+np.sin(phase)*rad*180))
swirl=np.column_stack((300+np.cos(phase+1.9)*rad*400,330+np.sin(phase+1.9)*rad*140))
land=.48+.20*(1-p[:,1]/640)+rng.uniform(0,.09,n)
pre=land-.12
above=p-np.column_stack((np.zeros(n),rng.uniform(100,260,n)))
paths=np.stack((cloud,cloud,swirl,above,p,p,p))
times=np.stack((np.zeros(n),np.full(n,.10),np.full(n,.31),pre,land,np.full(n,.94),np.ones(n)))
brightness=(strength*180+75).astype(int)
length=rng.uniform(25,110,n)
star=[]
for j in range(10):
 angle=-math.pi/2+j*math.pi/5; r=100 if j%2==0 else 43
 star.append((math.cos(angle)*r,math.sin(angle)*r))
poly=' '.join(f'{x:.1f},{y:.1f}' for x,y in star)
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="640" viewBox="0 0 600 640" role="img" aria-label="A white star bursts into shooting stars that form Mani’s portrait"><title>White shooting-star portrait</title><defs><linearGradient id="tail" x1="0" y1="0" x2="0" y2="1"><stop stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white" stop-opacity=".8"/></linearGradient><filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3"/></filter></defs><rect width="600" height="640" rx="14" fill="#05070b"/>']
parts.append(f'<g transform="translate(300 300)"><g><animateTransform attributeName="transform" type="scale" values=".7;1;0;0" keyTimes="0;.06;.105;1" dur="14s" repeatCount="indefinite"/><polygon points="{poly}" fill="white" opacity=".25" filter="url(#glow)"/><polygon points="{poly}" fill="#f5f7ff"/></g></g>')
for i in range(n):
 vals=';'.join(f'{v[0]:.2f} {v[1]:.2f}' for v in paths[:,i]); kt=';'.join(f'{v:.5f}' for v in times[:,i]); b=brightness[i]
 parts.append(f'<g><animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{kt}" dur="14s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.085;.13;.94;1" dur="14s" repeatCount="indefinite"/><circle r="{.65+strength[i]*.45:.2f}" fill="rgb({b},{b},{b})"/>')
 if i%2==0:
  parts.append(f'<path d="M0 {-length[i]:.1f}V-2" stroke="url(#tail)" stroke-width=".85" opacity="0"><animate attributeName="opacity" values="0;0;.8;.8;0;0" keyTimes="0;.32;{pre[i]:.5f};{land[i]:.5f};{land[i]+.035:.5f};1" dur="14s" repeatCount="indefinite"/></path>')
 if i%23==0:
  parts.append('<path d="M-3.8 0H3.8M0 -3.8V3.8" stroke="white" stroke-width=".8"><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.12;.30;.47;1" dur="14s" repeatCount="indefinite"/></path>')
 parts.append('</g>')
parts.append('</svg>'); (B/'profile-ascii.svg').write_text(''.join(parts))
frames=[]
for frame in range(210):
 t=frame/210
 im=Image.new('RGB',(W,H),'#05070b'); light=Image.new('RGB',(W,H)); d=ImageDraw.Draw(light)
 if t<.105:
  s=np.interp(t,[0,.06,.105],[.7,1,0]); d.polygon([(300+x*s,300+y*s) for x,y in star],fill=(245,247,255))
 for i in range(n):
  if t<.085: continue
  ts=times[:,i]; k=min(5,max(0,np.searchsorted(ts,t,side='right')-1)); u=(t-ts[k])/(ts[k+1]-ts[k]); v=paths[k,i]*(1-u)+paths[k+1,i]*u
  alpha=min(1,(t-.085)/.045,max(0,(1-t)/.06)); b=int(brightness[i]*alpha)
  if i%2==0 and .32<t<land[i]+.035:
   opacity=np.interp(t,[.32,pre[i],land[i],land[i]+.035],[0,.8,.8,0])
   for q in range(8):
    g=int(220*opacity*alpha*(1-q/8)); d.line((v[0],v[1]-length[i]*q/8,v[0],v[1]-length[i]*(q+1)/8),fill=(g,g,g))
  d.ellipse((v[0]-.8,v[1]-.8,v[0]+.8,v[1]+.8),fill=(b,b,b))
  if i%23==0 and .1<t<.47:
   gl=int(255*alpha*np.interp(t,[.1,.12,.30,.47],[0,1,1,0])); d.line((v[0]-3,v[1],v[0]+3,v[1]),fill=(gl,gl,gl)); d.line((v[0],v[1]-3,v[0],v[1]+3),fill=(gl,gl,gl))
 im=ImageChops.add(im,light); im=ImageChops.add(im,light.filter(ImageFilter.GaussianBlur(2)).point(lambda z:int(z*.32)))
 im=im.resize((450,480),Image.Resampling.LANCZOS)
 if frame==100: im.save(B/'shooting-stars-preview.png')
 if frame==175: im.save(B/'portrait-preview.png')
 frames.append(im.quantize(colors=96))
frames[0].save(B/'sample-preview.gif',save_all=True,append_images=frames[1:],duration=67,loop=0,optimize=False)
print(f'Created reference-inspired star burst and outline portrait with {n} points.')
