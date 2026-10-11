"""숏폼 v2 「퍼가요 말고 허락부터」 — 스타일 가이드 v2(2026-10-07 승인) 2장·0장·3장 구현.
1080x1920 30fps H.264 + AAC 48k. 음원 audio/T2.wav. 영상 생성 크레딧 0(6컷 원화 + 줌·팬·하드컷).
usage:
  python make_short_v2.py                 # 렌더 → out/v2/숏폼_v2.mp4 + out/v2/render_params.json
  python make_short_v2.py --still 0 2.2   # 지정 시각 프레임 PNG (out/v2/qa/)
  python make_short_v2.py --sheet         # 장면별 시작·끝 프레임 시트 (out/v2/qa/)
"""
import json, math, os, subprocess, sys
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "proposals", "type"))
import make_type_proposal as T            # 조판 함수 재사용(자간·대체 글리프·외곽선·효과음). import 시 cwd=프로젝트 루트
os.chdir(HERE)

# ---------------------------------------------------------------- 0장 공통
INK, BG, PURPLE, YEL, RED, LINE, WHITE = (40, 34, 60), (242, 238, 252), (150, 90, 200), (255, 216, 74), \
    (229, 72, 77), (217, 209, 240), (255, 255, 255)
F_TITLE, F_NARR, F_TALK, F_SFX = T.F["title"], T.F["narr"], T.F["talk"], T.F["sfx"]
F_B, F_XB, F_SB = T.F["b"], T.F["xb"], T.F["sb"]
AI_NOTE = "본 작품은 생성형 AI를 활용해 제작되었습니다"          # 한 글자도 바꾸지 않는다
W, H, FPS = 1080, 1920, 30
WIN_Y0, WIN_Y1 = 236, 1436                                         # 그림 창 (0,236)-(1080,1436) 9:10
WW, WH = W, WIN_Y1 - WIN_Y0
BAND = (0, 1436, 1080, 1484)                                       # 필수 표기 띠
AUDIO, OUT_DIR = "audio/T2.wav", "out/v2"
OUT = f"{OUT_DIR}/숏폼_v2.mp4"
VOLUME_DB = 2.2                                                   # 실측: 엔딩 후렴 포함 +2.3dB → -13.9 LUFS, +2.2dB → -14.0 LUFS

# ---------------------------------------------------------------- 실측 시각(초) — 보컬 스템 에너지 × 구간 Whisper 재인식 × 자음(마찰·파찰·비음) 교차
ON = dict(L1=0.84, L2=2.24, L3=3.47, L3b=4.48, L4=7.37, L4b=9.54, L5=11.16, L5b=13.26, L6=14.80, L6b=16.02,
          L7=18.40, L7b=20.80, L8=21.68, L8b=24.18, L9=25.38, L9b=27.52, NO=29.33, L10=30.06, CLAP1=31.76,
          CLAP2=32.08, L10b=32.32, L11=35.68, VOC_END=39.10)
CAP_LEAD = (0.10, 0.15, 0.12)                                      # 자막은 실제 시작보다 0.10~0.15초 먼저(목표 0.12)


def cap_frame(on):
    lo, hi, tgt = CAP_LEAD
    cands = [f for f in range(int((on - hi) * FPS) - 1, int((on - lo) * FPS) + 2) if lo - 1e-6 <= on - f / FPS <= hi + 1e-6]
    return min(cands, key=lambda f: abs(on - f / FPS - tgt))


def hit_frame(on): return int(round(on * FPS - 1))                 # 자막 변화 없는 컷·타격: 1프레임 앞



CHORUS = (18.39, 21.62)                                            # 엔딩 음원: 원곡 후렴 '퍼가요'(18.40) 직전 틈 ~ '(허락부터!)' 뒤·'쓸'(21.68) 앞
CHORUS_AT = 39.27                                                  # 엔딩 음원이 타임라인에서 시작하는 시각
XFADE = 0.025                                                      # 본곡 끝 ↔ 엔딩 음원 크로스페이드 25ms(페이드아웃·인 없음 → 무음 구멍·'…인' 조각 없음)
SONG_TRIM = round(CHORUS_AT + XFADE, 3)                            # 본곡은 39.295s에서 자름(마지막 25ms가 엔딩 첫 25ms와 겹침)
LOOP_FADE = 0.030                                                  # 루프 끝 마지막 30ms 페이드
TOTAL = round(CHORUS_AT + CHORUS[1] - CHORUS[0], 6)                # 42.5s
TOTAL_F = int(round(TOTAL * FPS)); assert abs(TOTAL_F / FPS - TOTAL) < 1e-9
END_F = cap_frame(CHORUS_AT + (ON["L7"] - CHORUS[0]))              # 엔딩 카드: '퍼'(타임라인 39.28s)보다 0.10~0.15s 앞 → 39.167s. 본곡 마지막 '매너인!'(~39.10s) 뒤
ENDING_LEN = round(TOTAL - END_F / FPS, 3)
AUDIO_DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO],
                                 capture_output=True, text=True).stdout)
SR = 48000


def ease(x): x = max(0.0, min(1.0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)
def ease_out(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def ease_out_back(x, c1=1.70158):
    x = max(0.0, min(1.0, x)); c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ---------------------------------------------------------------- 원화 + 원화 위 텍스트 처리(v1 로직 재사용, 가이드 글꼴로 교체)
art = {n: Image.open(f"img/P{n}.png").convert("RGB") for n in range(1, 7)}
cs = Image.open("img/charsheet.png").convert("RGB")

d = ImageDraw.Draw(art[1])                                         # 1컷 화면 라벨: 노트북 사진 아래 바(1448,1280)-(1639,1339)
d.rounded_rectangle((1450, 1282, 1637, 1337), 6, fill=(254, 229, 198))
T.draw_line(d, 1543.5, 1309.5, "출처: 인터넷", F_B, 34, track=-0.01, fill=INK)

art["2c"] = art[2].copy()                                          # 효과음 없는 2컷: 'FWEET!'(x930~) 앞에서 자르는 클로즈업용
d = ImageDraw.Draw(art[2])                                         # 2컷 영문 효과음 FWEET! → '삐익!!' (12각 폭발형 + 효과음 규격, -8°)
d.polygon(T.star((1056, 912), (176, 108), (236, 152), 12, rot=0.10, jitter=(1, .93, 1.06, .96, .9, 1.04)),
          fill=YEL, outline=INK, width=9)
T.sfx(art[2], (1056, 906), [("삐", 124, 6, 4), ("익", 142, -4, -3), ("!", 142, -6, -9), ("!", 142, -10, -15)],
      F_SFX, angle=8, fill=RED, strokes=((20, INK), (11, WHITE)), track=-0.05)

d = ImageDraw.Draw(art[6])                                         # 6컷 이젤 그림 이름표(출처 표시): 캔버스 왼쪽 아래
d.rounded_rectangle((712, 1172, 912, 1224), 8, fill=WHITE, outline=INK, width=4)
T.draw_line(d, 812, 1198, "그림: 복붙이", F_B, 31, track=-0.01, fill=INK)

art["6v"] = Image.open("img/_P6_v1.png").convert("RGB")             # 29.93~39.2s·엔딩: 웃는 복붙이·그린카드·꽃가루 원화(v1)
a = np.array(art["6v"]).astype(float); y0, y1, x0, x1 = 880, 1035, 290, 450   # 노트북 마크 제거: make_comic.py v1 평면 근사
yy, xx = np.mgrid[y0:y1, x0:x1]; inner = (yy >= 905) & (yy < 1010) & (xx >= 318) & (xx < 422)
A = np.c_[xx[~inner], yy[~inner], np.ones((~inner).sum())]
for c in range(3):
    coef, *_ = np.linalg.lstsq(A, a[y0:y1, x0:x1, c][~inner], rcond=None)
    blk = a[y0:y1, x0:x1, c]; blk[inner] = (coef[0] * xx + coef[1] * yy + coef[2])[inner]
art["6v"] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
art["6vL"] = art["6v"].copy()                                      # L·엔딩용 '그림: 복붙이' 라벨(K·K2에는 원화 그대로 → 가장자리에서 글자 안 잘림)
d = ImageDraw.Draw(art["6vL"])                                     # 원화의 빈 라벨(1191~1320 x 1447~1533) 지우기: ① 종이 흰색으로 덮고
d.rectangle((1186, 1445, 1328, 1539), fill=(254, 254, 253))
SH = 234                                                               # ② 같은 행의 왼쪽 해칭을 복제(이음 구간 위상 최적 + 언덕선 회피 탐색값)
src = art["6vL"].crop((1150 - SH, 1436, 1329 - SH, 1541))          #    원본 행 그대로라 아래 종이 여백·해칭 끝 모양 유지
mk = np.zeros((1541 - 1436, 1329 - 1150), np.float32)
for yy_ in range(mk.shape[0]):
    xr = 1316 - 1150 - (yy_ * 18) / mk.shape[0]                    #    오른쪽 경계: 원래 잔디 끝선처럼 기울임(1316→1298)
    xs_ = np.arange(mk.shape[1])
    mk[yy_] = np.clip((xs_ - 0) / 30, 0, 1) * np.clip((xr - xs_) / 6, 0, 1) * min(1.0, yy_ / 9)   # 왼쪽 30·오른쪽 6·위 9px 섞기
art["6vL"].paste(src, (1150, 1436), Image.fromarray((mk * 255).astype(np.uint8)))
LBL = (1140, 1350, 1294, 1422)                                     # 새 라벨: 원래보다 109px 위(덤불 아래), 푸시인 전 구간에서 자막 박스와 안 겹침
d = ImageDraw.Draw(art["6vL"])
d.rounded_rectangle(LBL, 10, fill=WHITE, outline=INK, width=4)
d.rounded_rectangle((LBL[0] + 2, LBL[1] + 2, LBL[2] - 2, LBL[1] + 24), 8, fill=(252, 206, 168)); d.rectangle((LBL[0] + 2, LBL[1] + 15, LBL[2] - 2, LBL[1] + 24), fill=(252, 206, 168))
d.line((LBL[0] + 2, LBL[1] + 25, LBL[2] - 2, LBL[1] + 25), fill=INK, width=3)
T.draw_line(d, (LBL[0] + LBL[2]) / 2, (LBL[1] + 26 + LBL[3]) / 2, "그림: 복붙이", F_B, 25, track=-0.02, fill=INK)

# 표기·테두리 안전 영역(원본 px): AI 원화 테두리 선과 상단 흰 띠 바깥은 쓰지 않는다(실측: 어두운 선/흰 행 검출 + 8px 여유)
SAFE = {1: (66, 280, 2333, 1718), 2: (129, 333, 2274, 1686), "2c": (129, 333, 922, 1686), 3: (65, 69, 2332, 1728), 4: (60, 353, 2339, 1736),
        5: (0, 282, 2389, 1792), 6: (0, 296, 2400, 1792),
        "6v": (61, 468, 2339, 1750), "6vL": (61, 468, 2339, 1750)}                               # _P6_v1: 상단 띠 선 452~460, 하단 선 1758~, 좌우 선 45~53 / 2347~


def C(key, cx, cy, h):                                             # 9:10 크롭 (중심, 높이)
    r = (cx - 0.45 * h, cy - 0.5 * h, cx + 0.45 * h, cy + 0.5 * h)
    s = SAFE[key]
    assert s[0] <= r[0] and s[1] <= r[1] and r[2] <= s[2] and r[3] <= s[3], (key, r, s)
    return r


def R(key, x0, y0, x1, y1):                                        # 좌표로 준 크롭: 9:10·안전 영역 검증
    assert abs((x1 - x0) / (y1 - y0) - 0.9) < 0.002, (key, x0, y0, x1, y1, (x1 - x0) / (y1 - y0))
    s = SAFE[key]
    assert s[0] <= x0 and s[1] <= y0 and x1 <= s[2] and y1 <= s[3], (key, (x0, y0, x1, y1), s)
    return (x0, y0, x1, y1)


# ---------------------------------------------------------------- 장면(이야기 시간순 P1→P6, 가사 시작점 하드컷). c0→c1 켄 번스
F = cap_frame
SC = [
    dict(n="A 퍼가요(P1 얼굴)", f=0, key=1, c0=(310, 600, 1210, 1600), c1=C(1, 760, 1090, 950), intro=True),
    dict(n="B 잠깐만(P2 호루라기)", f=F(ON["L2"]), key=2, c0=C(2, 742, 1015, 1340), c1=C(2, 705, 990, 1250), hit=True),
    dict(n="C1 마음에 쏙 든(P1)", f=F(ON["L3"]), key=1, c0=C(1, 1150, 999, 1420), c1=C(1, 1160, 1010, 1380)),
    dict(n="C2 사진 한 장(P1 사진)", f=hit_frame(ON["L3b"]), key=1, c0=C(1, 1560, 1150, 860), c1=C(1, 1560, 1170, 770)),
    dict(n="D 퍼 가기 전에(P5 돋보기)", f=F(ON["L4"]), key=5, c0=C(5, 690, 1010, 1300), c1=C(5, 720, 1010, 1180)),
    dict(n="D2 누가 만든 건지(P5 돋보기)", f=int(round(9.27 * FPS)), key=5, c0=C(5, 800, 1060, 820), c1=C(5, 820, 1065, 750)),
    dict(n="E 출처만?(P2 복붙이)", f=F(ON["L5"]), key=2, c0=C(2, 1782, 1000, 1083), c1=C(2, 1760, 985, 1000)),
    dict(n="E2 아니죠(P2 레드카드)", f=int(round(12.80 * FPS)), key="2c", c0=C("2c", 540, 800, 845), c1=C("2c", 560, 795, 800)),
    dict(n="F 무료로(P5 요정)", f=F(ON["L6"]), key=5, c0=C(5, 1690, 1040, 1500), c1=C(5, 1700, 1000, 1380)),
    dict(n="F2 공유마당(P5 태블릿)", f=hit_frame(ON["L6b"]), key=5, c0=C(5, 1565, 1229, 1122), c1=C(5, 1565, 1235, 1100)),
    dict(n="G 허락부터(P4 요정)", f=F(ON["L7"]), key=4, c0=R(4, 1365, 353, 2325, 1419.67), c1=R(4, 1368, 365, 2300, 1400.56)),
    dict(n="G2 (허락부터!)(P4 요정)", f=F(ON["L7b"]), key=4, c0=C(4, 1720, 760, 800), c1=C(4, 1720, 770, 750)),
    dict(n="H 출처까지(P6 댓글·이름표)", f=F(ON["L8"]), key=6, c0=C(6, 610, 1040, 1089), c1=C(6, 640, 1030, 1000)),
    dict(n="H2 (출처까지!)(P6 이름표)", f=F(ON["L8b"]), key=6, c0=C(6, 750, 1061, 822), c1=C(6, 760, 1050, 760)),
    dict(n="I AI한테(P3)", f=F(ON["L9"]), key=3, c0=C(3, 1380, 899, 1640), c1=C(3, 1360, 905, 1600)),
    dict(n="I2 똑같이·비슷하게(P3 그림)", f=hit_frame(ON["L9b"]), key=3, c0=C(3, 580, 575, 1010), c1=C(3, 545, 560, 940)),
    dict(n="J NO(P4 로봇 X)", f=hit_frame(ON["NO"]), key=4, c0=C(4, 1550, 1000, 1222), c1=C(4, 1540, 1000, 1180), hit=True),
    dict(n="K 창작자에게 박수(P6 v1 복붙이)", f=F(ON["L10"]), key="6v", c0=R("6v", 334, 468, 1487.8, 1750), c1=R("6v", 360, 490, 1485, 1740)),
    dict(n="K2 K-저작권 매너(P6 v1 요정)", f=hit_frame(ON["L10b"]), key="6v", c0=R("6v", 1276, 508, 2339, 1689.11), c1=R("6v", 1280, 515, 2335, 1687.22)),
    dict(n="L 오늘부터(P6 v1 복붙이 그림)", f=F(ON["L11"]), key="6vL", c0=R("6vL", 430, 515, 1480, 1681.67), c1=R("6vL", 760, 900, 1480, 1700)),
    dict(n="END 엔딩", f=END_F, key="end"),
]
for i, s in enumerate(SC): s["f1"] = SC[i + 1]["f"] if i + 1 < len(SC) else TOTAL_F
assert all(SC[i]["f"] < SC[i + 1]["f"] for i in range(len(SC) - 1))

# ---------------------------------------------------------------- 자막(가사 v2 화면 표기). 핵심어 노랑
Y = YEL
LINES = [
    dict(on="L2", rows=[[("…",), ("잠깐만!", Y)]]),
    dict(on="L3", rows=[[("마음에 쏙 든 ",), ("사진", Y), (" 한 장,",)], [("노래", Y), (" 한 소절",)]]),
    dict(on="L4", rows=[[("퍼 가기 전에 잠깐 멈춰,",)], [("누가 만든 건지", Y), (" 봐요",)]]),
    dict(on="L5", rows=[[("출처만 쓰면 괜찮다?",)], [("아니죠, ",), ("허락", Y), ("이 먼저",)]]),
    dict(on="L6", rows=[[("무료로 쓰고 싶다면",)], [("공유마당", Y), (" 이용 조건 확인!",)]]),
    dict(on="L7", rows=[[("퍼가요 말고 ",), ("허락부터!", Y)]], add=("L7b", [("(",), ("허락부터!", Y), (")",)])),
    dict(on="L8", rows=[[("쓸 때는 ",), ("출처까지!", Y)]], add=("L8b", [("(",), ("출처까지!", Y), (")",)])),
    dict(on="L9", rows=[[("AI한테 시킬 때도",)], [("똑같이·비슷하게는 ",), ("NO!", Y, "pop")]]),
    dict(on="L10", rows=[[("창작자에게 박수 짝짝,",)], [("K-저작권 매너!", Y)]]),
    dict(on="L11", rows=[[("오늘부터 우리 모두",)], [("저작권 매너인!", Y)]]),
]
CAP_SIZE, CAP_TRACK, CAP_LEAD_K = 68, -0.02, 1.25                  # Jua 68, 자간 -2%, 줄간 1.25
BOX_MAXW, BOX_PAD_Y, BOX_PAD_X, BOX_R, BOX_BOTTOM = 840, 24, 36, 24, 1400
SAFE_RIGHT = W - 140                                               # y960-1520 구간 오른쪽 140px 비움


def flat(runs): return "".join(r[0] for r in runs)


def runs_layout(runs, size):
    out, x = [], 0.0
    for r in runs:
        col = r[1] if len(r) > 1 else None; tag = r[2] if len(r) > 2 else None
        for ch in r[0]:
            fnt = T.gfont(F_TALK, ch, size); a = fnt.getlength(ch)
            out.append((x, a, ch, fnt, col, tag)); x += a + CAP_TRACK * size
    return out, (x - CAP_TRACK * size if out else 0)


def draw_runs(d, xc, yc, runs, size, skip_tag=None, fill=WHITE):
    gl, w = runs_layout(runs, size)
    x0, by = xc - w / 2, yc + T.base_off(F_TALK, size)
    for gx, a, ch, fnt, col, tag in gl:
        if skip_tag and tag == skip_tag: continue
        d.text((x0 + gx, by), ch, font=fnt, fill=col or fill, anchor="ls")
    return [(x0 + gx, a, ch, fnt, col, tag) for gx, a, ch, fnt, col, tag in gl], by


@lru_cache(None)
def cap_layer(li, nrows):
    """자막 박스 RGBA + 박스 위치 + pop 글자 정보"""
    rows = LINES[li]["rows"] + ([LINES[li]["add"][1]] if "add" in LINES[li] else [])
    rows = rows[:nrows]
    size = CAP_SIZE
    while max(runs_layout(r, size)[1] for r in rows) > BOX_MAXW - 2 * BOX_PAD_X: size -= 1
    assert size >= 64, (li, size)
    tw = max(runs_layout(r, size)[1] for r in rows)
    bw, pitch = round(tw + 2 * BOX_PAD_X), size * CAP_LEAD_K
    bh = round(2 * BOX_PAD_Y + size + (len(rows) - 1) * pitch)
    lay = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((0, 0, bw - 1, bh - 1), BOX_R, fill=(*INK, round(255 * 0.92)))
    pops = []
    for i, r in enumerate(rows):
        yc = BOX_PAD_Y + size / 2 + i * pitch
        gl, by = draw_runs(ld, bw / 2, yc, r, size, skip_tag="pop")
        pg = [g for g in gl if g[5] == "pop"]
        if pg: pops.append((pg, by))
    cx = min(W / 2, SAFE_RIGHT - bw / 2)                           # 박스 오른쪽 끝이 x940을 넘지 않게
    return lay, (cx - bw / 2, BOX_BOTTOM - bh), size, pops


CAPS = []                                                          # (시작 프레임, 줄 index, 행 수, 등장 애니 종류)
for li, ln in enumerate(LINES):
    CAPS.append((cap_frame(ON[ln["on"]]), li, len(ln["rows"]), "appear"))
    if "add" in ln: CAPS.append((cap_frame(ON[ln["add"][0]]), li, len(ln["rows"]) + 1, "grow"))
CAPS.sort()
NO_POP_F = hit_frame(ON["NO"])


def draw_caption(im, n):
    cur = [c for c in CAPS if c[0] <= n]
    if not cur or n >= END_F: return
    f0, li, nr, kind = cur[-1]
    lay, (x, y), size, pops = cap_layer(li, nr)
    tau = (n - f0) / FPS
    if kind == "appear": s, ax, ay = 0.9 + 0.1 * ease_out_back(tau / 0.15), 0.5, 0.5
    else: s, ax, ay = 0.95 + 0.05 * ease_out_back(tau / 0.15), 0.5, 1.0
    layer = lay.copy(); im_pop = None
    for pg, by in pops:                                          # NO! — 외침 지점에서 1.0→1.35→1.0 펀치
        k = (n - NO_POP_F) / FPS
        ps = 1 + 0.35 * math.sin(math.pi * k / 0.3) if 0 <= k <= 0.3 else 1.0
        gw = pg[-1][0] + pg[-1][1] - pg[0][0]
        spr = Image.new("RGBA", (int(gw + size), int(size * 2)), (0, 0, 0, 0)); sd = ImageDraw.Draw(spr)
        for gx, a, ch, fnt, col, tag in pg: sd.text((gx - pg[0][0] + size / 2, size * 1.25), ch, font=fnt, fill=col, anchor="ls")
        cxs, cys = size / 2, size * 1.25 - size * 0.35                   # 기준점: NO! 왼쪽 끝·글자 높이 중앙(오른쪽으로 커짐)
        lx, ly = pg[0][0] - size / 2 + cxs, by - size * 1.25 + cys        # 박스 레이어 안 같은 점
        if ps != 1.0: spr = spr.resize((round(spr.width * ps), round(spr.height * ps)), Image.LANCZOS)
        if ps != 1.0:                                              # 커진 글자는 박스 밖으로 나가도 되게 프레임에 직접
            im_pop = (spr, (lx - cxs * ps, ly - cys * ps))
        else:
            layer.alpha_composite(spr, (round(lx - cxs), round(ly - cys)))
    if abs(s - 1) > 1e-3:
        nw, nh = max(1, round(layer.width * s)), max(1, round(layer.height * s))
        sl = layer.resize((nw, nh), Image.LANCZOS)
        px, py = x + layer.width * ax - nw * ax, y + layer.height * ay - nh * ay
        im.alpha_composite(sl, (round(px), round(py)))
    else:
        im.alpha_composite(layer, (round(x), round(y)))
    if im_pop:
        spr, (px, py) = im_pop
        im.alpha_composite(spr, (round(x + px), round(y + py)))


# ---------------------------------------------------------------- 레이아웃 정적 요소
def make_base():
    im = Image.new("RGBA", (W, H), (*BG, 255)); d = ImageDraw.Draw(im)
    pat = Image.new("RGBA", (W, H - BAND[3]), (*BG, 255)); pd = ImageDraw.Draw(pat)   # y1484 아래: 연한 사선 패턴
    for k in range(-H, W + H, 44):
        pd.polygon([(k, 0), (k + 20, 0), (k + 20 - (H - BAND[3]), H - BAND[3]), (k - (H - BAND[3]), H - BAND[3])], fill=(*LINE, 255))
    im.paste(Image.blend(pat.convert("RGB"), Image.new("RGB", pat.size, BG), 0.45), (0, BAND[3]))
    t = "퍼가요 말고 허락부터!"                                       # 제목: Bagel Fat One 88, 흰 외곽선 + 연라인 그림자
    s = T.fit([t], F_TITLE, 88, W - 120)
    T.draw_line(d, W / 2, 184, t, F_TITLE, s, fill=INK, strokes=((9, WHITE),), shadow=(0, 7, LINE, 9))
    d.rectangle((0, WIN_Y0 - 6, W, WIN_Y0), fill=INK)              # 그림 창 위 6px 잉크선(만화 테두리 규격)
    draw_band(d)
    return im


def draw_band(d):
    d.rectangle(BAND, fill=INK)                                    # 필수 표기 띠: 잉크 + 흰 Pretendard Bold 30, 상시
    T.draw_line(d, W / 2, (BAND[1] + BAND[3]) / 2, AI_NOTE, F_B, 30, track=-0.01, fill=WHITE)


BASE = make_base()

# ---------------------------------------------------------------- 첫 1초: '퍼가요~♡' 댓글 말풍선(불투명)
AVA = cs.crop((175, 470, 705, 1000)).resize((112, 112), Image.LANCZOS)


@lru_cache(None)
def comment_card(scale100, heart100, grow100=0):
    sc, gr = scale100 / 100, grow100 / 100
    bw, bh = 620, round(196 + 58 * gr)                             # 0.84s: 둘째 줄 '출처: 인터넷 ㅎ'만큼 아래로 늘어남
    lay = Image.new("RGBA", (bw + 80, 196 + 58 + 120), (0, 0, 0, 0))
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    ox, oy = 40, 30
    sd.rounded_rectangle((ox, oy + 12, ox + bw, oy + bh + 12), 40, fill=(*INK, 110))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(lay)
    tail = [(ox + 120, oy + bh - 6), (ox + 92, oy + bh + 62), (ox + 190, oy + bh - 6)]   # 꼬리: 아래(복붙이 쪽)
    d.polygon(tail, fill=WHITE, outline=INK); d.line(tail, fill=INK, width=7, joint="curve")
    d.rounded_rectangle((ox, oy, ox + bw, oy + bh), 40, fill=WHITE, outline=INK, width=7)
    d.polygon([(ox + 126, oy + bh - 8), (ox + 105, oy + bh + 44), (ox + 182, oy + bh - 8)], fill=WHITE)
    m = Image.new("L", AVA.size, 0); ImageDraw.Draw(m).ellipse((0, 0, AVA.width - 1, AVA.height - 1), fill=255)
    lay.paste(AVA, (ox + 30, oy + 42), m)
    d.ellipse((ox + 28, oy + 40, ox + 30 + AVA.width + 1, oy + 42 + AVA.height + 1), outline=INK, width=5)
    tx = ox + 30 + AVA.width + 26
    d.text((tx, oy + 44), "복붙이", font=T.font(F_B, 30), fill=INK, anchor="ls")
    d.text((tx + T.font(F_B, 30).getlength("복붙이") + 12, oy + 44), "방금", font=T.font(F_SB, 24), fill=(140, 130, 165), anchor="ls")
    body = [("퍼가요~",), ("♡", RED)]
    gl, w = T.layout(body, F_TALK, 92, -0.02)
    by = oy + 150
    for gx, a, ch, fnt, col, hl in gl:
        if ch == "♡" and heart100 != 100:
            hs = heart100 / 100; g = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
            ImageDraw.Draw(g).text((100, 100), ch, font=T.font(F_TALK, round(92 * hs)), fill=col, anchor="mm")
            cx = tx + gx + a / 2; cy = by - 92 * 0.36
            lay.alpha_composite(g, (round(cx - 100), round(cy - 100)))
        else:
            d.text((tx + gx, by), ch, font=fnt, fill=col or INK, anchor="ls")
    if gr > 0.02:                                                  # 둘째 줄: Jua 40
        l2 = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        ImageDraw.Draw(l2).text((tx + 2, by + 56), "출처: 인터넷 ㅎ", font=T.font(F_TALK, 40), fill=(*INK, round(255 * min(1, gr))), anchor="ls")
        lay.alpha_composite(l2)
    if sc != 1: lay = lay.resize((round(lay.width * sc), round(lay.height * sc)), Image.LANCZOS)
    return lay


def draw_comment(im, t):
    k = (t - ON["L1"]) / 0.32                                      # 보컬 '퍼가요'(0.84s)에 맞춰 하트 펄스 + 말풍선 들썩
    bump = math.sin(math.pi * k) if 0 <= k <= 1 else 0.0
    grow = ease_out_back((t - ON["L1"]) / 0.15) if t >= ON["L1"] else 0.0
    sc = 1 + 0.07 * bump
    card = comment_card(round(100 * sc), round(100 + 45 * bump), round(100 * grow))
    cx, top = 560, 282                                             # 카드 위끝 y282 고정(그림 창 안, 얼굴 위), 아래로 늘어남
    im.alpha_composite(card, (round(cx - card.width / 2), round(top - 30 * sc)))


# ---------------------------------------------------------------- H: '퍼가요~♡' 댓글이 그림으로 몰려옴(원화 좌표 고정)
@lru_cache(None)
def mini_chip():
    gl, w = T.layout([("퍼가요~",), ("♡", RED)], F_TALK, 46, -0.02)
    bw, bh = round(w + 56), 74
    lay = Image.new("RGBA", (bw + 30, bh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((12, 18, 12 + bw, 18 + bh), 22, fill=(*INK, 90))
    lay = lay.filter(ImageFilter.GaussianBlur(5)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((12, 10, 12 + bw, 10 + bh), 22, fill=WHITE, outline=INK, width=5)
    by = 10 + bh / 2 + T.base_off(F_TALK, 46)
    for gx, a, ch, fnt, col, hl in gl: d.text((12 + 28 + gx, by), ch, font=fnt, fill=col or INK, anchor="ls")
    return lay


CHIPS = [((300, 860), 0.00, -4), ((470, 1060), 0.40, 3), ((285, 1250), 0.80, -2)]   # (원화 좌표, 컷 후 등장 지연 s, 기울기)

# ---------------------------------------------------------------- K: 효과음 '짝짝!'(Black Han Sans, 빨강 + 흰 11 + 잉크 20, 7°)
@lru_cache(None)
def sfx_sprite(text_spec, angle):
    lay = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    T.sfx(lay, (320, 320), list(text_spec), F_SFX, angle=angle, fill=RED, strokes=((20, INK), (11, WHITE)), track=-0.05)
    return lay


CLAPS = [(hit_frame(ON["CLAP1"]), (("짝", 150, 4, 8),), 7, (190, 450)),
         (hit_frame(ON["CLAP2"]), (("짝", 164, -6, -6), ("!", 164, -4, -12)), 7, (420, 340))]

# ---------------------------------------------------------------- 그림 창
SHAKE = [(12, -8), (-12, 10), (10, -12), (-10, 8), (6, -6), (-4, 4)]   # 6프레임 ±12px


def scene_at(n): return max(i for i, s in enumerate(SC) if s["f"] <= n)


def crop_at(s, n):
    span = max(1, s["f1"] - s["f"])
    k = ease((n - s["f"]) / span)
    r = [s["c0"][i] + (s["c1"][i] - s["c0"][i]) * k for i in range(4)]
    cx, cy, w, h = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2, r[2] - r[0], r[3] - r[1]
    m = 1.0
    if s.get("intro"): m = 1.15 - 0.15 * ease_out(n / FPS / 0.3)    # 첫 0.3초 1.15→1.0 펀치인
    elif n - s["f"] < 4: m = 1.06 - 0.06 * ease_out((n - s["f"]) / 4)   # 하드컷 후 4프레임 1.06→1.0
    w, h = w / m, h / m
    dx = dy = 0
    if s.get("hit") and 0 <= n - s["f"] < len(SHAKE):
        dx, dy = (v * w / WW for v in SHAKE[n - s["f"]])
    box = [cx - w / 2 + dx, cy - h / 2 + dy, cx + w / 2 + dx, cy + h / 2 + dy]
    sf = SAFE[s["key"]]                                            # 셰이크가 안전 영역을 넘지 않게 클램프
    if box[0] < sf[0]: box[2] += sf[0] - box[0]; box[0] = sf[0]
    if box[2] > sf[2]: box[0] -= box[2] - sf[2]; box[2] = sf[2]
    if box[1] < sf[1]: box[3] += sf[1] - box[1]; box[1] = sf[1]
    if box[3] > sf[3]: box[1] -= box[3] - sf[3]; box[3] = sf[3]
    return box


def picture(s, n):
    box = crop_at(s, n)
    pic = art[s["key"]].resize((WW, WH), Image.LANCZOS, box=tuple(box))
    if WW / (box[2] - box[0]) > 1.2:                               # 1.2배 넘게 키운 컷은 선화가 무르지 않게 약한 언샤프
        pic = pic.filter(ImageFilter.UnsharpMask(radius=1.2, percent=45, threshold=3))
    pic = pic.convert("RGBA")
    if s["n"].startswith("H "):
        sc = WW / (box[2] - box[0])
        for (ax, ay), dl, rot in CHIPS:
            k = (n - s["f"]) / FPS - dl
            if k < 0: continue
            chip = mini_chip(); zs = (0.55 + 0.45 * ease_out_back(k / 0.18)) * min(1.25, max(0.9, sc))
            c2 = chip.resize((round(chip.width * zs), round(chip.height * zs)), Image.LANCZOS).rotate(rot, Image.BICUBIC, expand=True)
            px, py = (ax - box[0]) * sc, (ay - box[1]) * sc
            pic.alpha_composite(c2, (round(px - c2.width / 2), round(py - c2.height / 2)))
    if s["n"].startswith("K "):
        for f0, spec, ang, (px, py) in CLAPS:
            if n < f0: continue
            k = (n - f0) / FPS; spr = sfx_sprite(spec, ang)
            zs = 0.6 + 0.4 * ease_out_back(k / 0.16)
            sp = spr.resize((round(spr.width * zs), round(spr.height * zs)), Image.LANCZOS)
            pic.alpha_composite(sp, (round(px - sp.width / 2), round(py - WIN_Y0 - sp.height / 2)))
    if s.get("hit") and 0 <= n - s["f"] < 2:                       # 2프레임 흰 플래시 60%
        pic = Image.blend(pic, Image.new("RGBA", pic.size, (*WHITE, 255)), 0.6)
    return pic


# ---------------------------------------------------------------- 엔딩(노래가 끝난 뒤): 잉크 배경 + 6컷 그린카드 + 슬로건 + AI 창작 매너 3
MANNERS = [["남의 작품을 똑같이·비슷하게", "따라 하게 시키지 않기"], ["쓸 땐 이용 허락·조건 먼저"], ["AI 활용 사실 밝히기"]]
END_ART_BOX = (575, 468, 2284, 1750)                               # _P6_v1 4:3: 웃는 복붙이(그림)·요정 그린카드·꽃가루, 테두리 밖
END_IMG = (160, 382, 920, 952)                                     # 760x570, 아래끝 y952(오른쪽 140px 규칙 시작선 y960 위)
END_ECHO_T = CHORUS_AT + (ON["L7b"] - CHORUS[0]) - END_F / FPS    # 엔딩 후렴 안 '(허락부터!)'(타임라인 41.68s) → 주제목 들썩


def make_end_layers():
    bg = Image.new("RGBA", (W, H), (*INK, 255)); d = ImageDraw.Draw(bg)
    pat = Image.new("RGB", (W, H - BAND[3]), INK); pd = ImageDraw.Draw(pat)
    for k in range(-H, W + H, 44):
        pd.polygon([(k, 0), (k + 20, 0), (k + 20 - (H - BAND[3]), H - BAND[3]), (k - (H - BAND[3]), H - BAND[3])], fill=(50, 43, 73))
    bg.paste(pat, (0, BAND[3]))
    draw_band(d)
    d.line((0, BAND[1], W, BAND[1]), fill=(70, 62, 98), width=2)
    layers = []
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)  # 0: 'K-저작권 매너송' 40 노랑
    T.draw_line(ld, W / 2, 168, "K-저작권 매너송", F_NARR, 40, fill=YEL)
    layers.append((L, 0.00, (W / 2, 168)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)  # 1: 주제목 '퍼가요 말고 허락부터!' Bagel 84 흰(후렴 가사와 같은 말)
    T.draw_line(ld, W / 2, 250, "퍼가요 말고 허락부터!", F_TITLE, 84, fill=WHITE)
    layers.append((L, 0.00, (W / 2, 250)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)  # 2: 부제 '허락부터, 출처까지' Do Hyeon 44 노랑
    T.draw_line(ld, W / 2, 330, "허락부터, 출처까지", F_NARR, 44, fill=YEL)
    layers.append((L, 0.02, (W / 2, 330)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)  # 3: 6컷 그린카드 장면(_P6_v1)
    x0, y0, x1, y1 = END_IMG
    img = art["6vL"].resize((x1 - x0, y1 - y0), Image.LANCZOS, box=END_ART_BOX).convert("RGBA")
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), 26, fill=255)
    L.paste(img, (x0, y0), m)
    ld.rounded_rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), 28, outline=BG, width=6)
    layers.append((L, 0.03, ((x0 + x1) / 2, (y0 + y1) / 2)))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)  # 4: 'AI 창작 매너 3' 흰 Do Hyeon + 번호 원
    hy = 1022
    T.draw_line(ld, W / 2, hy, "AI 창작 매너 3", F_NARR, 58, fill=WHITE)
    ld.line((150, hy + 46, 930, hy + 46), fill=(80, 72, 110), width=2)
    y = hy + 108
    for i, rows in enumerate(MANNERS):
        cx = 178
        ld.ellipse((cx - 28, y - 28, cx + 28, y + 28), fill=YEL)
        T.draw_line(ld, cx, y + 1, str(i + 1), F_NARR, 40, fill=INK)
        for j, r in enumerate(rows):
            w = T.line_w(r, F_NARR, 46)
            T.draw_line(ld, 230 + w / 2, y + j * 56, r, F_NARR, 46, fill=WHITE)
        y += 56 * len(rows) + 30
    layers.append((L, 0.06, (W / 2, 1200)))
    return bg, layers


END_BG, END_LAYERS = make_end_layers()


def ending(n):
    t = (n - END_F + 1) / FPS                                      # 첫 프레임부터 요소가 보이게(빈 프레임 없음)
    im = END_BG.copy()
    for L, dl, (ax, ay) in END_LAYERS:
        k = (t - dl) / 0.18
        if k <= 0: continue
        s = 0.92 + 0.08 * ease_out_back(k)
        if L is END_LAYERS[1][0]:                                  # 후렴 '(허락부터!)'에 맞춰 주제목 1.0→1.06→1.0
            kb = (t - END_ECHO_T) / 0.3
            if 0 <= kb <= 1: s *= 1 + 0.06 * math.sin(math.pi * kb)
        if abs(s - 1) > 1e-3:
            bb = L.getbbox(); part = L.crop(bb)
            nw, nh = round(part.width * s), round(part.height * s)
            part = part.resize((nw, nh), Image.LANCZOS)
            cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
            im.alpha_composite(part, (round(cx - nw / 2), round(cy - nh / 2)))
        else:
            im.alpha_composite(L)
    return im


# ---------------------------------------------------------------- 하단 빈 띠 'AI 창작 매너 3' 진행 표시(y1520~1640, x60~940)
# 만화 하단 띠와 같은 잉크 칩 + 번호 원 + Do Hyeon 40. ③은 처음부터, ②는 '출처만…허락이 먼저'(11.03s), ①은 'AI한테…NO'(25.27s)에 노랑으로 켜짐
STRIP = (60, 1520, 940, 1640)
MANNER_CHIPS = [(1, "똑같이·비슷하게 NO", cap_frame(ON["L9"])), (2, "허락·조건 먼저", cap_frame(ON["L5"])), (3, "AI 활용 사실 밝히기", 0)]
CHIP_H, CHIP_FS = 56, 40


@lru_cache(None)
def manner_chip(num, label, lit):
    tw = T.line_w(label, F_NARR, CHIP_FS); w = round(7 + 44 + 10 + tw + 22)
    lay = Image.new("RGBA", (w, CHIP_H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w - 1, CHIP_H - 1), CHIP_H // 2, fill=INK)
    cy = CHIP_H / 2; cx = 7 + 22
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=YEL if lit else (72, 64, 100))
    T.draw_line(d, cx, cy + 1, str(num), F_NARR, 32, fill=INK if lit else (150, 140, 180))
    T.draw_line(d, 7 + 44 + 10 + tw / 2, cy, label, F_NARR, CHIP_FS, fill=WHITE if lit else (150, 140, 180))
    return lay


@lru_cache(None)
def manner_label():
    runs = [("AI 창작 매너 ",), ("3", YEL)]; tw = T.line_w(runs, F_NARR, CHIP_FS); w = round(tw + 44)
    lay = Image.new("RGBA", (w, CHIP_H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w - 1, CHIP_H - 1), CHIP_H // 2, fill=PURPLE)
    T.draw_line(d, w / 2, CHIP_H / 2, runs, F_NARR, CHIP_FS, fill=WHITE)
    return lay


def draw_manners(im, n):
    on = {num: n >= f0 for num, _, f0 in MANNER_CHIPS}
    sprites = {num: manner_chip(num, lab, on[num]) for num, lab, _ in MANNER_CHIPS}
    rows = [[manner_label(), sprites[1]], [sprites[2], sprites[3]]]
    nums = [[None, 1], [2, 3]]
    for r, (row, nr) in enumerate(zip(rows, nums)):
        tw = sum(sp.width for sp in row) + 10 * (len(row) - 1)
        x = W / 2 - tw / 2; y = STRIP[1] + r * (CHIP_H + 8)
        assert STRIP[0] <= x and x + tw <= STRIP[2]
        for sp, num in zip(row, nr):
            sc = 1.0
            if num:
                f0 = dict((a, c) for a, _, c in MANNER_CHIPS)[num]
                k = (n - f0) / FPS / 0.3
                if f0 > 0 and 0 <= k <= 1: sc = 1 + 0.12 * math.sin(math.pi * k)   # 켜질 때 1.0→1.12→1.0
            if sc != 1.0:
                s2 = sp.resize((round(sp.width * sc), round(sp.height * sc)), Image.LANCZOS)
                im.alpha_composite(s2, (round(x + sp.width / 2 - s2.width / 2), round(y + CHIP_H / 2 - s2.height / 2)))
            else:
                im.alpha_composite(sp, (round(x), round(y)))
            x += sp.width + 10


# ---------------------------------------------------------------- 프레임
def frame(n):
    s = SC[scene_at(n)]
    if s["key"] == "end": return ending(n).convert("RGB")
    im = BASE.copy()
    im.alpha_composite(picture(s, n), (0, WIN_Y0))
    if s.get("intro"): draw_comment(im, n / FPS)
    draw_manners(im, n)
    draw_caption(im, n)
    return im.convert("RGB")


def audio_filter():
    e = round(SONG_TRIM * SR); c0, c1 = round(CHORUS[0] * SR), round(CHORUS[1] * SR); xf = round(XFADE * SR)
    assert e + (c1 - c0) - xf == round(TOTAL * SR) and (e - xf) == round(CHORUS_AT * SR)
    clen = (c1 - c0) / SR
    return (f"[1:a]asplit=2[x0][x1];"
            f"[x0]atrim=end_sample={e},asetpts=PTS-STARTPTS[s0];"
            f"[x1]atrim=start_sample={c0}:end_sample={c1},asetpts=PTS-STARTPTS,"
            f"afade=t=out:st={round(clen - LOOP_FADE, 3)}:d={LOOP_FADE}[s1];"
            f"[s0][s1]acrossfade=ns={xf}:c1=tri:c2=tri,volume={VOLUME_DB}dB[aout]")


ART_NAME = {1: "P1", 2: "P2", "2c": "P2(효과음 덮기 전 원본)", 3: "P3", 4: "P4", 5: "P5", 6: "P6", "6v": "_P6_v1(노트북 마크 제거)", "6vL": "_P6_v1(노트북 마크 제거 + 스케치북 라벨 '그림: 복붙이')"}


def params():
    lines = [dict(line=flat(LINES[i]["rows"][0]) + (" / " + flat(LINES[i]["rows"][1]) if len(LINES[i]["rows"]) > 1 else ""),
                  onset_s=ON[LINES[i]["on"]], caption_on_s=round(cap_frame(ON[LINES[i]["on"]]) / FPS, 3),
                  lead_s=round(ON[LINES[i]["on"]] - cap_frame(ON[LINES[i]["on"]]) / FPS, 3)) for i in range(len(LINES))]
    return {
        "script": "make_short_v2.py", "style_guide": "스타일가이드.md v2 (2026-10-07 승인)",
        "output": OUT, "video": {"width": W, "height": H, "fps": FPS, "codec": "H.264 (libx264, crf 18, yuv420p)",
                                 "duration_s": round(TOTAL, 3), "frames": TOTAL_F},
        "audio": {"source": AUDIO, "source_duration_s": AUDIO_DUR, "codec": "AAC 48 kHz stereo 256 kbps",
                  "volume_db": VOLUME_DB,
                  "song_trim_s": SONG_TRIM, "crossfade_s": XFADE, "crossfade_timeline_s": [CHORUS_AT, SONG_TRIM],
                  "crossfade_curve": "tri(선형)", "song_fade_out": "없음(크로스페이드로 연결)",
                  "loop_end_fade_s": LOOP_FADE, "loop_end_fade_timeline_s": [round(TOTAL - LOOP_FADE, 3), TOTAL],
                  "ending_card_start_s": round(END_F / FPS, 3), "ending_card_length_s": ENDING_LEN,
                  "ending_audio_source_s": list(CHORUS), "ending_audio_timeline_s": [CHORUS_AT, TOTAL],
                  "segments": [
                      dict(use="본곡", source_range_s=[0.0, SONG_TRIM], timeline_s=[0.0, SONG_TRIM],
                           end=f"{CHORUS_AT}~{SONG_TRIM}s 25ms 크로스페이드로 엔딩 음원과 겹침(본곡 페이드아웃 없음)"),
                      dict(use="엔딩 배경음: 원곡 후렴 구간 반복 사용", lyric="퍼가요 말고 허락부터! (허락부터!)",
                           source_range_s=list(CHORUS), timeline_s=[CHORUS_AT, TOTAL],
                           start="크로스페이드 25ms(페이드인 없음)", end="마지막 30ms 페이드 후 영상 처음으로 루프")],
                  "ending_audio": f"원곡 T2.wav {CHORUS[0]}~{CHORUS[1]}s 후렴('퍼가요 말고 허락부터! (허락부터!)')을 타임라인 {CHORUS_AT}~{TOTAL}s에 한 번 더 사용. "
                                  "새 음원·효과음 추가 없음",
                  "filter": audio_filter()},
        "manner_progress": {"area_px": list(STRIP), "font": "Do Hyeon 40", "style": "잉크 칩 + 번호 원(켜짐: 노랑) + 보라 라벨 'AI 창작 매너 3'",
                            "items": [dict(n=num, label=lab, lit_from_s=round(f0 / FPS, 3)) for num, lab, f0 in MANNER_CHIPS],
                            "note": "진행 칩은 쇼츠 하단 UI 영역(y>1520)에 걸리지만 감독 결정으로 유지함: 심사는 파일로 보고, 엔딩 카드에 같은 정보(전체 문구 목록)가 있음. "
                                    "엔딩 카드에서는 칩 대신 전체 문구 목록을 보여 줌"},
        "ai_notice": {"text": AI_NOTE, "method": "화면 하단 상시 띠 — (0,1436)-(1080,1484) 잉크(#28223C) 바탕 + 흰 Pretendard Bold 30, "
                      "0초부터 영상 끝까지 전 프레임(엔딩 포함). 쇼츠 하단 UI(y>1520) 밖, 오른쪽 버튼열과 겹치지 않음",
                      "position_px": list(BAND), "font": "Pretendard Bold 30", "always_visible": True},
        "lyric_sync": {"caption_lead_rule_s": [CAP_LEAD[0], CAP_LEAD[1]], "lines": lines,
                       "line1_note": "1줄 '퍼가요~♡'는 0.00s부터 댓글 말풍선으로 표시(가이드 2장), 보컬 0.84s에 하트 펄스",
                       "echo_rows": [dict(row="(허락부터!)", onset_s=ON["L7b"], caption_on_s=round(cap_frame(ON["L7b"]) / FPS, 3)),
                                     dict(row="(출처까지!)", onset_s=ON["L8b"], caption_on_s=round(cap_frame(ON["L8b"]) / FPS, 3))],
                       "no_accent": dict(onset_s=ON["NO"], pop_s=round(hit_frame(ON["NO"]) / FPS, 3)),
                       "vocal_end_s": ON["VOC_END"]},
        "hits": {"whistle_flash_shake_s": round(SC[1]["f"] / FPS, 3), "no_flash_shake_s": round(hit_frame(ON["NO"]) / FPS, 3),
                 "flash": "2프레임 흰 60%", "shake": "6프레임 ±12px"},
        "scenes": [dict(name=s["n"], start_s=round(s["f"] / FPS, 3), end_s=round(s["f1"] / FPS, 3),
                        art=ART_NAME[s["key"]] if s["key"] != "end" else "_P6_v1(엔딩 썸네일)",
                        crop_from=[round(v) for v in s["c0"]] if "c0" in s else list(END_ART_BOX),
                        crop_to=[round(v) for v in s["c1"]] if "c1" in s else list(END_ART_BOX)) for s in SC],
        "fonts": "Bagel Fat One / Do Hyeon / Jua / Black Han Sans / Pretendard (SIL OFL 1.1, fonts/)",
    }


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True); os.makedirs(f"{OUT_DIR}/qa", exist_ok=True)
    if "--still" in sys.argv:
        for t in [float(x) for x in sys.argv[sys.argv.index("--still") + 1:]]:
            frame(int(round(t * FPS))).save(f"{OUT_DIR}/qa/s_{t:05.2f}.png")
        sys.exit()
    if "--sheet" in sys.argv:
        th = []
        for s in SC:
            for n in (s["f"] + 5, s["f1"] - 1):
                im = frame(min(n, TOTAL_F - 1)).resize((270, 480), Image.LANCZOS); dd = ImageDraw.Draw(im)
                dd.rectangle((0, 0, 270, 22), fill=INK); dd.text((4, 2), f"{s['n'][:16]} {n / FPS:.2f}", font=T.font(F_SB, 15), fill=WHITE)
                th.append(im)
        cols = 10; rows = math.ceil(len(th) / cols)
        sheet = Image.new("RGB", (cols * 274, rows * 484), (90, 90, 90))
        for i, im in enumerate(th): sheet.paste(im, ((i % cols) * 274, (i // cols) * 484))
        sheet.save(f"{OUT_DIR}/qa/sheet.png"); sys.exit()
    tmp = f"{OUT_DIR}/_video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-i", AUDIO, "-filter_complex", audio_filter(), "-map", "0:v", "-map", "[aout]",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
                            "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
                            "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for n in range(TOTAL_F):
        enc.stdin.write(frame(n).tobytes())
        if n % 150 == 0: print(f"{n}/{TOTAL_F}", flush=True)
    enc.stdin.close(); enc.wait()
    pr = params()
    log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, encoding="utf-8", errors="replace").stderr.split("Summary:")[-1]
    num = lambda key: float(log.split(key)[1].split()[0])
    pr["audio"]["measured_integrated_lufs"] = num("I:")             # 출력 파일 실측(EBU R128)
    pr["audio"]["measured_true_peak_dbtp"] = num("Peak:")
    pr["audio"]["measured_lra_lu"] = num("LRA:")
    json.dump(pr, open(f"{OUT_DIR}/render_params.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("done", round(TOTAL, 3))
