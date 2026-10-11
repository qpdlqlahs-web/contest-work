# -*- coding: utf-8 -*-
"""v2 썸네일: 수건 C10e 1.22배 펀치인(C10e_thumb.png). 제목 포함 1장(감초=#E8B64C+먹 외곽선) + 없는 것 1장."""
from PIL import Image
import numpy as np
import render as R
R.build_sprites()
base = np.array(Image.open(R.PREP / "stills/C10e_thumb.png").convert("RGB"))
Image.fromarray(base).save(R.OUT / "_check" / "thumb_v2_notext.jpg", quality=95)
t = base.copy()
a1 = R.outlined(["약방에"], R.F_HAH, 215, R.INK, R.HANJI, 10)[0]
a2 = R.outlined(["감초"], R.F_HAH, 300, R.YEL, R.INK, 13)[0]
R.paste_c(t, a1, 540, 320)
R.paste_c(t, a2, 540, 545)
Image.fromarray(t).save(R.OUT / "_check" / "thumb_v2_title.jpg", quality=95)
print("ok")
