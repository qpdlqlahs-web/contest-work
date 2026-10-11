# A' 「정전 점검의 아침」 스타일 가이드 + 이미지 생성 프롬프트 세트

- 작성: 디자인팀(아트 디렉터) · 2026-10-08
- 근거: `최종기획안.md` 2장 컷 목록 + 맨 끝 '감독 결정 기록'(최우선), `상의라운드_패널의견.md`, 공식 자산(PPA-300 사진 20장, BI) 직접 확인·실측
- 상태: 크리에이티브 리뷰·독립 검수 전 초안. 기존 파일은 수정하지 않았다.
- 규격: 9:16, 1080×1920. Nano Banana 2는 가능한 최고 해상도(2K 이상)로 생성한 뒤 1080×1920으로 내린다.

---

## 0. 한눈에 보기

| 구분 | 수량 | 내용 |
|---|---|---|
| 인물 시트 | 2장 | CS-F 가족 3명 / CS-N 이웃 3명 |
| 정지 컷 이미지 | 21장 | 신규 생성 13장(환경 마스터 ENV-1 포함) + Nano Banana 편집 파생 8장 |
| Kling 시작 프레임 | 5장 | K1~K5 (K1·K2는 배경 생성 → 공식 사진 합성 → 물줄기 편집 1회씩 추가) |
| 생성 없이 합성·편집만 | 8프레임 | 컷 2(색보정), 컷 8(공식 뒷면), 10-2, 11-1·11-2·11-3(공식 사진 합성), 컷 19·20(그래픽) |
| 1차 생성 호출 합계 | 약 30회 | 시트 2 + 정지 21 + 시작 프레임 5 + 물줄기 편집 2. 재생성은 컷당 최대 2회(무료 경로) |

---

## 1. 룩(Look)

### 1-1. 룩 키워드
- **실사 시네마틱 · 한국 가정 내추럴리즘**: 연출된 광고 세트가 아니라 "주말 오전, 누군가의 진짜 빌라 거실"처럼 보이게 한다. 약간의 생활감(접힌 행주, 냉장고의 아이 그림)은 남기고, 잡동사니는 줄인다.
- **비대칭 3분할**: 주 피사체는 항상 좌/우 1/3선 위. 정중앙·좌우 대칭 구도는 쓰지 않는다(1회 대상작 웨스 앤더슨풍 대칭과 반대 축).
- **프레임 안 프레임**: 문틀(K4), 창틀(K5), TV 화면 반사(컷 12)를 적극 활용한다.
- **창 자연광**: OFF 상태의 빛이 오히려 가장 아름답다. 방향성 있는 측광, 키:필 = 약 4:1.
- **35mm 필름 그레인 · 저채도 웜뉴트럴**: 채도 -15~-20%. 그레인은 편집 마지막에 **모든 소스(AI 스틸, Kling 클립, 공식 사진)에 같은 그레인 레이어를 한 번에** 입혀 이질감을 없앤다.
- **금지 룩**: 파스텔 민트·핑크 주조색, 대칭 정면 구도, 광택 CG풍 피부, 과한 보케 하트·플레어, 틸앤오렌지 과보정, 어두운 '정전 = 깜깜함' 표현.

### 1-2. 색온도 스크립트 (정전을 '빛의 색'으로 보여 준다)

| 상태 | 색온도 | 빛의 성격 | 적용 컷 |
|---|---|---|---|
| **ON** (전기 있음) | **3000K** 인공광 + 약한 창빛 | 천장등·펜던트의 평평한 앰버. 대비 낮음(키:필 1.5:1), 그림자 흐림. **'덜 예쁜 빛'** | 1, 16(16-1·16-2) |
| **OFF** (정전) | **5600K** 창빛만 | 방향성 있는 측광, 블루그레이 그림자, 맑은 하이라이트. **'가장 예쁜 빛'** | 2(편집), 3~15, 16-3, 17, 18 |
| 계단실 | 5600K | 간유리 창의 확산광, 센서등 꺼짐 | 4, 14 |

- 카메라 화이트밸런스는 **전 컷 5600K 고정**으로 가정한다. 그래서 ON 장면은 앰버로, OFF 장면은 중립~약간 차갑게 읽힌다.
- 컷 2는 생성하지 않는다. 컷 1 스틸을 3000K→5600K로 색보정하고, 펜던트·천장등의 발광과 TV 화면만 마스크로 끈다(감독 결정).
- 설정 시각: 토요일 오전 10시(가족이 모두 잠옷 차림으로 집에 있는 이유).

### 1-3. HEX 팔레트

**빛과 환경**

| 용도 | HEX | 메모 |
|---|---|---|
| OFF 창빛 하이라이트 | #F4EBDD | 장면에서 이보다 밝은 면은 창밖뿐 |
| OFF 그림자 | #3A3F45 | 블루그레이 |
| ON 인공광 캐스트 | #F2B66D | 3000K 앰버 |
| ON 상태 벽 중간톤 | #C9A57A | 컷 1·16의 벽 기준 |
| 벽(거실·주방) | #CFC8BC | 저채도 웜그레이 |
| 상부장 | #D9D3C9 | 무광 그레이지 화이트. 제품보다 어둡게 |
| 하부장 | #8E857A | 웜 토프 |
| 주방 상판 | #6F6A64 | 무광 다크 웜그레이 쿼츠. 크림 제품과 물잔이 도드라지게 |
| 백스플래시 타일 | #BDB5A9 | 작은 직사각 타일, 웜그레이 |
| 바닥 | #A8875F | 저채도 오크 강마루 |
| 식탁 | #C4A27C | 라이트 오크 |
| 소파 | #8C8780 | 웜그레이 패브릭 |
| TV 콘솔 | #5A4636 | 월넛 |
| 커튼 | #F2EFE9 | 시어 화이트 |
| 계단실 벽 | #D8CDB8 | 오래된 베이지 페인트 |

**인물 의상(식별 앵커: 얼굴이 조금 흔들려도 옷 색으로 알아보게 한다)**

| 인물 | HEX |
|---|---|
| 아빠 잠옷(네이비 + 오프화이트 핀스트라이프) | #2E3B55 / #E8E4DA |
| 엄마 카디건(오트밀) / 티셔츠 | #D8CBB3 / #F2F0EA |
| 아이 잠옷(머스터드) | #D4A23C |
| 할머니 퀼팅 조끼(자주) | #7A3B4E |
| 대학생 후드(헤더 그레이) | #8A8D91 |
| 아랫집 아저씨 러닝셔츠 / 츄리닝 바지 | #F0F0EC / #6B6256 |

**그래픽(편집 단계 참고)**: BI 블루 #0971CE(공식 BI.png 실측 #0870CC, 오차 범위 내 동일).

### 1-4. 제품 색: 공식 사진 실측 보정 (크림 아이보리 세트 = 사진 (1)~(4)·뒷면·윗면)

공식 사진에서 면별로 픽셀을 뽑아 중앙값과 밝은 면(상위 80~95%) 평균을 냈다.

| 면 | 실측값 | 확정 기준값 |
|---|---|---|
| 조명 받는 면(lit) | 뒷면 #F3ECE1, 정면 측면띠 #EAE3D9, 윗면 #ECE4D8 → 평균 #EEE6DB | **#F1E9DC 유지**(채널당 오차 3 이내). 화면 속 제품의 가장 밝은 면 목표값 |
| 측면·도어 중간톤 | 도어 측면 중앙값 #D5CEC4, 3/4 도어 #D3CAC5 | **#D4CDC4** (패널의 #E4E0D5는 측면의 밝은 부분값 #E1DBD1에 해당) |
| 그늘 면(하단 몸체·받침) | #C4BCAF, 더 깊은 곳 #B7ADA1 | **#BFB5A8** |
| 크롬(리브·레버·발) | 어두운 #6F6D6E / 중간 #828284 / 스펙큘러 #FBFBFD | 주변 반사로 바뀌는 재질이라 고정값 없음. 4-5 참고 |
| ON 장면(3000K)의 조명 면 | 계산값(#F2B66D 40% 곱) | **약 #ECCEAA** |

- 공식 사진은 스튜디오 주광(약 5500K)으로 찍혀 있어 **OFF 장면에는 거의 그대로** 맞는다. ON 장면만 앰버를 더한다.
- 배치 원칙: 제품은 **창밖을 빼면 화면에서 가장 밝은 오브제**여야 한다. 그래서 상판(#6F6A64)과 상부장(#D9D3C9)을 제품보다 어둡게 설계했다.

### 1-5. 렌즈·카메라 규칙
- 풀프레임 환산 기준
  - 설정 와이드: 24~28mm(ENV-1, 컷 1, K4)
  - 인물: 35~50mm
  - 제품: 65~100mm. 공식 사진의 원근(망원 촬영)에 맞추려고 제품 컷에는 광각을 쓰지 않는다.
- 어안, 더치앵글, 부감 제품 컷은 쓰지 않는다. 제품이 나오는 컷의 카메라 높이는 4-4 표를 따른다.
- 9:16 안전영역: 하단 20%와 오른쪽 UI 영역에는 핵심 피사체를 두지 않는다. 하단은 바닥·상판·식탁 면으로 채운다.

### 1-6. 편집 단계 룩 처리(참고)
- OFF: WB 5600K, 채도 -18%, 하이라이트 롤오프 부드럽게, 그림자를 #3A3F45 쪽으로 살짝 띄움.
- ON: 앰버 캐스트 #F2B66D, 대비 -15%, 그림자 흐리게. "형광등 켜진 평범한 오전" 느낌.
- 정지 컷의 미세 핸드헬드 흔들림은 편집에서 넣는다(Kling 고정 컷의 재플레이트 이후에 적용).

---

## 2. 장소 설계

### 2-1. 설정
- 4층 빌라(엘리베이터 없음)의 3층. 한 층에 두 세대. 아랫집 아저씨는 2층, 할머니는 4층, 대학생은 3층 맞은편 세대.
- LDK 일체형, 약 4.2m(동서) × 6.4m(남북). 북쪽 끝이 주방, 가운데가 식탁, 남쪽 끝이 거실.
- **조리기구는 인덕션(검은 유리)으로 고정하고, 가스레인지와 가스 밸브는 어느 컷에도 보이지 않게 한다.** 가스레인지가 보이면 "정전이어도 물은 끓일 수 있잖아"라는 반론이 생겨 포트 개그의 전제가 무너진다(7장 위험 1).

### 2-2. 가구 배치도 (위에서 본 평면, 단위 cm)

```
                         N  (back wall: single-wall kitchen, counter H85 / D60)
 x=0                                                                 x=420
  +-------------------------------------------------------------------+
  |[FRIDGE][ MW ][ IH ][  SINK  ][free][P][      free 80      ]  [KW] |  <- KW: kitchen window
  |   80     50    60     80      40   11            ^            (E wall,
  |                                    ^             |             sill 105)
  |                                    |   C9/C10 ---+ (K2, S10, S11: looks WEST at P's door side)
  |                          P faces S |
  |                                     \___ C6 (K1: 3/4 from front-right) 
  |                                     \___ C18 (S18: front axis, low)
  |              ( pendant: linen drum )                              |
  |   [DOOR]     +-----------------+                     C5 (S05)     |
W |  to stair    |  TABLE  4 seats |  +2 stools for K3                 | E
  |  landing <-- +-----------------+                                  |
  |   C4 (K4: looks WEST out the door)       C3 (K3: from W side) ->  |
  |                                                                   |
  | [TV 43"]                                         [   SOFA    ]    |
  | [console]   C12a                                 [           ]    |
  |                                  C15 (K5: from E, looks W) ->     |
  |                                                          C1 (S01) |
  +=================[ LW: large living-room window, sheer curtain ]===+
                         S
```

- 표기
  - FRIDGE 냉장고, MW 전자레인지(상판 위), IH 인덕션, SINK 개수대, P 퓨리얼 PPA-300 자리(합성)
  - KW 주방 창(동쪽 벽, 상판 끝 위), LW 거실 큰 창(남쪽 벽)
- **제품 방향 규칙(가장 중요)**
  - P는 뒷면(급수 피팅)을 북쪽 벽에 붙이고 정면(출수구)이 남쪽(방)을 향한다.
  - 공식 3/4 사진 (2)와 측면 사진 (3)(4)에서 보이는 **도어 면은 정면에서 봤을 때 화면 오른쪽(동쪽, 주방 창 쪽)**이다.
  - 반대쪽(서쪽) 측면은 공식 사진이 없다. → **제품을 보는 카메라는 전부 '정면축~동쪽' 사분면에 둔다.** 서쪽에서 제품이 보이는 구도(K3 등)는 제품이 프레임에 들어오지 않게 자른다.
  - 그래서 P 오른쪽 상판 80cm를 비워 둔다. 측면 컷의 카메라 자리이면서, 주방 창빛이 도어 면을 비스듬히 비추는 통로다.
- 카메라 위치 요약

| 카메라 | 컷 | 위치·방향 | 높이 |
|---|---|---|---|
| C1 | ENV-1, 1, (2) | 거실 남동 모서리 → 북서 | 140cm |
| C3 | K3 | 식탁 서쪽 → 동쪽 | 115cm(앉은 눈높이) |
| C4 | K4 | 현관 안쪽 → 서쪽 문밖 | 150cm |
| C5 | 5 | 식탁 동쪽 → 북서(제품은 배경) | 120cm |
| C6 | K1 | 제품 앞 오른쪽 약 1m → 북서 | 상판 + 40cm (125cm) |
| C9/C10 | K2, 10, 11 | 제품 동쪽 빈 상판 위 → 서쪽(도어 면 정면) | 상판 + 14~17cm (99~102cm) |
| C15 | K5, 16 | 소파 쪽 → 서쪽(창은 화면 왼쪽, TV는 배경) | 150cm |
| C18 | 18 | 제품 정면축, 낮게 → 북쪽 | 상판 + 17cm (102cm) |

### 2-3. 연속성 앵커 (모든 컷에서 같은 공간으로 보이게 하는 고정 요소)
1. 상판 #6F6A64 무광 다크그레이 + 백스플래시 웜그레이 작은 타일 + 그레이지 상부장
2. 주방 창(KW) 창턱의 작은 스킨답서스 화분 1개
3. 냉장고 문에 붙은 아이 크레용 그림 2장(해와 집. 글자 없음)
4. 식탁 위 라탄 바구니(컷 12의 휴대폰 바구니) + 리넨 드럼 펜던트 등
5. 거실 창의 시어 화이트 커튼, 월넛 TV 콘솔
- ENV-1(무인 환경 마스터)을 먼저 확정하고, 이후 모든 실내 컷 생성에 **환경 참조 이미지로 같이 넣는다.**

### 2-4. 소품 목록 (전부 로고·글자 없음)

| 소품 | 형태 규정 | 피해야 할 형태(브랜드 연상) | 등장 컷 |
|---|---|---|---|
| 냉장고 | 연식 있는 2도어, 무광 라이트그레이 강판, 매립형 세로 손잡이, 디스플레이 없음 | 컬러 패널 조합형, 유리 전면, 도어 디스플레이 | ENV-1, 1, 배경 |
| 전자레인지 | 작은 흰색 상판형, 검은 유리 도어, 작은 사각 디지털 창(생성 시 **완전히 꺼진 빈 창**), 버튼에 글자 없음 | 특징적인 다이얼·은색 프레임 레트로형 | 1, 3-1 |
| TV | 43인치, 얇은 검은 베젤, 단순 스탠드, 베젤 로고 없음. 켜진 화면은 흐릿한 추상 색면(글자·방송사 로고 없음) | 틀 액자형(액자 TV), 특징적 스탠드 | 1, 3-2, 12-1, 15, 16 |
| 휴대폰 | 3대 **화면이 위로**(꺼진 검은 화면), 단색 실리콘 케이스(네이비·베이지·머스터드) | 뒷면 카메라 배열(삼각 3구 등)이 보이는 각도 | 12-2 |
| 전기포트 | 브러시드 스테인리스 몸체, 검은 손잡이, **본체에 직접 연결된 전원선**, 흰색 **한국형 둥근 핀 2개 플러그**(둥근 플러그 몸체, 표기 없음) | 둥근 레트로 파스텔 포트, 납작한 핀(미국형), 플러그 몸체 각인 | 14, CS-N |
| 컵 | 무늬 없는 투명 원통 유리잔, 높이 10cm, 지름 7cm. 전 컷 동일 | 브랜드 각인 잔 | 6, 7, 9, 13, 15, 17 |
| 텀블러 | 슬림 무광 스테인리스 350ml, 손잡이 없음, 단순 플립 뚜껑 | 대형 손잡이 텀블러, 특정 로고 위치의 원통형 | 14, CS-N |
| 냄비 | 스테인리스 양수 냄비 지름 20cm, 스테인리스 뚜껑 | 각인·로고 손잡이 | 14, CS-N |
| 리모컨 | 검은 기본형, 버튼에 글자·아이콘 없음 | | 16-2 |
| 펜던트 등 | 리넨 드럼 쉐이드, 전구 3000K | | 1, 13, 16, 17 |
| 천장등 | 거실 사각 LED 평판등(ON 때 평평한 빛의 원인) | | 1, 16 |
| 인덕션 | 검은 유리, **인쇄 아이콘·글자 없음** | 가스레인지, 가스 밸브 | ENV-1, 배경 |
| 수전 | 싱글레버 크롬, 단순형 | | 배경 |
| 현관문 | 진회색 철문 안쪽 면, 단순 레버 손잡이, **도어락 키패드·호수 표시가 보이지 않게** | | 14 |
| 슬리퍼 | 단색 회색·베이지 | **줄 3개 슬리퍼** | 전 인물 |

- 게시판 안내문, 시계 숫자, 자막은 생성하지 않는다. 빈 종이·빈 화면으로 만들고 편집 그래픽으로 넣는다.

---

## 3. 인물 시트

### 3-1. 고정 사양

| ID | 인물 | 외모 | 의상(고정) | 들고 다니는 소품 |
|---|---|---|---|---|
| F1 | 아빠, 40대 초 | 175cm, 보통 체격에 살짝 나온 배. 짧은 검은 머리, 자연스러운 옆가르마인데 자다 일어나 약간 뻗침. 옅은 수염 자국. **얇은 검은 사각 안경**. 차분하고 조금 피곤한 눈 | 네이비 #2E3B55 + 오프화이트 세로 핀스트라이프 긴팔 단추 잠옷 상의, 같은 네이비 하의, 회색 슬리퍼 | - |
| F2 | 엄마, 40대 초 | 163cm, 마른 편. 어깨 길이 생머리(짙은 갈색)를 낮게 느슨히 묶고 잔머리 몇 가닥. 화장기 없는 얼굴, 실용적이고 따뜻한 표정 | 오트밀 #D8CBB3 굵은 짜임 롱 카디건, 오프화이트 라운드 티, 연베이지 와이드 면바지, 베이지 슬리퍼 | - |
| F3 | 아이, 8세 여아 | 125cm. **턱선 길이 단발 + 일자 앞머리**, 동그란 볼, 호기심 많은 눈 | 무지 머스터드 #D4A23C 긴팔 면 잠옷 세트, 흰 양말 | - |
| N1 | 아랫집 아저씨, 60대 중반(2층) | 168cm, 다부지고 둥근 배. 정수리가 살짝 올라간 짧은 회색 스포츠머리, 그을린 피부, 깊은 웃음 주름, 굵은 눈썹, 멋쩍은 웃음 | 흰 #F0F0EC 민소매 골지 러닝셔츠, 회갈색 #6B6256 헐렁한 츄리닝 바지, 무지 회색 슬리퍼 | 스테인리스 전기포트(전원선·둥근 핀 플러그) |
| N2 | 할머니, 70대 초(4층) | 152cm. 짧고 촘촘한 회색 뽀글 파마, 주름진 온화한 얼굴 | 자주 #7A3B4E 퀼팅 패딩 조끼, 아주 작은 무채색 점무늬 크림 블라우스, 진회색 고무줄 바지, 베이지 슬리퍼 | 스테인리스 양수 냄비 |
| N3 | 대학생, 20대 초(3층 맞은편) | 165cm, 마른 편. 대충 올려 묶은 검은 똥머리, 잠이 덜 깬 부은 눈, 화장기 없음 | 오버사이즈 헤더그레이 #8A8D91 무지 후드(모자 내림), 검은 조거 팬츠, 흰 양말, 회색 슬리퍼 | 슬림 스테인리스 텀블러 |

### 3-2. 공통 규칙
- 전원 **가상의 인물**이다. 실존 인물·연예인·아이돌과 닮지 않게, '모델 같은' 수식어(handsome, beautiful, idol)는 쓰지 않고 **평범한 생활 얼굴, 피부 결, 약간의 좌우 비대칭**을 지정한다. 실존 인물 사진은 참조로 넣지 않는다.
- 시트를 생성할 때 후보를 4장 이상 뽑는다. 검수자가 유명인 닮음 여부를 육안으로 확인한 뒤 1장을 확정한다.
- 얼굴 클로즈업은 아이(컷 7)만 허용한다. 나머지 인물은 미디엄·뒷모습·반사·아웃포커스로 처리한다.
- 의상에 로고, 글자, 그래픽 프린트를 넣지 않는다.

### 3-3. Nano Banana 2 캐릭터 시트 프롬프트

**CS-F 가족 시트** (16:9 가로)
```
Photorealistic character reference sheet for film continuity, three original fictional Korean family members. Plain warm light-gray seamless studio backdrop (#D9D6D0), soft even 5600K daylight, gentle shadows. Layout: three columns, one per character; in each column show a close-up headshot (front), a full-body front view, and a full-body 3/4 view plus a side profile. Natural skin texture with visible pores, slight facial asymmetry, ordinary everyday faces, not models, not resembling any celebrity, actor, idol or real person.
Character F1 - DAD: Korean man, early 40s, 175 cm, average build with a slight belly, short black hair with a natural side part, slightly messy from sleep, light morning stubble, thin black rectangular glasses, calm slightly tired eyes. Wears a navy (#2E3B55) long-sleeve button-up cotton pajama shirt with thin off-white vertical pinstripes, matching navy pajama pants, plain gray indoor slippers.
Character F2 - MOM: Korean woman, early 40s, 163 cm, slim, shoulder-length straight dark-brown hair in a loose low ponytail with a few loose strands, natural no-makeup look, warm practical expression. Wears an oatmeal (#D8CBB3) chunky-knit long cardigan over a plain off-white crew-neck T-shirt, light beige wide cotton trousers, plain beige slippers.
Character F3 - CHILD: Korean girl, 8 years old, 125 cm, chin-length black bob with straight blunt bangs, round cheeks, bright curious eyes. Wears a plain mustard-yellow (#D4A23C) long-sleeve cotton pajama set with no print, white socks.
All clothing plain. No text labels, no name tags, no numbers on the sheet. no text, no logos, no brand marks.
```

**CS-N 이웃 시트** (16:9 가로)
```
Photorealistic character reference sheet for film continuity, three original fictional Korean neighbors living in the same low-rise villa. Plain warm light-gray seamless studio backdrop (#D9D6D0), soft even 5600K daylight. Layout: three columns, one per character; in each column show a close-up headshot (front), a full-body front view holding their item at waist height, and a full-body 3/4 view plus a side profile. Natural skin texture, slight facial asymmetry, ordinary everyday faces, not resembling any celebrity, actor, idol or real person.
Character N1 - DOWNSTAIRS MAN: Korean man, mid-60s, 168 cm, stocky with a round belly, very short gray buzz-cut hair with a receding hairline, tanned skin, deep smile lines, thick eyebrows, friendly sheepish grin. Wears a white (#F0F0EC) sleeveless ribbed cotton undershirt, loose gray-brown (#6B6256) track pants, plain solid gray slippers without stripes. Holds a plain brushed-stainless electric kettle with a black handle and an attached power cord ending in a white round-bodied plug with two round metal pins (Korean type).
Character N2 - GRANDMA: Korean woman, early 70s, 152 cm, short tightly permed gray curly hair, gentle wrinkled face. Wears a quilted plum-burgundy (#7A3B4E) padded vest over a cream long-sleeve blouse with a tiny muted dot pattern, dark gray elastic-waist trousers, beige slippers. Holds a plain stainless-steel two-handled cooking pot with a stainless lid.
Character N3 - STUDENT: Korean woman, early 20s, 165 cm, slim, messy top-knot bun of black hair, sleepy puffy eyes, no makeup. Wears an oversized plain heather-gray (#8A8D91) hoodie with the hood down, black jogger pants, white socks, gray slippers. Holds a slim matte stainless-steel tumbler with a plain flip lid and no handle.
All clothing and items plain. No text labels, no name tags on the sheet. no text, no logos, no brand marks.
```

---

## 4. 제품 합성 규칙

### 4-1. 원칙
1. **AI가 그린 제품 형태는 한 프레임도 쓰지 않는다.** 배경 이미지를 만들 때 제품 자리는 비워 두고, 공식 사진을 합성한다.
2. 제품 위에 다른 요소(물줄기, 컵, 손)가 겹치는 컷은 다음 순서로 만든다.
   1. 공식 사진을 합성한다.
   2. Nano Banana 편집으로 겹치는 요소만 추가한다.
   3. **겹침 마스크 밖의 제품 영역을 공식 사진 레이어로 다시 덮는다(재플레이트).**
3. Kling 클립(K1·K2)도 같은 방식이다. 카메라가 고정이므로 시작 프레임에 쓴 제품 레이어를 모든 프레임에 그대로 덮고, 물줄기·컵 영역만 마스크로 남긴다.

### 4-2. 각도별 공식 사진 매핑 (제품 크기는 흰 배경 경계 상자 실측)

| 공식 파일 | 각도 | 사진 속 제품 크기(px) | 환산 | 쓰는 컷 | 최대 표시 크기 |
|---|---|---|---|---|---|
| `PPA-300 (1).jpg` | 정면 | 282 × 909 | 2.67px/mm (높이 340mm) | 18 | 높이 ≤ 864px(화면 45%) → 0.95배 이하 |
| `PPA-300 (2).jpg` | 3/4 (정면 + 도어 면) | 679 × 848 | 약 2.49px/mm (높이) | 1, 5(배경), K1 | 높이 ≤ 864px → 1.02배 이하 |
| `PPA-300 (3).jpg` | 도어 측면, 닫힘 | 825 × 691 | 2.04px/mm (깊이 405mm) | K2, 10-1, 11-4, 11-5 | 폭 ≤ 810px(화면 75%). K2 근접 크롭은 1.6배 이하 |
| `PPA-300 (4).jpg` | 도어 측면, 열림(필터 03을 꺼내 앞에 세운 상태) | 821 × 707 | 2.03px/mm | 10-2, 11-1·11-2·11-3 | 위와 같음. 11-1 타이트 크롭 1.2배 이하 |
| `PPA-300_제품 뒷면.jpg` | 뒷면(급수 피팅 2개, 전원선 없음) | 643 × 2035 | 5.99px/mm | 8 | 1.0배 이하(풀스크린 틸트) |
| `제품 윗면`, `유로관` | | | | A'에서는 쓰지 않음 | |

- 민트·핑크·화이트 세트 (5)~(17)은 쓰지 않는다. 크림 아이보리 (1)~(4)와 뒷면·윗면만 쓴다.
- K2 '출수구 매크로' 조정: 공식 측면 사진이 1000px라 진짜 매크로는 화질이 깨진다. → **세미 매크로(출수 헤드~받침이 화면 높이의 약 55%, 1.6배 이하)**로 찍고, 초점은 생성한 물줄기·컵에 두며 제품 본체는 얕은 심도로 살짝 흐리게 한다.

### 4-3. 스케일 기준: H340 × W110 × D405mm

각 합성 컷에서 아래 비율 중 **최소 2개**로 검수한다(같은 거리에 있는 기준물끼리 비교).

| 기준물 | 실제 크기 | 제품과의 비율 |
|---|---|---|
| 유리잔(전 컷 동일 잔) | 높이 10cm | 제품 높이 = 잔의 **약 3.4배** (허용 3.0~3.6) |
| 성인 손 길이(손목 주름~가운뎃손가락 끝) | 약 19cm | 제품 높이 = 손 길이의 **약 1.8배** |
| 성인 손바닥 폭 | 약 8.5cm | 제품 정면 폭 11cm = 손바닥 폭의 **약 1.3배** |
| 성인 머리 높이(정수리~턱) | 약 23cm | 제품 높이 = 머리의 **약 1.5배** (컷 10의 아빠) |
| 상판 높이 / 깊이 | 85cm / 60cm | 제품 높이 = 상판 높이의 **0.4배**, 제품 깊이 = 상판 깊이의 **약 2/3** |
| 상판~상부장 바닥 간격 | 약 60cm | 제품이 간격의 **약 57%**를 차지 |
| 전자레인지 높이 | 약 26cm | 제품이 **약 1.3배** 높다 |
| 8세 아이(서 있음) | 125cm, 눈높이 약 113cm | 상판 위 제품 꼭대기(119cm) ≈ 아이 눈높이 바로 위 |

- **출수구 아래 공간: 약 19cm**(측면 사진 실측 추정. 출수구 하단이 상판에서 약 23.5cm, 받침 윗면이 약 4cm). → 출수구 아래에는 **유리잔(10cm)만** 둔다. 텀블러·냄비·포트를 출수구 아래에 두는 장면은 만들지 않는다.

### 4-4. 원근·카메라 높이 맞추기 (배경을 생성할 때부터 지정)

| 공식 사진 | 사진의 시점 | 배경 플레이트 카메라 |
|---|---|---|
| (1) 정면 | 제품 중간 높이에서 거의 수평. 받침 윗면이 살짝 보인다 | 상판 + 17cm, 수평, 85mm |
| (2) 3/4 | 제품 꼭대기 높이 바로 위. 상단 물결 윤곽이 살짝 보인다 | 상판 + 40cm, 수평에 가깝게, 65mm |
| (3)(4) 측면 | 제품 중간~약간 위 | 상판 + 14~17cm, 수평, 35~100mm |

- 배경 플레이트의 수평선(소실점 높이)이 위 높이와 다르면 합성하지 말고 배경을 다시 만든다. 원근이 틀린 합성은 보정으로 살릴 수 없다.

### 4-5. 합성 절차 (그림자·반사·색)
1. **컷아웃**: 흰 배경을 펜툴로 수동 마스크한다. 자동 배경 제거는 크롬 하이라이트(#FBFBFD)를 배경으로 오인해 구멍을 낸다. 가장자리는 1px 페더 + 흰 테두리 제거(디프린지).
2. **크기·위치**: 4-2 최대 배율 이하, 4-3 비율로 검수. 비율을 유지한 균등 스케일만 쓴다.
3. **색**
   - OFF 장면: 조명 면 #F1E9DC, 측면 #D4CDC4, 그늘 #BFB5A8에 커브로 맞춘다. 장면 하이라이트 #F4EBDD보다 밝게 두지 않는다.
   - ON 장면: 앰버 #F2B66D를 곱하기 40%로 얹어 조명 면이 약 #ECCEAA가 되게 한다.
4. **방향광**: 창 쪽 면은 닷지 10~15%, 반대쪽 면은 번 15~20%. 주방 창(KW)은 동쪽이라 정면 기준 화면 오른쪽에서 빛이 온다.
5. **크롬 반사**: 공식 사진의 크롬에는 흰 스튜디오가 비친다. 배경 플레이트를 20px 블러해 리브·레버·발 영역에 소프트라이트 25~35%로 얹어 방 색을 비치게 하고, 스펙큘러 점만 남긴다.
6. **그림자**
   - 접지: 크롬 원뿔 발 4개 아래 작고 진한 점 그림자 + 받침 아래 좁은 띠. 불투명도 60~70%, 블러 3~6px(1080 기준).
   - 캐스트: 창 반대 방향으로 드리운다. OFF는 40~55%, 블러 25~40px. ON(평평한 천장광)은 15~25%로 아주 흐리게.
7. **상판 반사**: 상판을 무광으로 설계했으므로 반사는 넣지 않는다.
8. **심도**: 같은 거리의 물체와 같은 양으로 블러한다(컷 1·5의 배경 제품).
9. **그레인**: 레이어 단위가 아니라 최종 프레임 전체에 한 번 입힌다.
10. **급수 피팅**: 측면 컷에서 뒷면 피팅은 벽 쪽 그림자로 어둡게 눌러 '연결 안 된 피팅'이 눈에 띄지 않게 한다. 튜브를 새로 그려 넣지는 않는다.

### 4-6. 물줄기·유리잔 추가 절차 (K1·K2 시작 프레임)
1. 배경 플레이트(KF1-BG / KF2-BG) + 공식 사진 (2) 또는 (3) 합성 → 4-5 절차 완료본.
2. Nano Banana 편집: 받침 위 유리잔 + 출수구에서 떨어지는 가는 물줄기 + 잔에 1/3 찬 물을 추가한다(프롬프트는 5장).
3. 재플레이트: 물줄기·유리잔 마스크 밖의 제품 영역을 1번 레이어로 다시 덮는다.
4. 검수: 출수구 위치와 물줄기 시작점 일치, 잔이 받침 타공판 위에 접지, 잔 높이 = 제품의 약 1/3.4.

### 4-7. 금지
- **좌우 반전 금지**: 배지 `pureal` 글자가 뒤집히고 도어 면 방향이 바뀐다.
- 비균등 스케일, 원근 왜곡 변형(리브 간격이 바뀐다) 금지.
- 공식 사진에 없는 각도(서쪽 측면, 부감, 뒤 대각선) 금지.
- 필터 라벨(한글·로고 포함)은 공식 사진 (4)의 필터만 쓴다. AI가 그린 필터는 쓰지 않는다.
- 필터 '클릭 & 로테이트'의 회전 방향, 레버를 당기거나 누르는 방향은 화살표·손동작으로 표현하지 않는다(근거 없음).
- 배지가 뭉개지면 공식 사진의 배지 영역을 다시 덮는다.

### 4-8. 합성 컷 검수 체크리스트 (컷마다)
- [ ] 공식 파일명과 각도가 4-2 표와 일치하고, 좌우 반전이 없다
- [ ] 스케일 비율 2개 이상 통과
- [ ] 배경의 카메라 높이·수평선이 4-4와 일치
- [ ] 조명 면 색이 목표 HEX ±5 이내
- [ ] 접지 그림자 + 캐스트 그림자 방향이 창 방향과 맞음
- [ ] 크롬에 흰 스튜디오 반사가 남지 않음
- [ ] 배지 글자 선명, 리브 개수·간격이 원본과 동일
- [ ] 출수구 아래에 잔 외 물체 없음, 손이 레버 근처에 없음

---

## 5. 컷별 이미지 생성 프롬프트

### 5-0. 공통 규칙
- 모든 프롬프트 끝에 `no text, no logos, no brand marks`를 넣는다. 제품이 없는 컷은 "정수기·디스펜서·커피머신이 화면에 없음"을, 제품이 있는 컷은 "제품 자리를 비워 둠"을 명시한다.
- 참조 이미지 순서: ① 인물 시트(CS-F / CS-N) ② 환경 마스터 ENV-1(실내 컷) ③ 편집 파생일 때는 원본 스틸.
- 화면비 9:16(세로). 생성 순서: CS-F → CS-N → ENV-1 → S01 → 나머지(주방 → 계단 → 거실).

### 5-1. 컷별 처리표

| # | 시간 | 이미지 ID | 처리 | 색온도 | 렌즈 | 제품 |
|---|---|---|---|---|---|---|
| - | - | ENV-1 | 신규: 무인 환경 마스터(참조용. 8·19 배경 블러에도 사용) | OFF | 24mm | 자리 비움 |
| 1 | 0.0–0.5 | S01 | ENV-1 편집: 가족 추가 + ON 조명 | ON | 24mm | (2) 작게 합성 |
| 2 | 0.5–1.4 | - | **생성 안 함**: S01을 색보정(3000K→5600K)하고 조명·TV만 마스크로 끈다 | OFF | - | S01과 같음 |
| 3 | 1.4–2.2 | S03-1, S03-2 | 신규 2장 | OFF | 50 / 35mm | 없음 |
| 4 | 2.2–3.0 | S04 | 신규(빈 안내문) | 계단 5600K | 35mm | 없음 |
| 5 | 3.0–4.0 | S05 | 신규 | OFF | 40mm | (2) 배경 아웃포커스 |
| 6 | 4.0–7.05 | KF1 | 시작 프레임(배경 + 합성 + 물줄기 편집) | OFF | 65mm | (2) |
| 7 | 7.1–9.05 | S07-1, S07-2 | 신규 1 + 편집 1 | OFF | 50mm | 없음 |
| 8 | 9.1–11.0 | - | **생성 안 함**: 공식 뒷면 컷아웃을 ENV-1 블러 배경 위에 두고 틸트 다운 | OFF | - | 뒷면 |
| 9 | 11.0–13.05 | KF2 | 시작 프레임(배경 + 합성 + 물줄기 편집) | OFF | 100mm | (3) 근접 |
| 10 | 13.1–17.05 | S10 → 10-1, 10-2 | 신규 1(아빠 플레이트). 10-1 = + (3), 10-2 = + (4) | OFF | 35mm | (3)→(4) |
| 11 | 17.1–22.3 | 11-1~11-5 | 11-1·2·3은 **합성만**, 11-4·11-5는 편집 2 | OFF | 35mm | (4)→(3) |
| 12 | 22.35–24.3 | S12-1, S12-2 | 신규 2장 | OFF | 35 / 50mm | 없음 |
| 13 | 24.35–26.65 | S13-3 → S13-2, S13-1 | 신규 1(잔 3개) + 편집 2(잔 제거) | OFF | 50mm | 없음 |
| 14 | 26.7–30.8 | KF4, S14 | 시작 프레임 + 신규 인서트 1 | 계단 5600K | 28 / 85mm | 없음 |
| 15 | 30.85–34.55 | KF5 | 시작 프레임 | OFF | 35mm | 없음 |
| 16 | 34.6–36.9 | S16-1, S16-2, S16-3 | 편집 1(KF5 기반) + 신규 1 + 편집 1 | ON→ON→OFF | 35 / 50mm | 없음 |
| 17 | 36.9–39.4 | KF3 | 시작 프레임 | OFF | 35mm | 없음(서쪽 시점) |
| 18 | 39.4–42.45 | S18 | 신규 배경 + (1) 합성 | OFF | 85mm | (1) 정면 |
| 19 | 42.45–46.0 | - | **생성 안 함**: 편집 그래픽(배경은 S18 블러) | - | - | - |
| 20 | 46.0–48.5 | - | **생성 안 함**: 편집 그래픽 | - | - | - |

- 신규 13장: ENV-1, S03-1, S03-2, S04, S05, S07-1, S10, S12-1, S12-2, S13-3, S14, S16-2, S18
- 편집 파생 8장: S01, S07-2, 11-4, 11-5, S13-2, S13-1, S16-1, S16-3
- 시작 프레임 5장: KF1~KF5 (+ KF1·KF2 물줄기 편집 2회)

### 5-2. 프롬프트

**ENV-1 · 환경 마스터** (참조: 없음, 인물 없음)
```
Photorealistic cinematic film still, vertical 9:16. Empty open-plan living-dining-kitchen of an older 4-story Korean villa apartment, 3rd floor, Saturday 10 a.m. during a power outage: every lamp and appliance is off, the room is lit only by 5600K daylight. Camera in the living-room corner at 140 cm height, 24mm lens, looking diagonally toward the kitchen at the back.
Layout: single-wall kitchen along the back wall, from left: a plain light-gray two-door refrigerator with two crayon drawings of a sun and a house taped on it, a small white countertop microwave with a dark blank display, a black glass induction cooktop with no printed icons, a stainless sink with a single-lever chrome faucet, then a clear empty stretch of countertop at the right end, and a small kitchen window on the right wall with a little pothos plant on its sill. Matte greige-white upper cabinets (#D9D3C9), warm taupe lower cabinets (#8E857A), matte dark warm-gray quartz countertop (#6F6A64), small warm-gray rectangular backsplash tiles (#BDB5A9). Mid-room: a light-oak four-seat dining table with a small rattan basket on it, a linen drum pendant lamp above (off). Left foreground: a low walnut TV console with a 43-inch thin-bezel black TV (off). Right edge: a warm-gray fabric sofa. Pale warm-gray walls (#CFC8BC), muted oak floor (#A8875F), sheer white curtains on the large living-room window off-frame right.
PRODUCT SLOT: the right end of the countertop, about 15 cm wide and 40 cm deep against the backsplash, stays completely empty and uncluttered. No water purifier, water dispenser or coffee machine anywhere.
COMPOSITION: asymmetric, kitchen weighted to the upper-right third, TV on the left third.
STYLE: natural Korean home realism, crisp directional window light with soft blue-gray shadows (#3A3F45), 35mm film grain, low saturation warm-neutral palette. No people. No gas stove.
no text, no logos, no brand marks.
```

**S01 · 컷 1 ON 와이드** (편집: 원본 ENV-1 + 참조 CS-F)
```
Edit the attached room image (ENV-1). Keep the camera, room, furniture and layout exactly the same. Change the lighting to "electricity ON": the square LED ceiling light and the linen pendant lamp are on, flooding the room with flat warm 3000K amber light (#F2B66D cast), low contrast, mixed with weak daylight from the windows; the TV is on and shows a soft out-of-focus abstract warm image with no text and no channel logo; the microwave display stays blank.
Add the family from the attached character sheet CS-F, small in frame, candid, nobody looks at camera: F2 Mom (oatmeal cardigan) at the sink with her back three-quarters to camera; F1 Dad (navy pinstripe pajamas, glasses) sitting at the dining table holding a phone with its screen facing away from camera; F3 Child (mustard pajamas, bob with bangs) sitting cross-legged on the floor in front of the TV, seen from behind.
PRODUCT SLOT: keep the right end of the countertop completely empty. No water purifier, water dispenser or coffee machine anywhere.
24mm lens, asymmetric composition as in the original, 35mm film grain, low saturation. no text, no logos, no brand marks.
```
- 합성: 공식 (2)를 상판 오른쪽 끝에 합성한다. 높이는 전자레인지의 1.3배. ON 색 보정(#ECCEAA) + 배경 블러를 맞춘다.
- 컷 2 지시(편집팀): 같은 프레임을 WB 5600K 쪽으로 플립한다. 천장등·펜던트의 발광부와 TV 화면만 마스크로 검게 꺼서 창빛만 남은 상태로 만든다. 제품 레이어는 OFF 색(#F1E9DC)으로 바꾼다.

**S03-1 · 컷 3 전자레인지** (참조: ENV-1, 인물 없음)
```
Photorealistic cinematic close-up, vertical 9:16. The front of the plain white countertop microwave from the reference kitchen (ENV-1): its small rectangular digital display window is completely dark, blank and clean, placed on the upper-left third of the frame. Power outage: 5600K daylight from the kitchen window on the right, soft blue-gray shadows, the rest of the kitchen softly blurred behind. 50mm lens, shallow depth of field, camera at the display's height. Buttons have no symbols.
PRODUCT SLOT: none in this shot. No water purifier, water dispenser or coffee machine anywhere.
35mm film grain, low saturation. no text, no logos, no brand marks.
```

**S03-2 · 컷 3 꺼진 TV** (참조: CS-F F3, ENV-1)
```
Photorealistic cinematic film still, vertical 9:16. The 43-inch thin-bezel TV on the walnut console in the reference living room (ENV-1), switched off: a glossy black screen with only a faint reflection of the bright window. In front of it, F3 Child from the character sheet (mustard pajamas, bob with bangs) sits cross-legged on the floor, seen from behind, frozen and staring at the dead screen. TV on the right two-thirds, child small at lower-left third. Power outage, 5600K daylight from the left, blue-gray shadows. 35mm lens, camera at 100 cm.
PRODUCT SLOT: none. No water purifier, water dispenser or coffee machine anywhere.
35mm film grain, low saturation. no text, no logos, no brand marks.
```

**S04 · 컷 4 계단 게시판** (참조: 없음, 인물 없음)
```
Photorealistic cinematic film still, vertical 9:16. Stairwell of an older 4-story Korean villa at mid-morning: polished terrazzo steps, stainless-steel handrail, slightly scuffed beige painted walls (#D8CDB8), a small frosted-glass window giving soft 5600K daylight, the ceiling motion-sensor light is off. On the wall, a plain cork bulletin board with one completely blank white A4 sheet held by four pins in the center of the board (left empty for graphics added later), plus two faded blank papers at its edge. Board on the right third, stairs rising on the left. 35mm lens, camera at 150 cm, slight angle to the wall.
PRODUCT SLOT: none. No water purifier anywhere. No people.
35mm film grain, low saturation. no text, no letters, no numbers on any paper. no text, no logos, no brand marks.
```

**S05 · 컷 5 아이 "목말라" / 아빠 "정전인데…?"** (참조: CS-F F1·F3, ENV-1)
```
Photorealistic cinematic film still, vertical 9:16, medium two-shot in the reference kitchen (ENV-1) during the power outage. F3 Child (mustard pajamas, bob with bangs) in the right-third foreground, shoulders up, looking up at her father with a thirsty pleading face. F1 Dad (navy pinstripe pajamas, thin black rectangular glasses) at the left third, mid-ground, leaning on the counter by the sink, looking at the dark ceiling light with a puzzled "but the power's out...?" expression. Lights off; 5600K daylight from the kitchen window on the right, directional, soft blue-gray shadows. 40mm lens, camera at 120 cm, looking north-west toward the counter.
PRODUCT SLOT: behind them, at the right end of the countertop between their heads, leave a clear empty patch of countertop (about 15 cm wide) against the backsplash, out of focus. No water purifier or dispenser anywhere in frame.
Natural candid moment, 35mm film grain, low saturation. no text, no logos, no brand marks.
```
- 합성: 빈 자리에 공식 (2)를 넣고 배경 심도만큼 블러한다. 아빠 머리 높이의 약 1.5배 크기인지 확인한다(거리 차이 고려).

**KF1-BG · 컷 6 히어로 출수 배경** (참조: ENV-1, 인물 없음)
```
Photorealistic background plate for product compositing, vertical 9:16. Close view of the reference kitchen countertop (ENV-1) from the front-right at a 3/4 angle; camera 40 cm above the countertop, nearly level, 65mm lens. On the right-center of the dark matte countertop, an area about 15 cm wide and 40 cm deep against the warm-gray tiled backsplash is completely empty and evenly lit. A single slanted beam of 5600K morning sunlight from the kitchen window on the right crosses the backsplash diagonally and lands on the empty spot; faint dust motes in the beam. Left background: the stainless sink and chrome faucet softly out of focus; top-left corner: the edge of a greige upper cabinet. Power outage: no artificial light.
PRODUCT SLOT: the empty spot is reserved for a 34 cm tall product; place nothing there. No water purifier, dispenser or appliance anywhere. No people, no hands.
COMPOSITION: asymmetric, empty spot on the right third, negative space on the upper-left.
35mm film grain, low saturation. no text, no logos, no brand marks.
```
- 합성: 공식 (2), 높이 ≤ 864px. 4-5 절차를 거친다.

**KF1 · 물줄기 편집** (편집: 합성본)
```
Edit the attached image. Add one plain clear straight-sided drinking glass, 10 cm tall, standing on the perforated drip tray directly under the chrome nozzle, and a thin, smooth, transparent stream of water falling from the nozzle into the glass; the glass is one-third full with gentle ripples. The sunbeam catches the stream. Do not change the appliance, its shape, colors, ribs, badge or lever; do not change anything else. No hands, no people. 5600K daylight, 35mm film grain. no text, no logos, no brand marks.
```
- 재플레이트(4-6) 후 Kling K1 시작 프레임으로 쓴다.

**S07-1 · 컷 7 꽉 찬 컵** (참조: CS-F F3, ENV-1)
```
Photorealistic cinematic close-up, vertical 9:16. F3 Child (mustard pajamas, chin-length bob with straight bangs) holds a plain clear glass full to the brim with water in both hands at chest height, away from her mouth, looking at it with wide delighted eyes. Face on the left third, glass on the lower-center. Power outage: 5600K window light from the right, soft blue-gray shadows; background the reference kitchen (ENV-1), softly blurred. 50mm lens, camera at her eye height 110 cm.
PRODUCT SLOT: none. No water purifier or dispenser anywhere in frame.
Natural skin, ordinary child, not a model. 35mm film grain, low saturation. no text, no logos, no brand marks.
```

**S07-2 · 컷 7 빈 컵 + "캬"** (편집: S07-1)
```
Edit the attached image. Same girl, same framing, same lighting and background. The glass is now completely empty and held slightly higher; she has just finished drinking: eyes squeezed shut, mouth open in a big satisfied "kyaa!" expression, one tiny water droplet on her upper lip. The glass is not touching her mouth. Keep her face identity, hair and clothes identical. no text, no logos, no brand marks.
```

**S10 · 컷 10·11 아빠 플레이트** (참조: CS-F F1, ENV-1)
```
Photorealistic cinematic film still, vertical 9:16. Side view along the reference kitchen countertop (ENV-1): camera 17 cm above the countertop, level, 35mm lens, looking along the counter toward the sink. The right two-thirds of the countertop in the foreground is a clear empty stretch about 45 cm long (reserved for a product to be composited). F1 Dad (navy pinstripe pajamas, thin black rectangular glasses) crouches at the left third in front of the counter, chin near countertop height, peering curiously at the empty spot with a bored "nothing else to do..." face, both hands resting on his knees. Power outage: 5600K daylight from the living-room window on the left, soft fill from behind camera, blue-gray shadows. Background: sink and fridge softly blurred.
PRODUCT SLOT: keep the empty stretch completely clear. No water purifier, dispenser or appliance there or anywhere.
COMPOSITION: asymmetric, Dad on the left third, empty space on the right two-thirds.
35mm film grain, low saturation. no text, no logos, no brand marks.
```
- 10-1 = S10 + 공식 (3), 10-2 = S10 + 공식 (4). 제품 측면 폭은 화면 폭의 60~75%. 아빠 머리 높이의 약 1.5배인지 확인한다.
- 11-1 = 10-2를 1.2배 이하로 타이트 크롭(필터 03이 상판에 서 있는 상태 = "톡")
- 11-2 = 공식 (4)의 필터 03 컷아웃을 빈 소켓 쪽으로 반쯤 들어 올린 위치에 둔다(합성만, 물건이 스스로 움직이는 스톱모션)
- 11-3 = 필터 03을 소켓 아래 01·02와 같은 높이에 정렬한다(합성만)

**11-4 · 컷 11 "내 손으로 착"** (편집: S10 + 공식 (3) 합성본)
```
Edit the attached image. The same man (F1 Dad, navy pinstripe pajama sleeve) reaches out with his right hand and presses his palm flat against the cream side door of the appliance, seen from the back of the hand, fingers together and relaxed, five fingers. His body position stays the same. Do not change the appliance's shape, color, door lines or vents; do not change anything else. 5600K daylight, 35mm film grain. no text, no logos, no brand marks.
```
- 재플레이트: 손·팔 마스크 밖의 제품은 공식 (3)으로 다시 덮는다.

**11-5 · 컷 11 끝 "뚝딱"** (편집: S10 원본)
```
Edit the attached image. Same man, same framing, lighting and background: he now stands half-up with arms folded across his chest, chin raised, a proud satisfied grin toward the empty countertop spot. Keep the countertop spot completely empty. Keep his face, glasses and pajamas identical. no text, no logos, no brand marks.
```
- 합성: 공식 (3)(도어 닫힘). 자막 "클릭 & 로테이트 셀프 교체"는 편집에서 넣는다.

**S12-1 · 컷 12 꺼진 TV에 비친 가족** (참조: CS-F, ENV-1)
```
Photorealistic cinematic film still, vertical 9:16. The glossy black screen of the switched-off 43-inch TV from the reference living room (ENV-1) fills the left two-thirds of the frame at a slight angle; the thin plain bezel runs along the right edge. In the dark reflection: the bright living-room window and the soft, dim silhouettes of the family from sheet CS-F sitting together at the dining table, recognizable by navy, oatmeal and mustard clothing. Power outage, 5600K daylight. 35mm lens, camera at 120 cm.
PRODUCT SLOT: none. No water purifier anywhere.
35mm film grain, low saturation. no text, no logos, no brand marks.
```

**S12-2 · 컷 12 방전된 휴대폰 바구니** (참조: ENV-1, 인물 없음)
```
Photorealistic cinematic film still, vertical 9:16. High three-quarter view of the small rattan basket on the light-oak dining table (ENV-1) holding three generic smartphones lying face-up with completely black, dead screens, in plain solid-color silicone cases (navy, beige, mustard); unplugged white charging cables curled beside the basket. Basket on the lower-left third. Power outage: soft 5600K window daylight from the right, long gentle blue-gray shadows, empty table space upper-right. 50mm lens.
PRODUCT SLOT: none. No water purifier anywhere. No people.
35mm film grain, low saturation. no text, no logos, no brand marks, no camera lenses visible.
```

**S13-3 · 컷 13 잔 3개** (참조: CS-F F2, ENV-1)
```
Photorealistic cinematic film still, vertical 9:16. Three identical plain clear drinking glasses, 10 cm tall, each filled with water, standing in a loose diagonal line on the light-oak dining table (ENV-1), on the right third of the frame. Morning 5600K window light from the right makes bright caustic patterns on the table. In the blurred background, F2 Mom (oatmeal cardigan) walks away toward the kitchen, soft and out of focus. 50mm lens, camera at seated eye height 115 cm.
PRODUCT SLOT: none. No water purifier, dispenser or pitcher in frame.
35mm film grain, low saturation. no text, no logos, no brand marks.
```
- S13-2, S13-1(편집): "Edit the attached image: remove the rightmost glass (then the middle glass). Keep everything else identical. no text, no logos, no brand marks."

**KF4 · 컷 14 현관 밖 이웃** (참조: CS-N N1·N2·N3, CS-F F1)
```
Photorealistic cinematic film still, vertical 9:16, frame-in-frame through a fully open front door, seen from inside a Korean villa apartment. Camera in the dim entryway at 150 cm, 28mm lens. Left foreground: F1 Dad's back and shoulder (navy pinstripe pajamas), out of focus, standing still inside the door frame. Through the doorway, on the bright stair landing, the three neighbors from sheet CS-N are already standing side by side facing camera, feet planted, with hopeful, slightly sheepish smiles: N2 Grandma (plum quilted vest) holding a stainless two-handled pot at waist height; N3 Student (gray hoodie, messy bun) holding a slim stainless tumbler at waist height; N1 Downstairs Man (white sleeveless undershirt) holding a stainless electric kettle at waist height, its power cord tightly coiled and gripped in the same hand, nothing hanging. Landing lit by soft 5600K daylight from a frosted stairwell window; apartment interior has no lights on. Plain dark-gray steel door, inner side, no keypad and no unit number visible. Door frame on the left third, neighbors grouped right of center.
PRODUCT SLOT: none. No water purifier anywhere.
35mm film grain, low saturation. no text, no logos, no brand marks.
```

**S14 · 컷 14 인서트: 덜렁거리는 플러그** (참조: CS-N N1)
```
Photorealistic cinematic insert close-up, vertical 9:16. N1 Downstairs Man's tanned hand (edge of his white ribbed undershirt visible) holds the stainless electric kettle by its black handle at the top of frame; from the kettle a white power cord hangs straight down and a white round-bodied plug with two round metal pins (Korean type) dangles in mid-air at the lower-left third, in sharp focus. Background: the bright stair landing, softly blurred. Soft 5600K daylight. 85mm lens, shallow depth of field.
PRODUCT SLOT: none. No water purifier anywhere.
No markings on the plug. 35mm film grain, low saturation. no text, no logos, no brand marks.
```

**KF5 · 컷 15 창가의 여섯 명** (참조: CS-F + CS-N, ENV-1)
```
Photorealistic cinematic film still, vertical 9:16. Six people stand together by the large living-room window of the reference apartment (ENV-1), seen from the sofa side: the window with sheer curtains on the left edge of frame lights them with soft 5600K daylight from the left; the switched-off black TV on the back wall at the right. Family from sheet CS-F in the center-left: F3 Child in front, F1 Dad and F2 Mom behind her. Neighbors from sheet CS-N toward the right and edges: N2 Grandma, N3 Student, N1 Downstairs Man. Everyone holds one plain clear glass of water at chest height, glasses well apart from each other, smiling and about to raise them. The neighbors' pot, tumbler and kettle sit on the windowsill. Feet visible and planted. 35mm lens, camera at 150 cm.
PRODUCT SLOT: none. No water purifier or dispenser anywhere in frame.
COMPOSITION: asymmetric, group weighted to the left two-thirds, open space on the right around the black TV.
35mm film grain, low saturation. no text, no logos, no brand marks.
```

**S16-1 · 컷 16 전기 복귀 "아…"** (편집: KF5. K5가 먼저 통과했으면 K5 마지막 프레임을 원본으로 쓰는 쪽이 연속성에 낫다)
```
Edit the attached image. Same six people, same framing. The power has just come back: the ceiling light and the pendant are on, flooding the room with flat, warm 3000K amber light (#F2B66D cast), low contrast; the TV on the back wall is on, showing a soft out-of-focus abstract image with no text and no channel logo. Everyone has their glass raised at face height and freezes, looking up at the ceiling light with deflated "aah..." faces. Keep every face, hairstyle and outfit identical. No water purifier in frame. no text, no logos, no brand marks.
```

**S16-2 · 컷 16 아이가 TV를 끈다** (참조: CS-F F3, ENV-1)
```
Photorealistic cinematic film still, vertical 9:16, medium shot. F3 Child (mustard pajamas, bob with straight bangs) stands in the living room holding her glass in one hand and pointing a plain black TV remote with unlabeled buttons toward the TV off-frame right, with a determined serious face. Flat warm 3000K overhead light (power just restored). Behind her, the family and neighbors blurred. Girl on the left third, 50mm lens, camera at 110 cm.
PRODUCT SLOT: none. No water purifier anywhere.
35mm film grain, low saturation. no text, no logos, no brand marks.
```

**S16-3 · 컷 16 다시 창빛** (편집: S16-1)
```
Edit the attached image. Same people and framing. The TV is now off (black screen) and the ceiling and pendant lights are off; the room is back to soft 5600K daylight from the window on the left with blue-gray shadows. Everyone lowers their glass and smiles warmly toward the girl, who holds the remote at her side. Keep every identity and outfit identical. No water purifier in frame. no text, no logos, no brand marks.
```

**KF3 · 컷 17 식탁 리얼 모먼트** (참조: CS-F + CS-N, ENV-1)
```
Photorealistic cinematic film still, vertical 9:16. Six people around the light-oak dining table of the reference apartment (ENV-1) under the switched-off linen drum pendant. Soft 5600K daylight from the living-room window on the right. Camera on the west side of the table at seated eye height 115 cm, 35mm lens, framed tight on the table (kitchen counter not visible). The family from sheet CS-F is in the center, sharp: F1 Dad center-left laughing, F2 Mom center-right turning toward him with a smile, F3 Child between them kneeling on her chair, giggling. Neighbors from sheet CS-N: N1 Downstairs Man (white undershirt) and N3 Student (gray hoodie) in the foreground with their backs to camera, out of focus; N2 Grandma (plum vest) at the right edge in soft profile. Hands rest on the table near plain clear glasses of water. A candid, warm, unposed conversation.
PRODUCT SLOT: none. No water purifier or dispenser anywhere in frame.
COMPOSITION: asymmetric, family weighted to the left two-thirds.
35mm film grain, low saturation. no text, no logos, no brand marks.
```

**KF2-BG · 컷 9 출수구 세미 매크로 배경** (참조: ENV-1, 인물 없음)
```
Photorealistic background plate for product compositing, vertical 9:16. Low side view along the reference kitchen countertop (ENV-1): camera 14 cm above the dark matte countertop, level, 100mm macro lens at f/2.8, very shallow depth of field. The center and right of the countertop in the foreground are empty (reserved for a product composited later). Left side of frame: the bright dining area and living-room window, heavily blurred into soft cream and daylight tones; light comes from the left. Background behind: sink faucet and refrigerator as soft blurred shapes. Power outage, 5600K.
PRODUCT SLOT: keep the foreground countertop completely empty. No water purifier, dispenser or appliance anywhere. No people, no hands.
35mm film grain, low saturation. no text, no logos, no brand marks.
```
- 합성: 공식 (3)을 출수 헤드~받침이 화면 높이의 약 55%가 되게(1.6배 이하) 배치한다. 출수구는 좌상 1/3 지점, 받침과 잔은 좌하 1/3 지점. 몸체는 오른쪽으로 화면 밖까지 이어진다.

**KF2 · 물줄기 편집** (편집: 합성본)
```
Edit the attached image. Add one plain clear straight-sided drinking glass, 10 cm tall, standing on the drip tray under the nozzle, in sharp focus, and a thin, smooth, transparent water stream from the nozzle into the glass; the glass is one-third full with small bubbles. Do not change the appliance's shape, color, nozzle or door lines; do not change anything else. No hands. 5600K, 35mm film grain. no text, no logos, no brand marks.
```

**S18 · 컷 18 정면 히어로 배경** (참조: ENV-1, 인물 없음)
```
Photorealistic background plate for a product hero shot, vertical 9:16. Front-on low view across the dark matte quartz countertop (#6F6A64) of the reference kitchen (ENV-1); camera 17 cm above the countertop, level, 85mm lens; the warm-gray tiled backsplash behind, softly defocused. A soft beam of 5600K morning window light from the right falls diagonally across the wall. The left third of the countertop is completely empty (reserved for a 34 cm tall product composited later). On the countertop just right of center, at the same depth, one plain clear glass of water, 10 cm tall. Upper-right third: calm, clean negative space for graphics.
PRODUCT SLOT: keep the left-third spot completely clear. No water purifier, dispenser or appliance anywhere. No people.
35mm film grain, low saturation. no text, no logos, no brand marks.
```
- 합성: 공식 (1), 높이 ≤ 864px(화면 45%), 왼쪽 1/3. 옆 유리잔이 제품 높이의 약 1/3.4인지 확인한다. 칩 그래픽은 오른쪽 위 1/3에 들어간다.

---

## 6. AI 영상이 약한 동작: 금지 목록 + Kling 모션 프롬프트

### 6-1. 금지 동작 (Kling 전 클립 공통. 정지 컷에서는 손 정지 포즈만 허용하고 손가락 수를 검수한다)

| 금지 동작 | 결함 유형 | 대체 방식 |
|---|---|---|
| **마시기**(입과 컵 접촉) | 수위가 줄지 않음, 입술과 컵이 붙음 | 컷 7: 꽉 찬 컵 → 빈 컵 + "캬" 정지 2장 |
| **보행**(걷기, 들어오기, 뒤돌기) | 발 미끄러짐, 다리 꼬임 | K4: 이웃이 이미 서 있음. 발은 붙인 채로 |
| **건배 충돌**(잔 맞대기) | 잔이 녹아 붙음, 손과 잔 융합 | K5: 잔끼리 떨어진 채 위로만 든다 |
| **손가락 디테일**(물건 주고받기, 필터 끼우기, 버튼 누르기) | 손가락 수 오류, 물체 관통 | 컷 11: 스톱모션 + 손바닥 정지 1장 / 컷 16: 리모컨 정지 |
| **늘어진 전선 움직임** | 전선이 녹거나 끊기거나 진자처럼 과장됨 | K4: 전선을 손에 감음. 덜렁거림은 S14 정지 인서트로만 |
| **레버 조작**(손이 레버 근처에 가는 것 포함) | 조작 방향 근거 없음 + 형태 변형 | 물줄기가 이미 흐르는 상태로 시작. "(톡!)"은 컷이 들어오는 순간에 맞춘다 |
| 손으로 따르기(용기→컵) | 물 궤적 오류 | 쓰지 않음 |
| 문 여닫기 동작 | 문이 휘거나 관통 | 문은 이미 열린 상태 |
| 카메라 회전·궤도·큰 이동 | 공식 사진에 없는 각도가 드러남 | 고정 또는 3% 이내 푸시인 |
| 제품 위 조명 변화(켜짐·꺼짐) | 제품 색과 형태 흔들림 | 조명 변화는 정지 컷과 편집으로 |

### 6-2. Kling 모션 프롬프트 (5초로 생성해 편집에서 자른다)

**K1 · 컷 6 히어로 출수 (3.05초) · 카메라 고정**
```
Locked-off static shot, no camera movement. A thin, clear, steady stream of water keeps pouring from the nozzle into the glass on the drip tray; the water level in the glass rises slowly and steadily; gentle ripples on the surface. The slanted sunbeam on the wall stays fixed while faint dust motes drift slowly through it. The appliance stays completely still and unchanged. No people, no hands.
```
Negative: `camera movement, zoom, pan, hands, fingers, lever moving, appliance moving or changing shape, morphing, extra water streams, splashing out of the glass, new objects, flicker, text, logos`

**K2 · 컷 9 출수구 세미 매크로 (2.05초) · 카메라 고정**
```
Locked-off static close-up, no camera movement, shallow depth of field. Clear water streams steadily from the nozzle into the glass; the water level rises from about one third to two thirds of the glass; small bubbles swirl; light glints on the water surface. The appliance stays perfectly still and unchanged. No hands.
```
Negative: `camera movement, focus shift onto background, hands, lever moving, appliance morphing, overflowing, splashing, extra streams, text, logos`

**K3 · 컷 17 식탁 리얼 모먼트 (2.5초) · 카메라 고정(필요하면 3% 이내 느린 푸시인)**
```
Static camera, optionally a very slow push-in of no more than 3 percent. The family at the table talk and laugh naturally: the father laughs with his shoulders shaking, the mother turns her head toward him smiling, the child giggles and leans toward her mother. Hands stay resting on the table; the glasses stay where they are. The neighbors in the foreground stay almost still with only slight breathing. The soft daylight stays steady.
```
Negative: `drinking, lifting glasses, passing objects, standing up, walking, clapping, hand gestures, finger movement, faces changing identity, lights turning on, camera orbit, text, logos`

**K4 · 컷 14 이웃 3명 (4.1초) · 카메라 고정**
```
Locked-off static shot through the open front door. The three neighbors stand on the landing with their feet planted. In one simultaneous motion they lift their items, the pot, the tumbler and the kettle, from waist height up to chest height and hold them there, with hopeful, slightly embarrassed smiles and small nods. The kettle's cord stays tightly coiled in the man's hand. The man in the out-of-focus foreground does not move.
```
Negative: `walking, stepping forward, entering the apartment, door moving, cord swinging, dangling cable, lids opening, finger close-ups, objects morphing, extra people, text, logos`

**K5 · 컷 15 창가에서 잔 들기 (3.7초) · 카메라 고정**
```
Static camera. The six people by the window raise their glasses together from chest height to just above head height and laugh, then hold the pose. Every glass stays clearly separated from the others: no clinking, no contact. Feet stay planted. The soft daylight from the window stays steady.
```
Negative: `clinking glasses, glasses touching, drinking, walking, turning around, jumping, spilling, hands merging with glasses, identity change, lights turning on, camera movement, text, logos`

- 공통 후처리: K1·K2는 재플레이트(4-1). K3~K5는 결함 프레임이 있으면 그 구간을 잘라 쓰고, 실패하면 시작 프레임 정지 + 줌으로 바로 대체한다(재작업은 1회까지).

---

## 7. 위험 요소와 감독 확인 요청

| # | 위험 | 대응 | 확인 필요 |
|---|---|---|---|
| 1 | **가스레인지가 보이면 "정전이어도 끓일 수 있다"는 반론**으로 포트 개그의 전제가 흔들린다 | 주방을 인덕션으로 고정하고 가스레인지·밸브 노출을 금지 | 아이디어팀·사실검증: 이웃 집도 전기 조리라는 전제를 받아들일지 |
| 2 | 출수구 아래 공간이 약 19cm(사진 추정)라 텀블러·냄비는 출수구 아래에 들어가지 않는다 | 출수구 아래에는 유리잔만. 이웃 용기는 들고 있거나 창턱에 둔다 | - |
| 3 | 공식 측면 사진이 1000px라 진짜 매크로(컷 9)는 화질이 깨진다 | 세미 매크로, 1.6배 이하, 초점은 물줄기 | 아이디어팀: '매크로'를 세미 매크로로 바꾸는 데 동의 여부 |
| 4 | 6인 컷(K3·K5·S16)에서 얼굴이 흔들린다 | 의상 색 앵커, 이웃은 뒷모습·아웃포커스, 시트 참조 고정 | - |
| 5 | 서쪽 측면 공식 사진이 없어 카메라 방향이 제한된다 | 모든 제품 컷을 정면~도어 쪽 사분면에서 찍는다. K3는 제품이 프레임 밖 | - |
| 6 | Nano Banana가 빈 자리에 정수기를 그려 넣거나 TV·전자레인지에 글자를 넣을 수 있다 | 프롬프트에 금지 명시, 검수 때 확인 후 재생성 | - |
| 7 | Kling이 배지·리브를 바꿀 수 있다 | 카메라 고정 + 재플레이트 | K1 단독 선결제 때 함께 확인 |
| 8 | 플러그가 미국형 납작 핀으로 그려질 수 있다 | S14 검수 항목: 둥근 핀 2개, 각인 없음 | - |
| 9 | 브랜드 연상 형태(줄 3개 슬리퍼, 대형 손잡이 텀블러, 뒷면 카메라 배열, 컬러 패널 냉장고) | 2-4 소품표의 금지 형태 | 규정 검수 |
| 10 | 인물이 실존 인물·연예인을 닮을 수 있다 | 후보 4장 이상 → 검수자가 육안 비교 후 확정 | 규정·권리 검수 |
| 11 | 컷 11-2, 11-3은 필터 03이 '스스로' 움직이는 스톱모션이고, 11-3의 장착 상태는 공식 사진 (4)의 01·02 장착 모습을 근거로 재구성한 것이다 | 소켓 위치를 정확히 정렬하고, 회전 방향은 표현하지 않는다 | 사실검증: 03 슬롯 위치(맨 왼쪽 빈 소켓)가 맞는지 |

---

### 사용자가 알아야 할 핵심 (한국어 요약)
- 제품은 AI로 그리지 않는다. 빈 자리를 둔 배경을 만들고 **공식 사진만 합성**한다. 각도별로 쓸 파일과 최대 확대 배율을 정했다.
- 제품 색 #F1E9DC는 공식 사진 실측과 일치해 그대로 쓴다. 측면 #D4CDC4, 그늘 #BFB5A8을 추가로 정했다.
- 정전은 색으로 보여 준다(전기 켜짐 3000K 앰버 ↔ 정전 5600K 창빛). 정전 때 빛이 오히려 더 예쁘게 보이도록 설계했다.
- 가족 3명, 이웃 3명은 옷 색으로 구분한다. 캐릭터 시트는 가족 1장, 이웃 1장이다.
- 이미지 생성: 인물 시트 2장 + 정지 컷 21장 + Kling 시작 프레임 5장. 모두 무료 경로(Nano Banana)로 만든다.
- 주의할 점
  - 주방에 가스레인지가 보이면 "정전이어도 물은 끓일 수 있다"는 허점이 생긴다. 그래서 인덕션으로 고정했다.
  - 출수구 매크로 컷은 공식 사진 해상도의 한계 때문에 '세미 매크로'로 조정했다.

---
## 감독 결정 (2026-10-08, 디자인·타이포 통합)
- **인덕션 채택**: 가스레인지가 보이면 포트 개그의 전제("물을 못 끓인다")가 무너진다. 아이디어팀 기획의 전제를 강화하는 변경이라 수용한다.
- **컷 9 세미 매크로(확대 1.6배 이하) 채택**: 공식 측면 사진 해상도의 한계 때문.
- **컷 11 필터**: 소켓 장착 위치·회전 방향은 근거가 없다. 공식 필터 사진(1년 필터 모음, 1·2·3번 필터)의 스톱모션과 손바닥 정지 컷만 쓰고, 끼우는 위치와 방향은 보여 주지 않는다(사실검증 생략 가능).
- **타이포 연동**: 글꼴 체계는 타이포팀안(proposals\type)으로 확정한다. 엔딩은 Noto Serif KR, 자막은 Pretendard, 안내문은 나눔고딕·명조, 시계는 DSEG7. 칩 #0971CE와 필수 문구 #3A3F45는 이 가이드 팔레트와 일치한다.
- **3번 컷 시계**: 정전 뒤 장면이므로 꺼진 상태. 켜진 '10:00'은 1번 컷에 쓴다.
- **5·7번 밝은 창빛 컷**: 대사 자막에 타원 스크림(31%)을 필수로 넣는다.
