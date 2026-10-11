## [critic] concept_v1 — REVISE

검토 대상: `concept_v1.md`. 함께 읽은 자료는 `product.md`, `ref/naver_product.png`, 프로젝트 `CLAUDE.md`, `series_bible.md`(v6.1), `EP09/review.md`의 9화 교훈이다. 파일은 고치지 않았다.
EP10 폴더에 `plan.md`, `episode.json`이 아직 없다. 그래서 이번 검토는 콘셉트 단계 검토이고, planner가 기획안을 쓰면 critic 검토를 한 번 더 한다.

### 판정 요약
방향(크루를 본 화면에 보여 줌, 모든 비트가 뽁뽁이 소리에서 나옴, 반전 '정보원이 제일 시끄러움')은 좋다. 그러나 다음 다섯 가지가 걸린다.
- 작전 컷이 2.5초를 넘는다.
- 반전 시작이 12.8초라 12초를 넘는다.
- 훅 자막과 창문 실루엣 연출이 공포 문법에 가깝다.
- 테스트 T1·T2를 고른 컷이 틀렸고, 가장 위험한 컷 C5의 이미지 대체안이 없다.
- 클립 7개·33cr는 프로젝트 기준(≤4개·≤12cr)의 약 3배라서 영수 님이 이 수치를 알고 승인해야 한다.

### 체크리스트

| 항목 | 판정 | 근거 |
|---|---|---|
| 훅: 0~1초 움직임 | PASS | 0프레임부터 '다리 달린 판'이 이동한다. 0초 감지 박스, 1.4초 줌도 좋다. |
| 훅: 첫 자막 | FAIL(경미) | "창문에 뭐가 기어감"은 괴담 문법이다(수정 4). "사람 3명…?"은 7자로 8~14자 규칙에 못 미친다. |
| 들킴 ≤12초 | PASS | 들킴 시작 10.4초. |
| 반전 ≤12초 | FAIL | 반전(#7) 시작이 12.8초다. 웃음 최고점 12.4초도 그 직전이다. 5화 성과(12초 안쪽 권고)와 어긋난다(수정 1). |
| 총 길이 28~32초 | PASS | 30.4초. |
| 작전 컷 ≤2.5초 | FAIL | #2 2.4초(통과)이지만 #3 2.6초, #4 2.8초다. 같은 이유로 #2도 느슨하다(수정 1). |
| 중간 지루함 | 조건부 | 작전 ①(판 세우기)은 개그가 없는 이동 컷이라 가장 약하다. 같은 소리(뽁) 개그는 ③→들킴→늦은 뽁→철퍼덕으로 변주되어 좋다. |
| 상품이 개그 중심 | PASS(조건부) | 운반·발소리·고양이 침대·문진·빛무늬가 모두 뽁뽁이다. 단, 화면 상품이 일부러 민트색·큰 기포라서 상품 사진과 연결되는 건 PPL 카드와 클립 스티커뿐이다(수정 8). |
| PPL 카드 판매처 정보 일치 | 조건부 | 네이버(6,180원, 리뷰 1,598, ★4.94, 33cm×10m)는 캡처와 일치한다. 1m당 618원도 계산이 맞다. 쿠팡은 상품 미확인이라 일치 여부를 판정할 수 없다(수정 9). |
| 톤: 병맛·두루·이전 화와 중복 | 조건부 | 고양이·구조(작전 3연타→들킴→반전→뭉치→일지→아침)가 9화와 같다. 장소(거실 창)와 반전(고양이가 가장 시끄러움)은 다르다. 연속 3편째는 피로하다. 두루는 이번 화에 없다(시리즈 '두루 등장' 항목은 이 시리즈에서 해당 없음으로 본다). |
| 공포·실제 상황 암시 | FAIL(경미) | 밤 창문 + 역광 어두운 형체는 공포 문법이다. 콘셉트 문서도 인정한다. 완화책은 방향이 맞지만 훅 자막이 이를 도로 깎는다(수정 4). |
| 효능 단정 금지 | 조건부 | 영상 안에는 온도·난방비 표현이 없어 좋다. 다만 PPL 줄 "단열 효과: 상품 페이지 참고"는 효과가 있다고 전제하는 문장이다(수정 5). 제목의 "6천원짜리 창문 단열"은 용도 서술이라 허용하지만 가격은 변동값이다(수정 6). |
| 대가성 문구 2종 / AI 표기 | PASS | AI 상황극 라벨 0~3초, AI 연출 상시, PPL 최하단 고지, 제목·설명란·고정 댓글·썸네일에 넣는 계획이 있다. 대가성 문구 원문과 '유료 프로모션·합성 콘텐츠 체크'는 plan.md에 명시해야 한다. |
| 상품 외형 차별·로고 | PASS | 색·기포·형태·포장 네 축으로 차별한다. 'AIR CAP' 글자, 박스, 롤을 금지한다. 판매 상품 사진을 레퍼런스로 넣지 않는다. 밤 흑백에서 색 축이 사라지는 점도 스스로 짚었다. |
| 비용: 클립 ≤4개 | FAIL(의도적 예외) | 7개다. 영수 님 지시(이미지스럽지 않게·크루 보이게)에 따른 것이므로 승인 사항이다. |
| 비용: 예상 ≤12cr | FAIL(의도적 예외) | 권장 41cr(예상 33cr)은 기준의 약 3배, 9화(약 15cr)의 2.2배다. 크레딧 규율(821cr 초과 지출 교훈)상 영수 님이 수치를 보고 승인하기 전에는 생성하지 않는다. 문서도 그렇게 적어 놓았다. 재사용 계획(C1 PPL 배경, C5 슬로 리플레이)은 있다. |
| SEO/AEO | 조건부 | 제목 앞부분 검색어가 약하다(수정 6). AEO 첫 줄 사실 문장은 아직 없다(plan.md 단계에서 확인). |
| 9화 교훈 | 부분 PASS | 아래 별도 표. |

### 9화 교훈 반영 점검
| 교훈 | 판정 | 근거 |
|---|---|---|
| AI 변형(판이 휘고 녹음) | 부분 | 판은 강체로 지시했지만 C1이 '운반 + 기울여 세우기'를 한 클립에 넣어 가장 변형되기 쉽다. 진짜 뽁뽁이는 휘는 재질이라 모델이 두꺼운 판자로 그릴 위험도 있다. |
| 눈 발광 | 부분 | `eyes stay closed` 부정 프롬프트에만 의존한다. 고개를 드는 동작(C4)에서는 모델이 눈을 뜨게 그리기 쉽다. 고양이를 옆·뒷모습으로 잡는 구도가 더 안전하다(수정 3). |
| 실·끈 막대화 | PASS(경미) | 매다는 줄은 없다. 반장 호루라기 줄과 방울·리본이 130px 크기에서 막대로 변할 수 있으니 T1에서 같이 본다. |
| 2.5초 안에 끝나는 동작 | FAIL | 문서 본문은 "C1은 2.5초 안에 끝냄"이라 했지만 콘티는 C1 0.2~4.0초(3.8초) 전부를 쓴다. C3 설계도 '4걸음 + 멈칫 + 고양이 보기 + 까치발 + 또 뽁'으로 2.5초 동작이 아니다. |
| 클립당 큰 동작 주체 1명 | 부분 FAIL | C1(판 + 크루 3 + 반장 유도 + 뭉치)과 C2(여사 매달림 + 물 퍼프 + 콩알이 엉덩방아 + 반장 묵념)가 사실상 주체 여럿이다. |

### 수정 요청(번호 목록)

**1. 컷 시간 재배분(필수).** 작전 컷을 모두 2.5초 이하로 줄이고, 반전 시작을 12초 안쪽으로 당긴다.
- 훅 #1: C1 0.2~2.6 (2.4초).
- 작전 ① #2: C1 2.8~4.0 + C2 0.3~1.1 (2.0초). 가장 약한 컷이니 가장 짧게.
- 작전 ② #3: C2 1.5~4.0 (2.5초). 현재 2.6초 표시인데 원본은 2.5초라 길이도 안 맞는다.
- 작전 ③ #4: C3 0.2~2.7 (2.5초).
- 들킴 #5: 1.4초, 늦은 뽁 #6: 1.0초.
- 결과: 들킴 시작 9.4초, 반전 시작 11.8초, 총 29.4초. 반전 이후는 그대로 두고 28~32초 안이다.

**2. C3·C1 동작 단순화(필수).**
- C3는 '직선 4걸음'만 요청한다. 멈칫은 편집의 0.2초 정지와 자막으로 만든다. "고양이 쪽을 봄 + 까치발"은 프롬프트에서 뺀다. 한 클립에서 모델이 못 따라올 연기다.
- C3는 4걸음인데 음향은 '7번째 뽁'에서 들킨다. 걸음 수와 뽁 수를 맞춘다. 편집에서 '뽁'을 걸음 외에 효과음으로 추가하거나 들킴 조건을 '네 번째 뽁'으로 바꾼다.
- C1은 '운반'과 '세우기'를 한 클립에 넣지 않는다. C1을 '운반(훅)' 전용으로 쓰고, 세우기는 ① 컷에서 정지 이미지 한 장 + 짧은 줌 + 효과음 '착'으로 처리한다. 이러면 판이 휘는 위험 구간이 사라지고 C1이 PPL 배경 루프로도 안전해진다.
- C2는 '분무기 레버 당김 + 물 퍼프 + 막내 엉덩방아' 세 가지로만 하고 반장 묵념은 뺀다(묵념은 #5 들킴 컷 쪽 이미지에서 해도 된다).

**3. 고양이 들킴 연출(필수).** '눈 감은 채 고개만 듦'은 들킴으로 읽히지 않고, 모델이 눈을 뜨기 쉽다.
- 고양이를 옆모습 또는 뒷모습으로 잡아 눈이 화면에 안 보이게 한다. 들킴은 '귀가 돌아 크루 쪽을 향함 + 고개 돌림'으로 만든다.
- 눈이 보이는 구도가 꼭 필요하면 `eyes stay closed`만 믿지 말고 T0 시작 프레임에서 눈 상태를 확인하고, T1 이후 클립도 0.5초 간격 시트로 눈 발광을 점검한다.

**4. 공포 방지 보강(필수).** 훅 자막을 코믹하게 바꾼다.
- "창문에 뭐가 기어감" → "뽁뽁이가 걸어간다"(9자).
- "사람 3명…?" → "사람 3명 추정"(8자). 바이블 0장 6 판독관 말투에 맞는다.
- T0 판정에 한 가지를 추가한다. 소리 없이 썸네일 크기로 봐도 '코미디'로 읽혀야 한다(어두운 형체가 창가에 있는 그림으로 읽히면 FAIL). 반장의 안전모·반사띠가 가장 밝은 점으로 보이도록 한다.
- 실제 상황 암시 금지에 맞춰 제목의 "CCTV에 찍힌"은 "CCTV 속"으로 바꾼다. `#실제상황` 등 해시태그는 바이블 0장 9대로 금지한다.

**5. PPL 카드 문구 정정(필수).**
- "※ 단열 효과: 상품 페이지 참고"는 효과가 있음을 전제하므로 "※ 단열 효과: 이 영상에선 측정 안 함"으로 바꾼다. 연출 표현이라 CLAUDE.md의 '기분 탓' 계열과 같은 처리다.
- 고지는 EP09 critic이 요구한 문장을 쓴다: "영상 속 장면은 AI 연출이며 실제 제품의 성능과 다릅니다. 기능·사용법은 상품 페이지 확인". 현재 "AI 연출 · 실제 상품 시연 아님"만으로는 성능 오인 방지가 약하다.
- 카드의 상품명은 상품 페이지 상품명을 그대로 옮긴다. 지금 "국내산 두꺼운 뽁뽁이 에어캡 롤"은 원문(…포장용 에어캡 완충 롤 창문 단열 테포르 33cm-10m)에서 단어를 뺀 요약이다. 원문 전체는 업로드 직전 상품 페이지에서 복사한다(캡처는 말줄임으로 잘려 있다). 판매처 상호(CF매직)는 쓰지 않는다. 수수료율 5%도 쓰지 않는다(약관 8조 5호).
- "'뽁' 소리: 기본 포함" 줄은 유지해도 된다.

**6. 제목·SEO.**
- "[AI 상황극] 6천원짜리 창문 단열, …"은 가격이 틀어질 수 있다(정가 12,830원 대비 51% 표시가 수시로 변동). "6천원대"로 쓰고, 업로드 직전 가격을 재확인한다.
- 검색어를 앞에 둔다: `[AI 상황극] 창문 단열 뽁뽁이 6천원대, 새벽 3시 CCTV 속 공사팀`.
- AEO 첫 줄은 사실 문장으로 쓴다(예: "33cm × 10m 뽁뽁이 에어캡 롤은 네이버 기준 6,180원이다. (10/9 기준)"). 확정은 plan.md에서 한다.

**7. 테스트 설계 변경(필수).** T1은 C1(C1을 '운반 전용'으로 바꾼 뒤)로 유지한다. T2는 C3 대신 **C5**로 바꾼다.
- 이유: C3는 주체 1명의 직선 걷기라 쉬운 컷이다. 반면 웃음 최고점인 반전 C5(고양이 이동 + 눕기 + 크루 튀어 오름, 고양이 몸통 변형 위험)는 실패 확률이 가장 높고 대체안이 약하다. 안 되는 컷을 먼저 알아야 돈을 덜 쓴다.
- T0(무료)에 C5 시작 프레임도 추가한다. C2·C4는 T1 통과 후 만든다.
- C5 대체안이 비어 있다. 현재 'Kling 3.0 Turbo 1회(7.5cr)'뿐이고 그것도 실패하면 반전이 없다. 이미지 대체안을 미리 쓴다: 고양이 서 있는 이미지 → 누운 이미지 2장 교차 + 화면 흔들림 + '뽁뽁뽁뽁' 효과음 + 크루 통통은 이미지 위 오버레이 이동. 무료이고 웃음의 핵심은 소리와 자막이라 살아남는다.
- T1 판정 기준을 보강한다: "형태 지글거림(얼굴·손·호루라기 줄) 없음"과 "크루 3명이 머리 실루엣 3종으로 구분됨"을 추가한다. 통과 기준이 '3개 중 2개'라 약해서 ① '한 번 보고 사람으로 읽힘'은 필수 조건으로 올린다.
- T2 통과 기준의 "발밑 기포가 눌림"은 폐기한다. 130px 크기에서 기포 하나가 눌리는 것은 화면에서 안 보인다. 눌림은 효과음과 편집(발 닿는 순간 프레임 정지)으로 연출한다.

**8. 비용 재구성(권장).** 크루가 보이는 컷에만 크레딧을 쓴다.
- C6(뭉치 문진 시소)와 C7(인간 발 한 걸음)은 영상으로 바꿔도 영수 님 지시 ②(크루가 보여야)에 기여하지 않는다. 뭉치만, 발만 나온다. 이 두 컷은 문서의 기존 대체안(이미지 2~3장 교차 + 줌, 무료)으로 확정한다.
- C4(고양이 귀·고개, 크루는 굳음)와 C5(크루는 작게 튐)는 크루 형태 안정이 덜 중요하니 480p로 낮출 수 있다(각 2cr). 단, 720p 클립과 해상도가 섞이므로 후처리 노이즈로 통일하고, T1 결과를 보고 판단한다.
- C5는 3초 이후를 안 쓰므로 5초(5cr)가 아니라 4초로 뽑는다.
- 제안 예산: C1 4 + C2 4 + C3 4 + C4 2~4 + C5 2~4 = 기본 16~20cr, 예비 재생성 2회 × 4 = 8cr, 최대 약 24~28cr, 예상 실지출 약 20cr. 영수 님 '조금 더 써도'의 범위이고 41cr 안보다 영상 가치당 효율이 좋다. 최종 예산 선택은 영수 님이 한다.
- 720p 효과를 증명하는 비교가 없다. T1을 480p 2cr와 720p 4cr로 나란히 뽑아 보고 싶으면 +2cr로 가능하다. 생략하려면 '720p 효과는 가정'이라고 기록한다.

**9. 쿠팡 상품 확인(업로드 전 필수, 생성과는 무관).** 쿠팡 링크 상품명·가격·외형·리뷰가 네이버 상품과 같은지 PD가 확인한다. 다르면 episode.json의 `product_alt`로 분리해 PPL 카드에 두 상품을 각각 정확히 쓴다. 클립판은 네이버만 쓴다. 설명란·고정 댓글에는 대가성 문구 2종 모두 토씨 그대로 넣는다.

**10. 문서 정리(경미).**
- 맨 위 "상품 링크는 나중에 받는다"는 7장(10-09 확정)과 모순된다. 삭제하거나 정정한다.
- 바이블 0장을 EP10에서만 표로 대체한다고 했다. PD가 이 예외를 승인했다는 기록을 `review.md`나 `plan.md`에 남긴다. 승인 전에는 바이블 0장 1(본편 와이드에서 크루 비노출)과 충돌한다.
- 뽁뽁이 판 색·크기 지시는 유지한다. 단, 밤 흑백 컷에서 시판 상품과 혼동될 수 있는 투명 질감이 나오지 않도록 프롬프트의 큰 기포 문구를 모든 컷에 고정한다(문서에 이미 있음).
- 자체 점수 8.6은 후하다. 실현성 7.5도 C5·C1 위험을 고려하면 6.5~7.0이 적정이다. 수정 1~5·7 반영 후 재산정을 권한다.

### 통과 후 확인할 것(2차)
- 수정 1~5·7 반영 여부, 수정 8 예산에 대한 영수 님 선택.
- T0 시작 프레임 3장(C1·C3·C5) 판정 결과를 critic에게 공유하면 공포 판정(썸네일 크기, 소리 없이)을 다시 본다.
- plan.md·episode.json이 생기면 효능 단정 문구·대가성 문구·SEO 제목·AEO 첫 줄을 최종 점검한다.

### 한국어 요약
1. 판정은 REVISE다. 크루 본 화면 연출과 '정보원이 제일 시끄러움' 반전은 좋지만, 작전 컷이 2.6~2.8초로 길고 반전이 12.8초에 시작해 12초를 넘는다.
2. 훅 자막 "창문에 뭐가 기어감"과 PPL 줄 "단열 효과: 상품 페이지 참고"는 각각 공포 문법·효능 전제 위험이라 고쳐야 한다. 고양이 눈 감은 들킴 연출도 모델이 눈을 뜨게 그릴 위험이 크다.
3. 테스트는 쉬운 C3 대신 가장 위험한 반전 컷 C5로 바꾸고 C5 이미지 대체안을 쓰며, 영상 클립은 크루가 보이는 5개(약 20~28cr)로 줄이는 안을 영수 님께 제안한다.

---

## [critic] concept_v2 — PASS (이월 확인 사항 4건, 재검토 불필요)

검토 대상: `concept_v2.md`. v1 필수 수정 1~6의 반영 여부를 문서 대조로 확인했다. 예산 결정(C1~C5 720p, C6·C7 무료 이미지)은 감독 결정이므로 쟁점으로 올리지 않고 계산만 검산했다.

### 1. 필수 수정 1~6 해소 확인
| # | 요구 | 판정 | 확인 근거 |
|---|---|---|---|
| 1 | 컷 시간 재배분, 반전 ≤12초 | 해소 | 훅 2.4 / ① 2.0 / ② 2.5 / ③ 2.5 / 들킴 1.4 / 늦은 뽁 1.0이고 들킴 시작 9.4초, 반전 시작 11.8초다. 콘티 시간을 합산하면 29.4초로 맞다(PPL 종료 29.4). 작전 컷은 모두 2.5초 이하다. 원본 구간도 컷 길이와 일치한다(#1 C1 2.4, #2 C1 0.8 + 이미지 1.2, #3 C2 2.5, #4 C3 2.3 + 정지 0.2, #5 C4 1.4, #7 C5 2.8). |
| 2 | C1 운반 전용, C3 4걸음, 뽁 수 일치, C2 묵념 삭제 | 해소 | 세우기는 이미지 S1로 분리했다. C3는 직선 4걸음이고 뽁 4회와 4번째 뽁 들킴으로 맞췄다. 멈칫은 편집의 0.2초 정지다. C2에서 반장은 정지다. |
| 3 | 고양이 들킴 구도 | 해소 | 고양이를 전경 뒷모습으로 잡고 귀가 뒤로 돎 + 고개 회전으로 들킴을 연기한다. 눈은 구도로 차단하고, 프롬프트 접미어에 `the cat's face is never visible`를 넣었다. T0 판정 ④에도 있다. |
| 4 | 훅 자막, 제목, 공포 판정 | 해소 | "뽁뽁이가 걸어간다" → "사람 3명 추정"(8자), 제목 "CCTV 속", 실제 상황 해시태그 금지, T0 ⑤(썸네일 크기·무음에서 코미디로 읽힘)가 들어갔다. |
| 5 | PPL 카드 | 해소 | "단열 효과: 이 영상에선 측정 안 함", EP09 고지 문장, 상품명 원문 전체, 판매처·수수료율 미표기, 정가·할인율 미표기가 모두 반영됐다. 1m당 618원 = 6,180 ÷ 10 맞다. |
| 6 | 테스트 | 해소 | T2를 C5로 바꾸고 T0에 C5 시작 프레임을 넣었다. 기포 눌림 기준은 폐기했다. C5 이미지 대체안(R1→R2 교차, 흔들림, 연타, 크루 레이어 통통)이 확정됐다. T1은 '사람으로 읽힘'을 필수로 올렸다. |

권장 사항(제목 검색어 앞배치, 쿠팡 product_alt 처리, 맨 위 모순 문장 정정, 점수 재산정)도 반영됐다. 자체 점수 8.1은 수정 후로서 납득할 수준이다(실현성 6.5 자기 평가 포함).

### 2. 비용 검산
- 기본 20cr = 5클립 × 4cr 맞다. 최대 28cr = 20 + 예비 2회 × 4 맞다. 예상 24cr = 20 + 재생성 1회 4 맞다.
- 단가 4cr(mini 720p 4초)은 v1에서 조회한 값과 같다. 클립 5개는 프로젝트 기준(≤4개)을 넘고 예상 실지출 24cr는 기준(≤12cr)의 2배지만, 영수 님 지시에 따른 감독 결정이라 이월 사유로만 기록한다.
- "EP09 대비 약 1.6배"는 예상 24cr 기준(24 ÷ 15)으로 맞다. 기본 20cr 기준이면 약 1.3배다.
- 재생성 예비는 2회인데 T1·T2·C3가 각각 재생성 1회를 적어 두었다(최대 3회 해석 가능). 138행의 "28cr를 넘는 지출은 없다 / 예비 소진 시 PD 보고"로 상한은 보호된다. 단 선착순으로 소진되므로 집행 때 'C5 재생성을 우선 확보'하도록 순서를 정해 두면 좋다.

### 3. bible 0장 1 예외 — PD 승인 근거 기록
- 예외 내용: EP10에 한해 bible 0장 1('본편 와이드에서 크루 비노출')을 적용하지 않고 '역광 공사판'(concept_v2 1장)을 쓴다. 0장 9(허구 명시)와 10(시그니처 소리)은 그대로 지킨다.
- 근거: 감독(PD 메인)의 전달에 따르면 영수 님이 채팅에서 직접 "크루들 오히려 보여야 보는 맛이 있을 거 같지 않니"라고 지시했다(2026-10-09). concept_v1 머리말의 영수 님 지시 ②("크루가 보여야 보는 맛이 있다")와 같은 내용이다.
- 기록 한계: 이 인용문은 감독 전달 기준이며 critic이 원본 대화를 직접 확인하지 못했다. 영수 님의 승인 원문은 PD가 보관한다.
- 적용 범위: EP10 한정이다. 시리즈 전체로 확대할지는 EP10 성과를 본 뒤 PD가 정한다(concept_v1 0장 표의 방침과 같다).
- 이 기록으로 concept_v2 머리말의 조건("PD 승인을 `review.md`에 기록하기 전에는 기획을 확정하지 않는다")은 충족된 것으로 본다.

### 4. 이월 확인 사항 (차단 아님)
1. **C1 사용 구간 모순:** 3장은 "각 클립 사용 구간 0.2~3.0초, 3.3초 이후 미사용"이라 했는데 T1 판정(0.2~3.4초)과 #2(C1 2.6~3.4)는 3.4초까지 쓴다. 3.3초 이후는 변형 위험 구간이므로 #2의 C1 구간을 2.6~3.3(0.7초)으로 줄이고 이미지 S1을 1.3초로 늘리거나, 3.4초까지 쓴다는 예외를 문서에 적는다.
2. **PPL 카드 가독성:** 상품명 원문 전체(긴 이름) + 5줄이 6.0초에 들어간다. 타이포그래퍼가 폰 실측으로 글자 크기·줄 수를 확인한다. 길면 상품명을 2줄로 줄바꿈하되 단어는 빼지 않는다.
3. **C5 동작량:** 2.8초 안에 '일어남 → 내려옴 → 눕기' 3단계다. 9화 교훈(2.5초 이내 단일 동작)과 어긋나는 가장 큰 위험이며, T2가 정확히 이것을 검증한다. T2 필수 기준이 '0.2~3.0초 변형 없음'이므로 그대로 유지한다. 실패 시 이미지 대체안으로 간다.
4. **자막 "단열판 인양 완료":** 작업 완료 표현이라 효능 단정은 아니다. 다만 'bible의 작업은 일부만/반전으로 원상복구' 원칙을 따르려면 "단열판 인양 중"이 더 안전하다. 선택 사항이다.
- 업로드 전 게이트는 그대로다: 쿠팡 상품 확인(product_alt), 가격·상품명 원문 재확인, 대가성 문구 2종, 유료 프로모션·합성 콘텐츠 체크.
- 다음 critic 확인 시점: T0 시작 프레임 3장 결과(공포 판정), 그리고 plan.md·episode.json 작성 후 효능 문구·SEO 제목·AEO 첫 줄.

### 한국어 요약
1. PASS입니다. v1 필수 수정 1~6이 문서에서 모두 확인됐고(반전 11.8초, 총 29.4초, 작전 컷 ≤2.5초), 비용 20/28/24cr 계산도 맞습니다.
2. bible 0장 1 예외는 영수 님 채팅 지시(감독 전달)를 근거로 EP10 한정 승인으로 기록했습니다. C1 사용 구간(3.3초 이후)과 PPL 카드 가독성은 차단 없이 이월합니다.

## [PD] 예산 승인 (10/9)
- 영수 님 채팅 승인 "ㅇㅇ": EP10 영상 예산 최대 28cr (기본 20 = C1~C5 mini 720p 4초 ×4cr, 예비 재생성 2회). 상한 초과 금지.
- 순서: T0(무료) 크리에이티브 판정 PASS → T1(C1)·T2(C5) 8cr → 판정 → C2·C3·C4. 예비 재생성은 C5 우선.

## [artist] T0
- 생성: 웹 NB2(Unlimited 켬 확인, 9:16, 1장) 컷당 1회, 0cr. C1은 레퍼런스 없이, C5·C3는 C1을 레퍼런스로 넣었다(EP10 기준 컷 없음). 판매 상품 사진은 안 썼다. 저장: C1/C5/C3_start.png, _480, _T0.jpg (재시도 0회 사용)
- 역광 실루엣·밝기: 창이 고르게 밝고 크루는 어두운 실루엣, 반장 안전모·반사띠가 가장 밝다(3컷 공통). 단 C3 걷는 콩알이는 창 한가운데 크게 서서 '창가 형체'로 읽힐 소지가 있다.
- 크기 대비: C1·C5는 크루 키가 큰 기포 약 8~10개(지시 4개보다 큼), C3는 콩알이가 반장·여사보다 3배 커서 비율이 틀렸고 맨발이다. 고양이는 세 컷 모두 크게 전경이다.
- 고양이: C5만 뒷모습(귀·뒤통수, 뺨 가장자리만 보임). C1·C3는 옆얼굴(감은 눈)이 보인다 → ④ 미충족, 재생성 시 'back to camera' 강화 필요.
- 코미디 읽힘·공포: 썸네일(130px)에서 C5(반장 주먹·여사 쪼그림·콩알이 외다리 + 고양이 뒷모습)가 가장 코미디로 읽힌다. C1은 뽁뽁이 밑 다리가 읽히나 작고, C3는 창가 큰 형체가 가장 불안하다. 눈 발광·긴 그림자 없음. C5는 여사 분무기가 연보라로 일부 착색됨.


## [creative] T0 시작 프레임 판정 — 3컷 모두 재생성 (T1·T2 보류)
판정자: creative. C1_start.png, C5_start.png, C3_start.png 원본과 _T0.jpg(썸네일 크기)를 직접 봤다. 파일은 고치지 않았다.

### 공통 결함 (3컷 모두, 이번 판정의 핵심)
artist가 짚은 네 가지(크루 키 기포 8~10개, C3 콩알이 과대, 고양이 옆얼굴, 분무기 연보라)는 모두 맞다. 그러나 이 네 가지보다 근본적인 문제가 따로 있다.

1. **카메라가 천장 CCTV가 아니다.** 세 컷 모두 바닥에서 1m 안팎의 낮은 눈높이로 창을 정면으로 본다. 소실선이 화면 중간에 있고, 바닥이 화면 아래 절반뿐이다. 천장 모서리 40도 부감이 아니라 '방 안에서 찍은 사진'이다. CCTV 정체성도 깨지고, 아래 2번 문제를 만든다.
2. **크기가 전혀 안 읽힌다.** 고양이는 카메라 바로 앞 전경에 있고, 크루는 창가 원경에 있다. 둘이 다른 깊이에 있어서 크기 비교가 안 된다. 썸네일로 보면 '고양이 한 마리 + 창가에 서 있는 아이들(또는 보통 사람들)'로 읽힌다. 소인 시리즈의 전제가 화면에서 사라졌다. 특히 C3는 '창가에 선 큰 형체'라 공포 판정도 FAIL이다.
3. **CCTV 질감이 없다.** 깨끗한 흑백 사진이다. 노이즈, 저해상도, IR 핫스폿이 없어 '이미지스럽다'.
4. **뭉치가 니들펠트 인형이다.** 세 컷 모두 눈이 크고 매끈한 봉제 인형으로 읽힌다. EP09에서 나온 실패와 같다.
5. 기포가 너무 크다. 지름이 크루 몸통 폭에 가깝다(지시는 '크루 키 = 기포 4개'). 띠도 33cm 띠가 아니라 넓은 정사각 매트다.

좋은 점도 있다. 역광 실루엣은 의도대로 나왔고, 반장 안전모와 반사띠가 가장 밝다. 크루 의상과 머리 실루엣 3종(안전모, 리본 두건, 방울 비니)도 잘 읽힌다. C5의 얼음 포즈 셋(주먹, 쪼그림, 외다리)은 연기가 좋아 다음 생성의 포즈 기준으로 쓴다.

### 컷별 판정
| 컷 | 판정 | 이유 |
|---|---|---|
| C1 | **재생성** | 공통 1~5 외에 다음이 걸린다. ① 띠를 허리 높이로 들어 탁자처럼 보인다(지시는 머리 위로 이기). ② 띠 밑 다리가 3쌍인데 반장이 따로 서 있어 크루가 4명이다. ③ 고양이 옆얼굴(감은 눈)이 보인다 |
| C5 | **재생성** | 포즈와 고양이 뒷모습(앉은 뒷모습)은 가장 좋다. 그러나 공통 1·2 때문에 크기가 안 읽힌다. 또 고양이와 띠가 멀어서 콘티(일어나 → 띠 위에 철퍼덕)를 2.5초 안에 할 수 없다. 분무기 연보라 착색은 흑백 처리로 쉽게 지워지지만, 재생성하므로 프롬프트에서 막는다 |
| C3 | **재생성** | 콩알이가 다른 크루의 약 3배이고 맨발이다. 창 한가운데에 사람 크기로 서 있어 '창가의 형체'로 읽힌다(공포 FAIL). 고양이 옆얼굴도 보인다 |
- 편집 보정으로 살릴 수 있는 컷은 없다. 카메라 높이와 크기 관계는 크롭이나 색 보정으로 고칠 수 없다.
- **T1·T2(각 4cr)는 보류**한다. 이 시작 프레임으로 영상을 만들면 '보통 크기 사람들이 걷는 영상'이 나와 크레딧만 쓴다.

### 재생성 방법 (무료, 컷당 2회 상한)
**순서를 바꾼다. 먼저 빈 세트 기준 컷 P0을 1장 만든다.** 무료이고 컷 상한과는 별개다. 그다음 C1·C5·C3을 P0 편집으로 만든다. 프롬프트 첫머리는 "Edit this exact image, keep the same camera angle…"로 한다(CLAUDE.md의 검증된 레시피). 세 컷의 카메라가 같아지고, 영상 모델에도 같은 공간이 들어간다.

#### P0 기준 컷 (크루·고양이 없음, 웹 NB2 Unlimited, 9:16, 레퍼런스 없음)
```
Grainy low-resolution frame grab from a cheap home security camera mounted high in the ceiling corner of an apartment living room, about 2.3 meters up, looking steeply down at about 45 degrees through a wide fisheye lens with curved edges. Strictly black-and-white infrared night vision: bright infrared hotspot in the middle of the floor fading to dark corners, heavy sensor noise and grain, soft low-resolution detail, faint compression blockiness. The floor fills most of the frame. A wide floor-to-ceiling window occupies only the top third of the frame, glowing evenly pale gray from a streetlight outside, no shapes or figures behind the glass. On the floor in the middle of the frame, close to the window, lies one long narrow strip of very large-bubble plastic wrap, about four times as long as it is wide, flat, with no cardboard box and no roll. Right beside the strip, at the same distance from the camera, on the right, a round floor cushion. Next to the strip on the left lies one adult house slipper as a size reference. The bottom quarter of the frame is plain dark floor, the top edge is dark wall and a curtain rod. No people, no animals, no text, no letters, no numbers, no logos, no watermark, no timestamp, no large shadows on walls or curtains.
```
- 판정: ① 부감이 맞는지(바닥이 화면의 60% 이상, 창은 위 1/3) ② 띠와 방석, 슬리퍼가 같은 깊이에 있는지 ③ 노이즈 질감이 있는지.

#### 세 컷 공통 삽입 문구 (P0 편집 프롬프트 뒤에 붙인다)
```
Keep the exact camera angle, room, window, bubble strip, cushion, slipper, noise and lighting of the reference image. Scale is critical: each tiny person is about as tall as the cat's head and shorter than the adult house slipper lying next to them, about four bubbles tall; each bubble is about twice as wide as a person's head. The tiny people stand on or right beside the bubble strip, at the same distance from the camera as the cat, so their size can be compared directly. They wear work boots, nobody is barefoot, nobody looks at the camera, they are caught mid-action with real body weight, faces too small to make out. The cat is a dark gray tabby with white paws; it is seen from behind with its back to the camera and its head turned toward the window, no part of its face, eyes or whiskers is visible. The little lamb is a loose clump of real dust and lint fibers with wispy edges and two tiny black bead eyes that do not glow, wearing a tiny dark vest, not a plush toy, not felt, not a stuffed animal. Grainy black-and-white infrared security footage, everything monochrome, no color tint on any object. No people or figures behind or outside the window, no large shadows, no glowing eyes, no text, no letters, no logos, no cardboard box, no roll of bubble wrap.
```

#### C1 (운반, 훅)
```
Edit this exact image, keep the same camera angle. Three tiny workers carry the long bubble strip held flat high above their heads with raised arms, walking in single file along its length toward the window; only their legs and work boots show beneath the strip, exactly three pairs of legs, mid-stride, the front pair stepping, the back pair half-tripping. The little dust lamb rides on top of the strip in the middle, sitting. The cat sleeps curled on the cushion right beside the strip, back to the camera. [공통 삽입 문구]
```
#### C5 (반전 직전)
```
Edit this exact image, keep the same camera angle. The cat stands on the edge of the cushion right next to the bubble strip, seen from behind, one front paw lifted, about to step down onto the strip. At the far end of the strip, well away from the cat, the three tiny workers are frozen in stiff poses: the stocky foreman in the white hard hat and reflective X vest with one fist raised straight up, the plump woman in the polka-dot bow headscarf crouching and hugging a small plain gray spray bottle, the tall skinny young man in the pompom beanie standing on one leg. The little dust lamb sits by the window corner of the strip. [공통 삽입 문구]
```
#### C3 (지름길)
```
Edit this exact image, keep the same camera angle. The tall skinny young worker in the pompom beanie and gray coverall is mid-stride crossing the bubble strip in a straight line, tiptoeing, arms out for balance; he is only slightly taller than the other two workers, who wait at the near end of the strip, the foreman making an X with his arms. He is in the lower middle of the frame on the strip, not in front of the window glass. The cat sleeps curled on the cushion beside the strip, back to the camera. [공통 삽입 문구]
```
- 2회 안에 크기가 안 맞으면(크루가 고양이 머리의 2배를 넘음) 다음 순서로 간다.
  - 같은 프롬프트를 FLUX.2 Pro(무료)로 한 번 더 돌린다. EP09에서 FLUX가 스케일은 가장 잘 따랐다.
  - 그래도 실패하면 PD에게 보고한다. concept_v2의 Plan B(띠 밑 다리만 보이는 운반 구도)로 전 컷을 통일한다.

### 시작 프레임 GO 기준 (재생성본)
- ① 고양이 머리 ≥ 크루 키
- ② 슬리퍼 > 크루 키
- ③ 천장 부감(바닥이 화면의 60% 이상)
- ④ 고양이 얼굴과 눈이 안 보임
- ⑤ 썸네일 크기에서 코미디로 읽힘(창가에 큰 형체가 없음)
- ⑥ 뭉치가 솜먼지 질감
- ⑦ 노이즈 질감이 있음
- 이 중 ⑤가 미달이면 무조건 재생성한다. 나머지는 6개 이상이면 GO.

### 영상 프롬프트 최종 문안 (재생성본이 GO일 때만 사용)
설정은 두 컷 모두 같다. `seedance_2_0_mini --resolution 720p --duration 4 --aspect_ratio 9:16 --generate_audio false`, 시작 프레임만 넣고 끝 프레임은 넣지 않는다. 생성 전에 cost를 재조회한다(4cr 예상).

**T1 = C1**
```
Fixed ceiling security camera, the camera never moves, no zoom, no cut. Grainy black-and-white infrared night footage with noise. The long strip of large-bubble wrap, held flat above the heads of three tiny workers, walks steadily across the floor toward the bright window: only their legs and work boots show beneath it, stepping quickly in a busy uneven shuffle, the back pair stumbles once and catches up. The strip bobs slightly with their steps but stays flat and rigid; it never folds, bends, melts or changes shape. The little dust lamb rides on top, swaying with each step. All the movement happens in the first three seconds, then they keep walking at the same pace. The cat sleeps on its cushion with its back to the camera and only breathes slowly. Natural continuous walking with real weight, not stop-motion, not toys being moved. No people or shapes outside the window, no large shadows, no glowing eyes, the cat's face is never visible, no text, no logos.
```
**T2 = C5**
```
Fixed ceiling security camera, the camera never moves, no zoom, no cut. Grainy black-and-white infrared night footage with noise. The big tabby cat, seen from behind, steps lazily off its cushion onto the bubble strip right next to it and flops down heavily onto its side on the strip in one smooth motion, then lies still, stretched out; its head stays turned toward the window the whole time, its face, eyes and claws are never visible. The bubble strip jolts and wobbles under its weight. At the far end of the strip, well away from the cat, the three tiny workers hold their frozen stiff poses without moving their arms or legs and bounce slightly in place with each jolt. The whole action is finished within two and a half seconds, then everything holds still. The cat keeps its exact shape and size, natural feline weight, no morphing. No people or shapes outside the window, no large shadows, no glowing eyes, no text, no logos.
```
- 판정은 0.5초 간격 시트로 한다. T1: 사람으로 읽힘(필수), 띠가 변형되지 않음(필수), 다리 형태 지글거림 없음. T2: 고양이 몸통에 변형이 없음(0.2~3.0초), 얼굴·눈·발톱이 안 보임. 실패 시 대체안은 concept_v2 4장을 따른다.

### 한국어 요약
1. 세 컷 모두 재생성이다. 크루가 큰 것보다 더 근본적인 원인은 카메라가 천장 CCTV가 아니라 눈높이라는 점이다. 고양이(전경)와 크루(원경)가 다른 깊이에 있어 '고양이 + 창가의 보통 사람들'로 읽힌다. 특히 C3는 창가 형체로 읽혀 공포 판정도 FAIL이다.
2. 해결책: 먼저 빈 세트 기준 컷 P0(천장 부감, 띠·방석·슬리퍼를 같은 깊이에 배치)을 만든다. 그다음 세 컷을 P0 편집으로 다시 만들고, "크루 키 ≈ 고양이 머리, 슬리퍼보다 작음"처럼 같은 깊이의 물체와 비교해 크기를 지시한다. 고양이는 뒷모습, 뭉치는 솜먼지 질감으로 고정한다.
3. T1·T2(각 4cr)는 시작 프레임이 GO 기준(7개 중 6개 이상, 코미디 읽힘 필수)을 통과할 때까지 보류한다. 영상 프롬프트 최종 문안은 위에 확정해 두었다.

## [artist] T0 v2
- 생성: 웹 NB2 Unlimited, 0cr. P0(기준 컷) 1회 → C1 1회, C5 2회(1회차 인형풍, 중간 실패 작업 1건은 미집계), C3 2회. P0를 레퍼런스로 "Edit this exact image" 방식. FLUX 불필요. 1회차 보존: C5_start_v2_try1.png, C3_start_v2_try1.png. 파일: P0.png, C1/C5/C3_start_v2.png, _480, _T0v2.jpg
- ③ 천장 부감·⑦ 노이즈: P0 통과(바닥 약 65%, 창 위 1/3, 슬리퍼·띠·방석 같은 깊이, 그레인 있음). 세 컷 모두 유지.
- ①② 크기: C1 크루가 띠 밑 다리 3쌍으로 고양이 머리·슬리퍼보다 작다. C5 크루는 슬리퍼 절반 정도, 고양이 머리 이하. C3 콩알이는 슬리퍼와 비슷하거나 약간 큼(경계), 반장·여사는 작다.
- ④ 고양이: C5 뒷모습으로 창 쪽(얼굴·눈 안 보임). C1·C3는 방석에 웅크려 머리가 창 쪽이나 옆얼굴 일부가 작게 보인다(눈 감음).
- ⑤ 코미디/공포: 130px 썸네일에서 '방 안의 작은 사람들'로 읽히고 창가 큰 형체 없음. C1은 띠 밑 다리 행렬, C5는 주먹·쪼그림·외다리 포즈가 읽힌다.
- ⑥ 뭉치: 3컷 모두 솜먼지보다 봉제 인형에 가깝다(실패). 크루는 C1 다리·C5·C3 모두 실사 질감이나 C5 1회차는 3D 인형풍이라 폐기. 일부 얼굴이 작게 식별된다(C5 여사·콩알이).


## [creative] T0 v2 재판정 — C5·C3는 국소 편집으로 축소, C1은 재생성 1회, T1·T2는 아직 보류
판정자: creative. P0.png, C1/C5/C3_start_v2.png 원본(1536x2752, 1116x2000으로 보고 측정)과 _T0v2.jpg를 직접 봤다. 파일은 고치지 않았다.

### 좋아진 점
v1의 근본 결함(눈높이 카메라)이 해결됐다. P0 기준 컷은 천장 부감, 창이 위 1/3, 그레인, 띠·방석·슬리퍼가 같은 깊이로 세트 기준 컷으로 GO다. ③⑦⑤는 artist 판정에 동의한다. 화면 위 35~50% 띠에 사건이 모여 있고 아래는 빈 바닥이라, 자막 영역과 구도도 맞다.

### artist 판정과 다른 점: ①② 크기는 세 컷 모두 미달
같은 깊이의 물체로 실측했다(표시 해상도 기준 px).

| 컷 | 크루 키 | 고양이 머리 | 슬리퍼 길이 | 실제 크기 환산(고양이 머리 약 9cm 기준) |
|---|---|---|---|---|
| C5 | 반장 약 200 | 약 65 | 약 115 | 약 28cm (목표 8cm의 3.5배) |
| C3 | 반장 약 190, 콩알이 약 200 | 웅크린 고양이 몸 전체가 약 170 | 약 115 | 약 25~28cm. **크루가 웅크린 고양이보다 크다** |
| C1 | 무릎 아래 다리만 약 슬리퍼 길이 | 약 50 | 약 115 | 전신 환산 약 50cm 이상 |

- 고양이와 같은 깊이에 섰기 때문에 이제 크기가 '읽힌다'. 그런데 읽히는 크기가 '손가락 소인'이 아니라 '고양이만 한 인형'이다. 고양이 키에 가까운 사람은 인형이나 피규어로 읽힌다. EP09에서 실패한 바로 그 지점이다(C5 여사 얼굴이 3D 인형처럼 또렷한 것도 같은 원인이다).
- **뭉치(⑥)도 같은 원인이다.** 지금 뭉치는 슬리퍼만 하다(목표는 골프공 크기, 고양이 앞발 정도). 이 크기에서는 얼굴·눈·조끼가 크게 그려져 봉제 인형이 된다.

### 목표 크기 재설정 (EP10 한정 예외, PD 기록 필요)
- 손가락 크기(8cm)를 고집하면 천장 와이드에서 크루 키가 720p 기준 약 37px가 되어 몸 연기가 안 보인다. 영수 님 지시 ②(크루가 보여야)와 충돌한다.
- 그래서 EP10은 **'손바닥 크기' 약 13~15cm**로 정한다. 기준은 **고양이 머리의 1.5배, 슬리퍼 길이의 약 절반**, 화면에서 약 100px(720p에서 약 64px, x1.3 펀치인하면 약 83px)이다.
- 현재 결과의 약 **50% 축소**다. 이 크기면 크루는 '고양이보다 확실히 작은 사람'으로 읽히고, 얼굴은 몇 픽셀이라 피규어 단서가 사라지며, 몸짓은 보인다.
- 뭉치는 고양이 앞발 크기(현재의 약 30%)로 줄인다.
- bible의 '검지 길이'와 다르다. 이 예외를 review.md에 PD 결정으로 기록해야 한다. 프롬프트 문구 "about as tall as the cat's head"는 지켜지지 않았으므로, 측정 가능한 비율 문장으로 바꾼다.

### 컷별 판정
| 컷 | 판정 | 이유와 조치 |
|---|---|---|
| C5 | **편집 보정(무료, NB2 국소 편집 1회)** 후 GO 후보 | 구도, 고양이 뒷모습, 앞발 든 동작, 얼음 포즈 셋이 모두 좋다. 다시 그릴 이유가 없다. 크루와 뭉치만 줄이면 된다. 아래 '축소 편집' 문구로 C5_start_v2를 레퍼런스 겸 편집 대상으로 넣는다. 결과의 ①②⑥을 다시 재서 GO를 판정한다 |
| C3 | **편집 보정(무료, 같은 방식)** | 콩알이 과대와 맨발은 해결됐다. 크기 문제는 C5와 같다. 고양이는 웅크린 등과 정수리 쪽이라 얼굴이 사실상 안 보여 ④는 허용한다. T1·T2 뒤에 만드는 컷이라 급하지 않다 |
| C1 | **재생성(남은 1회)** | 크기 문제에 더해 **띠가 바닥에 깔려 있고 다리가 띠 앞에 떨어져 걷는다.** '몸 없는 다리 3쌍'으로 읽혀 기괴하고, 공포 쪽으로 기운다. 띠를 들어 올린 상태(바닥에 그림자, 다리가 띠 바로 밑)로 다시 그려야 하는데, 이는 국소 편집으로 고치기 어려운 구조 문제다. 고양이 옆얼굴은 작고 눈을 감고 있어 허용한다 |

- 재생성 횟수 운영: '국소 편집(축소)'은 구도를 새로 뽑는 재생성이 아니라 보정 작업으로 보고, 컷당 1회만 쓴다. 무료다. 이 판단이 맞는지는 PD가 확정한다.

#### 축소 편집 문구 (C5·C3 공통, 웹 NB2 Unlimited, 대상 이미지 1장만 레퍼런스)
```
Edit this exact image. Keep everything exactly the same: camera angle, room, window, carpet, bubble strip, slipper, cushion, the cat and its pose, lighting, grain and noise. Change only the size of the three tiny workers and the little lamb: shrink each worker to about half of their current height, keeping their exact poses, clothes and positions on the strip (their feet stay where they are now). After the change, each worker is about one and a half times the height of the cat's head and about half the length of the slipper. Replace the lamb with a much smaller loose clump of grey dust and lint, about the size of the cat's front paw, fuzzy wispy edges, two tiny black dots for eyes, a thin dark vest strap, not a plush toy, not felt, no big eyes, no smooth face. Their faces become too small to make out. Add small soft contact shadows under their boots. Grainy black-and-white infrared security footage. No text, no logos, no glowing eyes.
```

#### C1 재생성 문구 (P0 레퍼런스 편집, 마지막 1회)
```
Edit this exact image, keep the same camera angle, room, window, bubble strip position, slipper and cushion. The long bubble strip is now lifted off the carpet and carried horizontally at a small height above the floor, casting a soft rectangular shadow on the carpet directly beneath it. Three tiny workers walk underneath it in single file, holding it up over their heads with raised arms: their heads and arms are hidden under the strip, and only their lower legs and work boots stick out below its edge, exactly three pairs of legs, all directly under the strip inside its shadow, mid-stride, the back pair half-tripping. The legs are short: each pair of legs is shorter than the width of the slipper, each worker would be about one and a half times the height of the cat's head. A small loose clump of grey dust and lint about the size of the cat's front paw, with a thin dark vest strap, sits on top of the strip in the middle, not a plush toy. The cat sleeps curled on the cushion right beside the strip, back to the camera. Grainy black-and-white infrared security footage, monochrome. No legs outside the strip's shadow, no disembodied legs, no people or figures outside the window, no large shadows on walls, no glowing eyes, no text, no logos.
```
- C1이 이번에도 '들린 띠 + 그 밑의 짧은 다리'가 안 되면 대안이 있다. 훅을 **C5 계열 구도의 '띠 끝을 셋이 잡고 끌고 가는' 운반**으로 바꾼다(띠는 바닥에 깔린 채 앞쪽이 들림, 크루 전신 보임, 크기는 축소 편집 기준). 같은 P0 편집으로 무료이고, 0프레임 움직임과 개그('끙차' 끌기)는 유지된다. 이 경우 콘티 #1 자막을 "뽁뽁이가 끌려간다"로 바꾼다.

### 뭉치 질감 질문에 대한 답
- **블러·노이즈만으로는 안 된다.** 문제는 질감이 아니라 형태다. 큰 둥근 눈, 매끈한 얼굴, 슬리퍼만 한 몸이 '봉제 인형'의 정체성이다. 노이즈를 덮으면 '흐린 인형'이 될 뿐이다.
- 크롭도 해결책이 아니다. 뭉치가 사건 영역 안에 있어 잘라 낼 수 없다.
- **해결은 크기 축소 + 형태 교체**다. 위 축소 편집에 포함했다. 고양이 앞발 크기로 줄이면 얼굴 디테일이 몇 픽셀로 줄어든다. 그 위에 IR 노이즈를 더하면 '솜먼지 덩어리 + 까만 점 두 개'로 읽힌다. 남는 인형 느낌은 편집 노이즈와 약한 블러로 마무리할 수 있다.
- 무료 편집 1회로 안 되면 마지막 수단이 있다. 뭉치를 시작 프레임에서 빼고(국소 편집으로 제거), 편집 단계에서 EP09 뭉치 이미지를 작게 합성한다. 영상 속 움직임은 키트 흔들림으로 대신한다.

### T1·T2 생성 여부
- **지금은 생성하지 않는다(보류 유지).** 현재 프레임으로 4cr를 쓰면 '고양이만 한 인형들'이 움직이는 영상이 나온다. EP09 테스트 1·2와 같은 실패를 돈 주고 반복하게 된다.
- **해제 조건과 순서:**
  1. C5 축소 편집(무료) → ①②⑥을 재측정해 통과하면 **T2 즉시 생성(4cr)**.
  2. C1 재생성(무료, 마지막 1회) → 통과하면 **T1 즉시 생성(4cr)**. 실패하면 위 대안 구도(끌고 가기)로 무료 생성한 뒤 판정한다.
- 재측정 기준(실측 px, 같은 깊이):
  - 크루 키 ≤ 고양이 머리의 2배
  - 크루 키 ≤ 슬리퍼 길이의 0.7배
  - 뭉치 ≤ 고양이 앞발의 1.5배
  - 나머지 ③④⑤⑦은 유지
  - creative가 판정하고, artist는 측정값을 review.md에 남긴다.
- 영상 프롬프트는 확정 문안(앞의 「T0 시작 프레임 판정」)을 그대로 쓴다. 단 한 문장을 추가한다.
  - T1·T2 공통: `The tiny workers keep their small size the whole time; they do not grow.`
  - C1을 대안 구도(끌고 가기)로 바꾸면 T1 문안의 첫 동작 문장을 바꾼다: "three tiny workers drag the bubble strip by its front edge toward the window, leaning back with effort, the strip sliding flat along the carpet behind them"

### 한국어 요약
1. 카메라 문제는 해결됐다(P0 GO). 하지만 세 컷 모두 크루가 실측 약 25~50cm로 고양이만 해서 '손가락 소인'이 아니라 '고양이만 한 인형'으로 읽힌다. 뭉치가 인형 같은 것도 같은 원인이다(슬리퍼 크기).
2. C5·C3는 구도가 좋아 무료 국소 편집으로 크루를 50%, 뭉치를 고양이 앞발 크기로 줄인다. 블러·노이즈만으로는 뭉치를 못 고친다. C1은 '몸 없는 다리'로 보여 마지막 재생성 1회를 쓰고, 그래도 안 되면 '띠 끌고 가기' 구도로 바꾼다.
3. T1·T2(각 4cr)는 아직 보류다. 축소 결과가 실측 기준(크루 ≤ 고양이 머리 2배, ≤ 슬리퍼 0.7배)을 통과하는 즉시 T2부터 생성한다. EP10 크루 크기는 '손바닥 크기(약 14cm)'로 예외를 두고, PD 결정으로 기록해야 한다.

## [PD] 결정 (T0 v2 후)
- EP10 크루 크기 = 손바닥 크기(약 13~15cm) 예외 채택. 근거: 손가락 크기면 천장 와이드에서 ~37px로 몸 연기가 안 보여 영수 님 지시(크루가 보여야)와 충돌. EP10 한정, 성과 보고 시리즈 적용 결정.
- NB2 국소 편집(축소)은 '보정'으로 보고 컷당 1회 허용(재생성 횟수와 별도). 무료.
- 실측 판정은 creative가 함(만든 사람이 판정하지 않음). 통과 시에만 T1·T2 각 4cr.

## [artist] T0 v3 (중간 보고, 진행 중단)
- C5 축소 편집을 2회 시도했다(1회차 지시 그대로, 2회차 강화 문구). 두 번 다 크루 크기는 거의 안 줄었다(반장 약 200px 유지, 표시 해상도 기준). 뭉치만 '솜먼지 덩어리 + 까만 점'으로 바뀌었다 → C5_start_v3.png(뭉치 GO, 크루 크기 미달). 1회차 결과는 C5_start_v3_try1_noshrink.png. NB2는 사람 크기를 줄이는 편집을 따르지 않는다.
- 실측(C5_start_v3, 1116x2000 표시 기준 px): 반장 약 200, 고양이 머리 약 65, 슬리퍼 길이 약 115, 뭉치 약 90x60(고양이 앞발 약 40의 약 2배). 목표(크루 ≤ 고양이 머리 2배=130, ≤ 슬리퍼 0.7배=80) 미달.
- 합성(P0 배경 + 축소 크루) 시도: P0와 편집본의 밝기·그레인이 달라 자동 마스크가 안 되고, cv2/rembg가 없어 중단했다.
- **중단 사유:** 10/10부터 웹 NB2 화면에서 UNLIMITED 표시와 Unlimited 토글이 사라졌고 생성 버튼에 2크레딧 표시가 뜬다(모델 목록 검색에서 NB2의 UNLIMITED 배지 없음, Seedream 4.5·5.0 lite는 UNLIMITED 유지). 크레딧 0 조건 위반이라 C1 재생성과 C3 편집은 시작하지 않았다.
- 같은 계정의 다른 세션이 프롬프트 입력창을 공유해 내 입력이 덮이거나 상대 레퍼런스가 섞인다. 생성 직전마다 확인이 필요하다.

## [artist] T0 v3 (무료 모델 경로 결과)
- NB2는 10/10부터 유료(2cr)라 중단. 무료 UNLIMITED인 Seedream 4.5와 FLUX.2 Pro로 진행(생성 버튼에 크레딧 표시 없음 확인, 0cr). P0를 레퍼런스로 넣었다. 파일: _T0v3.jpg (C1_start_v3s, C5_start_v3, C5_start_v3s_try2, C5_start_v3f_try1 순).
- **C1_start_v3s.png (Seedream 1회, GO 후보):** 띠가 들려 있고 바닥에 사각 그림자, 그림자 안에 짧은 다리 3쌍, 띠 위 솜먼지, 방석 위 고양이 웅크림(옆얼굴 일부), 부감·그레인 유지. 실측(원본 1440x2560 px): 다리 한 쌍 높이 약 90, 슬리퍼 길이 약 150(비 0.6), 고양이 머리 약 60(비 약 1.5), 솜먼지 고양이 앞발 정도. 주의: 바닥에 창빛 같은 큰 밝은 사각형과 긴 그림자가 생겼다.
- **C5 (미달):** Seedream 2회(try1 만화풍, try2 인형풍+카메라 낮아짐), FLUX 1회(try1 크루가 슬리퍼의 약 1.3배, 고양이가 거대, 얼굴 이상). NB2 v3는 크루 크기 미줄임. 실측(표시 px): NB2 v3 크루 200/슬리퍼 115(1.7배), Seedream try1 크루 130/슬리퍼 110(1.2배), try2 크루 130/슬리퍼 100(1.3배), FLUX 크루 100/슬리퍼 75(1.3배, 고양이 머리 대비 1.8배). 어느 것도 '슬리퍼의 0.7배 이하'를 못 맞췄다.
- C3는 시도하지 않았다(C5와 같은 문제 예상). 요청하신 대로 여기서 멈춘다.


## [creative] T0 v3 판정 — C1 v3s 보정 후 GO(T1 진행 가능), C5는 '고양이만 생성 + 크루 후합성'
판정자: creative. C1_start_v3s.png 원본(1440x2560)을 직접 보고 밝기를 수치로 쟀다. 파일은 고치지 않았다.

### 1. C1_start_v3s — **편집 보정 1건 후 GO**
**좋은 점**
- v2의 '몸 없는 다리'가 해결됐다. 띠가 들려 있고, 다리 3쌍이 띠 바로 밑에 있으며, 띠 위에 솜먼지가 탔다.
- 뭉치가 처음으로 '먼지 덩어리'로 읽힌다(⑥ 통과).
- 보이는 다리가 슬리퍼의 0.6배라서, 몸이 가려진 이 구도에서는 '작은 것들이 띠를 이고 간다'로 읽힌다(①② 통과).
- 0프레임 훅 그림으로는 지금까지 나온 컷 중 가장 좋다.

**고양이 옆얼굴:** 웅크린 정수리 쪽이고 눈이 감긴 부분은 몇 픽셀이다. T1에서 고양이는 숨쉬기만 하므로 **허용**한다. 영상 시트에서 눈 뜸·발광이 보이면 그 프레임 이후는 쓰지 않는다.

**밝은 사각형과 긴 그림자: 보정 필수**
- 실측(원본 px, 휘도 0~255): 사각형 내부 평균 **209**로 창(225)과 거의 같다. 주변 카펫은 75~97이다.
- 화면에서 두 번째로 밝은 면이라 시선이 사건(띠·다리, y 1000~1400)보다 아래 빈 바닥으로 끌려간다.
- 그 위에 다리 그림자 3줄이 길게 뻗는다. bible 4장 공포 방지 '긴 그림자 금지'에 걸리고, 영상에서 그림자가 따라 움직이면 더 눈에 띈다.
- **크롭으로는 해결되지 않는다.** 사각형이 화면 가운데~아래에 넓게 걸쳐 있다.

**보정 지시 (editor, 무료, T1 생성 전)**
1. `C1_start_v3s.png` → `C1_start_v3s_fix.png`
   - 사각형 영역(원본 약 x 280~1170, y 1330~1900)의 휘도를 **평균 110~120**으로 낮춘다.
     - IR 핫스폿이 가운데에 있는 정도로, 띠 주변 카펫(97)보다 조금 밝게 둔다.
     - 마스크 경계는 80px 이상 페더로 처리해 사각형 모서리가 남지 않게 한다. 창빛 사각형이 아니라 둥근 핫스폿 그라디언트로 보이게 한다.
   - 다리 그림자 3줄은 지우지 않는다. 대비만 낮춰 **발에서 다리 높이의 약 1.5배까지만** 진하게 남기고, 그 너머는 카펫 톤으로 페이드한다. 띠의 사각 그림자(다리 바로 뒤)는 유지한다. 띠가 들려 있다는 증거다.
   - 노이즈: 보정 영역에 카펫 평평한 부분과 같은 그레인(표준편차 약 5~10)을 다시 얹어 매끈한 패치가 생기지 않게 한다.
2. 같은 마스크를 **T1 결과 영상의 전 프레임에도** 적용한다. 카메라가 고정이라 정적 마스크 하나로 된다. 모델이 사각형이나 그림자를 다시 진하게 그려도 편집에서 눌린다.
3. 판정(creative, 0.5배 썸네일): 가장 밝은 면이 창이고, 다음이 띠와 핫스폿이며, 시선이 띠·다리에 먼저 간다.

**T1 = C1 영상 프롬프트 최종본** (`seedance_2_0_mini --resolution 720p --duration 4 --aspect_ratio 9:16 --generate_audio false`, 시작 프레임 = `C1_start_v3s_fix.png`, 끝 프레임 없음, 생성 직전 cost 재조회)
```
Fixed ceiling security camera, the camera never moves, no zoom, no cut. Grainy black-and-white infrared night footage with noise, soft even light. The long strip of large-bubble wrap, held up above the floor by three tiny workers hidden underneath it, walks steadily to the left along the window, away from the sleeping cat: only their short legs and work boots show beneath it, stepping quickly in a busy uneven shuffle, the back pair stumbles once and catches up. The strip bobs slightly with their steps but stays flat and rigid; it never folds, bends, melts or changes shape. The small clump of grey dust on top sways with each step. The tiny workers keep their small size the whole time; they do not grow and their bodies stay hidden under the strip. All the movement happens in the first three seconds, then they keep walking at the same pace. The cat sleeps curled on its cushion and only breathes slowly; its face is never visible. Shadows stay short and faint. No people or shapes outside the window, no long shadows, no glowing eyes, no text, no logos.
```
- 방향을 '왼쪽(고양이 반대편), 창과 나란히'로 정했다. 띠가 창과 평행이라 '창 쪽으로'라고 쓰면 모델이 띠 방향을 비틀거나 고양이 쪽으로 걸을 수 있다. 콘티 #1('창으로 간다')은 자막과 의미가 같아 수정할 필요가 없다.
- T1 판정 기준(0.5초 시트):
  - 필수: 사람(살아 있는 것)으로 읽힘, 띠가 변형되지 않음, 다리가 띠 그림자 밖으로 나오거나 커지지 않음.
  - 추가: 다리 형태가 지글거리지 않음, 솜먼지 형태 유지, 고양이 눈이 보이지 않음.

### 2. C5 합성 — 방식 수정: **크루는 영상에 넣지 않고 후합성한다**
**판단:** 크루를 합성한 시작 프레임으로 Seedance i2v를 돌리면 위험이 크다.
- ① 모델은 시작 프레임 속 '사람 형상'을 자기 크기 감각대로 다시 그린다. 1~2초 안에 크루가 커지거나, 얼굴이 생기거나, 인형으로 바뀌기 쉽다. NB2·Seedream·FLUX 모두 이 크기를 거부했으니 영상 모델도 같은 성향일 가능성이 높다.
- ② 약 60px 크기 인물은 480·720p i2v에서 형태가 녹는 크기다.
- ③ 합성 경계(마스크 테두리)가 프레임마다 '헤엄치며' 오려 붙인 티가 오히려 커진다.
- ④ 고양이가 가까이서 큰 동작을 하면 모델이 크루와 고양이를 섞을 수 있다.

**대신 이렇게 한다.** C5는 크루가 '얼음' 상태로 거의 안 움직이는 컷이라 이 방법이 정확히 맞는다.
1. **T2 시작 프레임 = `C5_plate` + 고양이만**(방석 가장자리에 서서 앞발을 든 뒷모습). 크루와 뭉치는 없다.
   - 배경판에 고양이가 없으면 Seedream 무료로 고양이 포함 버전을 만든다.
   - 고양이가 눕는 자리는 띠의 오른쪽 절반으로 지정해, 크루를 올릴 왼쪽 끝을 비워 둔다.
2. T2 영상은 고양이의 '내려와 철퍼덕' 동작만 생성한다. 영상 프롬프트에서 크루 관련 문장을 빼고 다음으로 바꾼다.
   - `The left end of the strip stays empty; the cat lies down only on the right half of the strip.`
3. 크루 셋과 뭉치는 편집에서 **정지 레이어로 얹는다**.
   - 소스: `C5_start_v3`의 얼음 포즈 셋과 뭉치.
   - 철퍼덕 순간(뽁 연타)에 맞춰 키트로 '통통'을 준다. 각자 위아래 4~6px, 0.12초 주기, 셋의 위상을 엇갈리게 하고, 그림자는 움직이지 않는다.
   - 크루는 영상 모델을 거치지 않으므로 **커지거나 무너질 위험이 0**이다. 비용도 같다(4cr).
4. 같은 방식은 **C4(들킴: 고양이 귀·고개 + 크루 굳음)와 콘티 #6(늦은 뽁)**에도 쓴다. 크루가 굳어 있는 컷이기 때문이다.
   - C4 영상도 고양이만 생성하고, 크루는 반장 '삑' 순간에 '걷는 포즈 정지 → 얼음 포즈 정지'로 레이어를 교체한다(0.1초 프레임 드롭 연출).

**'오려 붙인 티'를 없애는 합성 기준 (editor 작업 → creative 판정)**
| 항목 | 기준 | 확인 방법 |
|---|---|---|
| 크기 | 크루 키 ≤ 고양이 머리 2배, ≤ 슬리퍼 0.7배(PD 지시 약 45%가 이 범위인지 실측해 맞춘다). 뭉치 ≤ 고양이 앞발 1.5배 | 같은 깊이 px 실측을 review.md에 기록 |
| 원근 | 소스(C5_start_v3)와 배경판의 카메라가 같은지 확인한다. 인물의 세로축은 화면 아래 중앙(카메라 바로 아래)에서 바깥으로 뻗는 방사선 방향으로 1~3도 기울인다(어안 부감에서 세운 물체가 기우는 방향) | 창틀 세로선 기울기와 비교 |
| 선명도 | 축소하면 배경보다 선명해진다. 축소 후 가우시안 0.6~1.0px로 배경판의 흐림에 맞춘다 | 200% 확대에서 크루 윤곽 선명도 = 띠 기포 윤곽 선명도 |
| 밝기·대비 | 흑점은 배경판에서 그 위치의 가장 어두운 그림자보다 어둡지 않게, 중간톤은 띠 주변 카펫 평균 ±15 이내로 맞춘다. **화면에서 가장 밝은 점은 반장 안전모와 반사띠**이되, 창(약 225)보다 밝지 않게 한다. 여사·콩알이는 중간 톤 | 휘도 히스토그램, 0.5배 썸네일 |
| IR 림 | 창 쪽(화면 위쪽) 윤곽에만 1~2px 밝은 테두리(+10~15 휘도). 카메라 쪽 면은 평평한 IR 정면광. 네 방향 모두 밝은 후광이 생기면 실패(오려 붙인 티의 1순위) | 200% 확대 |
| 접지 그림자 | 발마다 부드러운 타원 그림자를 넣는다: 불투명도 35~50%, 블러 4~6px, 폭은 발 간격의 1.3배. 발과 띠가 닿는 곳에 2~3px의 진한 접촉 그림자를 넣는다. 긴 그림자는 금지하고, 길이는 키의 0.3배 이하로 배경판의 빛 방향과 맞춘다 | 발이 떠 보이지 않는지 0.5배 썸네일로 확인 |
| 띠와의 접촉 | 부츠 밑의 기포 1~2개를 살짝 어둡게 해 눌린 느낌을 준다. 부츠가 기포 하이라이트 위에 '떠' 있으면 실패 | 200% 확대 |
| 테두리 | 마스크는 1px 안쪽으로 줄이고 1px 페더를 준다. 원래 배경색 테두리(밝은 띠 반사)를 제거한다. 후광·계단 현상 0 | 400% 확대 |
| 그레인 통일 | **합성 후 전체 프레임에** 같은 노이즈 레이어를 얹는다(카펫 평평한 부분 표준편차 약 5~10에 맞춘 휘도 노이즈, 매 프레임 새로 생성). 마지막에 전체를 JPEG q75 상당으로 재압축해 블록 질감을 통일한다. 크루만 따로 노이즈를 넣지 않는다 | 크루 위 그레인 크기 = 카펫 그레인 크기 |
| 동작 | 통통 튈 때 접지 그림자는 제자리에서 진하기만 바뀐다(뜰 때 옅어짐). 크루 몸은 형태 변화 없이 위치만 움직인다(얼음이라 맞음) | 0.5배속 재생 |
- 최종 판정은 '처음 보는 사람에게 썸네일과 1회 재생으로 보여 줘서, 합성 같다는 말이 안 나오면 통과'로 한다. creative가 판정하고 qa가 재확인한다.

### 3. 남은 문제 (PD 보고용): 크루가 '움직이는' 컷 C2·C3
- 후합성은 크루가 굳어 있는 컷에서만 통한다. 크루가 걷고 당기는 C2(분무기)와 C3(지름길)는 영상 모델이 크루를 직접 그려야 한다. 그런데 무료 모델 셋 다 이 크기를 거부했다.
- 선택지는 셋이다.
  - (a) C1처럼 '몸을 가리는 구도'로 다시 짠다. C3는 '띠 밑으로 기어가는 볼록 자국 + 발만 보임', C2는 '분무기 뒤에 숨은 몸 + 발과 방아쇠만 보임'으로 한다.
  - (b) 이 두 컷만 크루를 슬리퍼 크기 수준으로 허용한다. 화면 일관성이 깨져 비추천이다.
  - (c) 크루가 걷는 영상을 단색 배경에서 따로 생성하고 축소 합성한다. 마스킹 도구(rembg 등)가 없어 현재 불가능하다.
- **추천은 (a)다.** C1에서 '가려진 몸 + 보이는 다리'가 크기와 피규어 문제를 동시에 풀었다. 판독 확대가 아닌 '흔적 + 일부'라서 증거 화면의 장점도 되살아난다.
- T1 결과를 본 뒤 creative가 C2·C3 구도를 다시 쓰겠다. 영수 님 지시 ②(크루가 보여야)는 얼음 컷(C4·C5·#6)에서 크루 전신 합성으로 채운다.

### 한국어 요약
1. C1_start_v3s는 바닥의 밝은 사각형(휘도 209, 창과 비슷함)과 긴 다리 그림자만 고치면 GO다. 사각형을 110~120으로 낮추고 그림자를 짧게 줄이는 무료 보정 후 T1(4cr)을 생성하고, 같은 마스크를 영상에도 적용한다. 고양이 옆얼굴은 허용한다.
2. C5는 크루를 합성한 프레임으로 영상을 돌리면 크루가 커지거나 녹을 위험이 크다. 그래서 고양이만 있는 배경으로 T2를 생성하고, 굳어 있는 크루는 편집에서 정지 레이어로 얹어 '통통'만 준다(C4·늦은 뽁도 같은 방식). 합성 기준은 크기, 선명도, 밝기, 창 쪽 림, 접지 그림자, 전체 그레인 통일이다.
3. 남은 문제는 크루가 움직이는 C2·C3다. C1처럼 몸을 가리고 발·흔적만 보이는 구도로 다시 짤 것을 추천한다.

## [editor] C1 보정
- 파일: C1_start_v3s_fix.png, C1_fix_mask.png(페더 마스크), apply_c1_fix.py(이미지·mp4 모두 가능, 영상은 프레임마다 새 그레인), 비교 C1_fix_compare.jpg. 크레딧 0.
- 지시 영역(x280~1170, y1330~1900) 평균 휘도 193.4 -> 111.0, 그레인(고주파 표준편차) 핫스폿 7.3(원본 카펫 평평부 8.9, 목표 5~10 안). 둥근 IR 핫스폿(중심 725,1600, 가장 밝은 곳 약 132).
- 변경점: 창빛 사각형 전체를 덮으려고 마스크를 지시 영역보다 바깥으로 확장(x240~1200, y1300~1960, 페더 약 80px). 다리 그림자는 발(y1290)~1450까지 유지, 이후 카펫 톤으로 페이드. 띠 사각 그림자 유지. 남은 우려: 사각형 모서리의 아주 옅은 잔흔과 핫스폿 하단 약간 어두운 띠. creative 0.5배 썸네일 판정 필요.

## [creative] C1 보정 판정 — GO
- C1_start_v3s_fix(0.5배 비교 확인): 시선이 띠와 다리에 먼저 가고 사각형은 둥근 핫스폿으로 읽혀 GO. 모서리 잔흔과 다리 아래 그림자 띠는 썸네일에서 거의 안 보이며, T1 결과 영상에 같은 정적 마스크를 적용할 때 마무리한다. T1(4cr)은 확정 프롬프트로 생성한다.

## [artist] 배경판 + T1
- 배경판(Seedream 4.5 UNLIMITED, 크레딧 표시 없음, 0cr): C5_plate.png(2회차 중 2번째 결과, 어두운 노출, 고양이 뒷모습·앞발 듦, 띠 왼쪽 끝 비움), C3_plate.png(2회, 띠가 아래 가운데 가로로 위치, 고양이 뒷모습으로 웅크림, 고양이에 옅은 보라 기미 약간). 각 _480 포함, 비교 시트 _plates.jpg. 1회차: C5_plate_try1.png(과노출·흰 테두리), C3_plate_try1.png(띠가 좁고 길며 과노출).
- 공유 입력창: 같은 계정의 다른 세션이 입력창·모델을 덮어써서 내 생성물 구분에 시간이 걸렸다(작업 ID로 구분).
- **T1 미생성:** 비용은 `higgsfield generate cost`로 4 credits 확인, 잔액 926.5 credits(`account status`), 입력 C1_start_v3s_fix.png(1440x2560, 9:16 그대로), 프롬프트 t1_prompt.txt(creative 확정문). 그러나 `generate create` 실행이 권한 시스템(실거래 분류)에 거부되어 제출하지 못했다. 우회하지 않았다. 영상 파일·프레임 시트 없음.


## [creative] T1 판정 — 부분 사용(원본 0.0~1.7초), T2 진행, C2·C3 재설계
판정자: creative. T1.mp4(720x1280, 4.04초)를 0.4초 간격 11장, 1.7~2.1초 0.1초 간격 5장으로 직접 뽑아 봤다(`_t1/sheet.jpg`, `_t1/g.jpg`). C5_plate·C3_plate도 확인했다. 파일은 고치지 않았다.

### 1. T1 결과: **부분 사용 — 원본 0.0~1.7초**
| 기준 | 결과 |
|---|---|
| 필수: 살아 있는 것으로 읽힘 | **통과.** 띠 밑의 작은 다리 3쌍이 끊김 없이 종종걸음으로 왼쪽으로 간다. 뒤쪽 다리가 반 박자 늦는 엇박이 살아 있다. 0.5배 썸네일에서 '뽁뽁이가 걸어간다'가 0.3초 안에 읽힌다 |
| 필수: 띠 변형 없음 | **통과.** 4초 내내 평판을 유지하고 살짝 출렁이기만 한다 |
| 필수: 크루가 커지지 않음 | **통과.** 다리 크기가 처음부터 끝까지 같다. 허리와 몸통 일부가 띠 아래로 보이지만 얼굴은 안 보인다 |
| 다리 형태 지글거림 | 경미. 720p에서 무릎 아래가 프레임마다 약간 흐르지만 걷는 동작에 묻힌다 |
| 솜먼지 | 통과. 띠 위에서 흔들리며 형태를 유지한다 |
| 고양이 | 통과. 숨만 쉬고 얼굴과 눈은 안 보인다 |
| **결함: 슬리퍼** | **1.7초부터 맨 앞 다리가 슬리퍼를 밟고 지나간다. 2.0초 이후 슬리퍼가 다리와 섞여 찌그러지다가 3.2초 이후 사라진다(AI 물체 소실).** 그래서 1.7초 이후는 사용 금지다 |
| 그림자 | 시작 프레임 보정 덕분에 바닥 사각형은 약하다. 다리 그림자는 여전히 길다. 편집에서 정적 마스크로 눌러야 한다(확정 사항) |

**편집 지시 (콘티 v2 #1·#2 수정)**
- #1 훅(2.4초) = **T1 0.0~1.7초를 0.7배속**으로 늘인다(2.43초). CCTV 영상이라 0.7배는 '무거운 걸음'으로 보일 뿐 슬로모션으로 읽히지 않는다. 1.4초 펀치인(x1.3)은 그대로 둔다.
- #2 작전 ①(2.0초) = 이미지 S1 1.2초 앞에 붙일 T1 2.6~3.4초 구간이 금지 구간이 됐다.
  - **S1 정지(띠가 창에 세워짐) 2.0초 + 키트 흔들림 + '끙차·착'**으로 바꾼다.
  - S1은 Seedream 무료로 만든다. P0 편집, 띠가 창 아래 유리에 세워져 기대고, 크루는 띠 뒤에 가려 흐린 실루엣만 보이게 한다(아래 C2 시작 프레임과 같은 세트라 같이 만든다).
- PPL 배경 루프도 0.0~1.7초 구간을 쓴다.
- 교훈: 다음 컷부터 **크루가 지나가는 경로에 슬리퍼 등 소품을 두지 않는다.** 동선 위의 물체는 AI가 밟고 녹인다.

### 2. 다음 진행
#### T2 = C5(반전) — **생성 GO (4cr)**
- 시작 프레임 `C5_plate.png`를 판정했다: GO.
  - 고양이가 방석 가장자리에서 앞발을 든 뒷모습이고, 고개가 창 쪽이라 얼굴이 안 보인다.
  - 띠가 방석 바로 왼쪽에 있고, 슬리퍼는 띠 아래 왼쪽이라 고양이 동선 밖이다.
  - 부감과 그레인이 P0와 같다.
- 크루는 넣지 않는다. 띠 왼쪽 끝을 비워 두고 편집에서 얼음 크루를 얹는다(앞 판정의 합성 기준).
- 설정: `seedance_2_0_mini --resolution 720p --duration 4 --aspect_ratio 9:16 --generate_audio false`, 시작 프레임만, 생성 직전 cost 재조회.
```
Fixed ceiling security camera, the camera never moves, no zoom, no cut. Grainy black-and-white infrared night footage with noise, soft even light. The tabby cat, seen from behind, steps lazily down off its cushion to the left onto the bubble-wrap strip and flops down heavily onto its side on the right part of the strip in one smooth motion, then lies still, stretched out; its head stays turned toward the window the whole time, its face, eyes and claws are never visible. The bubble strip jolts and wobbles under its weight but stays flat on the floor. The left end of the strip stays empty. The slipper stays exactly where it is and nothing else moves. The whole action is finished within two and a half seconds, then everything holds still. The cat keeps its exact shape and size, natural feline weight, four legs, one tail, no morphing. No people, no shapes outside the window, no long shadows, no glowing eyes, no text, no logos.
```
- 판정(0.5초 시트):
  - 필수: 고양이 몸통·다리·꼬리 개수가 변하지 않음(0.2~3.0초), 얼굴·눈·발톱이 안 보임, 띠 왼쪽 끝에 크루를 얹을 빈 자리가 남음.
  - 추가: 띠가 출렁임(반동으로 읽힘), 슬리퍼 유지.
  - 실패하면 재생성 1회. 그래도 실패면 concept_v2 4장의 이미지 대체안(R1→R2 교차 + '뽁' 연타)으로 간다.

#### C3 재설계 — 「위장 복귀」 (C1 방식 재사용: 몸은 덮개 밑, 다리만)
- **아이디어:** 콩알이가 뽁뽁이 조각 하나를 머리 위에 이고 '위장'한 채 큰 띠 위를 까치발로 건넌다. 조각 밑으로 다리 한 쌍만 보이고, 한 걸음마다 '뽁'이 난다(4걸음 = 뽁 4회).
- C1에서 검증된 '덮개 + 다리' 방식이라 크기와 피규어 문제를 함께 피한다. 위장한 채 들킨다는 개그가 하나 더 생긴다.
- 자막: 배지 ③ + "위장 복귀 중" → "…뽁?"
- 들킴 연결(#5): 반장의 '삑'에 콩알이의 덮개 조각이 스르륵 미끄러져 떨어지고, 한 발 든 얼음 포즈가 드러난다. 편집에서 정지 레이어 2장을 교체하는 웃음 박자다.
- **시작 프레임** = `C3_plate.png` 편집(Seedream 무료).
  - 판 위치가 C4와 같아 장면이 이어진다.
  - 동선은 왼쪽으로, 슬리퍼를 피해 띠 위만 지난다.
```
Edit this exact image, keep the same camera angle, room, window, carpet, cushion, sleeping cat, slipper and the large bubble strip exactly as they are. On the large strip, slightly right of its middle, a small square piece of bubble wrap, about one quarter of the length of the strip, is held up flat just above the floor by one tiny worker hidden underneath it; only one pair of short legs in a gray coverall and small work boots shows below the small piece, caught mid-tiptoe, one boot lifted, the legs about as long as the cat's ear is tall. A tiny knit pompom pokes out from under the front edge of the small piece. The small piece casts a soft small shadow on the strip. Grainy black-and-white infrared security footage, monochrome. No other people, no full bodies, no faces, no long shadows, no glowing eyes, no text, no logos.
```
- **C3 영상** (같은 설정, 4cr):
```
Fixed ceiling security camera, the camera never moves, no zoom, no cut. Grainy black-and-white infrared night footage with noise, soft even light. The small piece of bubble wrap, held up by one tiny hidden worker, tiptoes to the left across the large bubble strip in exactly four careful steps, the short legs lifting high on each step and pausing slightly after the second step; the small piece bobs but stays flat and rigid. The worker stays hidden under the small piece and keeps the same small size the whole time; he does not grow. He stays on the strip and does not touch the slipper. All four steps happen within two and a half seconds. The cat sleeps curled on its cushion and does not move except slow breathing; its face is never visible. Shadows stay short and faint. No people or shapes outside the window, no long shadows, no glowing eyes, no text, no logos.
```
- 판정: 4걸음이 셀 수 있게 읽히고(편집에서 발 닿는 프레임에 '뽁'), 조각 형태를 유지하고, 다리가 커지지 않아야 한다. 경로 위에 물체가 없어야 한다.

#### C4(들킴) — 같은 판, 고양이만 생성
- 시작 프레임 = `C3_plate.png` 그대로(크루 없음). 얼음 크루와 덮개 조각은 편집 레이어로 얹는다.
```
Fixed ceiling security camera, the camera never moves, no zoom, no cut. Grainy black-and-white infrared night footage with noise. The curled sleeping tabby cat suddenly swivels both ears backward and lifts its head slightly, still facing the window, then freezes, alert; its face, eyes and whiskers are never visible to the camera. The action happens within one and a half seconds, then everything holds still. The bubble strip, slipper and everything else stay perfectly still. The cat keeps its exact shape and size, no morphing. No people, no shapes outside the window, no long shadows, no glowing eyes, no text, no logos.
```

#### C2 재설계 — 「접착수 살포」 (몸은 반투명 띠 뒤 실루엣)
- **아이디어:** 띠를 창 아래 유리에 세워 붙인 직후다. 크루 셋은 **세워진 띠 뒤(띠와 유리 사이)**에 있어, 반투명 기포 너머 흐린 실루엣으로만 보인다.
  - 띠의 윗변(높이 약 33cm)이 크루 키의 상한이 되므로, 모델이 크루를 키울 수 없는 구조다. 기포가 블러 필터 역할을 해 피규어 단서도 사라진다.
  - 분무기 꼭지만 띠 윗변 위로 나와 있다. 실루엣 하나(여사)가 방아쇠에 매달려 '칙'을 쏘면, 퍼프가 띠 앞에 있던 **뭉치(솜먼지)**를 맞혀 뭉치가 두 바퀴 데굴데굴 굴러간다.
  - 콘티 v2의 '막내 엉덩방아'는 '뭉치 세척'으로 바꾼다. 마스코트가 15초 안에 한 번 더 등장하는 효과도 있다.
- 자막: 배지 ② + "접착수 살포" → "뭉치 먼저 세척됨"
- 같은 세트로 #2 작전 ①의 S1(정지)도 만든다. S1은 띠가 막 세워진 순간, 실루엣 셋이 만세하는 장면이다.
- **C2 시작 프레임** = P0 편집(Seedream 무료). 띠를 세우는 위치는 고양이 반대편인 왼쪽 창 아래이고, 슬리퍼는 동선 밖이다.
```
Edit this exact image, keep the same camera angle, room, window, carpet, cushion and slipper. The long bubble-wrap strip now stands upright on its long edge, leaning against the lower part of the left window glass, about as tall as the cat's head is wide plus a little, translucent and glowing from the window light behind it. Behind the strip, between the strip and the glass, three tiny workers are visible only as soft blurred dark silhouettes through the bubbles; the tops of their heads stay below the upper edge of the strip, and one silhouette with a bow on its head hangs with both hands from the trigger of a plain gray spray bottle whose top and nozzle stick up just above the strip's upper edge, the nozzle pointing toward the camera side. On the carpet in front of the strip sits a small loose clump of grey dust about the size of the cat's paw. The cat sleeps curled on its cushion on the right, its back to the camera. Grainy black-and-white infrared security footage, monochrome. No people in front of the strip, no faces, no long shadows, no glowing eyes, no text, no logos.
```
- **C2 영상** (같은 설정, 4cr):
```
Fixed ceiling security camera, the camera never moves, no zoom, no cut. Grainy black-and-white infrared night footage with noise, soft even light. Behind the upright translucent bubble strip, the blurred silhouette hanging from the spray bottle trigger pulls it down with its whole body weight; the nozzle fires one short puff of fine water mist over the top of the strip toward the camera side, and the puff hits the small dust clump on the carpet, which tumbles backward and rolls over twice, then stops, slightly flattened and damp. The other silhouettes behind the strip flinch. The strip stays upright, flat and rigid. Everything happens within two and a half seconds. The silhouettes stay behind the strip and keep their small size. One short puff only, no fog, no spreading cloud. The cat sleeps and does not move; its face is never visible. No people or shapes outside the window, no long shadows, no glowing eyes, no text, no logos.
```
- 판정: '칙 → 굴러감'이 2.5초 안에 읽히고, 실루엣이 띠 윗변을 넘지 않고, 뭉치가 굴러간 뒤에도 솜먼지 형태를 유지해야 한다(깔리지 않음).
- 위험: 띠 뒤 실루엣이 창가 형체로 읽히면 공포 FAIL이다. 띠가 밝게 빛나야 하고, 실루엣은 띠 높이 안의 작은 형체여야 한다. 시작 프레임에서 썸네일로 먼저 확인한다.

### 3. 예산
| 항목 | 크레딧 |
|---|---|
| 승인 | 28 |
| 사용 (T1) | 4 |
| 잔액 | **24** |
| 계획: T2(C5) → C3 → C4 → C2 | 4 × 4 = **16** |
| 예비(재생성 2회) | 8 |
| 합계 | 24 (승인 내) |
- 생성 순서는 위험이 큰 순서다. 시작 프레임 4장(C3, C2, S1, 그리고 이미 GO인 C5_plate)은 Seedream·FLUX 무료로 만든다. 각 시작 프레임은 creative가 GO를 낸 뒤에만 영상을 만든다.
- 예비 8cr를 다 쓰면 남은 컷은 이미지 대체안(concept_v2 5장)으로 가고 추가 지출은 없다.

### 한국어 요약
1. T1은 부분 사용이다. 원본 0.0~1.7초는 '뽁뽁이가 걸어간다'가 살아 있고 띠·크기도 안정적이다. 1.7초부터는 다리가 슬리퍼를 밟아 녹이므로 쓰지 않고, 0.0~1.7초를 0.7배속으로 훅 2.4초를 채운다(작전 ①은 정지 S1 2.0초로 대체).
2. T2는 C5_plate(고양이 뒷모습, 크루 없음)로 바로 생성 GO이고 최종 프롬프트를 확정했다. C3는 '뽁뽁이 조각을 쓰고 위장한 다리 4걸음', C2는 '세워진 띠 뒤 실루엣이 분무해 뭉치가 굴러감'으로 재설계했다. 두 컷 모두 덮개가 크루 크기의 상한이 되는 구조다.
3. 예산은 잔액 24cr = T2·C3·C4·C2 각 4cr(16) + 예비 8cr로 승인액 안이다. 동선 위에 슬리퍼 같은 소품을 두지 않는 것이 이번 교훈이다.


## [creative] T2 판정 — 부분 사용(원본 0.3~3.1초) / C3_start_v4 — NO-GO(재생성)
판정자: creative. T2.mp4에서 12장(0.0~3.9초, 약 0.3초 간격, `_t2/sheet.jpg`)을 직접 뽑아 봤고 C3_start_v4.png 원본도 확인했다. 파일은 고치지 않았다.

### 1. T2: **부분 사용 — 원본 0.3~3.1초** (재생성 안 함)
| 기준 | 결과 |
|---|---|
| 필수: 몸통 변형 없음 | **통과(조건부).** 0.0~0.9초 방석에서 내려오는 걸음, 1.2초 도약(모션 블러로 몸이 번짐), 1.5초 착지 후 3.9초까지 엎드린 채 정지한다. 다리 4개·꼬리 1개를 유지하고, 블러는 '빠른 동작'으로 읽힌다 |
| 필수: 얼굴·눈 비노출 | **경미 위반, 허용.** 0.6~0.9초와 엎드린 뒤(1.5초~)에 고양이 옆얼굴 윤곽이 작게 보인다. 눈은 몇 픽셀이고 발광도 없다. 이 규칙의 목적(눈 발광·공포 방지)은 지켜진다 |
| 필수: 띠 왼쪽 빈자리 | **통과.** 띠 왼쪽 약 1/3과 슬리퍼 사이가 비어 크루 셋을 얹을 수 있다. 슬리퍼는 내내 그대로다 |
| 추가: 띠 반동 | 약함. 고양이 몸 앞쪽 절반(앞발·가슴)만 띠 위에 있고 뒤쪽은 카펫 위다. '뽁뽁이 위에 철퍼덕'은 앞발과 가슴이 띠를 덮는 것으로 충분히 읽히지만, 띠가 출렁이는 반동은 거의 없다 → 편집에서 착지 프레임(약 1.5초)에 2프레임 흔들림 + '뽁' 연타로 보강한다 |
| 결함: 방석 | 0.9~1.5초 고양이가 도약할 때 방석이 낮은 원형에서 단추 달린 높은 푸프로 바뀌고 오른쪽으로 밀린다(AI 물체 변형). 동작 중이라 1회 재생에서는 잘 안 보이지만, 정지 프레임에서는 보인다 |

**사용 지시 (콘티 v2 #7·#8)**
- #7 반전(2.8초) = **원본 0.3~3.1초** 1.0배속. 0.3초부터 시작해야 방석에서 이미 움직이는 상태로 붙는다.
- #8 다시보기(1.2초) = **원본 1.2~1.8초를 0.5배속**(도약 → 착지).
- 방석 변형은 착지 직전 0.9~1.5초에 생긴다. 다시보기 구간이 이 구간과 겹치므로 **다시보기는 x1.3 펀치인으로 고양이와 띠만 잡아 방석을 프레임 밖으로 뺀다**. 펀치인 중심은 띠 가운데다.
- 크루 합성 위치: 띠 왼쪽 끝(슬리퍼 오른쪽 위). 1.5초 착지 프레임에 '통통'을 시작한다. 고양이 앞발과 크루 사이는 크루 키 이상 띄운다.
- 재생성하지 않는 이유: 핵심 웃음(고양이가 뽁뽁이 쪽으로 철퍼덕)이 읽히고 결함은 편집으로 가릴 수 있다. 4cr를 다시 써도 방석·옆얼굴 문제가 사라진다는 보장이 없다.

### 2. C3_start_v4: **NO-GO → 재생성(Seedream 무료, 최대 2회)**
- **크기 실패.** 콩알이 몸이 조각 아래로 허리·벨트·팔까지 다 보이고, 키가 슬리퍼의 약 1.7배다(표시 해상도 기준 몸 약 200px, 슬리퍼 약 115px). '고양이만 한 아이가 판을 들고 있다'로 읽힌다.
- **연출 실패.** 조각을 팔을 뻗어 머리 위 높이 들어 '피켓'처럼 보인다. 위장(덮개 밑에 숨기)이 아니다. 위치도 띠 위가 아니라 띠 위쪽 카펫에서 띠로 들어서는 중이다.
- 좋은 점: 부감, 띠·슬리퍼·고양이 배치, 그레인은 판(C3_plate) 그대로다. 고양이 얼굴도 안 보인다.
- **원인과 수정:** '머리 위로 든다(held up)'라고 쓰자 모델이 팔과 몸통을 그렸다. T1이 성공한 이유는 덮개가 **바닥 가까이 낮게** 있어 몸이 들어갈 공간 자체가 없었기 때문이다. 이 구조를 그대로 쓴다. 덮개 높이를 슬리퍼보다 낮게 묶어 크기의 상한으로 삼는다.

**C3 시작 프레임 재생성 문구** (C3_plate 레퍼런스 편집)
```
Edit this exact image, keep the same camera angle, room, window, carpet, cushion, sleeping cat, slipper and the large bubble strip exactly as they are. On top of the large strip, a little right of its middle, a small square piece of bubble wrap about the size of the slipper hovers flat just above the strip, lower than the height of the slipper, carried by one tiny hidden worker underneath it like a turtle shell. Nothing of him shows except two very short legs in gray trousers and tiny black work boots below the piece, one boot lifted mid-tiptoe; his legs are shorter than the width of the slipper. The small piece hides his whole body and head; a tiny knit pompom pokes out from under its front edge. A small soft shadow under the piece. Grainy black-and-white infrared security footage, monochrome. Nothing held overhead, no visible torso, no arms, no face, no other people, no long shadows, no glowing eyes, no text, no logos.
```
- GO 기준:
  - 덮개 아래로 정강이와 부츠만 보인다(몸통·팔 0).
  - 덮개 높이가 슬리퍼 높이 이하다.
  - 다리가 슬리퍼 폭보다 짧다.
  - 띠 위에 있다.
  - 걸어갈 경로(왼쪽) 위에 물체가 없다.
  - 썸네일에서 '작은 뽁뽁이 조각이 걷는다'로 읽힌다. 훅의 축소판이라 콜백 웃음이 된다.
- **C3 영상 프롬프트 수정** (앞 판정의 문안에서 두 문장 교체):
  - "held up by one tiny hidden worker" → `carried low over one tiny hidden worker like a turtle shell, hiding his whole body`
  - 추가: `The small piece stays low, never higher than the slipper.`

### 3. 예산
| 항목 | 크레딧 |
|---|---|
| 승인 | 28 |
| 사용 (T1·T2) | 8 |
| 잔액 | **20** |
| 계획: C3 → C4 → C2 | 각 4 = **12** |
| 예비 | 8 |
- C3는 시작 프레임 GO 뒤에 생성한다. C4는 C3_plate 그대로라 바로 생성할 수 있다(앞 판정의 프롬프트, 4cr).
- C2·S1 시작 프레임은 아직 없으므로 무료로 만든 뒤 판정한다.

### 한국어 요약
1. T2는 부분 사용이다. 원본 0.3~3.1초에서 고양이가 내려와 뽁뽁이 쪽으로 철퍼덕 눕는 장면이 읽힌다. 방석 변형과 작은 옆얼굴은 다시보기를 1.3배 펀치인해 가리면 되므로 재생성하지 않는다(다시보기는 1.2~1.8초를 0.5배속).
2. C3_start_v4는 NO-GO다. 콩알이가 조각을 피켓처럼 높이 들어 몸 전체가 보이고, 키가 슬리퍼의 1.7배다. 조각을 슬리퍼보다 낮게 '거북이 등껍질'처럼 덮고 다리만 보이게 Seedream으로 무료 재생성한다.
3. 잔액 20cr는 C3·C4·C2 각 4cr(12)와 예비 8cr로 쓴다. C4는 C3_plate로 바로 생성할 수 있고, C3는 새 시작 프레임이 GO를 받은 뒤 생성한다.

## [creative] C4 판정 — 부분 사용(원본 1.0~2.4초)
- 확인: 0.3초 간격 12장(`_c4/sheet.jpg`). 0.0~1.1초 웅크려 잠 → 1.2초 고개 번쩍(블러) → 1.5초부터 고개를 들고 왼쪽(띠 방향)을 본 채 경계 자세로 정지(3.9초까지). 들킴 연기가 0.3초 안에 읽힌다.
- 얼굴·눈: 고개를 든 뒤 왼쪽 옆얼굴 윤곽이 작게 보이나, 눈은 몇 픽셀이고 발광은 없다. T2와 같은 기준으로 허용한다. 형태: 웅크림에서 식빵 자세로 자연스럽게 바뀌고, 다리·꼬리 개수와 방석 형태 변형이 없다.
- 사용: 콘티 #5(1.4초) = 원본 1.0~2.4초. 1.2초 고개 번쩍에 맞춰 반장 삑을 넣는다(편집 기준 #5 시작 +0.2초). 얼음 크루와 덮개 조각 레이어는 띠 위에 얹는다. #6 늦은 뽁은 원본 2.4초 프레임을 정지 화면으로 쓰고 크루 레이어만 교체한다.
- 예산: 잔액 16cr = C3(4) + C2(4) + 예비 8.


## [creative] C2_start_v4 판정 — NO-GO (try1 포함), C2를 '크루 없는 분무 + 후합성'으로 단순화
판정자: creative. C2_start_v4.png와 C2_start_v4_try1.png 원본을 직접 봤다. 파일은 고치지 않았다.

| 파일 | 판정 | 근거 |
|---|---|---|
| C2_start_v4 | **NO-GO** | ① **카메라가 바뀌었다.** 창이 대각선으로 기울고 어안이 강해져, P0·C3_plate·T1·T2·C4와 같은 방으로 이어지지 않는다. ② 띠가 커튼봉에 매달린 바닥~천장 높이 기둥이 됐다(33cm 띠가 아님). 띠 높이로 크기를 묶는 설계가 무너졌다. ③ 크루가 띠 '뒤'가 아니라 앞 카펫에 선 검은 실루엣 셋이다. 크기는 작아서 좋지만 장난감 병정처럼 보이고, 아무도 분무기를 쏘지 않는다(분무기는 창턱 위). ④ 고양이 얼굴(감은 눈)이 정면으로 보인다. 좋은 점은 뭉치(솜먼지)가 띠 앞 카펫에 있다는 것 하나다 |
| C2_start_v4_try1 | **NO-GO(강하게)** | 카메라가 눈높이로 내려왔다. 리본 실루엣이 분무기 끝에 **끈으로 매달려 있다. '목 매단 형체'로 읽혀 공포 판정 FAIL이다.** 검은 실루엣 크루는 장난감 병정처럼 보이고, 띠 뒤 실루엣도 띠 높이의 절반이 넘는다 |

### 원인과 방향
- 이 컷은 '세운 띠 + 띠 뒤 실루엣 + 매달린 크루 + 분무 + 뭉치'를 한 장에 다 요구한다. 무료 모델이 감당하지 못하고, 매번 카메라를 새로 잡는다. 같은 지시로 더 돌려도 결과가 나아질 가능성이 낮다.
- **단순화한다.** C3·C4·C5와 같은 판(`C3_plate`, 띠가 바닥에 누운 상태)을 그대로 쓴다. 분무기와 뭉치만 더한다. **크루는 영상에 넣지 않는다.**
  - 방아쇠가 '보이지 않는 누군가'에 의해 당겨지는 동작만 생성한다.
  - 크루(얼음·작업 포즈 레이어)는 편집에서 얹는다. T2·C4에서 검증한 방식이다.
  - 분무기 뒤에 여사의 리본 두건 실루엣 끝만 1~2px 테두리로 살짝 보이게 합성하면, 쏘는 사람이 숨어 있다는 것이 읽힌다. 매달린 모습은 금지한다.
- **콘티 정합성:** 띠가 밤 내내 바닥에 누워 있으므로 C3·C4·C5와 이어진다. 띠가 창에 붙은 모습은 아침 컷에서 처음 공개한다("밤새 결국 붙였다").
  - 그래서 #2 작전 ①의 S1은 '창에 세운 띠'가 아니다. **"단열판 운반 완료" 정지 화면**으로 바꾼다. C3_plate 위에 작업 포즈 크루 레이어를 합성하고, 생성은 하지 않는다.
  - #3 자막은 "접착수 살포" → "뭉치 먼저 세척됨"으로 유지한다.

### C2 시작 프레임 (C3_plate 레퍼런스 편집, Seedream 무료, 최대 2회)
```
Edit this exact image. Keep the exact same camera angle, room, window, carpet, cushion, sleeping cat, slipper and the large bubble strip lying flat on the floor exactly as they are; do not move or tilt the camera. Add only two things: a plain unbranded gray spray bottle standing upright on the carpet just left of the left end of the strip, about as tall as the cat's head is high plus a little, its nozzle pointing to the right along the strip; and a small loose clump of grey dust and lint about the size of the cat's paw sitting on the left part of the strip, a short distance in front of the nozzle. Nothing else is added. Grainy black-and-white infrared security footage, monochrome. No people, no figures, no silhouettes, no strings, nothing hanging, no hands, no long shadows, no glowing eyes, no text, no logos.
```
- GO 기준:
  - P0·C3_plate와 카메라가 같다(창 위치·기울기 비교).
  - 분무기와 뭉치가 띠 왼쪽에 있고, 슬리퍼는 그대로다.
  - 사람·실루엣·매단 것이 없다.
  - 고양이는 C3_plate 그대로다.

### C2 영상 프롬프트 (교체본, `seedance_2_0_mini 720p 4초 9:16`, 오디오 끔, 4cr)
```
Fixed ceiling security camera, the camera never moves, no zoom, no cut. Grainy black-and-white infrared night footage with noise, soft even light. The trigger of the plain spray bottle standing at the left end of the bubble strip is pulled down once, firmly, as if by someone small hidden behind the bottle; the bottle rocks slightly but stays upright, and the nozzle fires one short puff of fine mist to the right along the strip. The puff hits the small dust clump, which tumbles backward across the bubbles and rolls over twice, then stops, slightly flattened and damp, still a fluffy clump. Everything happens within two and a half seconds, then everything holds still. One short puff only, no fog, no spreading cloud. No people, no hands, no figures appear. The cat sleeps curled on its cushion and does not move; its face is never visible. The slipper and the strip stay exactly where they are. No long shadows, no glowing eyes, no text, no logos.
```
- 판정:
  - '칙 → 데굴'이 2.5초 안에 읽힌다.
  - 분무기와 뭉치의 형태가 유지된다(솜먼지가 녹거나 사라지지 않음).
  - 사람이나 손이 생기지 않는다.
  - 안개가 퍼지지 않는다.
- 실패 시: 재생성하지 않는다. concept_v2의 이미지 대체안(분무 전, 퍼프, 뭉치 굴러감 3장 교차 + '칙' 효과음)으로 간다(무료).
- 예산: 잔액 16cr = C3(4) + C2(4) + 예비 8. 변동 없다.

### 한국어 요약
1. C2_start_v4와 try1 모두 NO-GO다. v4는 카메라가 바뀌고 띠가 천장까지 닿는 기둥이 됐으며 아무도 분무기를 쏘지 않는다. try1은 리본 실루엣이 끈에 매달려 '목 매단 형체'로 읽혀 공포 판정 FAIL이다.
2. C2는 C3_plate 그대로에 분무기와 솜먼지만 더해, '보이지 않는 누군가가 방아쇠를 당겨 뭉치가 데굴' 영상으로 단순화한다(무료 시작 프레임 GO 후 4cr). 크루는 편집에서 얹고, 띠를 창에 붙이는 모습은 아침 컷에서 처음 공개한다.

## [artist] S1·C3v5·C2v5 (진행 기록)
- S1 완료: S1_try1.png는 창 밖에 만세 하는 큰 실루엣 2개와 천장 봉에 매달린 띠(세운 것 아님)가 있어 쓰지 않음. 2회차 S1_try2.png를 S1.png(+S1_480.png)로 저장. Seedream 4.5 UNLIMITED(버튼 'Unlimited', 크레딧 표시 없음, 0cr), 작업 ID 21628a51-9157-48bc-96ab-41ad39b14856, 레퍼런스 P0.png. 관찰: 띠가 창 아래 벽에 기대 서 있고 아랫단이 약간 들림, 창은 빈 유리, 사람·실루엣·매달린 것 0, 방석 비어 있음(고양이 없음). 카메라는 P0보다 낮은 눈높이 정면에 가까움(부감 약함). 실측(1440x2560 기준): 띠 높이 약 830px·폭 약 300px, 슬리퍼 폭 약 240px, 띠 높이는 슬리퍼 폭의 약 3.5배. 고양이 없음.
- C3_start_v5 1회차(C3_start_v5_try1.png, 작업 ID eea3ab91-bcbf-4f4d-98d5-8981973dfc03, Unlimited 0cr): 덮개가 기포 조각이 아닌 슬리퍼 모양 천 덮개로 나왔고(표시 기준 폭 약 355px로 슬리퍼 길이 약 115px의 3배 이상), 보풀 방울이 달렸고, 정강이·부츠만 보임(몸통·팔 없음). 카펫에 별도 기포 조각이 하나 더 생김. 슬리퍼·고양이·띠는 판 그대로. 2회차를 프롬프트 수정해 재생성 중.
- C3_start_v5 2회차(C3_start_v5_try2.png, 작업 ID c09eee60-55fa-4fc5-833e-5bf743413dd3, Unlimited 0cr): 투명 기포 판(표시 기준 폭 약 340px)이 띠 위가 아니라 카펫 위 고양이·슬리퍼 사이에 따로 떠 있고, 다리(부츠·정강이)는 판 아래가 아니라 띠 위에 따로 잘린 듯 서 있음(연결 안 됨). 1회차보다 나쁨. 최대 2회를 모두 써서 더 생성하지 않음.
- C3_start_v5.png(+_480) = 1회차(try1)를 복사해 둔 것(2회차보다 나아서). 관찰(1440x2560 실측, 표시값x1.28): 덮개 폭 약 460px·높이 약 150px, 슬리퍼 길이 약 147px(덮개는 슬리퍼의 약 3.1배), 고양이 머리 약 110px(덮개는 약 4.2배). 덮개는 기포판이 아니라 슬리퍼 모양 천 느낌에 보풀 방울이 붙음. 덮개 밑으로 정강이·부츠만 보이고 몸통·팔·얼굴 없음, 부츠 높이 약 90px. 띠 위에 있음. 크기 조건(슬리퍼보다 낮게)은 높이는 충족, 폭은 초과. 판정은 creative가 한다.
- C2_start_v5 완료(1회차만 사용, 2회차 안 씀): C2_start_v5.png(+_480, 원본 C2_start_v5_try1.png 동일), 작업 ID 2535dddf-37a1-40f0-b793-e9721b7b1608, 레퍼런스 C3_plate.png, Unlimited 0cr. 관찰: 카메라·창·카펫·방석·잠든 고양이(얼굴 안 보임)·슬리퍼·띠는 판 그대로. 분무기는 띠 왼쪽 밖이 아니라 띠 위(왼쪽 1/3 지점)에 서 있고 노즐은 오른쪽을 향함. 노즐 앞에 가는 분무 흔적(안개)이 이미 그려져 있고 그 끝에 솜먼지 뭉치가 카펫에 있으며, 띠 위 왼쪽에도 뭉치 2개가 보임. 사람·실루엣·끈·손 없음. 실측(1440x2560, 표시값x1.28): 분무기 높이 약 380px·폭 약 130px, 슬리퍼 길이 약 147px(분무기는 슬리퍼의 약 2.6배), 고양이 머리 약 110px(분무기는 약 3.5배, 요청한 '머리보다 조금 큼'보다 큼), 뭉치 약 50~60px(고양이 앞발 크기 수준). 판정은 creative가 한다.

### [artist] 요약 (S1·C3v5·C2v5)
- 쓴 크레딧 0cr(전부 Seedream 4.5 Unlimited 웹, 버튼 'Unlimited' 확인, CLI·영상 생성 없음). 생성 횟수: S1 1회(이번 세션, try1은 이전 세션분), C3v5 2회, C2v5 1회.
- 파일: S1.png/_480, C3_start_v5.png/_480(+try1·try2 원본, try2_480), C2_start_v5.png/_480(+try1).
- 유의: C3v5는 2회 모두 지시와 달라(1회차: 슬리퍼 모양 천 덮개·폭 슬리퍼 3.1배, 2회차: 덮개 분리) 1회차를 임시 채택. 같은 컷 최대 2회를 다 써서 추가 재생성은 PD 결정 필요. S1은 카메라가 P0보다 낮은 정면 시점.

## [creative] S1·C3v5·C2v5 판정 — C3만 GO, C2 이미지 대체, S1은 아침 컷으로 전용
판정자: creative. S1·C3_start_v5·C2_start_v5(각 _480)와 비교용 C3_plate·C5_plate·C5_start_v3를 직접 봤다. 이미지 파일은 고치지 않았다.

| 컷 | 판정 | 근거 |
|---|---|---|
| **S1** | **#2에는 사용 안 함 → 소스표 #9 아침 컷으로 전용(무료)** | ① 카메라가 눈높이 정면이라 P0·C3_plate 부감과 이어지지 않는다. ② 띠가 '창 아래 벽에 기대 세워진' 상태다. C2 판정에서 정한 '밤 내내 띠는 바닥, 세운 모습은 아침에 처음 공개'와 맞지 않아 #2(밤)에는 못 쓴다. ③ 다만 밝은 낮빛, 빈 방석(고양이 없음), 창이 아니라 **벽**에 기댄 띠는 그대로 아침 컷의 펀치라인이 된다: "결국 세웠다(벽에)". 카메라가 다른 것은 OSD를 'CAM 02'로 바꿔 정당화한다 |
| **C3_start_v5** | **GO (4cr)** | ① 덮개 밑으로 정강이·부츠만 보이고 몸통·팔·얼굴 0, 덮개 높이는 슬리퍼 이하 — T1에서 검증된 '덮개+다리' 구조 그대로다. ② 덮개가 기포 조각이 아니라 **슬리퍼 모양 천에 방울**이 달렸고 진짜 슬리퍼의 3배다. 이것을 결함이 아니라 개그로 쓴다: 바로 옆 진짜 슬리퍼와 비교되는 '3배 큰 슬리퍼로 위장'. 썸네일에서 '방울 달린 뭔가가 다리로 걷는다'가 0.5초 안에 읽힌다. ③ 경로(왼쪽, 띠 위) 위에 물체가 없다. 결함: 카펫 위 고양이 앞의 잉여 기포 조각 → 편집에서 C3_plate 같은 자리 픽셀로 정지 패치(페더 20px)해 지운다(C4·#6 판과 일치시키기 위해 필수) |
| **C2_start_v5** | **이미지 대체(무료, 영상 안 씀)** | ① 분무 흔적이 이미 그려져 있어 영상의 '칙' 순간이 없다. ② 노즐과 안개가 고양이 방석 쪽을 향한다. 영상 모델이 퍼프를 노즐 방향으로 쏘면 **고양이에게 물을 뿌리는 그림**이 될 위험이 크다(동물 학대 연상, 고양이가 깨어나는 오작동). ③ 분무기가 슬리퍼 2.6배로 크지만 '분무기'로는 읽혀 정지 이미지에선 문제없다. ④ 장점: C3_plate를 편집한 판이라 **C3_plate 픽셀로 안개·뭉치를 지우고 옮기는 패치가 이음매 없이 된다** → 3장 교차를 무료로 만들 수 있다. 4cr를 아끼고 위험을 없앤다 |

### C3 영상 생성 지시
- 시작 프레임 `C3_start_v5.png`(1440x2560) 그대로. `seedance_2_0_mini --resolution 720p --duration 4 --aspect_ratio 9:16 --generate_audio false`, 끝 프레임 없음, 직전 cost 재조회.
- 프롬프트: `c3_prompt.txt`(한 줄, 공통 금지 문구 포함).
- 판정 기준(0.3초 시트): 필수 = 걸음이 4번 셀 수 있게 읽힘, 덮개 형태·크기 유지, 다리가 커지거나 팔·몸통이 생기지 않음, 슬리퍼·잉여 조각 그대로. 추가 = 2걸음 뒤 멈칫, 마지막에 한 발 든 채 정지.
- 실패 시: 형태 붕괴면 재생성 1회(4cr, 잔액 안). 그래도 실패면 **이미지 대체** — 시작 프레임 정지 + 덮개 부분(사각 패치·페더)을 키트로 왼쪽 4회 '폴짝' 이동(회당 24px, 0.5초 간격, 들릴 때 4px 위로) + 뽁 4회.

### 예산
| 항목 | 크레딧 |
|---|---|
| 승인 / 사용 | 28 / 12 |
| 잔액 | 16 |
| C3 | 4 |
| 예비(C3 재생성 1회만) | 4 |
| 반납 예상 | 8~12 |

## [creative] 최종 소스표 (편집 담당은 이 표만 보고 조립)
- 원칙: 지금 있는 자산만 쓴다. 새 이미지 생성 없음. 크루 '정지 레이어' = `C5_start_v3.png`에서 반장·여사·콩알이·뭉치를 손 마스크로 오려 **슬리퍼 0.7배 이하(손바닥 크기)**로 축소, 합성 기준표(이 문서 「'오려 붙인 티'를 없애는 합성 기준」) 그대로 적용.
- 'C3 패치' = 같은 판(C3_plate 계열)끼리 같은 좌표의 사각 영역을 페더 20px로 옮겨 붙이는 것. 마스크 도구 없이 이음매가 안 생긴다.
- 전 컷 공통: 그레인·블룸·20fps 블렌드 통일(합성 후 전체 프레임), 'AI 연출' 상시 라벨, 0~3초 'AI 상황극' 라벨, 광고 표시 첫·마지막 화면, OSD 03:14:20부터 단조 증가.
- 콘티 v2 대비 삭제: #9 마스코트(M1·M2 없음), #12 눈알 버튼(자산 없음), 아침의 '인간 발' 콜백(A1~A3 없음). 무료 이미지가 나중에 생기면 복원 가능. 총 길이 29.4 → **25.8초**(성과 데이터상 짧을수록 유리).

| # | 편집 구간 | 소스 | 원본 구간 | 처리 | 자막 / 효과음 |
|---|---|---|---|---|---|
| 1 | 0.0–2.4 | `T1.mp4` | 0.0–1.7 | 0.7배속. `apply_c1_fix.py` 정적 마스크(바닥 사각형·그림자). 0초 감지 박스, 1.4초 x1.3 펀치인 + OSD 'ZOOM x2' | "뽁뽁이가 걸어간다" → "사람 3명 추정" / 종종종, 1.4 띡 |
| 2 | 2.4–4.4 | `C3_plate.png` 정지 | — | 크루 작업 포즈 3 + 뭉치 레이어를 띠 왼쪽 위에 합성(띠를 막 내려놓은 자세). 0.3초에 2프레임 흔들림 | 배지 ① "단열판 운반 완료" / 끙차, 착 |
| 3 | 4.4–6.9 | `C2_start_v5.png` 3장 교차 | — | **C2a**(0.0–1.0): 안개 영역을 C3_plate 픽셀로 패치, 분무기 1px 떨림(누가 당기는 중). **C2b**(1.0–1.5): 원본 그대로(안개) + 2프레임 흔들림. **C2c**(1.5–2.5): C2a에서 끝쪽 뭉치 자리를 C3_plate로 지우고, 뭉치 오린 것을 **아래쪽(카메라 쪽, 고양이 반대)**으로 40px 이동·90도 회전·세로 0.85·10% 어둡게(젖음). 1.5–1.7은 45도 중간 단계. 권장: 분무기 뒤 여사 리본 끝 1~2px 실루엣 | 배지 ② "접착수 살포" → "뭉치 먼저 세척됨" / 끼익, 칙!(1.0), 철썩(1.6) |
| 4 | 6.9–9.4 | `C3.mp4` (판정: 부분 사용) | **0.3–2.6** + 두 번째 발 닿는 프레임에서 0.2초 프레임 정지 | 고양이 앞 잉여 기포 조각을 C3_plate 정지 패치로 전 프레임 제거. 발 닿는 프레임에 뽁. 실패 시 위 '이미지 대체'안 | 배지 ③ "슬리퍼로 위장 복귀" → "…뽁?" / 뽁 뽁 [정지] 뽁 뽁!(4번째 가장 큼) |
| 5 | 9.4–10.8 | `C4.mp4` | 1.0–2.4 | C3.mp4 **2.6초 프레임**의 덮개+다리 영역을 C3 패치로 같은 좌표에 얹음. +0.2초(고개 번쩍) 삑 → 0.15초 동안 덮개 패치 아래로 미끄러지며 사라지고 콩알이 한 발 든 얼음 레이어 + 반장·여사 얼음 레이어 등장(0.1초 프레임 드롭) | "얼음!" + 도장 '들킴' / 삑!, BGM 정지 |
| 6 | 10.8–11.8 | `C4.mp4` 2.4초 프레임 정지 | — | 정적 0.6초 → 콩알이 레이어를 든 발 내린 버전으로 6px 하강(F2) + x1.3 펀치인 | "…뽁." / 무음 0.6 → 뽁 |
| — | 11.8 | 전환 | — | **2프레임 신호 끊김 글리치**(띠 위치가 C3_plate→C5_plate로 바뀌는 점프를 가림) | 지직 |
| 7 | 11.8–14.6 | `T2.mp4` | 0.3–3.1 | 얼음 크루 3 레이어를 띠 왼쪽 끝(슬리퍼 오른쪽 위)에 얹고, 원본 1.5초(착지)부터 통통(4~6px, 0.12초, 위상 엇갈림). 착지 프레임 2프레임 흔들림 | "정보원이 제일 시끄러움" / 뽁뽁뽁뽁 연타 + BGM 복귀 |
| 8 | 14.6–15.8 | `T2.mp4` | 1.2–1.8 | 0.5배속, x1.3 펀치인(중심 = 띠 가운데, 방석 변형 프레임 밖으로) | "REPLAY" + "판독: 고의 아님" / 슬로 뽀오옥 |
| 9 | 15.8–18.0 | `S1.png` 정지 | — | 아침. 따뜻한 톤 보정(약한 세피아/주황, 채도 낮게)으로 '주간'을 표시, OSD 'CAM 02 · 07:30', 미세 줌 1.00→1.04. 원 카메라와 다른 것은 CAM 02로 정당화 | "결국 세웠다(벽에)" / 새소리 |
| 10 | 18.0–19.8 | `S1.png` 정지(어둡게 40%) + 오버레이 | — | 작업일지 카드 | "동절기 단열 공사 제10호 / 결과: 벽 1, 고양이 침대 1" → 도장 '반려(사유: 소음)' / 쾅 |
| 11 | 19.8–25.8 | PPL 카드 + `T1.mp4` 0.0–1.7 저채도 루프 배경 | 0.0–1.7 | concept_v2 6장 문구 그대로(상품명 원문은 업로드 직전 PD 복사) | BGM |

- 남은 위험: #5 덮개 패치는 C3.mp4와 C4.mp4의 노출이 다르면 사각 테두리가 보인다 → 패치 영역 평균 휘도를 C4 쪽에 맞추고(±5) 페더를 30px까지 늘린다. creative가 0.5배 썸네일로 판정하고 qa가 재확인한다.
- #3은 정지 3장이라 '움직임'이 약하다 → 칙 순간 2프레임 흔들림과 효과음 타이밍(1.0초 정확히)이 웃음을 맡는다.

### 한국어 요약
1. S1은 카메라·설정이 밤 장면과 맞지 않아 #2에는 쓰지 않고, '벽에 세운 띠'를 살려 아침 컷(CAM 02, "결국 세웠다(벽에)")으로 전용한다. #2는 C3_plate에 크루 레이어를 얹은 정지 화면이다.
2. C3_start_v5는 GO(4cr)다. 3배 큰 '슬리퍼 위장'을 개그로 쓰고, 프롬프트는 `c3_prompt.txt`에 저장했다.
3. C2_start_v5는 안개가 이미 그려져 있고 노즐이 고양이 쪽이라 영상은 위험하다. C3_plate 패치로 3장 교차(분무 전·칙·뭉치 굴러감)를 무료로 만든다.
4. 최종 25.8초, 지출 예정 4cr(최대 8cr), 8~12cr 반납 예상. 마스코트·눈알 버튼·인간 발 콜백은 자산이 없어 뺐다.

## [creative] C3 판정 — 부분 사용(원본 0.3~2.6초)
판정자: creative. C3.mp4(720x1280, 24fps, 4.04초)를 0.5초·0.25초 간격으로 직접 뽑아 봤다(`_c3/mid.jpg`, `_c3/legs.jpg`). 파일은 고치지 않았다.
- 통과: 슬리퍼 모양 덮개가 4초 내내 형태·크기를 유지하고, 밑의 다리 한 쌍이 끊김 없이 왼쪽으로 걷는다. 다리가 커지지 않고, 팔·몸통·얼굴이 생기지 않는다. 고양이·슬리퍼·잉여 조각은 그대로다. 썸네일에서 '방울 달린 거대 슬리퍼가 걸어간다'가 바로 읽힌다(훅의 콜백).
- 아쉬움: 4걸음 + 멈칫이 아니라 일정한 종종걸음이다 → 편집에서 두 번째 발 닿는 프레임에 0.2초 정지로 멈칫을 만든다. 부츠는 띠 아래쪽 가장자리의 카펫을 밟는다 → 부감이라 1회 재생에서는 띠 위로 읽히고, 뽁은 발 닿는 프레임에 맞춘다. 다리 아래 옅은 대각선 그림자는 허용 범위다.
- 사용 금지 구간: 약 3.0초부터 덮개가 띠 왼쪽 끝을 넘어 카펫으로 나간다. 그래서 **0.3~2.6초**만 쓴다. #5 덮개 패치는 2.6초 프레임에서 뜬다.
- 예산: 사용 16cr(승인 28), 잔액 12cr. 재생성 없음.

## [editor] EP10 preview v1 (검수 전, 크레딧 0)
- 산출물: `output/EP10/EP10_youtube.mp4`(25.8초, 1080x1920, 30fps), `EP10_youtube_upload.mp4`(2.8MB), `EP10_preview.png`, 핵심 프레임 시트 `EP10_keyframes_1.jpg`·`EP10_keyframes_2.jpg`, 크루 200% 확대 `EP10_crew_zoom.jpg`. 틱톡·클립은 아직 렌더하지 않음(v1은 youtube만).
- 총 길이 25.8초. 들킴 컷 시작 9.4초, 삑 9.6초, BGM 무음 9.6~11.8초(bgm_mute). 소스표 길이 그대로: 훅 2.4 / ① 2.0 / ② 2.5 / ③ 2.5 / 들킴 1.4 / 늦은 뽁 1.0 / 반전 2.8 / 다시보기 1.2 / 아침 2.2 / 일지 1.8 / PPL 6.0.
- 조립 방식: 합성이 필요한 컷은 `ep10_build.py`가 1080x1920 클립으로 미리 만들고(`T1_hook`, `T1_ppl`, `S2_comp`, `S3_comp`, `C3_comp`, `C4_comp`, `T2_comp` .mp4, `S1_warm.png`), `ep10_make_json.py`가 episode.json을 쓴다. 타이밍을 바꾸면 두 스크립트를 다시 실행.
- 소스표 대응
  - #1 훅: T1 0.0~1.7 + `apply_c1_fix.py`(전 프레임), 0.7배속(미리 구워 REPLAY 라벨 방지), 0초 감지 박스, 1.4초 x1.3 펀치인 + 'ZOOM x2'. 자막 "뽁뽁이가 걸어간다" → "사람 3명 추정"(컷 2개로 나눠 교체).
  - #2: C3_plate + 크루 3 + 뭉치(정지), 0.3초 2프레임 흔들림. 크루는 얼음 포즈 한 종류뿐이라 '작업 포즈' 대신 같은 얼음 포즈를 썼다.
  - #3: C2_start_v5 3장 교차. C2a 안개를 C3_plate로 패치+분무기 1px 떨림, C2b 원본+칙(1.0) 2프레임 흔들림, C2c 뭉치 지움 후 45도(0.2초)→90도, 아래 40px·세로 0.85·10% 어둡게. 자막 두 컷으로 분리("접착수 살포"→"뭉치 먼저 세척됨").
  - #4: C3 0.3~2.6초, 잉여 기포 조각을 C3_plate 패치(페더 22, 고리 휘도 맞춤)로 전 프레임 제거. 원본 0.6초(두 발이 닿은 프레임)에서 0.2초 정지. 뽁 4번(0.10, 0.30, 0.95, 2.2 가장 큼).
  - #5·#6: C4 1.0~2.4 + 2.4초 프레임 1초 정지. C3 2.6초 프레임의 덮개+다리를 물체 마스크로 얹고, 0.2초 삑 → 0.2~0.3 프레임 드롭 글리치 → 덮개 아래로 슬라이드아웃 → 크루 얼음 3. 2.0초에 콩알이 6px 하강, 펀치인 + ZOOM x2.
  - 전환 11.8: frame_drop(노이즈 바 2프레임 + 시계 1칸 점프) + 지직(radio 자막 자동음).
  - #7·#8: T2 0.3~3.1, 얼음 크루 3을 띠 왼쪽 끝에 얹고 1.4초(착지)부터 통통(5px, 0.12초 주기, 위상 엇갈림, 1.3초간 감쇠, 그림자는 제자리에서 옅어짐), 착지 2프레임 흔들림. 다시보기 1.2~1.8 0.5배속 + 펀치인.
  - #9·#10: S1 따뜻한 톤(S1_warm), CAM 02 · 07:30, 줌 1.00→1.04. 일지 카드 + 도장 '반려'(사유 줄은 일지 3번째 줄).
  - #11: PPL 카드(T1_fix 0.0~1.7 루프 배경, dim 0.6). 상품명은 캡처명 그대로 + _todo.
- 합성 기준표 적용값: 크루 키 반장 86px(1080폭 기준) = 슬리퍼 길이(약 125px)의 0.69배, 뭉치 약 44px. 위치별 평균 = 띠 아래 카펫 +15(허용 ±15 상단), 상한 반장 220/나머지 195(창 225 미만), 하한 = 그 위치 카펫 1% 휘도. 축소 후 블러 0.8px + 국소 대비 0.5 복원, 마스크 1px 침식+1px 페더, 위쪽 윤곽 림 +12, 접지 타원 그림자 42%(폭 = 발 간격 1.3배)+접촉 그림자+기포 눌림, 방사 방향 1~3도 기울임, 합성 후 프레임 전체에 그레인 σ4.5(프레임마다 새로)+JPEG q75. 마스크: u2net.onnx(rembg 공식 릴리스 danielgatis/rembg v0.0.0)를 onnxruntime으로 직접 실행, 뭉치는 타원 마스크. opencv-python-headless, rembg(--no-deps, 실제 미사용) 설치.
- 코드 변경(하위 호환): `make_cctv.py`에 선택 키 2개 추가. 컷별 `cam`(OSD 카메라 이름), `ppl_notes_lines`(※ 문구를 줄마다 표시). EP09 확인: 코드 diff는 이 두 키뿐이고, 이전 렌더와 8개 시점 프레임 비교 시 픽셀 차 최대 26(평균 약 4, 전 시점 균일)으로 정적 노이즈(PIL effect_noise가 실행마다 달라짐)와 같다. 구조적 차이 없음. 해시는 매번 달라지는 것이 원래 동작.
- 남은 우려(creative·qa 확인 필요)
  1. 크루 가독성: IR 룩(감쇠·감마·블룸) 뒤에서 크루가 작고 어둡다. 특히 #2(3.5초), 들킴 이후 정지 장면(9.9~11.4초)에서 200% 확대해야 사람으로 읽힌다. 상한(슬리퍼 0.7배)이 이미 한계라 키우려면 PD 판단(0.8배)이 필요하고, 크루 위 국소 밝기(예: 반장 반사띠만 +)로 보강하는 안도 있다.
  2. 크루가 한 가지 얼음 포즈(손 든 반장, 쪼그린 여사, 한 발 든 콩알이)만 있어 #2 '작업 포즈'·#5 '걷는 포즈→얼음' 교체 연출은 못 했다. 콩알이 '발 내림'은 변형 없이 6px 하강만 했다.
  3. T1 보정(apply_c1_fix) 핫스폿 하단에 둥근 패치의 경계(흐린 사각 느낌)가 훅 프레임 아래쪽에 남아 있다. C1 판정 때 지적된 우려 그대로.
  4. #5 덮개 패치는 마스크 방식(덮개·부츠만 얹음, 바닥 빛 변화 제외)으로 사각 테두리는 없다. 덮개 왼쪽 끝이 약간 깎여 밝게 보임. 0.5배 썸네일 판정 필요.
  5. 효과음 파일 없음: 새소리(아침), 종종종은 roller.wav로 대체. 아침 컷은 현재 무음 + 자막.
  6. 들킴 도장 '들킴'이 고양이 위를 가린다(EP09와 같은 좌표 사용). 위치 조정 여부 결정 필요.
  7. 고양이 눈·얼굴: 반전 컷 착지 구간에서 고양이 옆얼굴이 보임(T2 원본 그대로, 눈 발광 없음). qa 시트 확인 필요.
  8. 쿠팡은 `product_alt_pending`(링크만)이라 PPL 카드·대가성 문구에 아직 없음. 고정 댓글은 네이버 문구만. _todo 참고.
  9. 훅 0.0초 프레임: 자막 글리치(치직)와 감지 박스가 같은 순간에 나오며 움직임은 0프레임부터 있음.

## [creative] EP10 preview v1 — REVISE (6.2/10, 편집으로 복구 가능, 크레딧 0)
판정자: creative. `EP10_youtube.mp4`를 0.5초 간격(270x480 타일)과 0.5배(540x960) 단독 프레임(3.5·5.6·10.4·11.5·13.4초)으로 직접 봤고, `EP10_crew_zoom.jpg`, 0.46초 창 RMS도 확인했다. 파일은 고치지 않았다. 글자 실측·기술 규격은 typo·qa 몫이라 제외.

### 점수
| 항목 | 점수 | 근거 |
|---|---|---|
| 훅 0~1초 | 8.5 | 0프레임부터 '다리 달린 뽁뽁이'가 걷고 감지 박스·자막이 즉시 읽힌다. 0.5배에서도 다리 3쌍이 보인다. 통과 |
| 크루 가시성 | **2.5** | 0.5배에서 #2·#3·#5·#6·#7 크루가 **보이지 않는다**. 200% 확대(crew_zoom)에서야 반사띠 X자로 사람임을 안다. 원인은 크기보다 **톤**: 밝은 회색 크루가 같은 밝기의 기포 하이라이트 위에 놓여 위장된다(콘셉트의 '밝은 배경 앞 어두운 실루엣 + 림'과 정반대) |
| 웃음 타이밍 | 5.0 | 박자(뽁 4번 → 삑 → 무음 약 0.9초 → 뽁)는 소리로는 맞다. 그러나 화면에는 '얼음!' 순간에 굳은 사람이 없고, 늦은 뽁 펀치인이 빈 띠를 비춘다. 웃음의 주어가 안 보인다. 슬리퍼 위장 걷기(7~9초)와 반전 철퍼덕(12~14초)은 0.5배에서 확실히 터진다 |
| 공포 요소 | 9.0 | 없음. 창 밝음, 큰 그림자 없음, 0초 BGM. 반전에서 고양이 옆얼굴이 보이나 귀여운 태비 옆모습이라 문제없다. 늦은 뽁 펀치인 프레임의 고양이 반쪽 잘림은 공포가 아니라 구도 문제 |
| 상품 적합도 | 8.5 | 모든 비트가 뽁뽁이·뽁 소리에서 나오고, 아침 '벽에 세움'·일지 '반려(소음)'로 잘 닫힌다 |
| **종합** | **6.2** | 훅·반전·결말은 8점대. 중반(2.4~11.8초) '크루가 안 보임'이 들킴 개그 전체를 무너뜨린다 |

### 비트별 0.5배 판독
- 0.0–2.4 훅: 읽힘. 
- 2.4–4.4 #2 '단열판 운반 완료': 크루가 안 보이고 띠만 바닥에 있다 → '운반 완료'가 증거 없는 자막이 된다.
- 4.4–6.9 #3: 분무기가 혼자 서 있다. 뭉치는 점 하나라 '뭉치 먼저 세척됨'이 보이지 않는다(웃음 0).
- 6.9–9.4 #4 슬리퍼 위장: 이번 화 최고의 그림. 0.5배에서 바로 웃긴다.
- 9.4–10.8 #5 들킴: 덮개가 사라진 뒤 빈 띠. 도장 '들킴'이 **고양이 머리를 덮어** 들킴 연기(고개 돌림)까지 가린다. 이중 손실.
- 10.8–11.8 #6 늦은 뽁: 펀치인 중심이 띠 가운데라 크루는 왼쪽 끝 작은 점, 고양이는 오른쪽 위에서 잘린다. 6px 하강은 보이지 않는다.
- 11.8–15.8 반전·다시보기: 고양이는 확실히 읽힌다. 띠 왼쪽 끝 크루 '통통'은 0.5배에서 안 보인다.
- 15.8–25.8 아침·일지·PPL: 아침 세피아와 '결국 세웠다(벽에)'는 띠가 벽에 기댄 게 보여 성립. 일지 '반려' 도장 좋음.

### 수정 지시 (편집만, 우선순위순)
1. **크루 톤 반전(필수, 가장 효과 큼)**: 크루 레이어 전 컷 공통으로 몸통 휘도를 놓인 자리 기포 평균보다 **-35~-45** 낮춰 '어두운 실루엣'으로. 그 위에 위쪽 윤곽 림을 +12 → **+40, 폭 2px**(IR 역광 테두리). 반장 안전모·반사띠만 국소 +50(화면 최밝점, 콘셉트 1장 1항). 접지 그림자 42% → 60%. 결과 기준: 540x960에서 '어두운 작은 사람 3명'이 0.3초 안에 셀 수 있을 것.
2. **크루 키 상한 0.7배 → 1.2배(약 150px/1080폭)로 상향(근거 아래)**. 뭉치도 44px → 70px.
   - 근거 ①: 훅(T1)의 크루 **다리만** 1080폭 기준 약 100px다. 86px 전신은 훅의 다리보다 작아 **같은 화 안에서 크기가 줄어드는 불일치**다. 150px여도 훅 다리 비례(다리 ≈ 키의 0.45~0.5)와 맞는다.
   - 근거 ②: concept_v2 1장 2항 기준은 '키 = 큰 기포 4개'였다. 지금 86px는 기포 약 1.2개다. 1.2배(150px)도 기포 약 2개라 여전히 '손가락만 한 크루'다.
   - 근거 ③: 상한 0.7배는 '피규어처럼 보이는 것' 방지용이었으나, 현재는 '안 보이는 것'이 더 큰 실패다. 1번 실루엣 처리를 같이 하면 확대해도 도색 얼굴 같은 피규어 단서는 드러나지 않는다.
   - '고양이 귀 하나 > 크루' 비교는 포기한다(고양이 몸통 대비로 충분히 작음).
3. **배치**: 크루를 밝은 기포 한가운데가 아니라 **띠 아래쪽 가장자리~카펫 경계**(어두운 바닥이 배경이 되는 자리)에 둔다. 셋은 일렬 금지, 높이차 20px 이상.
4. **들킴(#5)**: 도장 '들킴'을 고양이에서 떼어 **크루 무리 바로 위(화면 중앙 좌측, 하단 25% 위)**로 옮기고, 고양이 고개가 돌아간 뒤 0.25초 지연해 찍는다. 고양이 귀·고개는 가리지 않는다. 덮개가 사라지는 순간 크루 셋이 '얼음' 포즈로 바로 보이게(1·2번 적용 후 확인).
5. **늦은 뽁(#6) 펀치인**: 중심을 띠 가운데 → **크루 무리 중심**으로, 배율 x1.3 → **x2.0**(OSD 'ZOOM x2'와 일치). 콩알이 발 하강 6px → 펀치인 화면 기준 16px + 발 닿는 프레임에 기포 눌림 하이라이트 2프레임(작은 흰 반짝). 고양이는 이 컷 프레임에서 빼도 된다(잘린 반쪽보다 낫다).
6. **#2**: 3.4초에 x1.5 펀치인 0.6초(중심 = 크루)로 '사람이 옮겼다'를 증명. 크루가 띠 모서리에 손을 얹은 위치로.
7. **#3**: 여사 레이어를 분무기 방아쇠 아래에 매달린 위치로 얹고(0.0~1.0 1px 떨림을 여사에도), 칙(1.0) 직후 1.4~2.5에 젖은 뭉치 중심 x1.6 펀치인. 뭉치는 2번 크기로.
8. **반전(#7)**: 1~2 적용 후 통통 진폭 5px → 9px. 띠 왼쪽 끝 크루가 0.5배에서 보이는지만 재확인.
9. 그대로 둘 것: 훅, 슬리퍼 위장 걷기, 뽁 박자, 반전 철퍼덕, 아침·일지·PPL 구성.

### 오디오(창작 관점만)
- 들킴 뒤 실제 무음 구간 약 10.1~11.0초(RMS -39dB) 뒤 뽁. 정적 길이는 0.6~0.9초 범위로 적정. 삑이 구간 최대(약 -13dB RMS)라 '들켰다' 신호는 충분.

### 재판정 조건
- 1~5번 반영 후 v2를 다시 0.5배로 본다. 1~5번이 되면 크루 가시성 7.5 이상, 웃음 8.0 이상이 되어 종합 8.0 이상 예상. 6~8은 권장.
- 키 상향(2번)은 콘셉트 기준(0.7배) 변경이므로 PD 기록 필요.

### 한국어 요약
1. REVISE 6.2점: 훅·슬리퍼 위장·반전·결말은 좋지만, 0.5배에서 크루가 거의 안 보여 '들킴 → 늦은 뽁' 웃음이 화면에서 성립하지 않는다.
2. 원인은 크기보다 톤이다. 밝은 크루가 밝은 기포 위에 놓여 묻힌다 → 어두운 실루엣 + 2px 밝은 림 + 안전모 최밝점, 카펫 경계에 배치.
3. 키 상한을 슬리퍼 0.7배 → 1.2배(150px)로 올리길 권한다(훅의 다리만 100px라 크기 불일치, 콘셉트 '기포 4개' 기준). 들킴 도장은 고양이에서 떼고, 늦은 뽁 펀치인은 크루 중심 x2.0으로.

## [qa] EP10 preview v1 — FAIL
검수자: qa. EP10_youtube.mp4·EP10_youtube_upload.mp4를 ffmpeg로 직접 열어 0.5초 시트, 0.1초 크롭, 오디오 측정을 했다. 파일은 고치지 않았다.

### 필수 수정 (FAIL 사유)
1. **true peak 기준 초과 (editor, 렌더 마스터링)**: ebur128 true peak가 EP10_youtube.mp4 -0.4dBFS, upload.mp4 -0.6dBFS다. 기준은 -1.0 이하다(volumedetect max는 -0.6 / -0.7). 수정안: 마스터 출력 직전 alimiter=limit=0.85(약 -1.4dBFS)를 걸고 재측정한다.
2. **들킴 이후 크루가 안 보인다 (editor, 9.4~11.8초, 정지 장면 약 2.4초)**: 9.9·10.2·10.8·11.1·11.3초를 1080 폭 그대로 크롭해 봤다. 띠 위에 크루 3명이 읽히지 않고 어두운 얼룩 1~2개만 보인다. '얼음!' 자막과 '들킴' 도장의 근거 화면이 없다. 크루 줌(EP10_crew_zoom.jpg)에서는 반투명한 유령처럼 보여 CLAUDE.md 톤 원칙(반투명 유령 금지)에도 걸린다. 수정안: 크루 레이어를 불투명하게 하고 키를 1.2배(약 150px)로 키우거나 국소 밝기를 올린다(editor 기존 제안대로). 들킴~늦은 뽁 구간은 크루가 한눈에 읽혀야 한다.
3. **'들킴' 도장이 고양이를 가린다 (10.0~10.8초)**: 도장이 고양이 몸통과 얼굴 아래를 덮는다(10.2초 크롭). 수정안: 도장을 방석 왼쪽 위 빈 카펫(약 x 520, y 760)으로 옮긴다.

### 권고
4. **T1 핫스폿 경계 (0.0~2.0초)**: 훅 프레임 아래쪽에 가로로 번지는 회색 패치 띠가 보인다. 2.0초 프레임에서 특히 눈에 띈다(1080 크롭). 0.5배에서도 어두운 띠로 읽힌다. 페더를 더 넓히거나 패치 경계 휘도를 맞춘다.
5. **C3 구간 (6.9~9.4초)**: 슬리퍼 덮개와 다리가 띠 위가 아니라 띠 아래 가장자리 카펫 쪽으로 걷는다. 소스표에서 이미 인지한 사항이며 위치는 허용 범위지만, 뽁이 '띠를 밟는' 것으로 읽히지 않는다. 뽁 시각은 7.0/7.2/7.85/9.1초인데, 0.1초 시트로는 발 닿는 프레임과 정확히 겹치는지 단정하지 못했다(걸음이 작아 판별이 어렵다). editor가 발 닿는 프레임 번호를 로그로 제시해야 한다.
6. **마지막 0.3초**: PPL 카드가 25.4초부터 훅 장면으로 디졸브된다. 광고 문구('광고·제휴 링크로 구매하면 수수료를 받아요')는 마지막 프레임까지 남아 있어 규정은 통과한다. 의도한 루프라면 유지해도 된다.
7. **11.1·11.2초와 12.7·13.5초에 흰 가로선 글리치**가 보인다. 문서화된 글리치(9.6초, 11.8초) 외의 것이면 제거하고, 의도면 그대로 둔다.
8. 늦은 뽁(11.4초) 펀치인이 'ZOOM x2' 표기와 달리 실제 x1.3이다. 라벨을 맞추거나 표기를 'ZOOM'으로 바꾼다.

### 통과 항목 (근거)
- 규격: 1080x1920, 30fps, 영상·오디오 모두 25.8초(upload 오디오 25.813). 오디오 스트림 있음. upload 2.84MB(10MB 미만).
- 움직임: 0.0/0.5/1.0초 연속 프레임 차이 평균 1.7/1.4/1.9(0~1초 구간은 정지 아님, 0.0 대비 0.5초 5.6).
- 금지 구간: 훅(0~2.4초)에 슬리퍼가 녹거나 사라지는 프레임 없음(0.0·0.5·1.0·2.0초). 고양이 눈 발광·정면 얼굴 없음(11.9·12.3초 T2 측면, 10.5·11.2초 방석 위 고양이 확인). 매달림·창 밖 형체 없음. 창턱 위를 걷는 고양이는 실제 고양이 동작으로 공포 요소 아님. C3·C4 구간도 덮개가 카펫 밖으로 나가거나 변형되는 프레임 없음(6.9~9.4초 25장).
- 시계: 03:14:20에서 단조 증가, 11.8초에 +1 점프, 아침 07:30:13 이후 PPL 03:14:41, 거꾸로 가는 곳 없음.
- 싱크: 삑 9.6초 에너지 피크 확인(-1.7dB 순간값). 뽁 9.1초(4번째) 확인. 무음: 9.9~11.3초 약 -40dB(룸톤 수준), 11.4초에 뽁(의도), 11.8초 BGM 복귀. 들킴 컷 9.4초 시작, 삑 9.6초 일치. 들킴 ≤12초 충족.
- 규정: 0~3초 'AI 상황극' 큰 라벨 + 'AI 연출' 상시. PPL 카드 6,180원 / 리뷰 1,598개 / 4.94 / 10/9 = episode.json = product.md = 업로드 txt. 효능 단정 없음('단열 효과: 이 영상에선 측정 안 함'). 할인율·수수료율·판매처 상호 미표기. 화면의 뽁뽁이는 로고·글자 없는 일반 투명 기포 띠로 실제 상품(롤+'AIR CAP' 박스)과 다르게 그려졌고 상품 사진을 쓰지 않음.
- 업로드 txt: 쇼핑커넥트 대가성 문구 원문 2회(설명란·고정 댓글) 일치, 링크 https://naver.me/FaeW9AkP = episode.json, AI 표기 3곳, 해시태그 5개. 쿠팡 링크는 product_alt_pending(미확인)이라 txt에 없음 — 업로드 전 PD 확인 항목(_todo).
- 자막: 화면 밖·겹침·잘림·오탈자 없음. 고양이와 겹치는 것은 '들킴' 도장뿐(3번).

### 합성 티 (200%)
- 크루 레이어 후광·접지 그림자: 훅의 다리는 자연스러움. 들킴 이후 크루는 너무 어두워 판별 불가(2번과 같음).
- 그레인은 전 프레임 통일되어 있고 차이를 못 찾았다.

### 한국어 요약
1. 판정은 FAIL이다. true peak가 -0.4/-0.6dBFS로 기준(-1.0) 초과다. 리미터를 걸고 재렌더해야 한다.
2. 들킴 이후 2.4초 동안 크루가 보이지 않고 도장이 고양이를 가린다. 크루를 불투명·확대하고 도장을 옮겨야 한다.
3. 규격, 금지 구간, PPL 숫자, 대가성 문구, AI 고지, 시계는 통과했다. 뽁 싱크는 발 닿는 프레임 로그가 필요하다.

## [typographer] EP10 preview v1 (2026-10-10, 영상 EP10_youtube.mp4 25.8초, 프레임 36장을 1080px와 폰 390pt로 실측)
판정: FAIL (2건 수정 필요, 나머지 PASS). 파일은 고치지 않았다.

| # | 점검 | 판정 | 근거 |
|---|---|---|---|
| 1 | 폰 실측 가독성 | PASS | 자막 66px(23.8pt), CAM 줄 40px(14.4pt), 현장 라벨·AI 연출·광고 표시 34px(12.3pt, 최소선). 밤 광고 표시 배경 중앙값 대비 6.9~8.2:1(+외곽 3). 자막 박스 위 흰 글자 8:1 이상. 아침 CAM 줄 판 110 적용 확인. 일지 본문(20,20,20)/종이 16:1, 반려 도장 5:1. 두부(□) 없음 |
| 2 | 글자 수 대비 시간 | FAIL(일지) | 일지 1.8초에 3줄 35자+도장 = 약 19자/초. 자막 12개는 모두 3~10자, 최대 7.5자/초(…뽁. 3자라 무관) PASS. PPL AI 고지 50자/6초 8.6자/초는 법정 소문자라 WARN(유지) |
| 3 | 두부 글리프 | PASS | 쓰는 문자열 전체를 fontTools로 검사. 블랙한산스에 「…」 없음 -> make_cctv GLYPH_FALLBACK이 「...」로 대체, 화면에서 정상 표시 확인. ※ ★ · × 는 Pretendard·갈무리 모두 있음 |
| 4 | 피사체 가림 | FAIL(들킴 도장) | 들킴 도장 (760,820)이 고양이 침대·몸통을 통째로 덮고 귀만 보임(9.8~11.0초). 감지 라벨과는 겹치지 않음(감지는 훅 구간만) PASS. 밤 자막 y380은 창문 위라 띠·크루·고양이 가림 없음(꼬리 끝 y568, 자막 하단 y493). 늦은뽁 자막 y1230은 확대 전 띠 하단과 맞닿음(WARN), 아침 자막 y1230은 띠 하단과 14px 간격(WARN) |
| 5 | PPL 카드 | PASS | 「※ 단열 효과: 이 영상에선 측정 안 함」「※ '뽁' 소리: 기본 포함」 원문 일치, 36px 줄 간격 약 50px(1.35배), 카드-AI 고지 간격 20px. 「1m당 약 618원」 = 6,180÷10 맞음. 상품명 두 줄 단어 잘림 없음(원문 교체는 PD 대기 _todo) |

수정 지시(episode.json)
1. 들킴 도장 이동: segments[이름 "들킴"].stamps[0] -> "x": 420, "y": 790 (고양이 왼쪽 빈 카펫, 슬리퍼 위). size 84 유지.
2. 작업일지 읽기 시간: segments[이름 "작업일지"] -> worklog.lines = ["결과: 벽 1, 고양이 침대 1","사유: 소음"] (제목 줄과 중복되는 "동절기 단열 공사 제10호" 삭제), "dur": 2.6, stamps[0].at = 1.8. 총 길이 25.8 -> 26.6초. 길이를 유지해야 하면 PPL dur 6.0 -> 5.4.
3. (선택, 규칙 일관) 늦은뽁 자막 y 1230 -> 380. 아침 자막은 y 1240으로 10px만 내려 띠와 간격 확보.
4. (선택) ai_label.size 34 -> 33 (갈무리 11px 격자 3배, EP09 규칙).

## [PD] preview v1 결정
- 크루 키 상한: 슬리퍼 0.7배 → 1.2배(약 150px), 뭉치 70px. creative·qa 공통 근거(훅 다리만 100px, 0.5배에서 안 보임). EP10 한정.
- 들킴 도장 위치 의견 3개(creative: 크루 무리 위 / typo: x420,y790 / qa: x520,y760) → creative안 채택(웃음 대상=크루, 고양이 비가림). 고양이와 겹치지 않는지 typo 재측정.
- 작업일지: typo안(2줄, dur 2.6, 도장 1.8) + PPL 5.4로 총 길이 유지.

## [editor] preview v2 (검수 전, 크레딧 0)
- 산출물(`output/EP10/`): `EP10_youtube.mp4`·`EP10_tiktok.mp4`·`EP10_clip.mp4`(각 26.0초), 업로드본 `EP10_{youtube,tiktok,clip}_upload.mp4`(각 약 2.7MB, 10MB 미만), 확인 시트 `EP10_v2_check.jpg`(0.5배 540x960, 0.3/3.4/5.0/7.5/10.2/11.5/13.0/18/24초), `EP10_preview.png`.
- **총 길이 26.0초**(v1 25.8). PD 지시 수치(작업일지 1.8→2.6, PPL 6.0→5.4)를 그대로 적용하면 +0.2초가 된다. 정확히 25.8초로 맞추려면 PPL을 5.2로 줄이면 된다(episode.json 한 값). 들킴 컷 시작 9.4초, 삑 9.6초, BGM 무음 9.6~11.8초는 v1과 같다.
- 항목별 수정 (재생성: `ep10_build.py s2 s3 c3 c4 t2 t1` → `ep10_make_json.py`)
  - creative 1 크루 톤: 어두운 불투명 실루엣. 몸통 = 그 자리 기포 평균 -40(띠 아래 카펫이 더 밝으면 카펫 -25 이하), 내부 디테일 0.45배, 위쪽 림 +40 2px, 반장 안전모·반사띠 국소 +50(최대 222), 접지 그림자 60%(접촉 80%), 알파는 가장자리 1px 페더만 남기고 완전 불투명.
  - creative 2 키: 반장 150px(슬리퍼 약 125px의 1.2배), 여사 108px, 콩알이 154px, 뭉치 폭 70px(#2).
  - creative 3 배치: 띠 아래 가장자리~카펫 경계, 일렬 아님. #2 발 y 1226/1252/1277(높이차 26·25px), #5·#6 1222/1247/1272, #7 884/910/936.
  - creative 4 도장: 크루 무리 바로 위(x330,y950), 고양이 비가림. 삑 0.2초 + 0.25초 = 0.45초에 찍힘(자막 '얼음!'도 0.45초).
  - creative 5 늦은 뽁: 펀치인 x2.0(중심 = 크루 무리 x0.285,y0.62), 'ZOOM x2' 라벨과 일치. 콩알이 발 하강은 펀치인 화면 기준 16px = 원본 8px로 해석해 적용(코드: 원본 8px 하강). 화면에서 정확히 16px 하강이 아니라 원본 16px을 원하면 `ep10_build.py` st_c4의 `8 if low` 값을 16으로 바꾼다. 발 닿는 프레임(2.0초)에 기포 눌림 반짝 2프레임. 고양이는 x2 화면 밖.
  - creative 6 #2: 전체 3.4~4.0초(로컬 1.0~1.6) x1.5 펀치인, 중심 크루(컷 3개로 분할, 자막 연속).
  - creative 7 #3: 여사를 분무기 방아쇠에 매달고(0~1.0초 1px 떨림 동행, 그림자 없음), 칙 직후(로컬 1.5초) 젖은 뭉치 중심 x1.6 펀치인. 뭉치 x1.25.
  - creative 8 반전: 통통 진폭 9px. 크루 150px, 고양이가 앞에 올 때는 가림 마스크로 크루가 뒤로 간다.
  - typo: 작업일지 2줄("결과: 벽 1, 고양이 침대 1" / "사유: 소음"), dur 2.6, 도장 1.8초, PPL 5.4. 늦은 뽁 자막 y380, 아침 자막 y1240.
  - qa 1 true peak: `limiter 0.8` 적용. ebur128 true peak(Peak): EP10_youtube.mp4 -1.6 dBFS, 업로드본 3종 모두 -2.1 dBFS(기준 -1.0 이하 충족).
  - qa 2·3: creative 1·2·4로 해결(9.9/10.2/11.0초 시트에서 크루 3명이 읽힘, 도장은 크루 위).
  - qa 4 T1 핫스폿: `apply_c1_fix.py` v2(마스크 페더 40→90px, 바깥 확장 110px, 핫스폿 기본 휘도 96→84 = 주변 카펫에 맞춤, 새 마스크 `C1_fix_mask_v2.png`, v1 마스크는 보존). 사각 패치 띠는 사라지고 완만한 빛 번짐만 남음.
  - qa 5 C3 뽁 싱크: 부츠 블롭 추적으로 발 닿는 시각을 구해 `c3_contacts.log`에 기록. C3_comp 로컬 기준 닿음 #1 21프레임(0.70초), #2 30프레임(1.00초, 여기서 0.2초 정지 = 프레임 30~36), #3 59프레임(1.97초, 정지 삽입 후), #4 70프레임(2.33초). 뽁은 0.70 / 1.00 / 1.97 / 2.33(4번째, 가장 큼)에 맞춤. 정지도 첫 닿음이 아닌 '두 번째 닿음'으로 이동(v1은 0.3초에 정지해 어긋났음). 0.63초 이전은 부츠가 검출 임계값 밖이라 첫 닿음은 0.70초로 추정(한계).
  - qa 7 흰 가로선: 원인은 make_cctv의 스캔라인(알파 18 흰 줄, 프레임마다 위치 이동). episode.json `"scanline": false` 선택 키를 추가해 EP10에서 끔(기본 true라 EP09 영향 없음). 11.1/11.2/12.7/13.5초 행 프로파일 검사에서 밝은 전폭 가로선 없음. 문서화된 글리치(9.6초 베이크 프레임 드롭, 11.8초 frame_drop)는 유지.
  - qa 6 마지막 0.3초 디졸브: 루프용으로 유지(변경 없음).
  - qa 8: 'ZOOM x2'가 실제 x2.0이 되어 일치.
- 하위 호환(EP09): 추가한 선택 키는 `scanline`, 컷별 `cam`, `ppl_notes_lines` 세 개뿐(기본값 = 기존 동작). EP09 8개 시점 프레임을 변경 전후 비교한 픽셀 차 평균 약 2.6~4.5, 최대 26으로 전 시점 균일한 정적 노이즈 수준(이전 비교와 같은 값, 구조 차이 없음).
- 남은 우려
  1. 실루엣이 '기포 -40'이라 회색 인물로 보인다. 0.5배 시트에서 3명이 읽히지만 더 어둡게(-55) 하려면 `Sprite` 톤식의 `bg_mean - 40`만 바꾸면 된다. creative 재판정 필요.
  2. 크루 150px는 슬리퍼 1.2배·기포 약 2개로 PD 결정 범위. 훅의 다리(100px)와 비례는 맞으나 고양이 머리(약 65px)보다 훨씬 커서 '고양이 귀 > 크루' 관계는 포기됨.
  3. #7 크루 위치(띠 왼쪽 아래)에서 고양이 앞발이 콩알이 왼팔 근처에 닿는다. 가림 마스크로 처리했으나 qa가 착지 프레임(1.4~1.7초)을 확인해야 한다.
  4. C3 첫 번째 뽁 시각은 검출 한계로 추정값. 효과음 새소리 파일 없음, 쿠팡 미확인, 상품명 원문 교체는 v1과 같다(_todo).

## [creative] EP10 preview v2 — PASS (8.2/10)
판정자: creative. v2 `EP10_youtube.mp4`(26.0초)를 v1과 같은 방식(0.5초 간격 270x480 타일 + 0.5배 540x960 단독 프레임 3.6·5.8·10.2·11.0·11.6·13.4초)으로 직접 봤다. 파일은 고치지 않았다.

| 항목 | v1 | v2 | 근거 |
|---|---|---|---|
| 훅 | 8.5 | 8.5 | 변화 없음, 통과 |
| 크루 가시성 | 2.5 | **7.5** | 0.5배에서 #2·#5·#6·#7 모두 '작은 사람 3명'이 셀 수 있게 읽힌다. 반사띠 X자 반장, 쪼그린 여사, 한 발 든 콩알이로 실루엣 3종이 구분된다. #3 여사는 방아쇠 옆 작은 형체로만 읽혀 약하다 |
| 웃음 타이밍 | 5.0 | **8.0** | 덮개가 사라지면 바로 얼음 크루가 보이고, 도장 '들킴'이 크루 위에 찍혀 고양이 고개 돌림이 보인다. 늦은 뽁 x2 화면에서 크루 3명이 크게 잡혀 '…뽁.'의 주어가 분명하다. 반전에서 띠 왼쪽 끝 크루와 철퍼덕 고양이가 한 화면에 들어온다 |
| 공포 | 9.0 | 9.0 | 없음 |
| 상품 적합도 | 8.5 | 8.5 | 그대로 |
| **종합** | 6.2 | **8.2** | PASS |

### 확인 요청 1: -40 회색 인물, 더 어둡게 해야 하나
- **-40 유지.** 0.5배에서 '회색 인물'로 충분히 읽힌다. 덜 어두워서 얼굴·옷 결이 조금 남아 피규어 느낌이 있지만, 이 화는 '얼음 = 일부러 피규어처럼'(concept_v2 1장 7항)이라 오히려 개그와 맞는다.
- -55로 내리면 밝은 기포 위에서 검은 구멍처럼 보여 반사띠·자세가 뭉개질 위험이 더 크다. 바꾸지 않는다.
- 선택(필수 아님): 반전 컷(#7)만 창 쪽 역광 때문에 크루가 가장 작고 옅다. 이 컷만 -48로 내리면 조금 낫다. 하지 않아도 PASS.

### 확인 요청 2: 들킴 → 늦은 뽁 → 반전
- 성립한다. 9.4 덮개 사라짐 → 얼음 3명 노출 → 0.45초 '들킴' 도장(크루 위, 고양이 비가림) → 정적 → x2 펀치인 '…뽁.' → 11.8 고양이 철퍼덕. 각 비트에서 웃음의 주어가 화면에 있다.

### 남은 소소한 점 (재판정 불필요)
- #3 여사 매달림은 0.5배에서 '분무기 옆 작은 것'으로만 읽힌다. 웃음은 '칙' 소리와 자막이 맡으므로 그대로 둔다.
- 크루 150px로 '고양이 귀 > 크루' 대비는 사라졌으나 고양이 몸통 대비로 충분히 작다. 결정 유지.

### 한국어 요약
1. PASS 8.2점: 크루 가시성 2.5 → 7.5, 웃음 타이밍 5.0 → 8.0으로 올라 들킴 → 늦은 뽁 → 반전이 화면에서 성립한다.
2. 몸통 -40은 0.5배에서 '회색 인물'로 읽히므로 유지한다. -55는 검은 구멍처럼 뭉개질 위험이 있어 하지 않는다(반전 컷만 -48은 선택).
3. #3 여사 매달림은 여전히 작게 읽히지만, 웃음은 소리와 자막이 맡으므로 재작업하지 않는다.

## [typographer] EP10 preview v2 재실측 (2026-10-10, 26.0초, 프레임 10장 0.5배 + 폰 크기 확인)
판정: PASS (WARN 1건, 선택).
- 들킴 도장(x330,y950): PASS. 도장 박스 x216~445, y875~1028, 고양이 침대 x700~890라 겹침 없음. 크루 무리(반장 헬멧 y1074)와 약 50px 간격. 감지 라벨과 겹침 없음. 참고: 도장이 슬리퍼(소품)를 덮는다(피사체 아님, 무시 가능).
- 작업일지 2줄: PASS. 줄 2개 16자(공백 제외)가 시작부터 보이고 도장은 1.8초에 찍힘. 전체 노출 기준 6.2자/초(권장 6~8), 도장 전 1.8초 기준 8.9자/초(상한). 도장이 카드 우하단 밖으로 약 40px 나오는 것은 의도된 연출.
- 늦은 뽁 자막 y380 / 아침 자막 y1240: PASS. 아침은 띠 하단(y1224)과 약 20px 간격, 디스클로저 박스와 60px 이상 간격. 늦은 뽁 자막은 x2 확대 후 슬리퍼 끝을 일부 덮음(WARN, 소품이라 유지 가능).
- ZOOM x2 라벨: PASS. 실제 x2.0 확대(0.6~0.8초)와 일치, 라벨은 0~1.0초 깜빡임(확대 전 0.6초 예고 포함), 자막·AI 라벨과 겹침 없음.

## [qa] EP10 preview v2 — PASS (권고 2건 포함)
검수자: qa. v2 youtube/tiktok/clip 본편 3개와 업로드본 3개를 ffmpeg로 직접 열어 확인했다. 파일은 고치지 않았다. 총 길이 26.0초는 PD 허용분.

### v1 FAIL 3건
1. true peak: 본편 3종 -1.6dBFS, 업로드본 3종 -2.1dBFS(ebur128). 기준 -1.0 이하 PASS.
2. 들킴 이후 크루: 10.0·10.5·11.0초 시트와 11.5초(x2 펀치인)에서 회색 불투명 실루엣 3명이 읽힌다(반장 안전모, 여사, 콩알이 한 발 든 포즈). 반투명 유령 느낌은 없다. PASS. 다만 13초대 반전 컷의 크루는 밝은 회색이 섞여 약간 흐리다(권고).
3. 도장: 10.0~10.8초 '들킴'이 크루 위 빈 카펫에 찍히고 고양이를 가리지 않는다. PASS.

### 권고 사항
- T1 경계(0.5·2.0초 1080 크롭): v1의 회색 사각 패치 띠가 사라지고 완만한 빛 번짐만 남는다. PASS.
- 흰 가로선: 전 프레임 행 프로파일 스캔 결과 전폭 밝은 선은 0.07(전환), 2.47(전환), 9.6(문서화 글리치), 11.8~11.87(문서화 frame_drop)뿐이다. 11.1·11.2·12.7·13.5초에는 없다. PASS.
- C3 뽁 싱크: c3_contacts.log 대로 뽁 7.6/7.9/8.87/9.23초(= 6.9+0.70, +1.00, 8.5+0.37, +0.73)가 오디오 피크(7.6, 7.9, 8.87, 9.23초, 마지막이 -6.7dB로 최대)와 일치한다. 7.6초·9.23초 프레임은 발이 모여 닿은 자세, 7.9·8.87초는 걸음 중간으로 0.1초 시트로는 접지 프레임 여부를 단정하지 못했다. 로그 신뢰 PASS(추정 한계는 editor 기재대로 첫 닿음).
- 삑 9.6초, 무음 구간(10.5~11.35초 -30dB 룸톤), 11.4초 뽁(-5.7dB), 11.8초 복귀 확인.

### #7 반전 착지 (12.9~13.65초, 0.15초 간격 6장)
고양이 앞발이 크루 오른쪽 둘 앞에 놓이고, 콩알이(밝은 회색, 세 번째)의 발과 고양이 앞발이 겹치는 부분은 크루가 뒤로 가는 가림 처리가 되어 있다. 앞발이 크루를 덮거나 크루가 앞발 위로 뜨는 프레임은 없다. 고양이 눈 발광 없음. PASS. 크루 밝기(밝은 회색)가 반장보다 높아 약간 떠 보이는 점은 권고.

### 업로드본 3종
| 파일 | 규격 | 용량 | CTA(PPL 카드 버튼) | 판정 |
|---|---|---|---|---|
| EP10_youtube_upload.mp4 | 1080x1920 30fps 26.0초 | 2.71MB | 링크는 영상 설명란에 | PASS |
| EP10_tiktok_upload.mp4 | 동일 | 2.73MB | 네이버·쿠팡에서 위 상품명 검색 | PASS(쿠팡은 미확인 상태 — 아래) |
| EP10_clip_upload.mp4 | 동일 | 2.70MB | 화면 스티커를 눌러 보세요 | PASS |
- 가격·리뷰·평점(6,180원 / 1,598개 / 4.94 / 10/9)과 '단열 효과: 이 영상에선 측정 안 함'은 3종 동일. 대가성 문구 원문은 youtube/clip txt 모두 설명란·고정 댓글에 있고, tiktok txt에도 있다. 링크 https://naver.me/FaeW9AkP = episode.json. 클립 txt에는 상품 링크 대신 스티커 안내.
- 주의: 틱톡 CTA가 '네이버·쿠팡에서 검색'이지만 쿠팡 상품은 아직 미확인(product_alt_pending)이다. 쿠팡에서 같은 상품이 실제로 검색되는지 PD가 확인하거나 CTA를 '네이버에서 검색'으로 바꿔야 한다(업로드 전 항목).

### 한국어 요약
1. v2는 PASS다. true peak -1.6/-2.1dBFS, 들킴 후 크루 가독, 도장 위치가 모두 해결됐다.
2. T1 경계, 흰 가로선, C3 뽁 싱크(오디오 피크가 접촉 로그와 일치)와 반전 착지 가림 처리도 통과했다.
3. 업로드본 3종은 규격·용량 통과이며, 틱톡 CTA의 '쿠팡 검색'은 쿠팡 상품 확인 전까지 업로드 보류 항목이다.

## [editor] v2.1 상품 반영
- 바꾼 것(상품 정보만): 네이버 상품명 원문 전체(`...테포르 33cm - 10m, 1개`), 6,180원 / 평점 4.95 / 리뷰 1,604 / 기준일 10/10(aeo_line 포함). 1m당 약 618원 유지.
- 쿠팡(다른 상품)은 product_alt로 이동: 셔니엘 자석식 창문 방풍뽁뽁이 외풍차단 바람막이 (옵션 S 150*120cm), 25,800원, 리뷰 345개, 평점 미표시, 링크 hH27FMl3rE. 클립판은 네이버만(카드 1장).
- 업로드 txt: youtube/tiktok에 쿠팡 링크·쿠팡 대가성 문구 원문, 고정 댓글 영역에 두 문구 모두 포함(EP07/08과 같이 config disclosure_text 자동 생성). pinned_comment 필드에서는 네이버 문구 중복 줄을 뺐다(clip txt에 쿠팡 문구가 섞이지 않게). 틱톡 CTA 그대로.
- _todo: 상품명·쿠팡 항목 삭제, 가격 항목 기준을 10/10으로 갱신.
- 코드: make_cctv.py ppl_two에서 한 줄에 안 들어가는 상품명은 2줄(24~28px)로 그린다(단어 생략 방지, 기존 EP07/08 카드는 한 줄이라 영향 없음). 백업: episode_v2.json.bak, ep10_make_json_v2.py.bak.
- 렌더: 본편 3종 true peak -1.6 dBFS, 업로드본 3종 -2.1 dBFS(기준 -1.0 이하 통과). 업로드본 youtube 2.67MB / tiktok 2.67MB / clip 2.74MB(10MB 미만). 길이 26.0초 그대로.
- PPL 카드 3종: output/EP10/EP10_v21_ppl.jpg (왼쪽 youtube, 가운데 tiktok, 오른쪽 clip).
- 남은 우려: 2상품 카드의 상품명이 약 22px로 작아 폰에서 읽기 힘들 수 있음(타이포 확인 요청). 쿠팡 평점 미확인으로 미표시. 가격이 7천원 이상으로 오르면 제목 '6천원대' 수정.

## [typographer] v2.1 — FAIL (youtube·tiktok 2상품 카드만, clip 1상품 카드는 PASS)
실측: EP10_{youtube,tiktok,clip}_upload.mp4 23초 프레임을 1080 원본과 390px 축소로 직접 확인. 파일은 고치지 않았다.

### 판정 근거
1. **상품명이 작다 (youtube·tiktok)**: 상품명 약 22px(x높이 기준 실측 한 글자 폭 약 20px). 390pt 환산 8pt 안팎이라 'ㅂ/ㅍ' 받침이 뭉쳐 읽힌다. 권장 하한 26px(약 9.4pt).
2. **가격이 상품명 둘째 줄을 눌러서 겹친다**: 네이버 카드는 둘째 줄 '롤 창문 단열…'과 '6,180원' 윗면이 맞닿고, 쿠팡 카드는 '외풍차단 바람막이'의 받침이 '25,800원' 윗면과 겹친다(1080 원본에서 확인, 390에서는 한 덩어리로 뭉침). 상품명 행간도 약 1.0으로 너무 빡빡하다.
3. **단어 누락 없음**: 네이버 전문(국내산 … 33cm - 10m, 1개) 일치. 쿠팡은 '셔니엘 자석식 창문 방풍뽁뽁이 외풍차단 바람막이' 일치, 뒤에 '(S 150*120cm)'가 더 붙었다(옵션 표기. 상품 페이지 표기와 같다면 유지, 다르면 삭제).
4. 겹침·잘림: 위 2번 외에 없다. 가격(약 70px)·리뷰(약 34px)·기준일·안내 2줄·광고 고지(흰 글자 / 어두운 바탕, 대비 15:1 이상)는 390에서 읽힌다. 리뷰줄·'단열 효과' 빨간 줄(빨강 #C62F1B 근처 / 크림, 약 5:1)도 통과.
5. clip 카드(상품 1개, 상품명 약 40px 굵게)는 겹침·누락 없이 PASS.

### 고칠 값 (editor 사양, youtube·tiktok 2상품 카드)
- 상품명: 22px -> **27px**, Pretendard Medium/SemiBold, 행간 **1.3**(35px), 2줄 고정. 줄 폭은 배지 오른쪽 ~ 박스 안쪽 끝 약 580px. 27px에서 첫 줄 '국내산 두꺼운 뽁뽁이 포장용 에어캡 완충'(21자)은 약 560px로 들어간다. 안 들어가면 26px, 그래도 안 되면 배지를 윗줄로 올리고 폭 700px를 쓴다.
- 상품 박스 높이: 현재 약 190px -> **약 235px**. 구성은 [배지+상품명 2줄 70px] -> 간격 **10px** -> [가격 64~70px] -> 간격 6px -> [리뷰 32px]. 가격은 상품명 박스 아래로 내리고 y가 겹치지 않게 한다.
- 두 박스 합계 +90px 늘어나므로 카드 전체를 아래로 키운다. 현재 카드 하단(약 y1230)~광고 고지(y1460) 사이와 y1500 이하가 비어 있다. 단, 광고 고지(y~1460)가 앱 UI 안전선(y 1500 이하)을 넘지 않게 한다. 안내 2줄 'AI 연출…' 박스를 줄이지 말고 CTA 버튼 위 간격(약 20px)·기준일 간격을 줄여 흡수한다.
- 가격 글꼴 크기·리뷰·광고 고지·AI 연출·OSD는 그대로 둔다.
- 쿠팡 옵션 '(S 150*120cm)'는 상품 페이지 표기 확인 후 유지/삭제를 editor가 결정.
- 재확인: 수정본 EP10_v21_ppl.jpg와 youtube_upload 23초 프레임을 390px로 줄여 상품명 두 줄이 가격과 안 닿는지 다시 본다.

### 한국어 요약
1. FAIL: 2상품 카드(youtube·tiktok)에서 상품명 22px(8pt대)이 작고, 가격이 상품명 둘째 줄과 겹친다. 단어 누락은 없다(쿠팡은 '(S 150*120cm)'가 덧붙음). clip 카드는 PASS.
2. 수정: 상품명 27px, 행간 1.3, 가격과 간격 10px, 박스 높이 약 190 -> 235px, 카드를 아래로 키우되 광고 고지는 y1500 이내.

## [qa] v2.1 — PASS
검수 대상: output/EP10/EP10_{youtube,tiktok,clip}_upload.mp4 + txt 3종 + episode.json (파일 직접 확인, 22초 PPL 프레임 3종 추출)
1. PPL 카드(22.0초 프레임): youtube·tiktok = 네이버 6,180원 / 리뷰 1,604개 / ★4.95 + 쿠팡 셔니엘 25,800원 / 리뷰 345개(평점 미표시), clip = 네이버 1장만. 모두 episode.json과 일치. 상품명 잘림·겹침 없음(확대 확인, 가격과 상품명 줄이 근접하나 닿지 않음). 기준일 10/10 표기.
2. 대가성 문구(grep -F 원문 일치): youtube txt 네이버 2회·쿠팡 2회(설명란+고정 댓글), tiktok txt 각 1회, clip txt 네이버 2회·쿠팡 0회. 모두 CLAUDE.md 원문과 토씨 동일.
3. 링크: youtube txt 네이버·쿠팡 각 3회 모두 episode.json과 동일, clip txt 네이버만, tiktok은 링크 없이 상품명 검색 안내(기존 정책 그대로).
4. 제목 "6천원대" = 6,180원 일치. 효능 단정 없음(카드 "단열 효과: 이 영상에선 측정 안 함", 설명란 "실제 효과와는 관계없어요").
5. 규격: 3종 모두 1080x1920, 26.000초, true peak -2.1 dBFS(기준 -1.0 이하), 2.67/2.67/2.74MB, AI 고지 "AI 상황극"(0~3.0초, 2.5초 프레임 확인) 후 "AI 연출" 상시, 마지막 카드에 AI 문구.
- 주의(차단 아님, 기록): product.md의 네이버 값은 아직 4.94 / 1,598(10/9, ref/naver_product.png)이다. 영상·txt의 4.95 / 1,604(10/10)는 의뢰서 기준과는 일치하지만 product.md에 근거 기록이 없다. 담당자는 product.md에 10/10 확인값을 추가하고, 업로드 직전 PD가 재확인할 것(다르면 재제작).
- 주의: 쿠팡 카드는 평점 없이 리뷰 345개만 표시(product.md에도 평점 없음, 정합).

### 한국어 요약
1. v2.1은 PASS: 카드 숫자·대가성 문구 원문·링크·6천원대·규격(26.0초, -2.1dBFS, 2.7MB)이 모두 맞다.
2. product.md에는 4.94/1,598(10/9)만 남아 있어 10/10 값(4.95/1,604) 근거 기록을 추가하고 업로드 직전 재확인할 것.

## [editor] v2.2 2상품 카드 타이포 수정 (typographer v2.1 FAIL 반영)
- 상품명 27px(안 들어가면 26), 행간 1.3, 상품명-가격 간격 10px, 박스 높이 235px(간격 10), 카드 높이 +40(PPL_V6_EXTRA). AI 안내 박스는 y1288~1396, 광고 고지 y~1440(1500 이내).
- 쿠팡 옵션은 상품명에서 빼고 가격 줄 앞 "S(150×120cm) 25,800원"으로 이동(episode.json product_alt.option). 상품명은 원문 그대로. txt에는 "옵션 S(150×120cm)"로 표기.
- 새 레이아웃은 episode.json "ppl_layout": "v6"일 때만 켜짐 -> EP07/EP08(키 없음)은 기존 경로 그대로. EP07/08 --preview 정상 렌더(그레인 때문에 PNG 해시는 실행마다 달라 바이트 비교는 불가). clip 카드 무변경.
- 재렌더: youtube/tiktok 마스터 -1.6dBFS, 업로드본 -2.1dBFS, 2.74MB/2.75MB. 프레임: output/EP10/EP10_v22_ppl.jpg. 백업 make_cctv_v21.py.bak.
- 남은 우려: 상품명이 26~27px 한계라 폰에서 여전히 작음(타이포 재확인 요청). 쿠팡 카드는 상품명이 1줄이라 가격 위 여백이 큼.

## [typographer] v2.2 — PASS (youtube·tiktok 2상품 카드)
실측: youtube·tiktok upload 23초 프레임을 1080 원본과 390px로 직접 확인. 파일은 고치지 않았다.
- 겹침 해소: 가격이 상품명 둘째 줄과 닿지 않는다(네이버 둘째 줄과 6,180원 사이 약 10px). 쿠팡은 상품명 1줄(원문 전체 한 줄에 들어감), 옵션은 가격 줄 'S(150x120cm)'로 이동. 잘림 없음.
- 단어 누락 없음: 네이버 전문·쿠팡 '셔니엘 자석식 창문 방풍뽁뽁이 외풍차단 바람막이' 모두 일치.
- 390pt: 상품명 27px는 약 9.8pt로 읽힌다(하한선 근처, 통과). 가격·리뷰·'단열 효과'·CTA·기준일·광고 고지·AI 연출 고지 모두 읽힌다. 광고 고지는 y1440대로 안전선 내.
- 권고(차단 아님): 쿠팡 박스 상품명 아래~가격 사이 여백이 크다(상품명 1줄이라). 박스 높이를 줄여 약 30px 회수하거나 상품명 폰트를 28px로 키워도 된다. 쿠팡 박스 하단과 '단열 효과' 빨간 줄 간격이 약 10px로 빡빡하니 +8px 권장.

## [publisher] 배포 보고 — 예약 완료 (2026-10-10)
- 채널: 새벽3시CCTV (UCs2-cOHrNbt4gkZUZJ0FVmw) 확인 후 Studio에서 업로드.
- 영상 URL: https://youtube.com/shorts/shrmvSMGmGM (파일 EP10_youtube_upload.mp4, 0:27)
- 예약 시각: 2026-10-11 19:00 KST (예약 완료 대화상자 "2026년 10월 11일 19:00에 공개 상태로 설정" 확인, 콘텐츠 목록 공개 상태 '예약됨'·날짜 2026.10.11.)
- 되읽어 확인한 항목: 제목 "[AI 상황극] 창문 단열 뽁뽁이 6천원대, 새벽 3시 CCTV 속 공사팀" 일치 / 설명 첫 줄 "[AI 상황극] 영상 속 장면은 AI 연출이며 실제 제품의 성능과 다릅니다." 일치 / 링크 2개(naver.me/FaeW9AkP, link.coupang.com/a/hH27FMl3rE) 존재 / 대가성 문구 2종(네이버 쇼핑 커넥트, 쿠팡 파트너스) 토씨 그대로 존재 / 해시태그 5개 / 아동용 아님 / 유료 프로모션 '예' / AI(변경·합성) '예' / 공개 범위 예약됨. '업로드 전 체크' 메모는 게시하지 않음.
- 미확인: 목록 화면은 시각 없이 날짜만 표시(시각은 업로드 직후 대화상자로 확인). 썸네일 자동. 같은 날 EP09 아닌 다른 영상(고양이 털 제거 편)은 10/11 예약으로 이미 표시되어 있음: 목록에 10/11 예약이 2건이므로 PD가 시각 충돌 여부 확인 필요.
- 공개 후 할 일(영수 님, 고정은 영수 님 몫): 2026-10-11 19:00 이후 EP10_youtube.txt 21~31행 문구(대가성 2종 + 링크 2개 + 영상은 AI 상황극)를 첫 댓글로 달고 고정.

## [creative] EP10 이야기 진단: 영수 님 피드백("이야기가 안 되고, 웃음이 적고, 뭘 말하는지 모르겠다") 수용
- 판정자는 creative다.
- `output/EP10/EP10_youtube.mp4`(26.0초)를 **무음으로, 기획서를 모르는 시청자 입장에서** 다시 봤다.
  - 0.5초 간격 타일과 0.4배 단독 프레임(3.0·5.5·10.2·13.4·16.5초)을 썼다.
  - EP09(29.7초)도 같은 방식으로 보고 비교했다.
  - 오디오 배치는 episode.json의 sfx 표로 확인했다.
- 파일은 고치지 않았다.

**결론: 피드백이 맞다.**
- 문제는 길이가 아니라 구조다. 설정(목표·규칙·위협)이 화면에 한 번도 나오지 않는다.
- 웃음은 거의 다 '뽁' 소리에 걸려 있어서 무음 시청자에게는 사라진다.
- 지난 8.2점은 기획서를 아는 판정자가 소리를 켜고 비트별 가시성만 채점한 결과였다.

### 1. 무음 첫 시청 판독표 (1초 단위)
| 초 | 화면 | 시청자가 이해한 것 | 의도 | 차이 |
|---|---|---|---|---|
| 0–1 | 다리 달린 뽁뽁이가 걷는다. 감지 박스와 "뽁뽁이가 걸어간다" | 뽁뽁이 밑에 작은 다리가 있다. 신기하다 | 훅: 공사 크루 등장 | 통과 |
| 1–2 | ZOOM x2, "사람 3명 추정" | 소인 3명이 뭔가를 나른다 | 같음 | 통과. 다만 **왜 나르는지는 없다** |
| 2–3 | 장면이 바뀌어 띠가 바닥 아래쪽에 깔려 있고 회색 인형 3개가 있다. ① "단열판 운반 완료" | 뽁뽁이를 바닥에 내려놨다. '단열판'이 뭔지는 모른다 | 작전 ①: 창문 단열 공사 시작 | **목표가 전달되지 않는다.** 띠가 창이 아니라 바닥에 있다 |
| 3–4 | 정지, x1.5 펀치인 | 인형 3개가 서 있다 | 크루가 옮겼다는 증거 | 정지 포즈라 '일하는 사람'이 아니라 '세워 둔 피규어'로 읽힌다 |
| 4–5 | 크루보다 4~5배 큰 분무기, ② "접착수 살포" | 분무기가 있다. '접착수'는 모른다 | 물을 뿌려 유리에 붙이는 공정 | **분무기가 유리가 아니라 바닥을 향한다.** 크기 비례도 깨진다 |
| 5–6 | 칙, 안개 | 뭔가 뿌렸다 | 칙! | 무음에서 약하다 |
| 6–7 | 확대, "뭉치 먼저 세척됨" | '뭉치'가 누군지 모른다(첫 등장). 점 하나가 젖었다 | 마스코트가 맞고 엉덩방아 | 웃음 0. 처음 나온 캐릭터에 개그를 걸었다 |
| 7–8 | 거대 슬리퍼가 다리로 걷는다. ③ "슬리퍼로 위장 복귀" | 슬리퍼 밑에 사람이 있다. 웃기다 | 무소음 이동 | **이번 화에서 가장 좋은 그림이다.** 다만 소리를 내면 왜 안 되는지 모르니 긴장은 없다 |
| 8–9 | "…뽁?" | 의성어 자막 하나 | 뽁 4박자와 멈칫 | 무음에서는 **박자 개그가 통째로 사라진다.** 발밑에 소리 글자가 없다 |
| 9–10 | 슬리퍼가 사라지고 회색 인형 3개. 고양이가 방석에서 고개를 든다. "얼음!" | 고양이가 깼다. 인형은 아까와 같은 자세다 | 들킴과 얼음 | **얼음의 대비가 없다.** 크루는 2.4초부터 줄곧 같은 정지 포즈라 굳은 것이 보이지 않는다. 고양이가 위협이라는 것도 이때 처음 나온다 |
| 10–11 | '들킴' 도장 | 누가 누구에게 들켰다 | 같음 | 고양이가 화면 위쪽 구석에 작게 있어, 누가 누구에게 들켰는지가 약하다 |
| 11–12 | x2 펀치인, "…뽁." | 인형 3개가 확대된다 | 늦은 뽁(가장 큰 웃음 예정) | 6px 발 내림이 안 보인다. 무음이면 아무 일도 없는 컷이다 |
| 12–13 | 글리치 뒤 띠가 창 아래로 옮겨져 있고 고양이가 걸어 나온다. "정보원이 제일 시끄러움" | 고양이가 움직인다. '정보원'이 뭔지 모른다 | 반전: 깨우면 안 되는 정보원이 직접 뽁뽁 소리를 낸다 | **'정보원' 설정이 한 번도 나오지 않았다.** 띠 위치가 튀어서 같은 방인지도 헷갈린다 |
| 13–15 | 고양이가 띠 옆 카펫에 눕는다 | 고양이가 누웠다. 귀엽다 | 철퍼덕, 뽁뽁뽁뽁 연타 | 고양이 몸은 대부분 띠가 아니라 카펫 위에 있다. 무음이면 '시끄러움'의 근거가 없다 |
| 15–16 | REPLAY 0.5x, "판독: 고의 아님" | 무엇을 판독하는지 모른다 | 고의로 뽁뽁 소리를 낸 게 아님 | 판독할 대상이 없는 판독이다 |
| 16–18 | 세피아 아침. 창 가운데에 띠가 세로로 붙어 있다. "결국 세웠다(벽에)" | 아침이다. 창에 뽁뽁이가 한 줄 붙었다 | 공사 실패, 벽에 기대 둠 | **화면은 '붙었다(성공)'로 보이는데 자막은 '세웠다(벽에)'라서** 서로 어긋난다 |
| 18–20 | 작업일지 "결과: 벽 1, 고양이 침대 1 / 사유: 소음" → 반려 | 뭔가 반려됐다 | 행정 개그로 마무리 | 목표가 앞에 나오지 않아 '반려'가 무엇의 실패인지 모른다. 가장 잘 이해되는 순간이 결말이라 이미 늦다 |
| 20–26 | PPL "뽁뽁이 공사 크루 채용" | 뽁뽁이 광고 | 같음 | 카피는 좋다. 여기서야 '공사'가 이해된다 |

**판독 요약**
- 무음 시청자가 확실히 따라가는 것은 네 장면뿐이다: 걷는 뽁뽁이 → 슬리퍼 위장 → 고양이가 깸 → 고양이가 누움.
- **'단열 공사', '소리 금지', '고양이 = 깨우면 끝', '정보원', '뭉치'** 다섯 개념은 화면에 없거나 단어로 한 번 지나갈 뿐이다.

### 2. 이야기 뼈대 점검
| 요소 | 기획 | 화면 | 판정 |
|---|---|---|---|
| 누가 | 공사 크루 3 + 마스코트 뭉치 | 회색 인형 3(줄곧 같은 정지 포즈), 뭉치는 점 하나 | 약함. 살아 있는 주인공이 훅 2.4초와 슬리퍼 2.5초에만 움직인다 |
| 원한다 | 소음 없이 창문 단열 | '단열판' 한 단어. 띠는 끝까지 바닥에 있고 창 쪽으로 가지도 않는다 | **불성립** |
| 방해 | 자는 고양이(정보원)가 소리에 깸 | 고양이는 9.6초에야 처음 의미를 얻는다. '소리 = 위험' 규칙은 소리를 켜야만 짐작된다 | **불성립**(무음), 약함(소리 켬) |
| 시도 | 작전 ①②③ | ①은 결과만 있다. ②는 방향(바닥)과 비례가 틀렸다. ③만 성립한다 | 1/3 |
| 위기 | 뽁 → 들킴 → 얼음 | 들킴은 보이지만 얼음은 대비가 없다 | 절반 |
| 반전 | 깨우면 안 되는 고양이가 제일 시끄럽다 | '정보원'이라는 말이 반전 자막에서 처음 나와, 반전이 아니라 새 정보가 된다. 고양이도 띠 위가 아니라 옆에 눕는다 | **불성립** |
| 결말 | 일을 못 해 반려(사유: 소음, 정작 소음은 고양이) | 아침 화면은 '붙음'인데 자막은 '세웠다(벽에)'다. 범인이 고양이라는 억울함이 쓰여 있지 않다 | 의미 불명 |

- **목표 '소음 없이 단열 공사'가 전달되나?** 아니다.
  - 단열은 '단열판' 한 단어와 PPL에서만 나온다.
  - 소음 금지는 어디에도 쓰여 있지 않다.
- **결말과 반전이 읽히나?** 아니다.
  - 반전에는 두 줄이 필요하다. '깨우면 안 된다'와 '그런데 그 고양이가 제일 시끄럽다'. 앞줄이 없다.
  - 결말 '반려(사유: 소음)'는 억울함이 핵심인데, '범인은 고양이'라는 연결이 쓰여 있지 않다.
- **EP09와 비교**
  - EP09의 흐름:
    1. 0초 "아무도 없는데?"
    2. 판독 "이거… 사람 맞음?"
    3. 목표가 보이는 작전: 털 도로 착공, 즉 고양이 털을 롤러로 치운다.
    4. 들킴
    5. 고양이가 다시 털어 원상복구
    6. 일지 "결과: 원상복구 / 사유: 고양이"
    7. 07:30 사람 손이 롤러를 쓴다.
  - EP09는 **목표·방해·결과가 모두 같은 물체(털, 롤러) 위에서 보였다.**
  - EP10은 목표(창)와 행동(바닥)이 다른 곳에 있다.

### 3. 웃음이 약한 원인
1. **셋업 없이 페이오프만 있다.** '소리 금지'를 깔지 않아서 세 웃음(뽁 박자, 늦은 뽁, 철퍼덕 연타)이 모두 근거를 잃는다. 웃음 지도 8개 중 5개가 이 한 줄에 매달려 있었다.
2. **개그가 소리에만 실려 있다.** 핵심 웃음은 모두 오디오다(뽁 4박자, 0.6초 정적 뒤 '…뽁.', 뽁뽁뽁뽁 연타). 쇼츠는 무음이나 작은 소리로 보는 경우가 많은데, 이 소리를 대신할 그림(발밑 의성어, 소음계, 고양이 귀 반응)이 화면에 없다.
3. **대비가 없다.** '얼음'은 움직이던 것이 멈출 때 웃기다. 크루 레이어는 처음부터 얼음 포즈 하나뿐이다(편집 기록 v1 우려 2번). 2.4~11.8초 내내 같은 자세라 들킴 전후가 똑같다.
4. **반복과 리듬이 무너졌다.**
   - 작전 ①②③은 같은 패턴(시도 → 작은 실패)으로 쌓여야 ③에서 터진다.
   - 그런데 ①은 결과 정지 화면이고, ②는 대상이 불명확하며, ③만 움직인다.
   - 처음 나온 '뭉치'에 개그를 거는 등, 반복 대신 새 정보가 계속 들어온다.
5. **캐릭터 반응이 구조적으로 없다.**
   - 크루는 역광 실루엣이라 얼굴이 없고, 고양이는 '얼굴 금지'라 뒷모습뿐이다. 웃음을 받아 줄 얼굴이 하나도 없다.
   - EP09는 고양이 얼굴이 나왔고, 사람 손(07:30)과 '눈 마주침' 판독이 리액션을 맡았다.
6. **자막이 보고서체다.** "운반 완료 / 접착수 살포 / 세척됨 / 위장 복귀 / 판독: 고의 아님"은 상황 설명이지 농담이 아니다. 무음에서 유일한 정보 채널인 자막이 웃음 대신 전문 용어를 나른다.
7. **짧아서가 아니다.**
   - 11비트를 26초에 넣어 비트당 평균 2초다. 셋업에 쓸 1.5~2초가 없었다.
   - 이야기를 닫던 '인간도 밟는다' 콜백(07:30)이 편집 단계에서 자산이 없어 빠졌다.

### 4. 지난 8.2점 판정이 놓친 것
- **채점표에 이야기 이해도 항목이 없었다.**
  - 항목은 훅 / 크루 가시성 / 웃음 타이밍 / 공포 / 상품 적합도였다.
  - '무음 첫 시청자가 목표·방해·결과를 말할 수 있나'를 보지 않았다.
  - 그래서 비트마다 주어가 보이는지만 확인했고, 비트끼리 이어지는지는 보지 않았다.
- **저자 시점 채점이었다.** 판정자가 콘티를 쓴 본인이라 머릿속 설정('정보원', '소음 금지', '단열')으로 빈칸을 채웠다.
- **소리를 켜고 채점했다.** 웃음 타이밍 8.0은 뽁 박자를 들은 점수였다. 무음 시청은 따로 채점하지 않았다.
- **상대 개선에 끌렸다.** v1 6.2 대비 크게 오른 점수(크루 가시성 2.5 → 7.5)를 보고, 절대 기준이 아니라 개선 폭으로 PASS를 줬다.
- **콘티를 줄인 뒤 다시 확인하지 않았다.**
  - 자산 부족으로 마스코트·눈알 버튼·인간 콜백을 빼고 29.4 → 25.8초로 줄였을 때, 줄인 이야기가 닫히는지 재검토하지 않았다.
  - 아침 이미지(S1)는 '붙음'으로 보이는데 '세웠다(벽에)'로 전용해 결말이 꼬였다.
- **시정**
  - 앞으로 creative 판정표에 **'무음 콜드 리드'**를 필수 항목으로 넣는다. 이 화를 모르는 사람이 15초 시점과 끝에서 이야기를 한 문장으로 말할 수 있는지를 본다.
  - 이 항목이 7점 미만이면 다른 점수와 관계없이 PASS를 주지 않는다.
  - 판정 방법: 기획서를 읽지 않은 에이전트(sonnet)에게 무음 프레임만 주고 줄거리를 받아 써서 로그라인과 비교한다.

### 5-a. EP10 재편집안 (무료, 기존 소스만, 크레딧 0)
**길이 판단: 35~40초로 늘리지 않는다. 26~28초로 간다.**
- 새 장면 없이 늘리면 정지 화면만 길어진다.
- 필요한 것은 설정 2초와 소리를 보여 주는 장치다. 나머지는 빼고 바꿔서 만든다.
- 성과 데이터(평균 17초에서 이탈)로 봐도 30초 안쪽이 맞다.

**핵심 장치 3개 (전 구간)**
1. **소음계 OSD**
   - 화면 오른쪽 위에 CCTV 계기를 둔다. 세로 막대와 dB 숫자로, 초록에서 빨강으로 바뀐다.
   - 뽁마다 막대가 튄다. 고양이 방석 옆 '수면 중 zzz' 라벨은 소음계가 빨강에 닿으면 꺼진다.
   - **무음 시청자에게 '소리 = 위험'을 그림으로 준다.** make_cctv OSD 오버레이로 만들 수 있고, 글꼴은 OSD 글꼴이다.
2. **발밑 의성어**
   - 뽁마다 발이 닿는 자리에 '뽁' 글자를 0.3초 띄운다.
   - 글꼴은 OSD가 아닌 만화체 효과음 글꼴로, 타이포팀이 정한다.
   - 4번째 뽁, 늦은 뽁, 철퍼덕 연타는 크게 쓴다.
3. **고양이 라벨**
   - 0~9초 동안 방석 위에 감지 라벨 "집주인 고양이 · 수면 중(깨우면 철수)"을 붙인다. EP09의 "뭉치·공사 가족(추정)" 라벨 방식이다.
   - '정보원'이라는 말은 쓰지 않는다.

**장면 순서 (새 타임라인)**
| 새 시간 | 소스 | 처리 | 자막(8~14자) | 소리 |
|---|---|---|---|---|
| 0.0–2.4 | 훅 T1_hook | 그대로 | "뽁뽁이가 걸어간다" → "사람 3명 추정" | 그대로 |
| 2.4–4.4 | 훅 마지막 프레임 정지(크루가 창 쪽을 향함) + **작업지시서 카드** | 카드는 작업일지와 같은 종이, 화면 위쪽 1/3. 창에 점선 박스와 '여기' 화살표. 고양이 라벨이 나타난다 | 카드 3줄: "작업지시 #010 / 창문 단열 1장 / ※ 소리 내면 철수" (2초 안에 읽힘) | 종이 착, BGM 유지 |
| 4.4–6.4 | S2_comp(①) | 자막만 바꾼다. 소음계 0 | ① "살금살금 운반" | 끙차(작게), 소음계 0 유지 |
| — | S3_comp(②) **삭제** | 분무기 방향(바닥)과 크기 비례가 이야기를 흐린다. 뭉치 첫 등장 개그도 같이 뺀다 | — | — |
| 6.4–9.2 | C3_comp(③) | 발밑 '뽁' 글자 4개. 소음계 20 → 45 → [멈칫 정지] → 60 → 85(노랑). 고양이 라벨 'zzz'가 흔들린다 | ② "슬리퍼로 위장" → "…들리나?" | 뽁 4박자 그대로 |
| 9.2–10.6 | C4_comp(들킴) | 소음계 빨강 'MAX'. 고양이 라벨이 "수면 중"에서 **"기상"**으로 바뀌고 빨간 박스가 된다. 도장 '들킴'은 그대로 둔다. 크루가 슬리퍼 밑에서 드러나는 순간 **크루 레이어를 2프레임 동안 12px 위로 튀게 한 뒤 굳힌다.** 움직임 → 정지 대비를 편집으로 만든다 | "얼음!" | 삑, BGM 정지 |
| 10.6–11.6 | C4_comp(늦은 뽁) | 펀치인 유지. 발밑에 큰 '…뽁.' 글자. 소음계가 다시 한 칸 오른다 | 자막 삭제(화면에 글자가 있으므로) | 정적 0.6 → 뽁 |
| 11.6–14.4 | T2_comp(반전) | 고양이 라벨 "집주인 고양이"가 따라붙는다. 고양이가 눕는 순간(원본 1.1초) 띠 쪽에 '뽁뽁뽁뽁' 글자 연타. 소음계가 화면 밖으로 튀어 나가 **'측정 불가'**. 띠 위치 점프는 글리치로 가린 그대로 둔다 | "범인은 집주인" | 뽁뽁뽁뽁 + BGM 복귀 |
| 14.4–15.6 | T2_comp(다시보기 0.5배) | 그대로 | "판독: 소음원 = 고양이" | 뽀오옥 |
| 15.6–17.8 | S1_warm(아침) | 띠가 창에 한 줄 붙은 화면을 '성공'으로 읽게 한다 | "07:30 시공 완료(1/10)" | 새소리(파일이 없으면 무음) |
| 17.8–20.6 | 작업일지 카드 | 줄 수정: "결과: 창문 1/10, 고양이 침대 1" / "사유: 소음" → 도장 '반려' → 0.4초 뒤 아래에 손글씨 "(소음원: 고양이)" 추가 | (일지) | 쾅 → 정적 |
| 20.6–26.0 | PPL | 그대로. 헤드라인 "뽁뽁이 공사 크루 채용" 유지. 이야기를 이해한 뒤라 이제 웃긴다 | — | BGM |
| 합계 | **26.0초** | S3 2.5초를 빼고 지시서 카드 2.0초와 일지 0.5초로 채운다 | | |

- **이 화의 로그라인:** 창문에 뽁뽁이를 조용히 붙여야 했는데, 정작 시끄러운 건 집주인 고양이였고, 반려 사유는 크루의 소음.
- **선택(+2초, 28초):** 반전 직후 0.8초를 넣는다.
  - 크루는 얼음 포즈 그대로 두고, 반장 고개만 고양이 쪽으로 2px 돌린다(레이어 회전 3도).
  - 자막은 "…우리 탓?". 억울한 리액션을 편집으로 만든다.
- **쓰지 않을 말:** 정보원, 접착수, 단열판, 세척, 판독: 고의 아님.

**(a)로 충분한가**
- 재편집하면 무음에서도 '목표 → 방해 → 반전 → 억울한 결말'이 읽힌다. 예상 이야기 이해도는 4 → 7, 종합 약 7.5다.
- **8점을 넘기려면 리액션 얼굴 한 컷이 필요한데, 기존 소스에는 없다.**
- 그래도 EP10에 크레딧을 더 쓰는 것은 권하지 않는다. 재편집본으로 내고 교훈은 EP11에 쓴다.
- 추가로 만든다면(선택, 권장하지 않음):
  - 정지 이미지 1장, **0cr**: 웹 Nano Banana 2 Unlimited로 '창에 띠 1장을 반쯤 붙인 크루 3명, 반장이 고양이 쪽을 돌아봄'. 지시서 카드 배경과 아침 컷 앞에 쓸 수 있다.
  - 리액션 영상 클립, **4cr**: seedance_2_0_mini 720p 4초. 예비 재생성을 포함하면 최대 8cr다. 잔액 12cr 안에서 가능하다.

### 5-b. EP11부터 시리즈 바이블에 넣을 원칙
1. **0~3초 안에 '목표 + 금지 규칙'을 글자 한 장으로 보여 준다**(작업지시서 카드나 OSD). 결말 일지는 이 지시서에 대한 답이어야 한다.
2. **행동은 목표물 위에서 일어난다.** 상품이 쓰이는 자리(창문, 털 묻은 소파 등)를 첫 컷부터 프레임 안에 두고, 작전 ①②③을 모두 그 자리에서 벌인다. 장소가 바뀌는 소스는 쓰지 않는다.
3. **모든 소리 개그에는 화면 대응물을 붙인다**(의성어 글자, 계기판, 리액션). 무음으로 보고도 웃겨야 PASS다.
4. **웃음을 받는 얼굴을 한 명 둔다**(고양이 얼굴, 크루 반장 클로즈업, 사람 손 등). 얼굴이 금지된 캐릭터만으로 짜지 않는다. 얼음 개그는 반드시 '움직이던 상태'를 먼저 보여 준다.
5. **판정 관문에 '무음 콜드 리드'를 넣는다.** 기획서를 읽지 않은 에이전트가 무음 프레임만 보고 쓴 줄거리가 로그라인과 맞아야 한다. 맞지 않으면 다른 점수와 관계없이 REVISE다. 자산 부족으로 콘티를 줄일 때도 다시 돌린다.

### 한국어 요약
1. 피드백이 맞다. 원인은 길이가 아니라 설정이 화면에 한 번도 나오지 않은 것이다('창문 단열', '소리 내면 안 됨', '고양이가 깨면 끝'). 그래서 반전('정보원이 제일 시끄러움')과 결말('반려: 소음')이 읽히지 않는다.
2. 웃음 대부분이 '뽁' 소리에만 실려 있어 무음에서는 사라진다. 크루는 처음부터 같은 정지 포즈라 '얼음'의 대비가 없고, 리액션 얼굴도 없다.
3. 지난 8.2점은 기획을 아는 판정자가 소리를 켜고 비트별 가시성만 채점한 점수다. '무음 첫 시청 이야기 이해도' 항목이 없었다.
4. 무료 재편집(26~28초)을 권한다. 작업지시서 카드("창문 단열 1장 / 소리 내면 철수"), 소음계 OSD, 발밑 '뽁' 글자, 고양이 라벨을 넣는다. 분무기 장면은 빼고, 보고서체 자막은 농담으로 바꾼다. 예상 점수는 약 7.5이고, 크레딧은 더 쓰지 않는 것을 권한다.
5. EP11부터 바이블에 넣을 원칙은 다섯 가지다. 3초 안에 목표와 규칙을 보여 준다. 행동은 목표물 위에서 일어난다. 소리 개그는 화면으로 옮긴다. 리액션 얼굴을 둔다. 무음 콜드 리드 관문을 거친다.
