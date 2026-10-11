# EP11 기획안 v1: 「무궁화 꽃이 피었습니다」 (planner, 2026-10-10)

> 기준: `concept_v2.1.md`(critic PASS, 격리 콜드 리드 PASS) + 영수 님 지시 "영상 길이를 좀 늘리면 되잖아".
> 총 **30.0초**(29~32초). 영상은 생성하지 않았다. 같은 폴더의 `episode.json`이 이 표와 1:1이다.

## 0. 한눈에 보기
| 항목 | 값 |
|---|---|
| 총 길이 | 30.0초 (콘셉트 26.7초에서 +3.3초) |
| 들킴 / 반전 시작 / 반전 끝 | 9.2초 / 10.8초 / 13.5초 (반전 시작 12초 이내) |
| 작전 컷 최대 길이 | 1.7초 (모든 세그먼트 2.5초 이하, PPL 5.5초만 예외) |
| 영상 클립 | 3개 (V1·V2·V3), 세그먼트 9개로 재사용. 나머지는 이미지+줌 |
| 크레딧 | 기본 7.5cr (3클립 × 2.5cr), 재생성 1회 포함 최대 10cr |
| 무료 이미지 | 15장 (웹 Seedream 4.5 또는 Nano Banana 2 Unlimited, 0cr) |
| 상품 | 네이버(PPL 메인) 송강 10,900원 + 쿠팡(product_alt) 메이스 11,900원, 기준일 10/10 |

## 1. 키워드 리서치

**한계(먼저 밝힘):** 이 환경에서는 검색량 도구(네이버 검색광고 키워드 도구, 검색 자동완성)를 읽지 않았다. 아래는 **상품이 푸는 고민을 검색 의도별로 추린 후보**이고, 검색량 수치는 없다. 업로드 직전 publisher가 자동완성으로 상위 문구를 확인한다.

| # | 고민 검색어 | 의도 | 영상과의 연결 | 쓰는 곳 |
|---|---|---|---|---|
| 1 | 겨울 거실 바닥 차가울 때 | 문제 인식 | 겨울 거실 실내화 필요를 떠올리게 하는 상황 검색어 | 제목 앞부분 |
| 2 | 부모님 실내화 선물 | 선물 구매 | 1만원대 가격, 앞막힘형 털 실내화 | 제목 후보 2, 해시태그(#부모님선물) |
| 3 | 겨울 거실화 / 털 거실화 | 상품군 | 상품명 그대로(송강 털 거실화) | 제목, AEO 문장 |
| 4 | 겨울 털 실내화 앞막힘 | 사양 비교 | 앞막힘형, 털 안감 | 제목 후보 3, 해시태그(#털실내화) |
| 5 | 거실 슬리퍼 겨울 | 상품군(넓은 범위) | 일반 검색어 | 설명란 본문 |

- **일부러 쓰지 않는 검색어:** "층간소음 슬리퍼". 검색 수요가 클 수 있으나 효능 단정이 된다. '층간소음방지'는 PPL 카드의 네이버 상품명 원문에만 나온다(자막·제목·설명·해시태그 금지).
- **경계(critic 확인 요청):** 제목 후보 1의 "겨울 거실 바닥 차가울 때"는 검색 의도를 앞에 둔 문구다. 상품이 바닥 냉기를 막는다고 단정하지는 않지만, 제품과 붙여 읽으면 '효과 암시'로 볼 여지가 있다. critic이 위험하다고 보면 후보 2를 대표 제목으로 바꾼다.
- **가격 문구:** 네이버 10,900원, 쿠팡 11,900원이라 둘 다 "1만원대"가 맞다. 어느 한쪽이 2만원대나 1만원 미만으로 바뀌면 업로드 직전에 수정한다.

## 2. SEO / AEO 문안

**제목 후보(검색어를 앞에, 가격은 1만원대)**
1. 겨울 거실 바닥 차가울 때 털 거실화 1만원대 [AI 상황극] 새벽 3시 CCTV
2. 부모님 실내화 선물 1만원대 털 거실화 [AI 상황극] 새벽 3시 CCTV
3. 겨울 털 실내화 앞막힘 거실화 1만원대, 코기가 챙긴 한 짝 [AI 상황극]

**설명란 구성(위에서 아래로)**
1. 첫 줄(AI 고지): `[AI 상황극] 영상 속 장면은 AI 연출이며 실제 제품의 성능·외형과 다릅니다.`
2. AEO 문장(사실만): `송강 털 거실화(앞막힘형, 회색·분홍 니트 골지 갑피, 털 안감)는 네이버 기준 10,900원(10/10 기준)이고, 쿠팡의 메이스 털 실내화는 11,900원입니다. 영상은 AI 상황극입니다.`
3. 상품 2줄: 네이버 상품명 원문 + 10,900원 + 링크 `https://naver.me/xIF6OIKh` / 쿠팡 `메이스 폭신폭신 털 실내화 슬리퍼` + 11,900원 + 링크 `https://link.coupang.com/a/hJqyjAdTXg` (기준일 10/10)
4. 대가성 문구 2종(토씨 그대로):
   - 이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.
   - 이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
5. 해시태그 5개: `#AI상황극 #겨울실내화 #털실내화 #부모님선물 #새벽3시CCTV`

**고정 댓글(쇼츠는 맨 위에 대가성 2종):** 대가성 2종 → "영상은 AI 상황극(연출)입니다." → 판독 요청 질문("코기는 길 안내원일까, 수고비 받는 경비일까?"). 전문은 episode.json `pinned_comment`.

**공개 시점:** EP10(10/11 19:00)과 구조가 비슷하므로 10/14 이후.

## 3. 고른 이유 초안 (확정은 영수 님 몫)
> 1만원대 털 안감 앞막힘형 거실화 중 평점 4.86·리뷰 81이 쌓인 상품이라, 겨울 부모님 실내화 선물 후보로 가격과 평을 비교해 볼 만해서 골랐다.

- 영수 님이 직접 고쳐 쓰거나 새로 쓴다. 후기·체험처럼 들리는 표현("써보니" 등)과 효능 단어는 넣지 않았다.
- 쿠팡 상품은 상품평 14개(평점 미확인)로 근거가 얇다. '네이버 메인, 쿠팡은 가격 비교용 보조'로 읽히게 두었다.

## 4. 영수 님 지시 반영: 늘어난 시간

| 구간 | 콘셉트 v2.1 | 이 기획 | 늘린 만큼 하는 일 |
|---|---|---|---|
| 0~카드 | 2.5초 | **3.0초** (+0.5) | 카드 1줄째를 0.0초, 2줄째("※ 코기가 보면 얼음")를 0.9초에 순차 등장, 본부 직인 1.0초. 두 줄이 동시에 뜨지 않아 한 줄씩 읽힌다. 코기·미끄럼 라벨은 카드가 내려간 3.0초에 |
| ② 방향 전환 | 2.4초 | **3.0초** (+0.6) | 우회 0.9 / 막음 1.1 / 현관 쪽 1.0. 인과 보강은 아래 5장 |
| 시간 점프 | 1.0초 | **1.4초** (+0.4) | 노이즈 바 2프레임 + 시계 03:52:09 + "38분 후" 0.6초. "…수고비?"는 0.5초 뒤 등장 |
| 결재 카드 | 2.5초 | **3.1초** (+0.6) | 카드 등장 → 1.2초 '승인' 도장 → 1.9초 손글씨 "수고비 인정"을 1.2초 유지. 두 세그먼트(1.6+1.5)로 나눠 2.5초 이하 유지 |
| 얼음 | 0.8초 | 1.0초 (+0.2) | CAM 2 인셋 0.8초가 온전히 보이게 |
| 오해 | 0.7초 | 0.9초 (+0.2) | 슬리퍼 눈알과 CAM 2 반응을 함께 읽을 시간 |
| 돌려 세움 | 0.8초 | 1.0초 (+0.2) | "…길 안내?" 읽기와 진행바 60→90% |
| 아침 b | 1.2초 | 1.5초 (+0.3) | 눈 굴림 교차(M1→M1b) 두 번 보이게 |
| 끝 | 1.7초 | 2.0초 (+0.3) | 광고·AI 고지 읽기 |
| 합계 | 26.7초 | **30.0초** | 반전 시작 9.3 → 10.8초(12초 이내), 들킴 7.9 → 9.2초 |

## 5. 콜드 리드 잔여 혼동 5건 반영
| # | 혼동 | 반영 |
|---|---|---|
| 1 | 0~2.5초 글자 밀도 | 3.0초로 연장, 카드 줄을 순차 등장(0.0 / 0.9초), 좌상단은 "광고 · AI 상황극" 한 가지만. 코기 라벨·미끄럼 라벨은 카드가 사라진 뒤 |
| 2 | 4.8~7.2초 방향 전환 인과 | 구간 3.0초. 우회 0.9초에 슬리퍼 눈알이 코 → 왼쪽 길 순으로 본다(줌이 왼쪽으로). 막음 1.1초에 앞발이 길 위에 놓이는 '척'을 0.5초에 두고, 줌인 1.0→1.25로 눈과 발을 크게 보여 준다. 현관 쪽 1.0초에 코끝과 슬리퍼가 현관을 향하고 진행바가 30%→60%로 **올라가는 것**을 보여 준다(자막은 넣지 않는다: v2.1의 "…저리 가라고?" 삭제 유지) |
| 3 | 11.8~12.8초 시간 점프 | 1.4초. 노이즈 바 2프레임(frame_drop) + 시계 03:52:09 + "38분 후" 0.6초(라벨, 효과음 없음). 직전 컷 시계는 03:14대라 점프가 숫자로 읽힌다. 아침 컷은 컬러로 한 번 더 구분 |
| 4 | 17~19.5초 결재 글자 | 3.1초. 카드 2줄(각 8자 안팎)을 순차 등장 → 1.2초 도장 → 1.9초 손글씨 1.2초 유지. 도장 뒤에도 카드가 남는 두 번째 세그먼트에서 손글씨를 읽는다 |
| 5 | CAM 2 두루 역할 | **두루 = 목격자 리액션 캠.** 관객이 느끼는 감정을 대신 보여 주는 역할로 고정. 첫 등장(4.65~5.45초)은 라벨 "CAM 2 · 목격자 두루"로 역할을 밝히고 눈알이 커진다(놀람). 둘째(9.95~10.75초)는 "CAM 2"만 쓰고 눈알이 위로 뒤집힌다("아 쟤네 또"). 메인 카메라 이름은 `ENTRY CAM`으로 둬서 인셋 "CAM 2"와 헷갈리지 않게 했다. 본 화면에는 두루가 없다 |

## 6. 컷 표 (30.0초)
이미지·영상 열의 ID는 7장(이미지)과 8장(영상)의 프롬프트 번호다. 시작·종료는 누적 시간이다.

| 컷 | 초 (길이) | 내용 | 이미지·영상 | 생성 프롬프트(영어) | 재사용 계획 | 예상 크레딧 |
|---|---|---|---|---|---|---|
| 훅a | 0.0–1.5 (1.5) | 0프레임부터 슬리퍼 두 짝이 작업화 다리로 현관 쪽으로 종종 걷는다. 카드 1줄째, 좌상단 "광고 · AI 상황극" | V1 0.0–1.5 | 8장 V1 / 시작 프레임 M0 | V1을 훅·걷기·달리기 4세그먼트에 | V1 2.5cr |
| 훅b | 1.5–3.0 (1.5) | 계속 걷는다. 카드 2줄째 "※ 코기가 보면 얼음", 본부 직인 | V1 1.5–3.0 | 〃 | V1 | 〃 |
| ① 걷기 | 3.0–3.9 (0.9) | 카드 퇴장. 라벨 "코기 · 수면 중 zzz", "⚠ 미끄럼". 진행바 30%. 자막 ① "무궁화 꽃이…" | V1 3.0–3.9 | 〃 | V1 | 〃 |
| ① 돌아봄 | 3.9–4.5 (0.6) | 코기가 귀를 세우고 눈을 뜨며 고개를 돌린다. 띵 | V2 0.5–1.1 | 8장 V2 / 시작 프레임 V1의 3.9초 캡처 | V2 | V2 2.5cr |
| ① 얼음 | 4.5–5.5 (1.0) | V2 1.1초 프레임 정지. 슬리퍼 앞코에 눈알 '팍'. CAM 2 인셋(두루 눈알 커짐). BGM 0.3초 끊김 | V2 정지 + CAM2a | 7장 CAM2a. 눈알은 editor 오버레이 | V2 | 0 |
| ② 우회 | 5.5–6.4 (0.9) | 슬리퍼 눈알이 코기 코를 흘끔 본 뒤 왼쪽(표지판)으로 튼다. "…돌아서 가자" | S2a | 7장 S2a | M0에서 파생, 코기 영역만 패치 | 0 |
| ② 막음 | 6.4–7.5 (1.1) | 코기가 눈을 뜨고 슬리퍼를 보며 앞발을 왼쪽 길 위에 '척'. 슬리퍼 눈알이 앞발을 본다 | S2b | 7장 S2b | S2a에서 파생 | 0 |
| ② 현관 쪽 | 7.5–8.5 (1.0) | 코끝이 현관을 향하고 슬리퍼가 곧은 길로 돌아선다. 진행바 30→60% (자막 없음) | S2c | 7장 S2c | S2b에서 파생 | 0 |
| ③ 달리기 | 8.5–9.2 (0.7) | 슬리퍼가 코기 코앞을 서둘러 지난다. '타다닥', 배지 ③ "뛰자!" | V1 3.9–5.0, 1.5배속 | 8장 V1 (재사용) | V1 4번째 사용 | 0 |
| ③ 들킴 | 9.2–9.9 (0.7) | V3 0.0초 정지. 플레이 바우 자세, 혀를 내민 웃는 입, 꼬리 잔상. "들킴" 도장 + 경보 박스. 라벨 "코기 · 기상 · 꼬리 붕붕" | V3 0.0초 정지(= S3) | 7장 S3 / 8장 V3 | V3 | V3 2.5cr |
| ③ 오해 | 9.9–10.8 (0.9) | 슬리퍼 눈알이 휘둥그레져 왼쪽 표지판 쪽으로 튄다. '흠칫!'. CAM 2 인셋(두루 눈알 뒤집힘). BGM 정적 시작 | S3b + CAM2b | 7장 S3b, CAM2b | S3에서 파생 | 0 |
| **④ 반전** | **10.8–12.5 (1.7)** | 코기가 서서 달려 슬리퍼를 지나쳐 슬리퍼와 표지판 사이에서 급정지(비접촉). '끽!' → "어? 안 잡네?" → 고개를 현관 쪽으로 | V3 0.6–2.3 + 3단 마스크 | 8장 V3 | V3 | 0 |
| ④ 돌려 세움 | 12.5–13.5 (1.0) | 슬리퍼 두 짝이 코기 시선을 따라 현관 쪽으로 돌아 한 발 내딛는다. "…길 안내?", 진행바 90%. BGM 복귀 | S4a~c 정지 3장 (0.34/0.33/0.33) | 7장 S4a~c | V3 끝 프레임에서 파생 | 0 |
| 단서 | 13.5–14.9 (1.4) | 노이즈 바 + 시계 03:52:09 + "38분 후". 매트 위에 한 짝, 코기가 다른 한 짝에 턱을 '척'. 슬리퍼 눈알이 옆으로 흘긴다. "…수고비?" | N1 | 7장 N1 | V3 끝 프레임 참조 | 0 |
| 아침 a | 14.9–16.5 (1.6) | 같은 앵글, 아침 햇빛(컬러). 자막 "07:30 한 짝만 도착". 새소리 | M1 | 7장 M1 | M0과 같은 앵글 | 0 |
| 아침 b | 16.5–18.0 (1.5) | 1.8배 크롭. 코기가 털 슬리퍼에 턱을 파묻고 눈만 카메라로 굴린다 (털 결이 보이는 판매 컷, 문구 없음). 쓰읍 | M1→M1b 교차 | 7장 M1b | M1 | 0 |
| 아침 c | 18.0–19.4 (1.4) | 출근복 바짓단의 맨발이 매트 위 한 짝 앞에서 멈칫. 현관에 가방. 라벨 "집주인 · 07:31 출근", "…한 짝 어디?" | M2 | 7장 M2 | M1에서 파생 | 0 |
| 일지 a | 19.4–21.0 (1.6) | 결재 카드가 놓이고 두 줄 "결과: 1짝 정렬" / "1짝: 코기가 압수", 1.2초에 '승인' 도장 | M2 + dim 오버레이 | — | M2 | 0 |
| 일지 b | 21.0–22.5 (1.5) | 카드 유지, 도장 완성 상태, 0.3초에 손글씨 "수고비 인정" | M2 + dim 오버레이 | — | M2 | 0 |
| PPL | 22.5–28.0 (5.5) | "코기 몫까지, 한 켤레 더?" 상품명 원문·가격·확인일 10/10 (네이버 + 쿠팡 product_alt) | M1 배경 + 키트 | — | M1 | 0 |
| 끝 | 28.0–30.0 (2.0) | 광고 표시, AI 연출 고지, "영상 속 슬리퍼는 판매 상품과 외형이 다릅니다" | M1 배경 + 키트 | — | M1 | 0 |

- 상품 장점이 보이는 장면(CLAUDE.md 규칙): 상품 장점이 '작전'에 직접 대응하지는 않는 이야기다(콘셉트 v2.1의 남은 약점). 대신 털 질감과 앞막힘 형태가 크게 보이는 **판매 컷**을 두 번 둔다: 아침 b(1.8배 크롭, 1.5초)와 단서(N1 줌, 1.4초). 두 컷 모두 효능 문구는 없다. 장점 장면이 부족하다는 지적이 나오면 critic과 상의한다.
- 영상 속 슬리퍼는 **머스터드 옐로 짧은 털 플러시, 매끈한 표면, 둥근 앞막힘, 두꺼운 흰 밑창, 라벨·로고·골지 없음**이다. 판매 상품(회색·분홍 니트 골지, 사각 라벨)과 쿠팡 상품(브라운)과 모두 다르다.
- 글자 원칙: 효능 단어(따뜻·보온·포근·시림)와 '젖음'은 어디에도 쓰지 않는다. '층간소음방지'는 PPL 카드의 상품명 원문에만 있다.

## 7. 무료 이미지 15장 (웹, 0cr)
**생성 방법:** Higgsfield 웹, Seedream 4.5 또는 Nano Banana 2, **Unlimited 토글을 켠 상태로** 한 번에 1장씩. 결제창이 뜨면 그 모델은 미포함이므로 닫고 다른 모델로 바꾼다. 비율 9:16. CLI는 이미지에 쓰지 않는다(장당 2cr).
**레퍼런스 첨부:** 코기 `assets/clips/EP05/master.png`, 두루 `assets/clips/EP08/duru.png`. M0 이후 모든 컷은 M0 또는 직전 컷을 첨부한다.
**공통 문장(COMMON):** `Fixed ceiling-corner security camera, looking down about 40 degrees, fisheye distortion, vertical 9:16, grainy black-and-white infrared night footage with fine noise, soft even light.`
**공통 금지(NEG):** `No text, no letters, no numbers, no logos, no brand names, no labels, no watermark, no subtitles, no timestamp, no on-screen interface, no ghosts, no horror, no glowing eyes, no blood, no hands, no human faces.`
**슬리퍼 정의(SLIP):** `plush mustard-yellow short-pile faux-fur closed-toe slippers with a thick white sole, smooth fur surface, rounded toe, no knit, no ribbing, no pompom, no label, no logo`
**눈알(EYES):** `two small plastic googly-eye stickers on the toe cap of each slipper (white disc, black pupil)`

| ID | 사용 컷 | 프롬프트(영어) | 첨부 |
|---|---|---|---|
| **M0** (기준 컷, 먼저) | V1 시작 프레임 | `[COMMON] A narrow living-room wooden floor corridor runs from the bottom of the frame up to a raised front-door entrance at the top, with a gray entrance mat at the top and a door frame on its right. The same Pembroke Welsh corgi as the reference sleeps curled on its side on the floor right next to the door frame, head toward the corridor, relaxed, mouth slightly smiling, no teeth visible. Halfway up the left side of the corridor: a stainless-steel water bowl with a small puddle beside it and a small yellow A-frame caution sign, two finger-widths tall, completely blank with no markings. At the bottom of the corridor, two [SLIP] walk side by side, mid-step, with two tiny legs in gray trousers and small gray work boots visible under each slipper; the slippers have no eyes yet. The straight path from the slippers to the mat passes right in front of the corgi's nose. The top 15% of the frame is empty dark wall and ceiling, the bottom quarter is plain floor and rug edge. [NEG]` | EP05 master.png |
| S2a | ② 우회 | `Edit this exact CCTV image, keep the same camera angle, room and lighting. The two [SLIP] stand mid-corridor with [EYES], their pupils glancing sideways at the corgi's nose, bodies turning toward the lower-left path by the yellow caution sign, one tiny work boot lifted. The corgi has lifted its head and looks toward the slippers, eyes half open. Nothing else changes. [NEG]` | M0 |
| S2b | ② 막음 | `Edit this exact CCTV image from the previous frame. The corgi now looks straight at the slippers with both eyes wide open and calmly places one front paw down on the floor across the left path in front of the slippers, knowing and deliberate, not asleep, mouth slightly smiling. The slippers' googly eyes look at the paw. Slippers, sign, bowl and room unchanged. [NEG]` | S2a |
| S2c | ② 현관 쪽 | `Edit this exact CCTV image from the previous frame. The corgi lifts its nose and points it toward the front-door mat at the top; its paw is still on the left path. The two slippers have turned to face the straight path toward the door mat, their googly eyes looking up toward the door. Room unchanged. [NEG]` | S2b |
| S3 | ③ 들킴, V3 시작 | `Edit this exact CCTV image, same camera, room and lighting. The corgi is in a joyful play bow near the door frame: front legs lowered, rear end up, tail a blurred wag, tongue out, mouth in a big happy smile, head tilted, no teeth visible, clearly playful and not threatening. The two [SLIP] with [EYES] stand mid-corridor close to the left yellow caution sign, bodies leaning away from the corgi toward the sign. [NEG]` | S2c |
| S3b | ③ 오해 | `Edit this exact CCTV image from the previous frame. Same composition, but the slippers' googly eyes are huge and wide and stare at the corgi, the two slippers leaning hard away toward the yellow caution sign, one boot off the floor. The corgi is unchanged and still cheerful. [NEG]` | S3 |
| S4a | ④ 돌려 세움 1 | `Edit this exact CCTV image (the last frame of the corgi video clip). The corgi stands tall and still on four straight legs in the gap between the two [SLIP] and the yellow caution sign, head turned toward the front-door mat, not touching the slippers (a few centimeters gap). The slippers still face the corgi with googly eyes. [NEG]` | V3 마지막 프레임 캡처 |
| S4b | ④ 돌려 세움 2 | `Edit this exact CCTV image from S4a. Only the slippers change: both turn about 45 degrees toward the front-door mat, googly eyes looking at the door. Corgi unchanged. [NEG]` | S4a |
| S4c | ④ 돌려 세움 3 | `Edit this exact CCTV image from S4b. Only the slippers change: both now face the door mat fully, one step forward onto the straight path, googly eyes looking at the door. Corgi unchanged. [NEG]` | S4b |
| N1 | 단서 (밤 03:52) | `Edit this exact CCTV image, same camera, room and infrared look. Night. One [SLIP] sits neatly on the gray entrance mat. The corgi lies belly-down on the floor beside the mat; its chin rests on top of the second slipper (if the contact looks melted, place the chin one centimeter above it as if about to settle). The second slipper's googly eyes glance sideways toward the camera, unamused. Bowl and sign remain in the left corridor. [NEG]` | M0 |
| M1 | 아침 07:30 | `Edit this exact image into soft morning daylight, full color, same camera angle and framing. The corridor, mat, bowl and sign are the same. One mustard-yellow slipper sits neatly on the gray mat. The corgi lies on the floor beside the mat with its chin buried in the fur of the second mustard-yellow slipper, eyes closed, content. Slippers have no googly eyes and no tiny legs now. [NEG]` | N1 |
| M1b | 아침 눈 굴림 | `Edit this exact image: change only the corgi's eyes. Its eyes are open and rolled toward the camera, a knowing sideways glance; everything else identical, pixel for pixel. [NEG]` | M1 |
| M2 | 아침 c | `Edit this exact image. Add a person's single bare foot in the upper-left of the frame, with the hem of dark office trousers above the ankle, the foot stopping in mid-air just above the one mustard-yellow slipper on the mat, toes spread in surprise. A commuter bag sits by the front door. No face, no upper body. The corgi still has its chin on the other slipper. [NEG]` | M1 |
| CAM2a | 얼음 인셋 | `Black-and-white infrared security-camera close-up of a plain white toilet paper roll standing upright on a small wooden bedside table, no print and no brand on the roll, in the style of the reference roll character; two googly-eye stickers on the roll are huge and wide with tiny pupils, startled. 4:3. [NEG]` | EP08 duru.png |
| CAM2b | 오해 인셋 | `Same close-up of the same plain white toilet paper roll on the bedside table, but the two googly-eye stickers are rolled upward so only whites show, an exasperated eye-roll. 4:3. [NEG]` | CAM2a |

- 총 15장(M0, S2a~c, S3, S3b, S4a~c, N1, M1, M1b, M2, CAM2a, CAM2b), 재시도 포함 약 25장 이내, 모두 0cr.
- 정지 컷 S2a~c, S3b, S4a~c는 영상 실제 프레임 캡처로 대체될 수 있다. 영상 프레임과 바닥·조명이 달라 보이면 **코기 영역만 잘라 영상 프레임 위에 패치**한다(editor, 0cr).
- 슬리퍼 외형이 판매 상품과 닮아 보이면(골지·분홍·회색·사각 라벨) 재생성한다. 판정은 qa.
- 두루(CAM2a·CAM2b)는 EP08 duru.png의 휴지 외형을 따르되, 브랜드·인쇄가 없는 일반 휴지다.

## 8. 영상 3클립 (seedance_2_0_mini, 480p, 5초, 오디오 없음, 각 2.5cr)
**실행 전:** `higgsfield generate cost`(무료)로 비용 확인, `higgsfield account status`로 잔액 확인. 영수 님이 비용 지출을 승인한 뒤에만 생성한다. **이번 단계에서는 생성하지 않았다.**
명령 형태: `higgsfield generate create seedance_2_0_mini --prompt "..." --start_image <파일> --resolution 480p --generate_audio false --duration 5` (끝 프레임은 넣지 않는다).

| 클립 | 시작 프레임 | 쓰는 구간 | 프롬프트(영어) |
|---|---|---|---|
| **V1** (테스트, 먼저) | M0 | 0.0–5.0 (훅a·훅b·① 걷기 0–3.9, ③ 달리기 3.9–5.0을 1.5배속) | `Fixed ceiling security camera, the camera never moves, no zoom, no cut. Grainy black-and-white infrared night footage with noise. Two plush mustard-yellow closed-toe slippers, each carried by a tiny hidden worker beneath it, with only two short legs in gray trousers and tiny gray work boots visible under each slipper, walk side by side in small quick steps at a steady rhythm up the wooden corridor from the bottom of the frame toward the gray mat at the top, never stopping, passing close in front of the sleeping corgi's nose by the end of the five seconds. The slippers keep their exact shape, color, fur texture and size and only bob slightly with each step; the workers stay completely hidden. The corgi sleeps beside the door frame and does not move except slow breathing. The water bowl, puddle and yellow sign stay exactly in place. No hands, no arms, no faces, no people, no glowing eyes, no text, no logos, no large shadows.` |
| V2 | V1의 3.9초 프레임 캡처 | 0.5–1.1(돌아봄), 1.1초 정지(얼음) | `Fixed ceiling security camera, the camera never moves. Grainy black-and-white infrared night footage. The two slippers and their tiny legs hold perfectly still mid-step, exactly as in the first frame, and the room, bowl and sign do not change. Only the corgi moves: its ears snap upright, its eyes open, and its head lifts and turns sharply toward the slippers within the first 1.2 seconds, then it holds that gaze with a slightly smiling mouth, no teeth visible, body staying in place. No text, no logos, no glowing eyes.` |
| V3 | S3 | 0.0(들킴 정지), 0.6–2.3(반전) | `Fixed ceiling security camera, the camera never moves. Grainy black-and-white infrared night footage. The corgi rises out of its play bow into a tall standing posture and sprints on straight legs down the corridor, running past the two frozen slippers, and stops abruptly in the gap between the slippers and the yellow caution sign, a few centimeters before the slippers, never touching them, standing tall and not crouching. It faces the slippers for a moment, then turns its head toward the front-door mat at the top and holds that gaze. The two slippers with googly eyes stay frozen in place and do not move. Sign, bowl and room do not change. No text, no logos, no glowing eyes.` |
| 재생성 | — | 가장 약한 클립 1개 | 판정 후 결정 |

| 구분 | 크레딧 |
|---|---|
| 기본 (V1 + V2 + V3) | 7.5cr |
| 재생성 1회 포함 상한 | 10cr |

- **판정 순서:** V1 테스트 → creative가 0.5초·2초 프레임으로 판정(작업화 다리로 읽히는가, 슬리퍼 형태·털이 유지되는가, 코기가 가만히 있는가) → 합격이면 V2·V3. V1이 실패하면 스톱모션 대체로 돌리고 크레딧은 V3에 우선 쓴다.
- **V3 판정:** 앞질러 서는 경로가 보이는가, 선 자세인가, 3단 마스크 경계가 보이지 않는가. 합성이 안 되면 S4a~c 정지 교차로 간다(0cr).
- **0cr 최소안:** 영상 없이 정지 교차만으로도 이야기는 닫히지만 ④의 '앞질러 달림'이 약해진다.
- **한도 확인:** 상한 10cr은 critic이 승인한 범위다. 이 이상이 필요하면 감독(PD)에게 보고하고 생성하지 않는다.

## 9. 효과음·BGM
- BGM `bgm_sneaky.wav` 0.5. 정적: 4.5–4.8초(얼음), 9.9–12.5초(오해~반전). BGM 복귀는 돌려 세움 컷(12.5초)에 맞춤.
- 기존 파일로 대체한 항목(전용 음원 없음): 종이 착, 종종(발소리), 새소리, 끽, 쓰읍, 사각. 상세는 episode.json `_todo`.

## 10. 자체 점검
| 규칙 | 결과 |
|---|---|
| 총 29~32초 | 30.0초 |
| 반전 시작 12초 이내 | 10.8초 (들킴 9.2초) |
| 작전 컷 2.5초 이하 | 최대 1.7초. 일지도 1.6+1.5로 분할 |
| 0~1초 큰 동작 | V1 0프레임부터 걷기. 정지 화면 없음 |
| 영상 클립 최대 4개 | 3개, 세그먼트 9개로 재사용 |
| 효능 단정 자막 금지 | 자막·라벨·카드에 따뜻·보온·포근·시림 없음. '층간소음방지'는 상품명 원문에만 |
| 슬리퍼 외형 차이 | 머스터드 플러시·무라벨 vs 판매 상품(회색·분홍 니트 골지·사각 라벨) |
| 대가성 2종 | 설명란과 고정 댓글에 토씨 그대로 |
| 광고·AI 표시 | 첫 화면 "광고 · AI 상황극"(0–3초), 항상 하단 광고 문구, 끝 2.0초 고지 |
| 유령·공포 금지 | 눈알 스티커 소품과 동물만 |
| 두루 이스터에그 | CAM 2 목격자 2회 |
| 영수 님 몫 | 고른 이유 확정, 영상 비용 승인, 업로드 |

## 11. 불확실한 점 (critic·PD가 볼 곳)
1. 제목 후보 1의 "겨울 거실 바닥 차가울 때"가 효과 암시로 읽힐 수 있다(1장 경계).
2. 쿠팡 상품명이 일부만 캡처됐고 평점이 미확인이다. 업로드 전 원문 확인 필요.
3. 상품 장점이 이야기에서 직접 쓰이지 않는다. 판매 컷 2곳으로 보완했다.
4. episode.json의 `overlays` 등 신규 키는 editor 구현 전에는 렌더되지 않는다(`_todo` 참고).
5. 총 길이를 30.0초로 맞추면서 후반(아침~일지~PPL~끝)이 17.6초로 전체의 59%다. 이탈 우려가 있으면 critic이 지적하고, 아침 b나 끝 2.0초를 줄이는 쪽으로 조정한다.
