from pathlib import Path
import xml.etree.ElementTree as ET
import html
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
B=Path(__file__).resolve().parent
rng=np.random.default_rng(24)
W,H=600,640
points=[]
for t in ET.parse(B/'original-portrait.svg').getroot().iter('{http://www.w3.org/2000/svg}text'):
 if t.get('textLength'):
  points.extend((float(t.get('x'))+j*8,float(t.get('y')),c) for j,c in enumerate(t.text or '') if not c.isspace())
xs,ys=zip(*[(p[0],p[1]) for p in points]); scale=min(500/(max(xs)-min(xs)),510/(max(ys)-min(ys)))
target=np.array([((x-(min(xs)+max(xs))/2)*scale+300,(y-min(ys))*scale+80) for x,y,c in points])
chars=[p[2] for p in points]; n=len(chars)
# A shower of bright heads and tapered tails, resolving into the original portrait.
arrival=.26+.24*target[:,1]/H+rng.uniform(0,.18,n)
start=np.maximum(.001,arrival-rng.uniform(.18,.30,n))
origin=target-np.column_stack((rng.uniform(40,130,n),target[:,1]+rng.uniform(40,130,n)))
tail=rng.uniform(30,95,n)
colors=[(255,255,255),(238,238,238),(215,215,215)]
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="640" viewBox="0 0 600 640" role="img" aria-label="Falling shooting stars reveal Mani’s portrait"><title>Shooting-star portrait</title><defs><linearGradient id="tail" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#ffffff" stop-opacity=".9"/></linearGradient></defs><rect width="600" height="640" rx="14" fill="#080d14"/>']
for i,c in enumerate(chars):
 p=target[i]; o=origin[i]; s=float(start[i]); a=float(arrival[i]); settle=a+.025
 col='#%02x%02x%02x'%colors[i%3]
 values=f'{o[0]:.2f} {o[1]:.2f};{o[0]:.2f} {o[1]:.2f};{p[0]:.2f} {p[1]:.2f};{p[0]:.2f} {p[1]:.2f}'
 parts.append(f'<g><animateTransform attributeName="transform" type="translate" values="{values}" keyTimes="0;{s:.5f};{a:.5f};1" dur="12s" repeatCount="indefinite"/>')
 parts.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{s:.5f};{s+.015:.5f};{a:.5f};{settle:.5f};1" dur="12s" repeatCount="indefinite"/>')
 if i%3==0:
  dx=tail[i]*(p[0]-o[0])/(p[1]-o[1]); dy=tail[i]
  parts.append(f'<path d="M{-dx:.2f} {-dy:.2f}L0 0" stroke="url(#tail)" stroke-width="1"/>')
 parts.append(f'<circle r="1.15" fill="{col}"/>')
 if i%31==0: parts.append('<path d="M-4 0H4M0 -4V4" stroke="#ffffff" stroke-width=".8"/>')
 parts.append(f'</g><text font-family="Menlo,Consolas,monospace" font-size="{12.9*scale:.2f}" fill="{col}" opacity="0">{html.escape(c)}<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a:.5f};{settle:.5f};.89;.98;1" dur="12s" repeatCount="indefinite"/></text></g>')
parts.append('</svg>'); (B/'profile-ascii.svg').write_text(''.join(parts))
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',max(7,round(12.9*scale)))
frames=[]
for frame in range(180):
 t=frame/180; im=Image.new('RGB',(W,H),'#080d14'); draw=ImageDraw.Draw(im)
 for i,c in enumerate(chars):
  p=target[i]; o=origin[i]; s=start[i]; a=arrival[i]; col=colors[i%3]
  if s<=t<a+.025:
   u=min(1,(t-s)/(a-s)); v=o+(p-o)*u
   alpha=min(1,(t-s)/.015,max(0,(a+.025-t)/.025))
   if i%3==0:
    slope=(p-o)/(p[1]-o[1])
    for k in range(8):
     v1=v-slope*tail[i]*k/8; v2=v-slope*tail[i]*(k+1)/8
     ink=tuple(int(q*alpha*(1-k/8)*.7) for q in col)
     draw.line((*v1,*v2),fill=ink,width=1)
   ink=tuple(int(q*alpha) for q in col)
   draw.ellipse((v[0]-1,v[1]-1,v[0]+1,v[1]+1),fill=ink)
   if i%31==0:
    draw.line((v[0]-4,v[1],v[0]+4,v[1]),fill=ink); draw.line((v[0],v[1]-4,v[0],v[1]+4),fill=ink)
  if t>=a:
   alpha=min(1,(t-a)/.025,max(0,(.98-t)/.09))
   draw.text(tuple(p),c,font=font,fill=tuple(int(q*alpha) for q in col),anchor='ls')
 im=im.resize((450,480),Image.Resampling.LANCZOS)
 if frame==72: im.save(B/'shooting-stars-preview.png')
 if frame==140: im.save(B/'portrait-preview.png')
 frames.append(im.quantize(colors=96))
frames[0].save(B/'sample-preview.gif',save_all=True,append_images=frames[1:],duration=67,loop=0,optimize=False)
print('Created falling-star SVG and animated preview.')
