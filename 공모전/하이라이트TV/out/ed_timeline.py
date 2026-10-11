"""「나, 주연」 편집 타임라인 (본편 + 숏폼 공용 박자 격자).
음악: audio/naJuyeon_t2.wav 를 S0 초부터 연속 구간으로 사용 (이어 붙이기 없음).
박자: 109.0 BPM (librosa+위상 피팅), 4/4. 영상 t = 곡 t - S0.
"""
BPM = 109.0
P = 60.0 / BPM            # 박 길이 0.5505s
SONG_PHASE = 0.505        # 곡에서 첫 박(팀파니 스팅) 위치
S0 = 0.46                 # 곡 사용 시작점 (첫 소리 직전)
T0 = SONG_PHASE - S0      # 영상에서 첫 박 위치 0.045s
FPS = 30


def tk(k):
    """박 인덱스 -> 영상 시간(초)"""
    return T0 + P * k


def fk(k):
    """박 인덱스 -> 프레임 번호"""
    return 0 if k == 0 else int(round(tk(k) * FPS))


MAIN_DUR = 58.0
SHORT_DUR = 29.0

# (이름, 소스종류, 시작박, 끝박, 옵션)
# 소스: still 이름 / clip 이름. 옵션은 render 에서 해석.
MAIN = [
    ("C01", "black", 0, 1),
    ("C02", "still", 1, 1.5, dict(fx="hit")),
    ("C03", "still", 1.5, 2, dict(fx="hit", zoom=1.7, focus=(0.5, 0.135))),
    ("C04", "still", 2, 3, dict(fx="hit")),
    ("C05", "still", 3, 7, dict(fx="kb_rev")),
    ("C06b", "still", 7, 12, dict(fx="kb", focus=(0.85, 0.35))),
    ("C07", "still", 12, 18, dict(fx="kb", focus=(0.62, 0.5))),
    ("C08", "still", 18, 21, dict(fx="kb", xfade=0.6)),
    ("C09", "still", 21, 24, dict(fx="hit")),
    ("K1", "clip", 24, 29, dict(src=0.5)),
    ("C10", "still", 29, 32, dict(fx="kb")),
    ("C11b", "still", 32, 35, dict(fx="kb")),
    ("C12", "still", 35, 36, dict(fx="hit")),
    ("C13b", "still", 36, 37, dict(fx="hit")),
    ("C14", "still", 37, 41, dict(fx="kb")),
    ("C15", "still", 41, 42.5, dict(fx="hit")),
    ("C15b", "still", 42.5, 44, dict(fx="hit")),
    ("C15c", "still", 44, 46, dict(still="C15b", fx="hit", zoom=1.5, focus=(0.62, 0.28))),
    ("K2c", "clip", 46, 56.5, dict(src=0.0)),
    ("C17b", "still", 56.5, 60, dict(still="C17c", fx="kb", focus=(0.3, 0.5))),
    ("C18", "still", 60, 64, dict(fx="hit")),
    ("K3", "clip", 64, 72, dict(src=0.0)),
    ("C19a", "still", 72, 77, dict(fx="hit")),
    ("C19b", "still", 77, 77.5, dict(fx="hit")),
    ("C19c", "still", 77.5, 80, dict(fx="hit")),
    ("C20", "still", 80, 86, dict(fx="kb", focus=(0.55, 0.6))),
    ("C21", "still", 86, 92, dict(fx="kb", sat_hit=88)),
    ("C22", "still", 92, 94, dict(still="K4Sb", fx="none", sepia=True)),
    ("K4", "clip", 94, 100, dict(src=0.0, sepia=True)),
    ("END", "end", 100, None),
]

# 숏폼 v2 (P안): 같은 곡 구간(S0=0.46) 처음 29.0초. 같은 박 격자. 김치 컷(C16c, K2b, C17b) 제외.
SHORT = [
    ("C01", "black", 0, 1, dict(under="C04", cx=400)),
    ("C02", "still", 1, 1.5, dict(fx="hit", cx=656)),
    ("C03", "still", 1.5, 2, dict(fx="hit", cx=656, zoom=1.7, focus=(0.5, 0.135))),
    ("C04", "still", 2, 3, dict(fx="hit", cx=400)),
    ("C05", "still", 3, 6, dict(fx="kb_rev", cx=380)),
    ("C07", "still", 6, 11, dict(fx="kb", cx=870, focus=(0.62, 0.5))),
    ("C06b", "still", 11, 19, dict(fx="none", pan=(600, 1250, None))),
    ("C08", "still", 19, 21, dict(fx="kb", cx=950, xfade=0.4)),
    ("C09", "still", 21, 24, dict(fx="hit", cx=780)),
    ("K1", "clip", 24, 29, dict(src=0.5, pan=(600, 1000, 0.8))),
    ("C10", "still", 29, 31, dict(fx="kb", cx=656)),
    ("C11b", "still", 31, 34, dict(fx="kb", cx=656)),
    ("C14", "still", 34, 38, dict(fx="kb", cx=656)),
    ("C15", "still", 38, 39, dict(fx="hit", cx=990)),
    ("C22", "still", 39, 41, dict(still="K4Sb", fx="none", sepia=True, cx=850)),
    ("K4", "clip", 41, 47, dict(src=0.0, sepia=True, cx=850)),
    ("END", "end", 47, None),
]


# K2c 시간 매핑 (v4.1): 원본(raw) 0-1.3s 를 SLOW 배속(슬로모션, minterpolate), 1.3-2.4s 는 1.0배, 3.12s 프레임 0.25s 홀드.
# 받는 순간(raw 3.05s)이 영상 29.07s(=K2c 시작 25.37s + 3.70s)에 오도록 SLOW = 0.6667.
K2C_SLOW = (0.0, 1.3, 2.0 / 3.0)
K2C_HOLD_AT, K2C_HOLD_LEN = 3.12, 0.25
K2C_RECEIVE_RAW = 3.05


def k2c_u_from_raw(raw):
    a, b, sp = K2C_SLOW
    u = min(raw, b) / sp
    if raw > b:
        u += raw - b
    if raw > K2C_HOLD_AT:
        u += K2C_HOLD_LEN
    return u


def k2c_raw_from_u(u):
    """영상 로컬 시간 u -> (원본 raw 시간, 홀드 중 여부, 홀드 진행 0..1)"""
    a, b, sp = K2C_SLOW
    u_hold0 = k2c_u_from_raw(K2C_HOLD_AT)
    if u_hold0 < u < u_hold0 + K2C_HOLD_LEN:
        return K2C_HOLD_AT, True, (u - u_hold0) / K2C_HOLD_LEN
    if u >= u_hold0 + K2C_HOLD_LEN:
        u -= K2C_HOLD_LEN
    ub = b / sp
    raw = u * sp if u <= ub else b + (u - ub)
    return min(raw, 4.8), False, 0.0


K2C_RECEIVE_U = k2c_u_from_raw(K2C_RECEIVE_RAW)


def sfx_events(short=False):
    """(종류, 시간(초), 게인) 목록. 곡은 그대로 두고 효과음만 위에 얹는다."""
    seg = SHORT if short else MAIN
    ev = []
    for s in seg:
        o = s[4] if len(s) > 4 else {}
        if s[1] == "still" and o.get("fx") == "hit":
            hook = s[0] in ("C02", "C03", "C04")
            ev.append(("hit", tk(s[2]), 0.55 if hook else 0.30))
    if not short:
        ev.append(("hit", tk(88), 0.14))
    ev.append(("ding", tk(19.5 if short else 19), 0.35))
    if not short:
        ev.append(("ding", tk(88), 0.35))
    if not short:
        ev.append(("chak", tk(46) + K2C_RECEIVE_U, 0.8))   # v4: K2c 김치 받는 순간
    k4 = 41 if short else 94
    ev.append(("chak", tk(k4) + 2.5, 0.8))
    return ev
