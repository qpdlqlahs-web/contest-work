# -*- coding: utf-8 -*-
"""v3 썸네일: 수건 C10e 1.25배 펀치인(캐릭터 3인 중심, 물 영역 축소) + 제목(감초=#E8B64C+먹 외곽선). 눈 뜬 버전은 이번엔 안 함."""
from PIL import Image
import numpy as np
import render as R
im = Image.open(R.ROOT / "img/C10e_1.png").convert("RGB")      # 1440x2560
s = 1440 / 1080
cw, ch = 1080 / 1.25, 1920 / 1.25                              # 864 x 1536 (1080 좌표)
x0, y0 = 113, 155
th = im.crop((int(x0 * s), int(y0 * s), int((x0 + cw) * s), int((y0 + ch) * s))).resize((1080, 1920), Image.LANCZOS)
th.save(R.PREP / "stills/C10e_thumb125.png")
R.build_sprites()
base = np.array(th)
Image.fromarray(base).save(R.OUT / "_check" / "thumb_v3_notext.jpg", quality=95)
t = base.copy()
a1 = R.outlined(["약방에"], R.F_HAH, 215, R.INK, R.HANJI, 10)[0]
a2 = R.outlined(["감초"], R.F_HAH, 300, R.YEL, R.INK, 13)[0]
R.paste_c(t, a1, 540, 320)
R.paste_c(t, a2, 540, 545)
Image.fromarray(t).save(R.OUT / "_check" / "thumb_v3_title.jpg", quality=95)
print("ok")
