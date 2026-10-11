# 「소인국 CCTV」 시리즈 바이블 v6.1 (creative, 2026-10-08)

> 새벽3시CCTV 9화부터 적용. **원칙: 실제로는 절대 촬영할 수 없는 장면만 만든다.** CCTV 화면 틀(천장 모서리·흑백 적외선·03:14)은 그대로 둔다.
> v5 변경: 독립 심사(6.9 FAIL)와 critic 규칙 검수(REVISE)를 반영했다. 반영표는 `assets/clips/EP09/review.md`의 "## [creative] v5 반영"·"## [creative] v5.1 반영"·"## [creative] v5.2 반영"에 있다.
> **v6·v6.1 변경(10-08, 영수 님 채택, v6.1은 critic·creative-review 반영): 연출 원칙을 '증거 화면'으로 바꿨다(아래 0장). 0장이 4장 '질감과 스케일'·5장 훅 설명보다 우선한다.**
> 9화 실행안: `assets/clips/EP09/concept_v6.md` (판독 확대 overlay ⑫ 포함). v5 실행안은 이력.

---

## 0. 연출 원칙 v6 — 증거 화면 (모든 화 공통)

**왜:** 모델 비교(GPT Image·Seedream·FLUX·Nano Banana 2)와 영상 테스트 2회에서, 크루를 또렷하게 보여 주면 모델과 상관없이 피규어로 읽혔다. 실사 소인이 '살아 있다'는 확신은 선명한 모습이 아니라 **흔적과 애매한 증거**에서 나온다(빅풋·UFO 영상 문법). 이게 '장난감으로 찍을 수 있는 영상'과 우리를 가르는 차별점이다.

1. **본편 와이드에서 크루는 보이지 않는다.** 보이는 것은 흔적뿐이다: 장비가 혼자 움직임(짧은 '끙차' 밀기 리듬), 털·먼지가 쓸림, 실밥·끈이 혼자 흔들림, 쿠션 눌림, 반사띠 번쩍(밝은 영역에서만), 뭉치는 흐릿한 솜덩어리 실루엣. 와이드 프롬프트에는 항상 `No people visible anywhere, no hands, no human shadows.`를 붙인다.
2. **판독 확대는 한 화에 2~3회만.** 역할을 나눈다: ① 정체 공개(훅 직후, 1~2초 안) ② 얼음(들킴 순간, 정지 화면) ③ 역감시 버튼(아침, 소인 쪽이 카메라를 보고 있었다). 4회 이상 쓰지 않는다.
3. **판독 화면은 일부러 뭉갠다.** 블록 모자이크 + JPEG 재압축 + 과보정 테두리 + 스캔라인. 보정 단계를 거쳐도 **얼굴 이목구비는 끝까지 안 보인다.** 읽히는 것은 머리 실루엣 3종(안전모·리본 두건·방울 비니)과 반장 반사띠의 흰 번쩍임, 뭉치의 까만 구슬 눈 두 점뿐이다. 사양은 concept_v6 overlay ⑫를 기준으로 한다.
4. **판독 소스는 재사용이 기본이다.** 크루가 또렷한 테스트 클립·이미지는 버리지 않고 판독 화면 소스로 쓴다(뭉개면 약점이 사라진다). 얼음 장면에서는 '피규어처럼 굳은' 모습이 오히려 정답이다.
5. **공포 방지(흔적 연출 전용):** 혼자 움직이는 물건은 원래 공포 문법이다. BGM은 0초부터 깔고, 정체 공개 판독은 1.5초 안에 넣고, 흔적은 IR 핫스폿(밝은 중앙)에서만 일어나게 한다. 어둠 속 형체·긴 그림자·빛나는 눈은 쓰지 않는다.
6. **자막 톤 = 판독관 + 무전 혼합.** "아무도 없는데?", "사람 3명 추정", "판독: 눈 마주침"처럼 담담한 판독관 말투에 작전 배지와 행정 개그(작업일지 '반려', 증거 사진 첨부)를 얹는다. 8~14자, 초당 7자 이하.
7. **시리즈 장치:** 화가 거듭될수록 판독 화면의 '보이는 정도'를 아주 조금씩 올릴 수 있다(블록 크기 하한을 화마다 1씩 낮추는 식). 단 얼굴 이목구비는 시리즈 내내 공개하지 않는다.
8. **4장 대체 규정:** '크루 키 화면 높이 9~10%', '0.0~0.8초 시작 프레임 x2.5 크롭 스케일 리빌'은 v6에서 폐기한다. 훅은 '흔적(0프레임부터 확실한 움직임 + 0초 감지 박스) → 판독 #1'이다.
   - **장비(상품) 색 규정(v6.1):** 회색 단색은 금지한다(수거함 달린 회색 재사용 롤러류가 시판품에 흔하다). 9화 롤러는 **파스텔 레몬 옐로 하우징 + 투명 수거창 + 천 드럼, 무로고**다. 흑백 IR에서는 밝은 회색, 아침 컬러 컷에서만 노랑으로 보인다.
   - 근거: 네이버 상품(파쿠파쿠 털 롤러)은 흰색·연회색 계열로 확인했다(PD, 10-08). 쿠팡 상품(반영구 펫 돌돌이)의 색은 아직 확인하지 않았다. 그래서 **publisher·QA가 업로드 전 상품 페이지에서 확인**하고, 레몬 옐로 계열이면 PD에게 보고해 화면 색을 다시 정한다(concept_v6 '업로드 전 체크').
   - 표현: 'sticky'·'끈끈'은 쓰지 않고 'fabric drum'(천 드럼)으로 쓴다. 접착 시트형으로 오인되지 않게 상품 형태(재사용 드럼형)와 맞춘다.
   - 매 화 공통: 화면 장비는 판매 상품과 '종류'만 맞추고 색·하우징은 그 화 판매 상품들과 다르게 정한다. 그 근거(상품 페이지 색 확인)를 이 항목처럼 기록한다.
9. **허구 명시(v6.1, 증거 화면 문법 전용):** 증거 화면은 '진짜 CCTV 기록'처럼 보이는 것이 무기다. 그래서 상품 성능의 증거 영상이나 실제 목격담으로 오인되지 않게 다음을 지킨다.
   - 제목 맨 앞, 설명란 첫 줄, 고정 댓글(대가성 문구 바로 다음 줄), 썸네일 좌상단에 `AI 상황극`을 명시한다.
   - 영상 0–3초에 `AI 상황극` 44px 라벨을 띄우고, 이후 `AI 연출` 상시 라벨을 이어 간다.
   - `#실제상황` `#소인목격` `#진짜` `#실화` 같은 실제 발견 암시어는 금지한다.
   - 댓글에서 실제인 척하지 않는다. 사실(AI 상황극)을 먼저 말하고, 그다음에만 세계관 농담으로 받는다. 영상을 상품 성능의 근거처럼 말하지 않는다.
10. **캐릭터를 '안 보이게' 쌓는 장치(v6.1):** 크루 얼굴은 안 보이므로 아래 시그니처를 매 화 고정한다.
   - 소리: 반장 호루라기 '삑', 여사 '끙차', 콩알이 '으앗'. 짧은 의성음이고 단어 발음은 하지 않는다.
   - 흔적: 반장 반사띠의 흰 번쩍임, 방울 비니 실루엣.
   - 판독 결과 문구에 `안전모 1, 두건 1, 방울 1`처럼 머리 실루엣 3종을 적는다.
   - 썸네일은 판독 #1 패널에 빨간 원 3개를 치는 구성으로 고정한다.

---

## 1. 세계관

인간의 집에는 손가락만 한 소인들의 공기업 **「밤살림공사(公社)」**가 몰래 들어와 있다. 이들은 인간이 어질러 놓은 집을 밤사이 '보수 공사'하고, 그 대가로 과자 부스러기·실밥·잃어버린 단추를 월급으로 받는다. 근무는 늘 **새벽 3시 14분**에 시작한다. 인간이 가장 깊이 자고 냉장고 모터마저 조용한 시간이다.
인간의 생활용품은 이들에게 **거대 장비**다. 털 롤러는 로드롤러, 분무기는 소방차, 수건은 낙하산이다.
공사 규칙 제1조는 **「인간에게 들키면 그 집에서 영구 철수한다」**이다. 그래서 위기가 오면 반장의 호루라기 신호에 맞춰 모두 **"얼음!"** 하고 장식 피규어처럼 굳는다. 반려동물·로봇청소기·센서등은 인간에게 고자질할 수 있는 '정보원'이라서 똑같이 얼음 대상이다.

**이 시리즈의 고유 무기 = 공기업 행정 개그.** 해외 'tiny workers' 매크로 영상과 겹치지 않게 하는 핵심 장치다. 작업 번호, 무전 보고("본부, 착공"), 안전수칙, 작업일지 결재(대부분 '반려'), 공사 가축 사원증 같은 한국 직장·공기업 풍자를 **편집 오버레이로** 매 화 화면에 노출한다. 생성 이미지에는 글자를 넣지 않는다.

- 왜 실사로 못 찍는가: 살아서 체중을 싣고 움직이는 손가락 크기 인간, 그들 눈에 거대한 실제 집, 진짜 동물과 마주치는 장면이다. 피규어는 움직이지 않고, 인형극은 무게감이 없다.
- 반복 장치(시청자가 기다리는 것): ① 0초 '판독 확대 → 줌아웃' 스케일 리빌 ② "얼음!" ③ 작업일지 '반려' 도장 ④ 아침에 주인은 모르고, 뭉치는 얼음 유지 중 → 마지막 한 박자에 카메라 정면 응시(버튼).

---

## 2. 고정 캐릭터 3명 (밤살림공사 제3현장팀)

480p 흑백에서는 얼굴이 뭉개진다. 그래서 세 가지로 구분한다.
- **머리 실루엣 3종:** 돔 안전모 / 리본 두건 / 방울 비니
- **키·체형 3단계:** 작고 땅딸 / 중간 동글 / 크고 마름
- **밝기 위계:** 화면에서 가장 밝은 점은 **반장의 흰 안전모와 반사띠뿐**이다. 여사와 막내는 중간 톤으로 둔다.

첫 화에서는 크루 이름 자막을 넣지 않는다(이름 자막은 4화쯤부터). 첫 화 이름 자막은 마스코트 '뭉치' 하나만 쓴다.

### ① 도반장 — 현장 소장
- 외형: 가장 작고 땅딸막하다. 흰 돔 안전모, 진회색 작업복, 가슴·등에 큰 X자 반사띠 조끼, 짙은 팔자 콧수염, 목에 호루라기.
- 성격: 원칙주의, 비장함 과잉. 털 한 가닥 앞에서도 전쟁 영화처럼 지휘한다.
- 시그니처: 호루라기를 물고 주먹 쥔 팔을 수직으로 든다("얼음!" 신호). 실패하면 안전모를 벗어 가슴에 대고 묵념한다.
- 무전 말투: "본부, 착공한다." "얼음!" "철수 없다."
- 고정 문구:
  `a tiny realistic middle-aged foreman about the length of an adult index finger, the shortest and stockiest of the crew, wearing a bright white dome-shaped hard hat, dark gray coveralls and a reflective safety vest with a big bright X-shaped stripe across the chest and back, a thick black mustache, a small whistle on a cord around his neck`

### ② 부릉여사 — 장비 기사
- 외형: 중간 키, 동글한 체형. 머리 위로 리본 매듭이 솟은 **중간 톤 두건(어두운 물방울무늬)**, 비행 고글, 진한 멜빵 작업바지, 회색 작업 장갑.
- 성격: 30년 경력의 무심한 베테랑. 거대 장비를 자가용처럼 몬다.
- 시그니처: 고글을 '척' 내리고 손잡이를 잡는다(가동 신호). 얼음 때도 혼자 운전 자세 그대로 굳는다.
- 무전 말투: "비켜, 들어간다."
- 고정 문구:
  `a tiny realistic plump older woman about the length of an adult index finger, medium height with a round silhouette, a medium-gray headscarf with dark polka dots tied in a bow that sticks up on top of her head, aviator goggles, dark denim bib overalls, gray work gloves`

### ③ 콩알이 — 신입 막내 (사고 담당)
- 외형: 가장 크고 마른 꺽다리. 큰 방울이 달린 줄무늬 니트 비니, 헐렁한 **중간 회색 작업복**(소매 걷음), 꺼진 헤드랜턴, 클립보드.
- 성격: 의욕은 1등, 늘 한 박자 늦다. 매 화 들킴의 원인이 된다.
- 시그니처: 장비에 매달려 깃발처럼 펄럭인다. 얼음 때 혼자 한 발 든 포즈로 굳는다.
- 무전 말투: "반장님?!" "저 여기요…"
- 고정 문구:
  `a tiny realistic skinny young man, the tallest and thinnest of the crew but still only finger-length, wearing a striped knit beanie with a big pompom, an oversized medium-gray coverall with rolled-up sleeves, a small switched-off headlamp`

### 크루 공통 문구 (캐릭터 문구 뒤에 붙인다)
`They are photorealistic living miniature humans with real skin, real fabric and natural body weight, visible weight shift and fabric wrinkles moving, not toys, not figurines, not tilt-shift toys, not cartoon characters. Each one is about the length of an adult index finger compared with the giant real household objects around them.`

---

## 3. 마스코트

### 후보 3안 (기록)
| 안 | 요약 | 판정 |
|---|---|---|
| **A. 먼지양 '뭉치'** | 먼지·보풀로 된 살아 있는 아기 양. 밤살림공사의 '공사 가축' | **채택** |
| B. 견인 햄스터 '대감' | 마구를 찬 진짜 햄스터 | 흔한 동물이라 채널 고유 IP가 되기 약함 |
| C. 공벌레 '도르르' | 공처럼 말리는 공벌레 | 벌레를 싫어하는 3040이 많아 썸네일 리스크 |

### 뭉치 최종 디자인 (v5)
- **크기:** 골프공만 하다. 크루 키의 절반으로, v4의 포도알에서 두 배로 키웠다.
- **몸:** 깨끗한 회백색 솜. 얼굴도 몸과 같은 톤의 짧은 솜이다. **얼굴·다리를 검게 칠하지 않는다.**
- **실루엣 표식:** 양옆으로 처진 큰 귀 2개, 작은 회색 발굽 4개(발 끝만 살짝 진함), 까만 구슬 눈 2개(작게, 빛남 금지).
- **어두운 소품:** 크루와 같은 공사 지급품인 **진회색 미니 작업 조끼**에 가는 반사띠 한 줄. 흰 솜 몸에 어두운 조끼 띠가 둘러져 '털 뭉치'와 구분된다. 조끼는 '공사 가축 사원증' 개그도 겸한다.
- **배치:** 항상 어두운 면(검은 코트, 진한 쿠션) 위에 둔다. 흰 털 더미 위에 두지 않는다.
- 성격·개그: 먹보에 순둥이다. 먼지·털을 먹으면 부풀고, 매 화 상품에 휘말린다. 얼음 규칙은 크루보다 잘 지킨다(눈만 데굴).
- **기존 캐릭터와 다른 점:** 숀 더 십과 달리 얼굴·다리를 검게 칠하지 않은 '전신 단색 솜 + 작업 조끼' 양이고, 검댕이와 달리 밝은 몸·작은 구슬 눈·처진 귀·발굽이 있는 '양' 실루엣이다.
- 고정 문구:
  `a tiny living dust-bunny lamb about the size of a golf ball, half the height of the tiny crew, a clean fluffy round body of soft light gray-white lint like cotton candy, its small face covered in the same light fluff with no dark coloring, two big floppy ears hanging down at the sides, four tiny gray hooves, two small shiny black bead eyes that do not glow, wearing a tiny dark gray work vest with one thin reflective stripe, a few soft wisps of fluff drifting off its body`

---

## 4. 비주얼 바이블

### 질감과 스케일
- 화면의 재미는 스케일 대비에서 나온다. 소인은 극사실 미니어처 인간이고, 집은 거대한 실사다.
- 소인 크기 기준: **성인 검지 길이(약 7~8 cm)**.
- **크루 키는 화면 높이의 9~10%**로 잡는다. 이를 위해 무대를 카메라 바로 아래 높은 면(코트 어깨·앞판 위쪽, 암체어 팔걸이)으로 당긴다.
- 매 컷에 크기 비교 물체를 하나 이상 둔다(단추, 고양이 앞발, 실밥 한 가닥).
- 피규어처럼 보이면 실패다. 0초부터 움직이게 하고, 프롬프트에 `visible weight shift, fabric wrinkles moving, not tilt-shift toys`를 넣는다. 예외는 '얼음' 컷 하나다. 여기서는 일부러 굳는 게 웃음이다.
- **밝기 위계(흑백):**
  - 1순위(가장 밝음): 반장 안전모·반사띠
  - 2순위: 뭉치 솜(어두운 조끼 띠로 끊김), 빠진 속털 몇 가닥
  - 3순위(중간): 고양이, 여사, 막내, 장비
  - 최하(가장 어두움): 검은 코트
- **고정 반려동물(9화):** 진회색 줄무늬(태비) 고양이, 흰 가슴털·흰 발. 몸은 중간 톤이고 빠진 밝은 속털만 화면에서 보인다.
  - 고정 문구: `a dark gray tabby cat with a white chest and white paws, medium-length fur, realistic, its eyes look normal and do not glow`
- **상품(거대 장비):**
  - 그 카테고리의 브랜드 없는 일반형으로, **상품 '종류'만 실제와 맞춘다**(드럼형·시트형·브러시형).
  - 색·하우징은 시판품과 다르게 한다. 회색 하우징은 피하고 임의의 파스텔 단색 또는 투명 하우징을 쓴다.
  - **효과 표현은 '얇은 한 줄'까지만** 허용한다. 결과 클로즈업은 금지한다.

### 카메라
- 천장 모서리 고정 CCTV, 바닥에서 약 2.3 m, 아래로 약 40도, 어안 광각. 9:16 세로. **카메라는 절대 안 움직인다.** 줌·흔들림·확대 박스는 편집에서만 넣는다.
- 구도: 크루·장비는 가운데 1/3 세로 띠에 둔다. 하단 25%는 자막 자리로 비우고, 상단 15%는 OSD·라벨 자리로 비운다.
- 고정 문구:
  `Fixed ceiling-corner security camera view looking down at about 40 degrees, wide fisheye lens with curved edges, vertical 9:16 frame, black-and-white infrared night vision, soft sensor noise, slight vignette, deep focus with everything sharp, the camera never moves.`

### 조명·색
- **밤 03:14:** 흑백 적외선, 위·정면 조명, 중앙이 밝고 가장자리는 어둡다.
- **아침 07:30 (후일담만 컬러):** 창으로 드는 부드러운 햇빛(약 4500K), 옅은 청회색 그림자, 낮은 채도. 밤과 같은 앵글이다.
  - 인간은 손·다리까지만 나온다.
  - 크루와 뭉치는 얼음 상태로 장식품인 척한다.

### 공통 금지 문구 (모든 이미지·영상 프롬프트 끝에 그대로)
`No text, no letters, no numbers, no logos, no brand names, no labels, no watermark, no subtitles, no timestamp, no on-screen interface, no ghosts, no horror, no glowing eyes, no blood, no injury, no human faces other than the tiny crew.`
- **공포 방지:** 긴 그림자·어둠 속 형체 금지. 소인의 놀란 얼굴 클로즈업 금지. 동물의 입·이빨·발톱 금지. 동물 코가 화면에 닿게 다가오는 구도 금지. BGM 정적은 1초 이내(한 화에 여러 번이어도 각 1초 이내).
- **동물:** 롤러를 동물 몸에 굴리지 않는다. **크루는 동물 몸에 붙은 털·꼬리·수염을 잡거나 당기지 않는다.** 크루가 매달리거나 당기는 줄은 동물과 떨어진 물건(풀린 실밥 등)으로 한다(`… not attached to the cat`). 실밥은 세계관상 공사 월급이라 개그 소재로 쓴다. 동물을 깨우는 원인은 소리·진동·빛으로 한다.
- **뭉치:** 장비·물건에 깔리거나 눌리는 구도 금지. 붙더라도 항상 바깥면(윗면·옆면·카메라 쪽 면)에 있다.
- **IP:** 제목·홍보 문구·해시태그에 지브리, 아리에티, 바로우어즈, 토이스토리를 쓰지 않는다. 소인을 카툰풍 소녀로 그리지 않는다. 마리오(빨강·파랑 멜빵)나 월리(빨강 흰 줄무늬) 색 조합을 피한다.
  - 굿즈를 만들기 전에 KIPRIS로 상표를 검색한다(밤살림공사, 콩알이, 뭉치, 부릉여사). 이건 PD가 병행한다.
- **법·채널 규칙:**
  - 상품 효과를 단정하는 연출·자막 금지. 작업은 늘 '일부만' 되거나 반전으로 원상복구된다.
  - 체험·후기 말투 금지.
  - 'AI 연출' 라벨을 0초부터 끝까지 상시 표시한다.
  - PPL 카드 최하단에 AI 연출 고지 문구를 넣는다(5장).
  - 상품 확정 전에는 영상을 생성하지 않는다(이미지만 무료로 생성).

---

## 5. 에피소드 공식 (총 약 29초)

| 구간 | 시간 | 길이 | 내용 | 원본 |
|---|---|---|---|---|
| 스케일 리빌 훅 | 0.0–2.4 | 2.4 | 0.0~0.8초는 **시작 프레임 고해상도 이미지를 x2.5 크롭**(+흔들림·입자)해 크루만 꽉 차게, 진짜 공사판처럼 보인다(480p 클립 크롭 금지). 0.8~1.4초에 줌아웃하며 0.8~1.1초에 클립으로 디졸브해 '코트 위·옆엔 자는 고양이'를 공개한다. 거대 장비는 이미 가동 중이고, 뭉치가 장비 위에서 무언가를 먹고 있다(심기) | 이미지 A0 → 영상 A |
| 작전 ① | 2.4–4.6 | 2.2 | 장비의 첫 쓰임(굴리기) | 영상 A 뒤 |
| 작전 ② | 4.6–6.8 | 2.2 | 난코스(고공·흔들림) | 영상 B |
| 작전 ③ | 6.8–9.0 | 2.2 | 막내가 '정보원'을 건드려 들킴의 원인을 만든다 | 영상 C |
| 들킴 | 9.0–10.8 | 1.8 | 정보원이 깨어남 → "얼음!". 정적 1초 이내 | 이미지 2장(무료) |
| 반전 1단 | 10.8–13.4 | 2.6 | 앞 설정 배신(원상복구 등). 큰 동작 1개 | 영상 D |
| 다시보기 | 13.4–14.6 | 1.2 | 반전 0.5배 슬로 | 영상 D 재사용 |
| 마스코트 | 14.6–17.6 | 3.0 | 뭉치 사고(심기 → 중간 0.4초 정지 컷으로 사라짐 → 회수). **15초 안쪽에 등장** | 이미지+키트 줌 |
| 작업일지 | 17.6–19.1 | 1.5 | 결재 카드(제목 + 2줄) + '반려' 도장 | 오버레이 |
| 아침 반전 2단 + 버튼 | 19.1–23.3 | 4.2 | 07:30 컬러. 2.6초: 인간이 상품을 '사용'하고 뭉치가 장비 바깥면에 붙어 함께 돈다(이미지 3장 0.2초 교차, 얼음 유지·눈만 데굴). 마지막 1.6초: 정지 + 뭉치가 카메라 정면 응시, 미세 줌인, 무음 1.0초 이내 → 짧은 코믹 효과음 + BGM 복귀. 첫 장을 만든 뒤 나머지는 그 장을 레퍼런스로 뭉치 위치만 바꿔 같은 노출로 만든다 | 이미지 4장 |
| PPL | 23.3–29.4 | 6.1 | 정보 카드, 마지막 줄 농담, AI 연출 고지(32px 이상) | 키트 |

- **영상 원칙:**
  - 4개 × 2.5 = **10크레딧(기본)**. 예비 5크레딧(총 15 이하, 재생성 최대 2회)은 **승인됨(10-08, 영수 님)**. 회차마다 같은 한도로 PD가 다시 확인한다.
  - **클립당 큰 동작 주체 1명**, 나머지는 작은 동작이나 정지다.
  - A를 먼저 1개 테스트한다. 0.5초·2초 프레임에서 '크루 3명 실루엣 구분 + 피규어 아닌 체중감'을 판정한 뒤 나머지를 만든다.
  - 클립마다 실패 시 정지 이미지 대체안을 둔다.
- **상품이 히어로가 되는 방식:**
  1. 크루가 상품을 운전·탑승하는 중장비다.
  2. 작전 ①②가 상품의 쓰임에서 나온다.
  3. 마스코트 사고의 무대가 상품이다.
  4. 아침에 인간이 상품을 '사용'하는 장면으로 끝난다(효과 결과는 보여 주지 않음).
- **자막:** 무전 말투, 8~14자. 작전 번호는 오버레이 배지로 단다. 들킴은 항상 "얼음!".

### 대가성·AI 표기 위치 (매 화 고정, 업로드 후 되읽기 항목)
- **유튜브 쇼츠:**
  - 고정 댓글 맨 위에 네이버 문구를 토씨 그대로 넣는다. 쿠팡을 병행하면 쿠팡 문구도 함께 넣는다.
  - 설명란에도 같은 문구를 넣는다.
  - 영상 첫·마지막 화면에 광고 표시를 넣는다.
  - '유료 프로모션 포함'과 '변경되거나 합성된 콘텐츠'를 체크한다.
- **네이버 클립:** 본문 맨 앞 [광고], 첫 댓글로 네이버 문구 고정. 쿠팡 링크는 쓰지 않는다. AI 표시 옵션이 있으면 켠다.
- **틱톡·릴스:** 캡션 첫 줄에 [광고]와 해당 문구를 넣고, 해시태그 사이에 숨기지 않는다. AI 생성 표시를 켠다.
- **문구 원문:**
  - 네이버: "이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다."
  - 쿠팡: "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."

---

## 6. 타이포그래피 체계 (용도별, 상업 이용 무료)

| 용도 | 글꼴 | 이유 | 공식 출처 | 라이선스 |
|---|---|---|---|---|
| CCTV OSD·현장 라벨·판독 확대·AI 연출 라벨 | **갈무리11 Bold (Galmuri11)** | 비트맵 감성이라 실제 CCTV 화면 표시처럼 읽힌다. 한글이 지원되고 작은 크기에서도 또렷하다 | github.com/quiple/galmuri (릴리스) | SIL OFL 1.1 |
| 무전 자막(메인 자막) | **검은고딕 (Black Han Sans)** | 굵고 각진 현장 지시 톤이다. 480p·폰 피드에서 가독성이 가장 높다 | fonts.google.com/specimen/Black+Han+Sans | SIL OFL 1.1 |
| 작업일지 카드·결재 도장 | **나눔명조 ExtraBold** | 관공서 공문서 톤이다. 도장의 '반려'는 명조 굵게 + 붉은 테두리로 쓴다 | hangeul.naver.com 나눔글꼴 / fonts.google.com/specimen/Nanum+Myeongjo | SIL OFL 1.1 |
| PPL 정보 카드·고지 문구 | **Pretendard** (기존) | 정보 가독성. 이미 assets/fonts에 있다 | github.com/orioncactus/pretendard | SIL OFL 1.1 |

- OFL 1.1은 영상 자막·상업 이용이 가능하다(영상 렌더는 글꼴 재배포가 아님). 글꼴 파일 자체를 판매하거나 수정·변환해 배포하는 것은 금지된다. 나눔글꼴은 Reserved Font Name 조항을 원문으로 확인한다.
- **글리프 대체:** 원숫자(①②③)·☐·아이콘 기호는 글꼴에 없을 수 있으니 글리프로 찍지 않고 코드로 그린다(노란 원 + 숫자 1·2·3, 사각형 도형). 렌더 전 사용 문자열 전체로 글리프 테스트를 하고, 두부(□)가 나오면 Pretendard로 대체한다.
- 받을 때 각 저장소의 LICENSE 원문을 `assets/fonts/`에 함께 둔다(Pretendard처럼 `OFL-<이름>.txt`).
- 다운로드는 공식 저장소에서만 한다. 위 판정은 기억 기준이라, 받을 때 라이선스 원문을 확인한다.

---

## 7. 1~8화를 이 세계관으로 다시 했다면 (리메이크 후보)

1. 현관·액막이 명태: 거대 명태를 신발장 위로 거는 크레인 작업. 새벽 귀가 구두에 얼음. 작업일지 사유 "액운 과다".
2. 거실·디퓨저: 리드 스틱 장대높이뛰기, 향 병 우물 작업. 막내가 병에 빠짐, 강아지가 킁킁.
3. 욕실·호텔수건: 수건 개기 = 낙하산 접기. 센서등이 켜져 얼음, 수건 산이 와르르.
4. 주방·방짜 수저: 젓가락 들것, 숟가락 스키점프.
5. 펫캠: 펫캠 렌즈 닦기 고공 작업. 코기가 다가와 화면 가득 코(메타 들킴).
6. 냉동실·냉동밥 용기: 남극 탐험대. 문 열림 빛에 얼음, 진짜로 얼어 버림.
7. 신발장·신발탈취제: 분사기 = 소방 호스. 반동에 막내가 날아감.
8. 세탁기·세탁조클리너: 세탁조 동굴 다이빙, 정제 바위 굴리기.

---

> ⚠ 9화부터 롤러는 concept_v6의 '롤러 고정 문구'(파스텔 레몬 옐로·투명 수거창·천 드럼·둥근 캡슐 몸체·무로고)를 쓴다. 아래 8장 v5 프롬프트의 '파스텔 민트' 문구는 복사하지 말 것.

## 8. 스타일 프레임 프롬프트 (Nano Banana 2 웹 + Unlimited, 무료)

> (a)를 먼저 뽑는다. (b)·(c)는 (a)를 레퍼런스로 붙이고 "Edit this exact CCTV image, keep the same camera angle, lighting and room…"으로 시작한다.
> v5.2 최종: (a) 그네용 실밥 배치, (b) 막내 실밥 월급 소품, (c) 뭉치 기쁜 표정 명시. 9화 컷 이미지(B1·C0·N1~N4)는 concept_v5.md의 컷별 문장을 이 프레임에 덧붙여 만든다.
> 롤러 색은 상품이 확정되면 시판품과 다르게 다시 고른다. 지금은 임시로 파스텔 민트 단색 + 뭉치가 들어갈 만한 크기의 수거함(투명 뚜껑)이다.

### (a) 9화 기준 컷 master — 코트 위 롤러 공사

```
Vertical 9:16 photorealistic still from a fixed ceiling-corner home security camera at 3 AM, looking down at about 40 degrees with a wide fisheye lens and curved edges, black-and-white infrared night vision, soft sensor noise, slight vignette, deep focus, the camera never moves.
A small walk-in closet. Directly below the camera, filling the middle third of the frame, a long plain black wool coat on a wooden hanger hangs from a low black metal garment rack, its shoulders and upper front very close to the camera. A few light shed cat hairs are scattered on the dark coat. To the right, a small armchair with a dark gray tabby cat with a white chest and white paws, medium-length fur, realistic, curled up asleep on the seat cushion with eyes closed, its tail tucked around its body. A thick long loose thread hangs from a frayed seam of the armrest fabric, not attached to the cat. The top 15 percent and the bottom quarter of the frame are calm and empty.
On the upper front of the coat, a plain generic reusable pet hair roller, much bigger than the tiny people, with a solid pastel mint plastic housing, a collection compartment with a clear lid large enough to hold a golf ball, a short handle and a soft fabric drum, no brand, no text, rolls downward like a road roller. A thin strip of light hairs lifts off behind it; most of the coat stays covered in hairs.
Sitting on top of the roller handle next to the woman is a tiny living dust-bunny lamb about the size of a golf ball, a clean fluffy round body of soft light gray-white lint like cotton candy, its small face covered in the same light fluff with no dark coloring, two big floppy ears, four tiny gray hooves, two small shiny black bead eyes that do not glow, wearing a tiny dark gray work vest with one thin reflective stripe, slurping one long light hair like a noodle, clearly visible against the dark handle.
Three tiny people ride the roller, each about 9 percent of the frame height:
- a tiny realistic middle-aged foreman about the length of an adult index finger, the shortest and stockiest of the crew, wearing a bright white dome-shaped hard hat, dark gray coveralls and a reflective safety vest with a big bright X-shaped stripe across the chest and back, a thick black mustache, a small whistle on a cord around his neck, standing on the housing and pointing forward;
- a tiny realistic plump older woman about the length of an adult index finger, medium height with a round silhouette, a medium-gray headscarf with dark polka dots tied in a bow that sticks up on top of her head, aviator goggles, dark denim bib overalls, gray work gloves, steering the handle;
- a tiny realistic skinny young man, the tallest and thinnest of the crew but still only finger-length, wearing a striped knit beanie with a big pompom, an oversized medium-gray coverall with rolled-up sleeves, a small switched-off headlamp, hanging off the end of the handle with his legs flying sideways.
They are photorealistic living miniature humans with real skin, real fabric and natural body weight, visible weight shift and fabric wrinkles moving, not toys, not figurines, not tilt-shift toys, not cartoon characters. The brightest things in the frame are only the foreman's white hard hat and reflective stripes.
No text, no letters, no numbers, no logos, no brand names, no labels, no watermark, no subtitles, no timestamp, no on-screen interface, no ghosts, no horror, no glowing eyes, no blood, no injury, no human faces other than the tiny crew.
```

### (b) 고정 캐릭터 3명 + 뭉치 캐릭터 시트 — 같은 CCTV 세계, 정면 나란히

```
Edit this exact CCTV image, keep the same camera angle, lighting and room.
(If no reference: Vertical 9:16 photorealistic still from a fixed ceiling-corner home security camera at 3 AM, looking down at about 40 degrees with a wide fisheye lens and curved edges, black-and-white infrared night vision, soft sensor noise, slight vignette, deep focus.)
Close to the camera in the middle of the frame, the dark fabric seat cushion of a small armchair. Standing side by side on the dark cushion, facing the camera in a straight line like a crew photo, each about 10 percent of the frame height, from left to right:
- a tiny realistic middle-aged foreman about the length of an adult index finger, the shortest and stockiest of the crew, wearing a bright white dome-shaped hard hat, dark gray coveralls and a reflective safety vest with a big bright X-shaped stripe across the chest and back, a thick black mustache, a small whistle on a cord around his neck, arms crossed, serious;
- a tiny realistic plump older woman about the length of an adult index finger, medium height with a round silhouette, a medium-gray headscarf with dark polka dots tied in a bow that sticks up on top of her head, aviator goggles pushed up on her forehead, dark denim bib overalls, gray work gloves, hands on hips, bored;
- a tiny realistic skinny young man, the tallest and thinnest of the crew but still only finger-length, wearing a striped knit beanie with a big pompom, an oversized medium-gray coverall with rolled-up sleeves, a small switched-off headlamp, waving eagerly, a small coil of loose thread slung over his shoulder like a paycheck;
- at their feet, a tiny living dust-bunny lamb about the size of a golf ball, half the height of the crew, a clean fluffy round body of soft light gray-white lint like cotton candy, its small face covered in the same light fluff with no dark coloring, two big floppy ears hanging down at the sides, four tiny gray hooves, two small shiny black bead eyes that do not glow, wearing a tiny dark gray work vest with one thin reflective stripe.
Their head shapes are clearly different in silhouette: dome hard hat, headscarf bow, pompom beanie, floppy lamb ears. Heights go short, medium, tall. For scale, the white front paw of a dark gray tabby cat rests at the edge of the cushion, bigger than their bodies.
They are photorealistic and alive, visible weight shift and fabric wrinkles, not toys, not figurines, not tilt-shift toys, not cartoon characters. The bottom quarter of the frame is empty dark cushion and rug.
No text, no letters, no numbers, no logos, no brand names, no labels, no watermark, no subtitles, no timestamp, no on-screen interface, no ghosts, no horror, no glowing eyes, no blood, no injury, no human faces other than the tiny crew.
```

### (c) 마스코트 뭉치 등장 컷 — 털을 너무 먹어 두 배로 부풀어 수거함 뚜껑이 퐁 (9화 컷 8 겸용)

```
Edit this exact CCTV image, keep the same camera angle, lighting, room and coat.
On the dark seat cushion of the armchair close to the camera, in the middle third of the frame, the plain generic reusable pet hair roller with the solid pastel mint housing lies on its side, no brand, no text, its small collection lid popped wide open. Bursting out of it is the tiny living dust-bunny lamb, now puffed up to twice its size from eating all the hair inside the compartment, about the size of a tennis ball, a clean fluffy round body of soft light gray-white lint like cotton candy, its small face covered in the same light fluff with no dark coloring, two big floppy ears, four tiny gray hooves stretched out, two small shiny black bead eyes that do not glow, the tiny dark gray work vest with one thin reflective stripe stretched tight around its puffy body, mouth open in a happy bleat, joyful expression, no struggling or distressed expression.
The three tiny crew members have just tumbled softly onto the cushion: the foreman with the white dome hard hat and the bright X-shaped reflective vest sits on the cushion holding his hard hat to his chest, the plump older woman with the medium-gray polka-dot headscarf bow still calmly holds the handle, the tall skinny young man with the pompom beanie is half buried in the lamb's fluff with only his legs and pompom sticking out. Behind them, the dark gray tabby cat stands on the armrest rubbing against the coat, out of focus.
Everyone is photorealistic and alive, not toys, not figurines. The lamb is soft, clean and cute, never dirty. The bottom quarter of the frame is empty dark cushion.
No text, no letters, no numbers, no logos, no brand names, no labels, no watermark, no subtitles, no timestamp, no on-screen interface, no ghosts, no horror, no glowing eyes, no blood, no injury, no human faces other than the tiny crew.
```

## 이야기 원칙 (2026-10-10, EP10 영수 님 피드백 "이야기가 안 되고 웃음이 없고 뭘 말하는지 모르겠다" 반영)
1. 0~3초 안에 목표와 금지 규칙을 글자 한 장(작업지시서 등)으로 보여 주고, 결말 일지는 그 지시에 대한 답이 되게 한다.
2. 행동은 목표물 위에서 일어나게 한다. 장소가 바뀌는 소스는 쓰지 않는다.
3. 모든 소리 개그에 화면 대응물(의성어, 소음계 OSD 등)을 붙인다. 무음으로 보고도 웃겨야 PASS.
4. 웃음을 받는 리액션 얼굴을 한 명 두고, 얼음 개그 전에는 반드시 움직이던 상태를 보여 준다.
5. 판정 관문에 '무음 콜드 리드'를 넣는다: 기획서를 모르는 에이전트가 무음 프레임만 보고 쓴 줄거리가 로그라인과 다르면 REVISE. 기획자 본인이 최종 판정하지 않는다.
6. 보고서체 자막(운반 완료·접착수 살포 등) 금지. 자막은 농담을 나른다.

## 길이 원칙 (2026-10-10 회의: analyst 데이터 + creative 의견 합의, 영수 님 질문 "30초만 하는 게 맞나")
- 고정 30초 폐기. 길이 = 웃음 비트 수 × 2.5~3초 + 설정 2.5초 + PPL 약 6초 → 보통 24~34초(최소 20~22, 상한 35).
- 근거: 8편 데이터에서 길이↔조회수 무관(상관 0.06), 길이↔계속시청률 -0.57. 40초 편은 35초 PPL 진입에서 급락. 10화는 길이가 아니라 구조 문제.
- 들킴·반전 ≤12초, 반전 뒤 꼬리 ≤50%, 정지 컷 연속 ≤2초. PPL은 이탈 전(20~24초 부근)에 시작.
- 늘릴 땐 비트를 추가, 줄일 땐 비트를 통째로 뺀다. 길이를 바꾸면 무음 콜드 리드 재실행.
- 검증: EP11 30초판 + 결재 컷 뺀 25초판 A/B(0cr). 보고서: reports/length_analysis_1010.md, length_creative_1010.md
