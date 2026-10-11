# -*- coding: utf-8 -*-
"""썸네일 후보: C10d_thumb(1.2배 펀치인) 기반. 제목 타이포 포함 1장 + 없는 것 1장."""
from PIL import Image
import numpy as np
import render as R
R.build_sprites()
base = np.array(Image.open(R.PREP / "stills/C10d_thumb.png").convert("RGB"))
Image.fromarray(base).save(R.OUT / "_check" / "thumb_notext.jpg", quality=95)
t = base.copy()
a1 = R.outlined(["약방에"], R.F_HAH, 225, R.INK, R.HANJI, 10)[0]
a2 = R.outlined(["감초"], R.F_HAH, 300, R.INK, R.HANJI, 11)[0]
R.paste_c(t, a1, 540, 270)
R.paste_c(t, a2, 540, 500)
Image.fromarray(t).save(R.OUT / "_check" / "thumb_title.jpg", quality=95)
print("ok")
