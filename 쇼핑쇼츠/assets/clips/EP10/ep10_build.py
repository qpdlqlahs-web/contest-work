"""EP10 사전 합성 (무료, 크레딧 0). 크루 정지 레이어 합성 + 패치 + 보정 클립 생성.
출력은 모두 이 폴더의 *.mp4 / *.png (1080x1920, 30fps). make_cctv.py가 일반 video/image 컷으로 읽는다.
사용: python ep10_build.py t1 s2 s3 c3 c4 t2 s1   (필요한 단계만 골라 실행)
합성 기준표(review.md 「오려 붙인 티를 없애는 합성 기준」)를 place()/Sprite에 구현:
 크기(슬리퍼 0.7배 이하) / 방사 기울임 1~3도 / 축소 후 블러 0.8px / 밝기 상한·하한·평균 ±15 / 창 쪽(위) 림 +12 /
 접지 그림자(타원 42%, 블러, 폭=발 간격 1.3배) + 접촉 그림자 + 기포 눌림 / 마스크 1px 침식+1px 페더 / 전체 프레임 그레인+JPEG q75."""
import sys, os, subprocess, math
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
FPS = 30
CREW_H = 150         # v2: 반장 키(px, 1080폭 기준). 슬리퍼(길이 약 125px)의 1.2배(PD 결정, EP10 한정)
CLUMP_W = 70         # v2: 뭉치 폭 70px
SPR_SCALE = CREW_H / 303.0
GRAIN = 4.5


def P(n): return os.path.join(HERE, n)


# ------------------------------------------------------------------ 입출력
def read_video(path, start, dur):
    """1080x1920 L(gray) float32 프레임, 30fps"""
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path, "-vf",
           f"scale={W}:{H}:flags=lanczos,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    r = subprocess.run(cmd, capture_output=True)
    n = len(r.stdout) // (W * H)
    a = np.frombuffer(r.stdout[: n * W * H], np.uint8).reshape(n, H, W)
    return [f.astype(np.float32) for f in a]


def load_L(path, size=(W, H)):
    im = Image.open(path).convert("L")
    if im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im, np.float32)


class Writer:
    def __init__(self, path, fps=FPS):
        self.p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(fps),
                                   "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path],
                                  stdin=subprocess.PIPE)
        self.n = 0

    def write(self, L, seed=0, grain=True):
        if grain:
            L = finalize(L, seed)
        self.p.stdin.write(np.clip(L, 0, 255).astype(np.uint8).tobytes())
        self.n += 1

    def close(self):
        self.p.stdin.close(); self.p.wait()
        print("  frames", self.n)


def finalize(L, seed):
    """합성 후 전체 프레임 공통 처리: 매 프레임 새 그레인 + JPEG q75 재압축(블록 질감 통일)"""
    rng = np.random.default_rng(5000 + seed)
    g = L + rng.normal(0, GRAIN, L.shape).astype(np.float32)
    g = np.clip(g, 0, 255).astype(np.uint8)
    ok, buf = cv2.imencode(".jpg", g, [cv2.IMWRITE_JPEG_QUALITY, 75])
    return cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE).astype(np.float32)


def blur(a, s):
    return cv2.GaussianBlur(a, (0, 0), s) if s > 0 else a


def feather_box(shape, box, f):
    """box 안쪽 1, 가장자리 페더 f px 알파"""
    m = np.zeros(shape, np.float32)
    x0, y0, x1, y1 = box
    m[y0:y1, x0:x1] = 1
    return np.clip(blur(m, f / 2.2), 0, 1)


def ring_offset(a, b, box, pad=24):
    """box 바깥 고리에서 a-b 평균 차 (a를 b 밝기에 맞출 때 쓴다)"""
    x0, y0, x1, y1 = box
    m = np.zeros(a.shape, bool)
    m[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad] = True
    m[y0:y1, x0:x1] = False
    return float((a[m] - b[m]).mean())


def patch_from(dst, src, box, f=20, match=True):
    """dst의 box 영역을 src 픽셀로 교체(같은 좌표, 페더 f). 고리 평균 휘도를 dst에 맞춘다."""
    s = src + (ring_offset(dst, src, box) if match else 0)
    m = feather_box(dst.shape, box, f)
    return dst * (1 - m) + s * m


def glitch(L, rng):
    """프레임 드롭 글리치(make_cctv.frame_drop과 같은 문법): 가로로 밀린 줄 + 밝은 가로선"""
    out = L.copy()
    for _ in range(3):
        y = int(rng.integers(300, H - 300)); h = int(rng.integers(14, 60)); dx = int(rng.integers(-55, 55))
        out[y:y + h] = np.roll(out[y:y + h], dx, axis=1)
    for _ in range(3):
        y = int(rng.integers(300, H - 300)); h2 = int(rng.integers(3, 12))
        out[y:y + h2] = np.clip(out[y:y + h2] + 90, 0, 255)
    return out


def shift(L, dx, dy):
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(L, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


# ------------------------------------------------------------------ 크루 정지 레이어
CAPS = {"boss": 220.0, "yeosa": 195.0, "kong": 195.0, "clump": 175.0}   # 상단(창 225보다 어둡게). 반장 안전모·반사띠가 가장 밝다


class Sprite:
    """준비(축소·블러·톤·림·그림자 마스크)를 한 번 하고, 프레임마다 위치(dy, dx)만 바꿔 붙인다.
    v2: 어두운 불투명 실루엣(기포 평균 -40, 단 띠 아래 카펫 -25보다 낮게), 위쪽 림 +40 2px, 반장 안전모·반사띠 +50, 접지 그림자 60%."""

    def __init__(self, name, foot, bgL, height=None, scale=None, rot=None, shadow=True, strip=True):
        self.name, self.foot, self.shadow = name, foot, shadow
        spr = Image.open(P(f"crew/{name}.png"))
        s = scale if scale is not None else (CREW_H / 303.0 if height is None else height / spr.height)
        fx, fy = foot
        ang = rot if rot is not None else float(np.sign(540 - fx) * np.clip(abs(540 - fx) / 540 * 3.0, 1.0, 3.0))
        L = spr.convert("RGBA")
        a = np.asarray(L.split()[3], np.float32) / 255.0
        g = np.asarray(L.split()[0], np.float32)
        inner = a > 0.9
        fill = g[inner].mean() if inner.any() else 128.0
        g = np.where(a > 0.5, g, fill)
        gi = Image.fromarray(g.astype(np.uint8)); ai = Image.fromarray((a * 255).astype(np.uint8))
        gi = gi.rotate(ang, resample=Image.BICUBIC, expand=True, fillcolor=int(fill))
        ai = ai.rotate(ang, resample=Image.BICUBIC, expand=True, fillcolor=0)
        nw, nh = max(2, int(round(gi.width * s))), max(2, int(round(gi.height * s)))
        g = np.asarray(gi.resize((nw, nh), Image.LANCZOS), np.float32)
        a = np.asarray(ai.resize((nw, nh), Image.LANCZOS), np.float32) / 255.0
        g_orig = g.copy()
        g, a = blur(g, 0.8), blur(a, 0.8)
        a = cv2.erode(a, np.ones((3, 3), np.uint8))
        a = np.clip(blur(a, 0.7), 0, 1)
        a = np.clip((a - 0.12) / 0.7, 0, 1)                   # 완전 불투명(가장자리 1px 페더만)
        ys, xs = np.where(a > 0.5)
        self.x0 = int(round(fx - (xs.min() + xs.max()) / 2)); self.y0 = int(round(fy - ys.max()))
        # --- 톤(v2): 그 자리 기포(배경) 평균보다 40 어둡게. 띠 아래 카펫이 더 밝으면 카펫-25 이하로
        bx0, bx1 = max(0, self.x0 + xs.min()), min(W, self.x0 + xs.max() + 1)
        by0, by1 = max(0, self.y0 + ys.min()), min(H, self.y0 + ys.max() + 1)
        bg_mean = float(bgL[by0:by1, bx0:bx1].mean())
        carpet = float(bgL[min(H - 6, fy + 22):min(H, fy + 92), max(0, fx - 100):min(W, fx + 100)].mean())
        body = float(np.clip(min(bg_mean - 40, carpet - 25), 25, 200))
        w = a > 0.5
        m_s = float(g[w].mean())
        gg = body + (g - m_s) * 0.45                          # 내부 디테일은 절반 이하로 눌러 '실루엣' 유지
        gg = np.clip(gg, max(8, body - 30), body + 30)
        if name == "boss":                                    # 안전모·반사띠: 국소 +50 (화면 최밝점, 창 225 미만)
            p80, p97 = np.percentile(g_orig[w], 80), np.percentile(g_orig[w], 97)
            hi = np.clip((blur(g_orig, 0.8) - p80) / max(p97 - p80, 1), 0, 1)
            gg = gg + 50 * hi
        up = np.zeros_like(a); up[2:] = a[:-2]
        rim = np.clip(a - up, 0, 1)                           # 창 쪽(위) 윤곽 2px +40
        gg = np.clip(gg + 40 * rim, 0, 222)
        self.g, self.a, self.bg_mean, self.body = gg, a, bg_mean, body
        hh, ww = a.shape
        low = (a > 0.5); low[: int(hh * 0.90)] = False
        n, lab, st, cen = cv2.connectedComponentsWithStats(low.astype(np.uint8))
        feet = [(cen[i][0], cen[i][1], st[i][2]) for i in range(1, n) if st[i][4] >= 2]
        if not feet:
            feet = [(ww / 2, hh - 2, ww * 0.4)]
        self.feet = [(fx_ + self.x0, fy_ + self.y0, fw_) for fx_, fy_, fw_ in feet]
        self.height, self.width = hh, ww
        self.strip = strip

    def shadow_mask(self, k=1.0):
        m = np.zeros((H, W), np.float32)
        fs = self.feet
        cx = float(np.mean([f[0] for f in fs])); cy = max(f[1] for f in fs)
        spacing = (max(f[0] for f in fs) - min(f[0] for f in fs)) if len(fs) > 1 else 0
        wd = max(spacing * 1.3 + np.mean([f[2] for f in fs]), 0.34 * self.height)
        ry = max(3.0, 0.045 * self.height)
        cv2.ellipse(m, (int(cx), int(cy + 0.03 * self.height)), (int(wd / 2), int(ry)), 0, 0, 360, 1.0, -1)
        m = blur(m, 3.2) * 0.60 * k                           # v2: 60%
        c = np.zeros((H, W), np.float32)
        for fx_, fy_, fw_ in fs:
            cv2.ellipse(c, (int(fx_), int(fy_ + 1)), (int(max(2, fw_ * 0.6)), 2), 0, 0, 360, 1.0, -1)
        c = blur(c, 1.0) * 0.8 * k
        return np.clip(m + c, 0, 0.85)

    def paste_shadow(self, L, k=1.0):
        if not self.shadow or k <= 0:
            return L
        return L * (1 - self.shadow_mask(k))

    def paste(self, L, dy=0, occl=None, dx=0):
        hh, ww = self.a.shape
        x0, y0 = self.x0 + int(dx), int(self.y0 + round(dy))
        ya, yb = max(0, y0), min(H, y0 + hh); xa, xb = max(0, x0), min(W, x0 + ww)
        if ya >= yb or xa >= xb:
            return L
        a = self.a[ya - y0:yb - y0, xa - x0:xb - x0]
        if occl is not None:
            a = a * (1 - occl[ya:yb, xa:xb])
        L[ya:yb, xa:xb] = L[ya:yb, xa:xb] * (1 - a) + self.g[ya - y0:yb - y0, xa - x0:xb - x0] * a
        return L


def stage_set(L, sprites, lifts=None, occl=None, amp=0.0):
    """sprites: [(Sprite, dy)] -> 그림자 먼저, 그다음 스프라이트. 떠 있을수록 그림자 옅음"""
    out = L.copy()
    for it in sprites:
        sp, dy = it[0], it[1]
        k = 1.0 - 0.45 * min(1.0, max(0.0, -dy / max(amp, 1.0))) if amp else 1.0
        out = sp.paste_shadow(out, k)
    for it in sprites:
        out = it[0].paste(out, it[1], occl, it[2] if len(it) > 2 else 0)
    return out


def sparkle(L, x, y, r=5, arm=16):
    """발 닿는 순간 기포 눌림 하이라이트(작은 흰 반짝, 십자+점)"""
    g = np.zeros((H, W), np.float32)
    cv2.circle(g, (int(x), int(y)), r, 1.0, -1)
    cv2.line(g, (int(x - arm), int(y)), (int(x + arm), int(y)), 0.9, 2)
    cv2.line(g, (int(x), int(y - arm)), (int(x), int(y + arm)), 0.9, 2)
    g = np.clip(blur(g, 1.3) * 1.6, 0, 1)
    return np.maximum(L, 250.0 * g)


# ------------------------------------------------------------------ 단계
def st_t1():
    """T1 훅: apply_c1_fix 적용 -> 0.7배속 2.4초(T1_hook) + PPL 배경 루프 6.0초(T1_ppl)"""
    cut = P("_T1_cut.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", P("T1.mp4"), "-t", "1.7", "-an", "-c:v", "libx264", "-crf", "12", cut], check=True)
    if not os.path.exists(P("T1_fix.mp4")):
        subprocess.run([sys.executable, P("apply_c1_fix.py"), cut, P("T1_fix.mp4")], check=True)
    fr = read_video(P("T1_fix.mp4"), 0, 1.7)            # 1.7초(41~51프레임) -> 30fps
    print("T1_fix frames", len(fr))
    # 훅: 0.7배속 = 1.7초 -> 2.43초, 앞 2.4초 사용 (시간 늘이기: 인접 프레임 블렌드)
    n_out = int(2.4 * FPS)
    w = Writer(P("T1_hook.mp4"))
    for i in range(n_out):
        s = i * 0.7                      # 원본 프레임 위치(30fps 기준)
        a = int(math.floor(s)); b = min(a + 1, len(fr) - 1); t = s - a
        w.write(fr[min(a, len(fr) - 1)] * (1 - t) + fr[b] * t, i, grain=False)
    w.close()
    # PPL 배경: 1.7초 루프 x 3.5, 저채도라 회색조 그대로, 어둡게는 make_cctv dim이 처리
    w = Writer(P("T1_ppl.mp4"))
    for i in range(6 * FPS + 6):
        w.write(fr[i % len(fr)], i, grain=False)
    w.close()


def crew_set(bgL, pts, **kw):
    return {n: Sprite(n, p, bgL, **kw.get(n, {})) for n, p in pts.items()}


def clump_sprite(foot, bgL):
    return Sprite("clump", foot, bgL, scale=CLUMP_W / 190.0, shadow=True)


def st_s2():
    """#2 작전 ① C3_plate + 크루 3 + 뭉치. v2: 띠 아래 가장자리~카펫 경계, 키 150px, 어두운 실루엣, 높이차 24px 이상. 0.3초 2프레임 흔들림. 2.0초"""
    plate = load_L(P("C3_plate.png"))
    sp = crew_set(plate, {"boss": (232, 1226), "yeosa": (352, 1252), "kong": (478, 1277)})
    sp["clump"] = clump_sprite((640, 1236), plate)
    base = stage_set(plate, [(sp["clump"], 0), (sp["boss"], 0), (sp["yeosa"], 0), (sp["kong"], 0)])
    Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).save(P("_S2_still.png"))
    w = Writer(P("S2_comp.mp4"))
    shakes = {9: (5, -3), 10: (-4, 2)}
    for i in range(int(2.0 * FPS)):
        f = shift(base, *shakes[i]) if i in shakes else base
        w.write(f, i)
    w.close()


def st_s3():
    """#3 작전 ② C2_start_v5 3장 교차. v2: 여사를 분무기 방아쇠에 매달고(0~1.0초 1px 떨림 동행), 뭉치 x1.25"""
    c2 = np.asarray(Image.open(P("C2_start_v5.png")).convert("L"), np.float32)
    pl = np.asarray(Image.open(P("C3_plate.png")).convert("L"), np.float32)
    mist = (640, 1120, 920, 1240)
    a = patch_from(c2, pl, mist, f=28)
    cx0, cy0, cx1, cy1 = (325, 1440, 435, 1535)
    m = np.zeros(c2.shape, np.float32)
    cv2.ellipse(m, (380, 1486), (46, 34), 0, 0, 360, 1.0, -1)
    m = blur(m, 5)
    cl_g = c2[cy0 - 20:cy1 + 20, cx0 - 20:cx1 + 20].copy()
    cl_a = m[cy0 - 20:cy1 + 20, cx0 - 20:cx1 + 20].copy()
    a_er = patch_from(a, pl, (cx0 - 10, cy0 - 10, cx1 + 10, cy1 + 10), f=14)

    def put_clump(base, deg, dy):
        h, w_ = cl_g.shape
        M = cv2.getRotationMatrix2D((w_ / 2, h / 2), deg, 1.25)       # v2: 뭉치 x1.25
        sy = 1 - 0.15 * min(1.0, deg / 90.0)
        M[1] *= sy
        M[1, 2] += h / 2 * (1 - sy)
        g = cv2.warpAffine(cl_g, M, (w_, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        al = cv2.warpAffine(cl_a, M, (w_, h), flags=cv2.INTER_LINEAR)
        g = g * (1 - 0.10 * min(1.0, deg / 90.0))
        out = base.copy()
        ox, oy = cx0 - 20, cy0 - 20 + int(dy)
        out[oy:oy + h, ox:ox + w_] = out[oy:oy + h, ox:ox + w_] * (1 - al) + g * al
        return out

    bx = (480, 1140, 680, 1540)
    c_a_jit = []
    for dx in (0, 1):
        t = a.copy()
        reg = a[bx[1]:bx[3], bx[0]:bx[2]]
        t[bx[1]:bx[3], bx[0] + dx:bx[2] + dx] = reg
        c_a_jit.append(t)
    c_c45 = put_clump(a_er, 45, 20)
    c_c90 = put_clump(a_er, 90, 40)

    def to1080(x):
        return cv2.resize(x, (W, H), interpolation=cv2.INTER_AREA)

    imgs = [to1080(x) for x in (c_a_jit[0], c_a_jit[1], c2, c_c45, c_c90)]
    for n_, im in zip(("a0", "a1", "b", "c45", "c90"), imgs):
        Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).save(P("_S3_%s.png" % n_))
    ys = Sprite("yeosa", (470, 1012), imgs[0], shadow=False)        # 방아쇠(약 469,904)에 매달림
    w = Writer(P("S3_comp.mp4"))
    shakes = {30: (6, -4), 31: (-5, 3)}
    for i in range(int(2.5 * FPS)):
        t = i / FPS
        jit = (i // 2) % 2 if t < 1.0 else 0
        if t < 1.0:
            f = imgs[jit]
        elif t < 1.5:
            f = imgs[2]
        elif t < 1.7:
            f = imgs[3]
        else:
            f = imgs[4]
        f = stage_set(f, [(ys, 0, jit)])
        if i in shakes:
            f = shift(f, *shakes[i])
        w.write(f, i)
    w.close()


def c3_object_mask(frame, plate, box):
    off = ring_offset(frame, plate, box)
    d = (plate + off) - frame
    x0, y0, x1, y1 = box
    m = np.zeros_like(d)
    m[y0:y1, x0:x1] = d[y0:y1, x0:x1]
    m = blur(m, 1.5)
    a = np.clip((m - 52) / 26, 0, 1)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    a = cv2.erode(cv2.dilate(a, k), k)
    a = cv2.dilate(a, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.3).astype(np.uint8))
    if n > 1:
        keep = 1 + int(np.argmax(st[1:, 4]))
        a = a * (lab == keep)
    a = np.clip(blur(a, 2.2) * 1.15, 0, 1)
    return a * feather_box(a.shape, box, 14)


# C3.mp4 부츠 추적으로 찾은 발 닿는 시각(원본 0.3초 기준 로컬, 정지 삽입 전). 로그: c3_contacts.log
C3_CONTACTS = [0.70, 1.00, 1.77, 2.13]
C3_HOLD_FRAME = 30          # 두 번째 발 닿는 프레임(1.00초)에서 0.2초(6프레임) 정지


def st_c3():
    """#4 C3.mp4 0.3~2.6초 + 두 번째 발 닿는 프레임에서 0.2초 정지, 잉여 기포 조각 제거 -> 2.5초"""
    plate = load_L(P("C3_plate.png"))
    fr = read_video(P("C3.mp4"), 0.3, 2.3)
    junk = (430, 825, 675, 985)
    seq = []
    for i, f in enumerate(fr[:69]):
        seq.append(f)
        if i == C3_HOLD_FRAME:
            seq += [f] * 6
    w = Writer(P("C3_comp.mp4"))
    for i, f in enumerate(seq):
        w.write(patch_from(f, plate, junk, f=22), i)
    w.close()
    log = ["C3 발 닿는 프레임 (C3.mp4 부츠 블롭 추적: 정지 후 x가 고정되는 첫 프레임). 원본 0.3초 시작, 30fps(24fps 원본 복제 프레임 포함)",
           "contact#  C3_comp 프레임  C3_comp 시각   비고"]
    for n_, t in enumerate(C3_CONTACTS, 1):
        fi = int(round(t * FPS))
        extra = 6 if fi > C3_HOLD_FRAME else 0
        note = ("<- 0.2초 정지 시작(프레임 %d~%d)" % (fi, fi + 6)) if fi == C3_HOLD_FRAME else ""
        log.append("  %d       %4d          %5.2fs       %s" % (n_, fi + extra, t + extra / FPS, note))
    log.append("뽁 효과음 시각(C3_comp 로컬): 0.70 / 1.00 / 1.97 / 2.33(가장 큼, 4번째). episode.json 작전3a·3b sfx와 일치. 0.63초 이전 부츠는 검출 임계값 밖이라 첫 닿음은 0.70으로 추정.")
    open(P("c3_contacts.log"), "w", encoding="utf-8").write("\n".join(log) + "\n")
    print("\n".join(log))


def st_c4():
    """#5/#6 C4.mp4 1.0~2.4 + 2.4초 프레임 1.0초 정지. v2: 크루 150px 불투명 실루엣, 띠 아래 가장자리, 콩알이 발 하강(펀치인 x2 화면 16px = 원본 8px) + 반짝 2프레임"""
    plate = load_L(P("C3_plate.png"))
    c3f = read_video(P("C3.mp4"), 2.55, 0.2)[0]
    obj_box = (110, 1000, 560, 1340)
    objm = c3_object_mask(c3f, plate, obj_box)
    c4 = read_video(P("C4.mp4"), 1.0, 1.4)[:42]
    off = ring_offset(c4[0], c3f, obj_box, pad=30)
    obj_L = c3f + off
    ys, xs = np.where(objm > 0.5)
    cx = (xs.min() + xs.max()) / 2
    last = c4[-1]
    sp = {
        "boss": Sprite("boss", (int(cx - 125), 1222), last),
        "yeosa": Sprite("yeosa", (int(cx + 10), 1247), last),
        "kong": Sprite("kong", (int(cx + 135), 1272), last),
    }
    kong_foot = (sp["kong"].x0 + sp["kong"].width * 0.95, sp["kong"].y0 + sp["kong"].height * 0.80 + 8)
    print("  crew center", int(cx + 10), 1190, "kong sparkle", kong_foot)
    rng = np.random.default_rng(3)
    w = Writer(P("C4_comp.mp4"))
    for i in range(72):
        t = i / FPS
        base = c4[min(i, 41)]
        if t < 0.2:
            f = base * (1 - objm) + obj_L * objm
        elif t < 0.35:
            k = (t - 0.2) / 0.15
            o = shift(obj_L, 0, 170 * k * k)
            om = shift(objm, 0, 170 * k * k) * (1 - k)
            f = base * (1 - om) + o * om
        else:
            f = base
        if t >= 0.3:
            low = t >= 2.0
            f = stage_set(f, [(sp["boss"], 0), (sp["yeosa"], 0), (sp["kong"], 8 if low else 0)])
            if 2.0 <= t < 2.0 + 2 / FPS:                    # 발 닿는 프레임에 기포 눌림 하이라이트 2프레임
                f = sparkle(f, *kong_foot)
        if 0.2 <= t < 0.3:
            f = glitch(f, rng)
        w.write(f, i)
    w.close()


def st_t2():
    """#7/#8 T2.mp4 + 얼음 크루 3 레이어. v2: 150px 어두운 실루엣, 통통 진폭 9px, 착지 1.4초"""
    fr = read_video(P("T2.mp4"), 0, 4.0)
    n = len(fr)
    med = np.median(np.stack(fr[::3], 0), 0).astype(np.float32)
    pos = {"boss": (212, 884), "yeosa": (300, 910), "kong": (392, 936)}
    sp = {k: Sprite(k, p, med) for k, p in pos.items()}
    amp, LAND = 9.0, 1.4
    w = Writer(P("T2_comp.mp4"))
    for i in range(n):
        t = i / FPS
        f = fr[i]
        d = np.abs(blur(f, 1.5) - blur(med, 1.5))
        occl = np.clip((blur(d, 3) - 18) / 20, 0, 1)
        occl = cv2.dilate(occl, np.ones((9, 9), np.uint8))
        dys = []
        for j, k in enumerate(("boss", "yeosa", "kong")):
            if LAND <= t < LAND + 1.3:
                decay = 1 - (t - LAND) / 1.3 * 0.6
                ph = (t - LAND) / 0.12 + j / 3.0
                dys.append((sp[k], -amp * decay * abs(math.sin(math.pi * ph))))
            else:
                dys.append((sp[k], 0))
        out = stage_set(f, dys, occl=occl, amp=amp)
        if i in (int(LAND * FPS), int(LAND * FPS) + 1):
            out = shift(out, 4 if i == int(LAND * FPS) else -3, -3 if i == int(LAND * FPS) else 2)
        w.write(out, i)
    w.close()


def st_s1():
    """S1 아침: 따뜻한 톤(약한 세피아·낮은 채도) -> S1_warm.png (1440x2560)"""
    im = np.asarray(Image.open(P("S1.png")).convert("L"), np.float32) / 255.0
    g = np.clip(im * 1.06 + 0.03, 0, 1) ** 0.95
    rgb = np.stack([g * 1.00 + 0.045, g * 0.90 + 0.02, g * 0.74], -1)
    rgb = np.clip(rgb, 0, 1)
    Image.fromarray((rgb * 255).astype(np.uint8)).save(P("S1_warm.png"))


if __name__ == "__main__":
    for s in sys.argv[1:]:
        print("==", s); globals()["st_" + s]()
