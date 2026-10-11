import os
from PIL import Image
R=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(R)
def after(n): return Image.open(f"{R}/stills/{n}.png")
def before(n):
    im=Image.open(f"{ROOT}/img/{n}_1.png").convert("RGB"); w,h=im.size
    if abs(w/h-16/9)>0.002:
        nw=round(h*16/9); x0=(w-nw)//2; im=im.crop((x0,0,x0+nw,h))
    return im.resize((1920,1080),Image.LANCZOS)
items={"C02":(640,470,860,700),"C03":(360,540,600,840),"C14":(680,930,1260,1060),"C19a":(1560,150,1760,260),
"C16c":(640,660,1560,900),"C21":(780,150,1040,330),"C18":(640,120,1000,560)}
for n,b in items.items():
    a,bf=before(n).crop(b),after(n).crop(b)
    s=2 if (b[2]-b[0])<400 else 1
    w,h=a.size
    sh=Image.new("RGB",(w*s*2+10,h*s),(0,0,0))
    sh.paste(a.resize((w*s,h*s)),(0,0)); sh.paste(bf.resize((w*s,h*s)),(w*s+10,0))
    sh.save(f"{R}/_check/still_{n}_before_after.jpg",quality=90)
