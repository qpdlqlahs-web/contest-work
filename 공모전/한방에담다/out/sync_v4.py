# -*- coding: utf-8 -*-
"""v4 가사 싱크: 가사지(명세 1절) 음절 수 + 단어 앵커(whisper large-v3 / stable-ts 강제정렬 2회 + 보컬 에너지 침묵 구간) +
보컬 스템 스펙트럴 플럭스 온셋 -> 줄별 DP 로 음절 시작 시각 결정. 결과 _work/lyrics_v4.json"""
import json, numpy as np
from timeline_v2 import SONG_START
d = json.load(open('_work/sync_data.json'))
ons = np.array([o[0] for o in d['onsets']]); st = np.array([o[1] for o in d['onsets']])
ref = np.percentile(st, 98); st = np.clip(st / ref, 0, 1)

# (표시줄들, [(단어, 앵커)], 창 시작, 창 끝, v3의 t_on)
SPEC = [
 (["제기동 한옥 지붕 아래"], [("제기동", 10.73), ("한옥", 11.80), ("지붕", 12.50), ("아래", 12.98)], 10.6, 13.75, 9.25),
 (["약재만 약 삼백팔십"], [("약재만", 14.86), ("약", 15.48), ("삼백팔십", 15.72)], 14.8, 17.12, 14.75),
 (["서랍 서랍 다 열어 봐도"], [("서랍", 18.58), ("서랍", 18.92), ("다", 19.36), ("열어", 19.54), ("봐도", 19.92)], 18.5, 20.5, 18.50),
 (["내 자리는 어디 있지?"], [("내", 20.58), ("자리는", 21.28), ("어디", 22.18), ("있지", 22.80)], 20.5, 23.9, 21.25),
 (["빼꼼 여기도 감초", "빼꼼 저기도 감초"], [("빼꼼", 24.03), ("여기도", 24.82), ("감초", 25.40), ("빼꼼", 26.35), ("저기도", 26.70), ("감초", 27.24)], 23.95, 28.0, 24.00),
 (["안 끼는 데가 없다지"], [("안", 28.90), ("끼는", 29.20), ("데가", 29.66), ("없다지", 30.26)], 28.85, 31.07, 28.75),
 (["군도 아냐 신도 아냐"], [("군도", 31.22), ("아냐", 33.70), ("신도", 34.32), ("아냐", 34.72)], 31.15, 35.15, 31.30),
 (["그럼 나는 뭐지?"], [("그럼", 35.26), ("나는", 35.54), ("뭐지", 35.94)], 35.2, 36.62, 35.25),
 (["감초 감초 약방에 감초"], [("감초", 36.88), ("감초", 37.70), ("약방에", 38.45), ("감초", 39.40)], 36.8, 40.4, 36.80),
 (["어디든 끼는 약방에 감초"], [("어디든", 40.46), ("끼는", 41.46), ("약방에", 42.14), ("감초", 43.02)], 40.4, 44.25, 40.46),
 (["머리는 시원 발은 뜨끈"], [("머리는", 44.28), ("시원", 45.14), ("발은", 45.92), ("뜨끈", 46.82)], 44.25, 47.1, 44.28),
 (["서울한방진흥센터로", "가자!"], [("서울한방진흥센터로", 47.70), ("가자", 50.98)], 47.6, 51.3, 47.80),
 (["널리 구제한다 보제원 옛터"], [("널리", 51.34), ("구제한다", 52.82), ("보제원", 53.62), ("옛터", 54.44)], 51.3, 54.95, 51.34),
 (["나는 감초"], [("나는", 55.10), ("감초", 55.54)], 55.05, 56.25, 55.10),
 (["다 어울리게 하지"], [("다", 56.28), ("어울리게", 57.00), ("하지", 57.90)], 56.25, 59.25, 56.28),
 (["감초 감초 약방에 감초"], [("감초", 59.46), ("감초", 59.96), ("약방에", 60.82), ("감초", 62.10)], 59.4, 62.8, 59.40),
 (["약방엔 감초,"], [("약방엔", 62.86), ("감초", 63.45)], 62.8, 64.65, 62.86),
 (["약령시엔 쉼 한 첩"], [("약령시엔", 64.70), ("쉼", 65.82), ("한", 66.34), ("첩", 66.62)], 64.65, 69.0, 64.70),
]

def dp_align(words, ws, we, lam=1.0, mu=0.35, mingap=0.07):
    sylls = []; prior = []
    for k, (w, a) in enumerate(words):
        nxt = words[k + 1][1] if k + 1 < len(words) else we - 0.15
        m = len(w)
        for j in range(m):
            sylls.append(w[j]); prior.append(a + (nxt - a) * j / m)
    N = len(sylls)
    cand = [(t, s) for t, s in zip(ons, st) if ws - 0.1 <= t <= we]
    # 앵커 자체도 약한 후보(온셋이 없을 때 대비)
    cand += [(p, 0.0) for p in prior]
    cand = sorted(set(cand))
    ct = np.array([c[0] for c in cand]); cs = np.array([c[1] for c in cand]); C = len(ct)
    INF = 1e9
    cost = np.full((N, C), INF); back = np.zeros((N, C), int)
    for c in range(C):
        cost[0, c] = lam * abs(ct[c] - prior[0]) - mu * cs[c]
    for i in range(1, N):
        for c in range(C):
            best = INF; bi = 0
            for p in range(C):
                if cost[i - 1, p] < INF and ct[c] - ct[p] >= mingap:
                    if cost[i - 1, p] < best: best = cost[i - 1, p]; bi = p
            if best < INF:
                cost[i, c] = best + lam * abs(ct[c] - prior[i]) - mu * cs[c]; back[i, c] = bi
    c = int(np.argmin(cost[N - 1])); path = [c]
    for i in range(N - 1, 0, -1):
        c = back[i, c]; path.append(c)
    path = path[::-1]
    return sylls, [float(ct[c]) for c in path], prior

out = []
for lines, words, ws, we, v3on in SPEC:
    sy, t, prior = dp_align(words, ws, we)
    out.append(dict(lines=lines, sylls=sy, t=t, prior=prior, win=[ws, we], v3_t_on=v3on))
json.dump(out, open('_work/lyrics_v4.json', 'w'), ensure_ascii=False, indent=1)
for o in out:
    print(o['lines'][0], f"| 첫음절 {o['t'][0]:.2f} (앵커 {o['prior'][0]:.2f}) 끝창 {o['win'][1]:.2f}")
    print('   ', ' '.join(f'{s}{x:.2f}' for s, x in zip(o['sylls'], o['t'])))
