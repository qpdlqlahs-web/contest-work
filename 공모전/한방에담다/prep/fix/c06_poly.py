import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
c=Image.open('img/C06c_1.png').convert('RGB'); d=Image.open('img/C06d_1.png').convert('RGB')
W,H=c.size; a=np.array(c).astype(float)
P=lambda pts:[(x*2+80,y*2+650) for x,y in pts]
body=P([(118,90),(118,55),(128,44),(148,40),(162,48),(165,78),(178,80),(195,88),(203,105),(200,118),
        (205,135),(210,150),(203,160),(203,170),(197,180),(192,192),(185,197),
        (205,215),(225,260),(238,320),(242,365),(230,400),(218,420),(216,480),(216,545),
        (70,545),(62,470),(48,420),(42,360),(50,290),(70,230),(95,195),(118,180),(125,150),(118,120)])
mk=Image.new('L',(W,H),0); dr=ImageDraw.Draw(mk)
dr.polygon(body,fill=255)
dr.ellipse(tuple(P([(66,99),(128,136)])[0]+P([(66,99),(128,136)])[1]),fill=255)   # ikseongwan wing
m=np.array(mk)>0
m=ndi.binary_dilation(m,iterations=4)
# per-row median shadow tone from inside the figure (lines are lighter -> median ~ shadow tone)
L=a.mean(2); tone=np.zeros((H,3))
for y in range(H):
    xs=np.where(m[y])[0]
    if len(xs)>10:
        px=a[y,xs]; lum=px.mean(1); sel=px[lum<=np.percentile(lum,40)]
        tone[y]=np.median(sel,0)
ys=np.where(tone.sum(1)>0)[0]
for k in range(3): tone[ys,k]=ndi.uniform_filter1d(tone[ys,k],61)
fill=np.repeat(tone[:,None,:],W,1)
sm=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(3.5)))[...,None]/255.
out=a*(1-sm)+fill*sm
o=Image.fromarray(np.clip(out,0,255).astype('uint8'))
mb=Image.new('L',(W,H),0); ImageDraw.Draw(mb).rectangle((0,2110,W,H),255); mb=mb.filter(ImageFilter.GaussianBlur(12))
o=Image.composite(d,o,mb)
o.save('prep/fix/C06_final3_1440.png'); o.resize((1080,1920),Image.LANCZOS).save('prep/fix/C06_final3.png')
o.resize((563,1000)).save(r'E:\ClaudeWork\temp\c06f3.jpg')
print('ok')
