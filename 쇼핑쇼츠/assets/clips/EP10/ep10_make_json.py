# -*- coding: utf-8 -*-
"""episode.json 생성기 (타이밍 조정은 여기서 하고 다시 실행). 기준: review.md 「[creative] 최종 소스표」 + C3 판정"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = {"font": "radio", "radio": True}

def cap(text, at=0.0, y=380, badge=None, cont=False):
    d = {"text": text, "at": at, "y": y, **R}
    if badge: d["badge"] = badge
    if cont: d["cont"] = True
    return d

def sfx(f, at, vol=0.8): return {"file": f, "at": at, "vol": vol}

STRIP_BOX = [0.16, 0.37, 0.80, 0.52]
segs = [
 # 1 훅 (T1.mp4 0.0-1.7, 0.7배속, apply_c1_fix 적용 -> T1_hook.mp4 2.4초)
 {"name": "훅a", "type": "video", "file": "T1_hook.mp4", "start": 0.0, "dur": 1.2,
  "alerts": [{"at": 0.0, "box": STRIP_BOX}],
  "captions": [cap("뽁뽁이가 걸어간다")], "preview_at": 0.4,
  "sfx": [sfx("roller.wav", 0.0, 0.7), sfx("thud.wav", 0.35, 0.35), sfx("thud.wav", 0.8, 0.35)]},
 {"name": "훅b", "type": "video", "file": "T1_hook.mp4", "start": 1.2, "dur": 1.2,
  "alerts": [{"at": 0.0, "box": STRIP_BOX, "silent": True}],
  "captions": [cap("사람 3명 추정", cont=True)],
  "zoom": {"at": 0.2, "dur": 0.2, "from": 1.0, "to": 1.3, "cx": 0.45, "cy": 0.43}, "zoom_label": "ZOOM x2", "zoom_label_until": 1.2,
  "preview_at": 0.9, "sfx": [sfx("roller.wav", 0.0, 0.6), sfx("beep.wav", 0.2, 0.7)]},
 # 2 작전① C3_plate + 크루 3 + 뭉치 (S2_comp.mp4). v2: 로컬 1.0~1.6초(전체 3.4~4.0초) x1.5 펀치인(크루 중심)
 {"name": "작전1a", "type": "video", "file": "S2_comp.mp4", "start": 0.0, "dur": 1.0,
  "captions": [cap("단열판 운반 완료", badge=1)], "preview_at": 0.5,
  "sfx": [sfx("gungcha.wav", 0.0, 0.8), sfx("thud.wav", 0.3, 0.8)]},
 {"name": "작전1b", "type": "video", "file": "S2_comp.mp4", "start": 1.0, "dur": 0.6,
  "captions": [cap("단열판 운반 완료", badge=1, cont=True)],
  "zoom": {"at": 0.0, "dur": 0.15, "from": 1.0, "to": 1.5, "cx": 0.34, "cy": 0.63}, "preview_at": 0.3},
 {"name": "작전1c", "type": "video", "file": "S2_comp.mp4", "start": 1.6, "dur": 0.4,
  "captions": [cap("단열판 운반 완료", badge=1, cont=True)], "preview_at": 0.2},
 # 3 작전② C2 3장 교차 (S3_comp.mp4: C2a 0-1.0, C2b 1.0-1.5, C2c 1.5-2.5)
 {"name": "작전2a", "type": "video", "file": "S3_comp.mp4", "start": 0.0, "dur": 1.5,
  "captions": [cap("접착수 살포", badge=2)], "preview_at": 1.2,
  "sfx": [sfx("creak.wav", 0.0, 0.7), sfx("chiik.wav", 1.0, 0.9)]},
 {"name": "작전2b", "type": "video", "file": "S3_comp.mp4", "start": 1.5, "dur": 1.0,
  "captions": [cap("뭉치 먼저 세척됨", cont=True)], "preview_at": 0.6,
  "zoom": {"at": 0.0, "dur": 0.15, "from": 1.0, "to": 1.6, "cx": 0.264, "cy": 0.596},
  "sfx": [sfx("thud.wav", 0.1, 0.7)]},
 # 4 작전③ C3.mp4 0.3-2.6 + 두 번째 발 닿는 프레임 0.2초 정지 (C3_comp.mp4 2.5초: 정지 0.3-0.5)
 {"name": "작전3a", "type": "video", "file": "C3_comp.mp4", "start": 0.0, "dur": 1.6,
  "captions": [cap("슬리퍼로 위장 복귀", badge=3)], "preview_at": 0.9,
  "sfx": [sfx("pop.wav", 0.70, 0.6), sfx("pop.wav", 1.00, 0.6)]},
 {"name": "작전3b", "type": "video", "file": "C3_comp.mp4", "start": 1.6, "dur": 0.9,
  "captions": [cap("…뽁?", cont=True)], "preview_at": 0.5,
  "sfx": [sfx("pop.wav", 0.37, 0.7), sfx("pop.wav", 0.73, 1.0)]},
 # 5 들킴 C4.mp4 1.0-2.4 (C4_comp.mp4 0-1.4) 삑 0.2, BGM 정지(bgm_mute)
 {"name": "들킴", "type": "video", "file": "C4_comp.mp4", "start": 0.0, "dur": 1.4,
  "captions": [cap("얼음!", at=0.45)],
  "stamps": [{"text": "들킴", "at": 0.45, "x": 330, "y": 950, "font": "osd", "plate": True, "size": 84}],
  "preview_at": 0.8, "sfx": [sfx("whistle.wav", 0.2, 0.9)]},
 # 6 늦은 뽁: C4 2.4초 프레임 정지 0.6 -> 콩알이 발 내림(6px) + 펀치인
 {"name": "늦은뽁", "type": "video", "file": "C4_comp.mp4", "start": 1.4, "dur": 1.0,
  "captions": [cap("…뽁.", at=0.6)],
  "zoom": {"at": 0.6, "dur": 0.2, "from": 1.0, "to": 2.0, "cx": 0.285, "cy": 0.62}, "zoom_label": "ZOOM x2", "zoom_label_until": 1.0,
  "preview_at": 0.9, "sfx": [sfx("pop.wav", 0.6, 0.9)]},
 # 7 반전 T2.mp4 0.3-3.1 (T2_comp: 얼음 크루 3 + 통통). 11.8 글리치(2프레임 노이즈 바 + 시계 1칸)
 {"name": "반전", "type": "video", "file": "T2_comp.mp4", "start": 0.3, "dur": 2.8,
  "frame_drop": {"frames": 2, "clock_jump": 1},
  "captions": [cap("정보원이 제일 시끄러움", at=0.0)], "preview_at": 1.5,
  "sfx": [sfx("thud.wav", 1.1, 0.8)] + [sfx("pop.wav", round(1.1 + 0.12 * k, 2), 0.55 + 0.05 * k) for k in range(6)]},
 # 8 다시보기 T2.mp4 1.2-1.8 0.5배속 + 펀치인
 {"name": "다시보기", "type": "video", "file": "T2_comp.mp4", "start": 1.2, "dur": 1.2, "speed": 0.5,
  "zoom": {"at": 0.0, "dur": 0.3, "from": 1.0, "to": 1.3, "cx": 0.38, "cy": 0.44},
  "captions": [cap("판독: 고의 아님", at=0.1)], "preview_at": 0.6,
  "sfx": [sfx("bounce.wav", 0.4, 0.7)]},
 # 9 아침 S1 (CAM 02 07:30, 따뜻한 톤, 미세 줌)
 {"name": "아침", "type": "image", "file": "S1_warm.png", "dur": 2.2, "color": True, "cam": "CAM 02", "clock": "07:30:12",
  "zoom": {"at": 0.0, "dur": 2.2, "from": 1.0, "to": 1.04, "cx": 0.5, "cy": 0.5},
  "captions": [cap("결국 세웠다(벽에)", at=0.0, y=1240)], "preview_at": 1.0},
 # 10 작업일지
 {"name": "작업일지", "type": "image", "file": "S1_warm.png", "dur": 2.6, "dim": 0.6, "color": True, "cam": "CAM 02", "clock": "07:30:15",
  "worklog": {"title": "작업일지 #010", "lines": ["결과: 벽 1, 고양이 침대 1", "사유: 소음"], "approval": False},
  "stamps": [{"text": "반려", "at": 1.8, "x": 790, "y": 990, "font": "doc", "shape": "circle", "dia": 220}],
  "preview_at": 1.2},
 # 11 PPL (T1 0.0-1.7 루프 배경)
 {"name": "PPL", "type": "video", "file": "T1_ppl.mp4", "start": 0.0, "dur": 5.4, "dim": 0.6, "ppl": True, "preview_at": 2.5},
]

ep = {
 "pinned_comment": "영상은 AI 상황극(연출)입니다.\n\n새벽 3시 거실, 뽁뽁이 공사팀을 판독해 봤습니다. 다음엔 어디를 판독해 볼까요? 장소 제보 받아요 👇\n판독 요청: 아침 장면에 몇 명?",
 "price_date": "10/10",
 "ppl_layout": "v6",
 "ppl_label": "[광고] PPL",
 "ppl_notes_lines": True,
 "ppl_cta": {"youtube": "링크는 영상 설명란에", "clip": "화면 스티커를 눌러 보세요"},
 "ir_look": True,
 "bgm": "bgm_sneaky.wav", "bgm_vol": 0.5,
 "title": "[AI 상황극] 창문 단열 뽁뽁이 6천원대, 새벽 3시 CCTV 속 공사팀",
 "titles": ["[AI 상황극] 창문 단열 뽁뽁이 6천원대, 새벽 3시 CCTV 속 공사팀"],
 "desc_first_line": "[AI 상황극] 영상 속 장면은 AI 연출이며 실제 제품의 성능과 다릅니다.",
 "aeo_line": "33cm × 10m 뽁뽁이 에어캡 롤은 네이버 기준 6,180원입니다(10/10 기준). 영상은 AI 상황극입니다.",
 "hashtags": ["#AI상황극", "#뽁뽁이", "#창문단열", "#에어캡", "#새벽3시CCTV"],
 "cam": "LIVING CAM", "date": "2026-10-13", "clock": "03:14:20",
 "site_label": {"text": "밤살림공사 제3현장 · 작업 #010", "from": 2.6, "until": 9.3},
 "ai_label": {"big": {"text": "AI 상황극", "size": 44, "until": 3.0}, "text": "AI 연출", "size": 34, "alpha": 190},
 "replay_y": 300,
 "ppl_notes": ["※ 단열 효과: 이 영상에선 측정 안 함", "※ '뽁' 소리: 기본 포함"],
 "ppl_headline": "뽁뽁이 공사 크루 채용",
 "bgm_mute": [[9.6, 11.8]],
 "scanline": False,
 "limiter": 0.8,
 "product": {
   "store": "네이버",
   "name": "국내산 두꺼운 뽁뽁이 포장용 에어캡 완충 롤 창문 단열 테포르 33cm - 10m, 1개",
   "short": "국내산 두꺼운 뽁뽁이 포장용 에어캡 완충 롤 창문 단열 테포르 33cm - 10m, 1개",
   "role": "33cm × 10m 롤 · 1m당 약 618원",
   "price": 6180, "reviews": 1604, "rating": 4.95, "aff_type": "쇼핑커넥트",
   "link": "https://naver.me/FaeW9AkP"},
 "product_alt": {"store": "쿠팡", "name": "셔니엘 자석식 창문 방풍뽁뽁이 외풍차단 바람막이", "short": "셔니엘 자석식 창문 방풍뽁뽁이 외풍차단 바람막이", "option": "S(150×120cm)",
   "price": 25800, "reviews": 345, "aff_type": "쿠팡파트너스", "link": "https://link.coupang.com/a/hH27FMl3rE"},
 "_todo": [
  "[업로드 전 PD] 가격·리뷰·평점은 10/10 기준(6,180원 / 1,604 / 4.95). 업로드 직전 재확인. 7천원 이상이면 제목의 '6천원대'를 '1만원 이하'로 변경. 1m당 618원 = 가격 ÷ 10.",
  "[효과음 미보유] 새소리(아침 컷), 종종종(훅)은 기존 roller.wav로 대체. 전용 효과음 없음 -> 필요 시 assets/sfx에 추가 후 sfx 키 갱신.",
  "[사전 합성] 이 폴더의 *_comp.mp4, T1_hook/T1_ppl.mp4, S1_warm.png는 ep10_build.py가 만든 것. 타이밍을 바꾸면 ep10_build.py의 해당 단계를 다시 실행.",
  "cam 키: 컷별 cam 지원(make_cctv.py, 선택 키). 아침 컷은 CAM 02."
 ],
 "segments": segs,
}
json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("total", round(sum(s["dur"] for s in segs), 2))
