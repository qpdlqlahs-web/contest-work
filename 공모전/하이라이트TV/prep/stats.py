import sys
from PIL import Image
import numpy as np
names="C02 C03 C04 C05 C06b C07 C08 C09 C10 C11b C12 C13b C14 C15 C15b C17b C16c C18 C19a C19b C19c C20 C21 K4Sb".split()
for n in names:
    im=Image.open(f"img/{n}_1.png").convert("RGB"); a=np.asarray(im.resize((480,270))).astype(float)
    r,g,b=a[...,0].mean(),a[...,1].mean(),a[...,2].mean()
    y=(0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]).mean()
    print(n,im.size,f"G/R={g/r:.2f} B/R={b/r:.2f} Y={y:.0f}")
