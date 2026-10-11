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
    ("C03", "still", 1.5, 2, dict(fx="hit")),
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
    ("C16c", "still", 44, 47, dict(fx="hit")),
    ("K2b", "clip", 47, 55, dict(src=0.0)),
    ("C17b", "still", 55, 60, dict(fx="kb", focus=(0.3, 0.5))),
    ("C18", "still", 60, 64, dict(fx="hit")),
    ("K3", "clip", 64, 72, dict(src=0.0)),
    ("C19a", "still", 72, 75, dict(fx="hit")),
    ("C19b", "still", 75, 77, dict(fx="hit")),
    ("C19c", "still", 77, 80, dict(fx="hit")),
    ("C20", "still", 80, 86, dict(fx="kb", focus=(0.55, 0.6))),
    ("C21", "still", 86, 92, dict(fx="kb", sat_hit=88)),
    ("C22", "still", 92, 94, dict(still="K4Sb", fx="none", sepia=True)),
    ("K4", "clip", 94, 100, dict(src=0.0, sepia=True)),
    ("END", "end", 100, None),
]

# 숏폼: 같은 곡 구간(S0=0.46) 처음 29.0초. 같은 박 격자.
SHORT = [
    ("C01", "black", 0, 1),
    ("C02", "still", 1, 1.5, dict(fx="hit", cx=656)),
    ("C03", "still", 1.5, 2, dict(fx="hit", cx=656)),
    ("C04", "still", 2, 3, dict(fx="hit", cx=400)),
    ("C05", "still", 3, 6, dict(fx="kb_rev", cx=380)),
    ("C06b", "still", 6, 10, dict(fx="kb", cx=1310)),
    ("C08", "still", 10, 12, dict(fx="kb", cx=950, xfade=0.4)),
    ("C09", "still", 12, 14, dict(fx="hit", cx=780)),
    ("K1", "clip", 14, 19, dict(src=0.5, cx=1000)),
    ("C10", "still", 19, 21, dict(fx="kb", cx=656)),
    ("C11b", "still", 21, 24, dict(fx="kb", cx=656)),
    ("C14", "still", 24, 28, dict(fx="kb", cx=656)),
    ("C16c", "still", 28, 30, dict(fx="hit", cx=960)),
    ("K2b", "clip", 30, 36, dict(src=0.0, cx=1180)),
    ("C17b", "still", 36, 39, dict(fx="kb", cx=200)),
    ("C22", "still", 39, 41, dict(still="K4Sb", fx="none", sepia=True, cx=850)),
    ("K4", "clip", 41, 47, dict(src=0.0, sepia=True, cx=850)),
    ("END", "end", 47, None),
]


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
    ev.append(("ding", tk(11 if short else 19), 0.35))
    if not short:
        ev.append(("ding", tk(88), 0.35))
    k4 = 41 if short else 94
    ev.append(("chak", tk(k4) + 2.5, 0.8))
    return ev
