import numpy as np, sys
from PIL import Image, ImageFilter
a=np.array(Image.open('img/C06c_1.png').convert('RGB')).astype(float); H,W,_=a.shape
L=a.mean(2)
# wall estimate: heavy blur of image with shadows replaced -> use per-row max-ish of clean band
x0,x1,y0,y1=150,600,700,1760
wall=np.zeros_like(a)
for y in range(y0,y1):
    l=a[y,60:140].mean(0); r=a[y,640:720].mean(0)
    t=(np.arange(W)-100)/(680-100); t=np.clip(t,0,1)
    wall[y]=l[None]*(1-t[:,None])+r[None]*t[:,None]
WL=wall.mean(2)
m=np.zeros((H,W)); m[y0:y1,x0:x1]=(WL[y0:y1,x0:x1]-L[y0:y1,x0:x1])>10
mi=Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
mi=mi.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(3))
mk=np.array(mi)[...,None]/255.
# right shadow ratio
rs=(a[1100:1300,1000:1100].mean((0,1)))/(a[1100:1300,1300:1400].mean((0,1))+1e-6)
ratio=float(np.clip(rs.mean(),0.5,0.85)); print('ratio',ratio)
flat=wall*ratio
a=a*(1-mk)+flat*mk
Image.fromarray(np.clip(a,0,255).astype('uint8')).save('prep/fix/C06c_flat.png')
