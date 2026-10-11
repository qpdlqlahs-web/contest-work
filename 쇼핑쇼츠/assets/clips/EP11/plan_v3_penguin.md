# EP11 기획 v3 「부모님 댁 거실, 남극 편입」 (2026-10-11, 형식 재정비 첫 편)

> 근거: reports/format_creative_1011.md 4장(원안 26.0초) + 커머스 권고(상품 태그 5.3초, 검색 CTA)
> + 무음 콜드 리드(이해 PASS, 병맛 7.5/10, 끝 카드 과밀 지적) 반영 → **24.3초**, 네이버 1상품.
> 이전 무궁화판(v2.1)은 중단. 영상 크레딧은 쓰지 않았고 버리는 건 무료 이미지뿐.

## 로그라인
새벽 3시, 부모님 댁 거실 바닥이 남극이 되어 펭귄 가족이 입주한다. 아침에 부모님은 "괜찮다"고 하고, 펭귄은 "안 괜찮음".
- 15초 콜드 리드 결과: "부모님 댁 홈캠에 펭귄이 와서 사는데, 아빠 엄마는 '괜찮다'면서 그냥 지나다니는 영상"
- 끝 콜드 리드 결과: "바닥 시린 부모님 댁에 사 드리라고 만 원짜리 털 거실화를 파는 광고"

## 컷 표 (episode.json과 1:1)
| 컷 | 초 | 화면 | 자막(한 번에 1줄) | 소스 |
|---|---|---|---|---|
| 훅 | 0.0–2.8 | 흑백 적외선 거실, 0프레임부터 황제펭귄 1마리가 뒤뚱뒤뚱 가로지름, 감지 박스 | 부모님 댁 거실 홈캠 | V1 |
| 1단 | 2.8–5.3 | 바닥 서리 + 펭귄 발자국, 천천히 줌 | 바닥 온도: 남극 | F1 |
| 2단 | 5.3–7.8 | 소파 밑에서 펭귄 4마리 줄지어 등장 (좌상단 태그 "광고 · 털 거실화 10,900원" 시작) | 가족 단위로 입주 중 | V2 0–2.5 |
| 3단 | 7.8–10.3 | TV 앞 허들링 → 거실 한가운데 무지 흰 깃발 '퍽' | 거실, 남극 편입 완료 | V2 2.5–4.1 + F2 |
| 점프 | 10.3–11.3 | 노이즈 바, 시계 07:02, 컬러 | 아침 7시 | M0 |
| 펀치1 | 11.3–13.8 | 양말 세 겹 아빠 발이 펭귄 사이를 태연히 지나감(0.4초 교차 스톱모션) | 아버지: "괜찮다." | M1a·M1b |
| 펀치2 | 13.8–16.0 | 엄마 발이 방석 징검다리를 건넘 | 어머니: "나도 괜찮다." | M2a·M2b |
| 버튼 | 16.0–18.8 | 펭귄 5마리가 동시에 고개를 홱 돌려 카메라를 무표정 응시 | 펭귄: "안 괜찮음." (0.9초) | V3 |
| 카드 | 18.8–24.3 | V3 끝 프레임 어둡게 + 카드: 양말 세 겹 신는 부모님께 / 송강 겨울 쿠션 털 거실화 / 10,900원 / 리뷰 81 ★4.86 / 앞막힘형 · 털 안감 / ※ 펭귄 퇴거: 보장 안 함 / 네이버에서 '송강 털 거실화' 검색 | — | V3 정지 |

## 생성 목록 (영수 님 PC 크롬에서, 크레딧 순서 준수)
이미지 8장은 웹 Nano Banana 2 또는 Seedream 4.5 + Unlimited(0cr), 9:16. 영상 3개는 CLI `seedance_2_0_mini --resolution 480p --generate_audio false --duration 5`(개당 2.5cr, 합계 7.5cr, 재생성 포함 최대 10cr). **V1 테스트 1개를 먼저 하고 판정 후 V2·V3. 영상 생성 전 영수 님 승인.**

공통 금지(모든 프롬프트 끝): `No text, no letters, no numbers, no logos, no watermark, no on-screen interface, no camera or camera dome visible, no slippers, no shoes, no cartoon penguins, no glowing eyes, no ghosts, no horror, no people falling or slipping.`

| ID | 용도 | 프롬프트 |
|---|---|---|
| N0 | 기준 컷, V1 시작 | `Vertical 9:16 photorealistic still from a fixed ceiling-corner home security camera at 3 AM, looking down about 40 degrees, wide fisheye, black-and-white infrared night vision, soft noise, bright center and darker edges. A modest Korean apartment living room of an older couple: a low fabric sofa, a TV cabinet, a framed photo silhouette on the wall, glossy vinyl floor. One real adult emperor penguin, about as tall as the sofa back, waddles across the floor from the lower right toward the center, calm, expressionless. Top 15% and bottom 25% of the frame are empty floor and wall. No people, no hands.` |
| F1 | 1단 | `Edit this exact image, same camera and infrared look. Thin white frost covers the vinyl floor in the center, with a trail of penguin footprints pressed into the frost. The penguin is out of frame. Completely black-and-white.` |
| F2 | 3단b | (V2 끝 프레임 캡처를 레퍼런스로) `Edit this exact frame. A plain white flag with no markings on a thin pole is planted upright in the middle of the living-room floor. Penguins unchanged. Completely black-and-white.` |
| M0 | 점프·펀치 배경, V3 시작 | (F2 레퍼런스) `Edit this exact image into soft morning daylight, full color, same camera angle and framing. Five real emperor penguins huddle tightly in front of the TV cabinet, the white flag still in the middle of the floor. No people.` |
| M1a / M1b | 펀치1 | (M0 레퍼런스) `Edit this exact image. Add one adult's feet and lower legs in gray sweatpants walking from the top of the frame between the penguins, the feet wearing three visibly layered socks (fuzzy sleep socks under thick hiking socks, a toe-sock tip sticking out), calm casual stride. No face, no upper body, no hands. Penguins unchanged.` b는 같은 프롬프트로 다음 걸음(발 위치만 앞으로). |
| M2a / M2b | 펀치2 | (M0 레퍼런스) `Edit this exact image. Square floor cushions are laid on the floor like stepping stones; one adult's feet in fuzzy sleep socks covered by an extra pair of thick hiking socks step from cushion to cushion. No face, no upper body. Penguins unchanged.` b는 다음 방석으로 한 걸음. |
| V1 | 훅 (N0 시작) | `The camera never moves. The penguin waddles steadily from the lower right to the center of the living-room floor in small realistic steps, flippers slightly out, then stops and tilts its head. Nothing else moves. No text, no glowing eyes.` |
| V2 | 2단·3단 (V1 끝 프레임 시작) | `The camera never moves. From the dark gap under the sofa, four more real emperor penguins waddle out one after another in a line and join the first one, then all five press tightly together in a huddle in front of the TV cabinet, slowly shuffling. No text, no glowing eyes.` |
| V3 | 버튼 (M0 시작) | `Soft morning daylight, full color, the camera never moves. Five emperor penguins huddle in front of the TV cabinet; at the same moment all five snap their heads toward the camera and hold a blank, unimpressed stare, only tiny breathing movement. No people, no text.` |

- 같은 컷은 최대 2회. 영상 시작 프레임으로 넣는 야간 이미지는 흑백 변환본을 쓴다.
- 판정 기준: 펭귄이 실사·무표정(귀여운 카툰 아님), 화면 어디에도 슬리퍼·실내화 없음, 사람 얼굴·손 없음, 하단 25%는 바닥만(자막 자리).

## 영수 님이 정할 것
1. V1 테스트 2.5cr(이미지 판정 뒤), 전체 최대 10cr 승인
2. '고른 이유' 한 줄 확정 (초안: plan.md 3장)
3. 쿠팡 병행 여부: 이번 편은 끝 카드를 단순하게 하려고 네이버 1상품만 넣었다(쿠팡 정보는 episode.json `_coupang_backup`에 보관)
