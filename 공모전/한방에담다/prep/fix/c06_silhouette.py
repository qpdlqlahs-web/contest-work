import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
base=np.array(Image.open('prep/fix/C06_final_1440.png').convert('RGB')).astype(float)
c=np.array(Image.open('img/C06c_1.png').convert('RGB')).astype(float)
H,W,_=c.shape
def wall_est(a):
    w=a.copy()
    t=np.clip((np.arange(W)-100)/(680-100),0,1)
    for y in range(680,1780):
        l=a[y,60:140].mean(0); r=a[y,640:720].mean(0)
        w[y]=l[None]*(1-t[:,None])+r[None]*t[:,None]
    return w
wc=wall_est(c)
L=c.mean(2); WL=wc.mean(2)
m=np.zeros((H,W),bool); m[700:1741,150:600]=(WL-L)[700:1741,150:600]>14
m=ndi.binary_closing(m,structure=np.ones((19,19)))
m=ndi.binary_fill_holes(m)
m=ndi.binary_opening(m,structure=np.ones((5,5)))
lab,n=ndi.label(m); 
if n>1:
    sizes=ndi.sum(m,lab,range(1,n+1)); m=lab==(1+int(np.argmax(sizes)))
mi=Image.fromarray((m*255).astype('uint8'))
d=ImageDraw.Draw(mi)
d.polygon([(320,880),(240,845),(205,790),(235,780),(290,820),(330,850)],fill=255)
d.ellipse((200,770,250,820),fill=255)
m=np.array(mi)>0; m=ndi.binary_fill_holes(m); m[1741:]=False
# erase old blurry shadow in work area
wb=wall_est(base)
rng=np.random.default_rng(3)
er=np.zeros((H,W),bool); er[700:1741,120:620]=True
out=base.copy()
erm=Image.fromarray((er*255).astype('uint8')).filter(ImageFilter.GaussianBlur(10))
erm=np.array(erm)[...,None]/255.
noise=rng.normal(0,1.2,base.shape)
out=out*(1-erm)+(wb+noise)*erm
# fill silhouette
sm=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(3.5)))[...,None]/255.
col=np.array([206,171,134],float)
# keep slight lighting variation: scale by wall luminance relative
rel=(wb.mean(2,keepdims=True)/np.maximum(wb.mean(2,keepdims=True)[1000,370],1))
fill=col[None,None,:]*rel
out=out*(1-sm)+fill*sm
o=Image.fromarray(np.clip(out,0,255).astype('uint8'))
o.save('prep/fix/C06_final2_1440.png'); o.resize((1080,1920),Image.LANCZOS).save('prep/fix/C06_final2.png')
o.resize((563,1000)).save(r'E:\ClaudeWork\temp\c06f2.jpg')
o.crop((80,650,760,1800)).resize((340,575)).save(r'E:\ClaudeWork\temp\c06f2crop.jpg')
print('ok')
