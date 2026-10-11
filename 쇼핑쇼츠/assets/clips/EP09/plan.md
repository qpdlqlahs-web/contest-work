# EP09 기획 v2 — 새벽 3시 옷방 1인 소파, 털 제거 롤러 특공대

- 상품군(가정): 재사용 반려동물 털 제거 롤러. 상품명·가격·리뷰·링크 = TBD (영수 님 선정 후 채움)
- 장소: 작은방(옷방) 1인 소파 + 검은 옷 더미. (1~8화: 현관·거실 디퓨저·주방·욕실·펫캠 코기·냉동실·신발장·세탁기 — 겹침 없음. 예시의 '거실 소파'는 2화 거실과 겹쳐 옷방으로 변경)
- 카메라: CLOSET CAM(키트가 cam 라벨 표시), 03:14 시작, 컬러 후일담 07:30
- 구성: 동물 1(밝은색 장모 고양이) + 눈알 소품(롤러 특공대). 대사 없음, 효과음+자막. 공포·유령 없음.
- 총 길이 29.8초 / 영상 클립 4개 / 예상 10크레딧

## 키워드
- 검색어: 고양이 털 청소, 소파 털 제거, 반려동물 털 제거 롤러, 옷 털 제거 강아지, 펫 털 청소 도구
- 제목 후보
  1. 고양이 털 청소, 새벽 3시 옷방 CCTV에 찍힌 롤러 특공대
  2. 소파 털 제거 작전 | 옷방 CCTV에 찍힌 롤러들의 야간 근무
  3. 고양이 털 옷에 붙는 집, 새벽 3시 롤러 특공대 출동
- AEO 첫 줄: 반려동물 털 제거 롤러는 소파·옷 표면을 굴려 붙은 털을 한곳에 모아 떼어내는 청소 도구입니다. (상품 확정 후 형태에 맞게 재확인)
- 해시태그: #고양이털청소 #털제거롤러 #소파청소 #반려동물용품 #새벽3시CCTV

## 0~1초 훅
첫 프레임부터 밝은색 장모 고양이가 몸을 확 털어 털이 폭죽처럼 사방으로 터짐(첫 프레임에 이미 털이 공중에, 어두운 옷 더미 위라 밝은 털이 대비됨). 정지 화면 없음. 0.0초 자막 "새벽 3시, 옷방에서 털이 터졌다"(사건 암시), 1.0초 감지 박스 점멸. (장소·시간은 cam/clock 라벨이 표시하므로 자막 중복 제거)

## 컷 표 (합 29.8초. 들킴 시작 9.9초 ≤12초, 반전 시작 12.3초)
영상 세그먼트는 원본 클립(5초) 안에서 start + dur x speed ≤ 4.9 (dur = 화면에 보이는 길이, make_cctv.py가 dur x speed만큼 원본을 읽음).

| # | 컷 | 시작초 | 길이 | 원본 구간 | 내용 | 이미지/영상 | 재사용 |
|---|---|---|---|---|---|---|---|
| 1 | 오프닝 | 0.0 | 3.0 | A 0.5~3.5 | 고양이가 소파 위에서 몸을 털어 털 폭발. 자막 "새벽 3시, 옷방에서 털이 터졌다" | 영상 A | A 앞부분 |
| 2 | 작전① 돌격 | 3.0 | 2.3 | B 0.3~2.6 | 눈알 롤러 3개가 쿠션으로 우르르 돌격, 한 개가 굴러가며 쿠션 위 털이 줄무늬로 쓸려 롤러에 감김(상품 장점). 자막 "작전 ① 롤러 특공대 돌격" | 영상 B | B 앞 |
| 3 | 작전② 팔걸이 | 5.3 | 2.3 | B 2.6~4.9 | 롤러가 팔걸이를 쓸어 올리자 털이 한 덩이로 모여 롤러에 붙음. 자막 "작전 ② 팔걸이 진입", 스탬프 "수거" | 영상 B | B 뒤 |
| 4 | 작전③ 옷 더미 | 7.6 | 2.3 | C 0.3~2.6 | 롤러가 검은 니트 위를 쓸자 털이 줄지어 모여 붙음(클로즈업). 자막 "작전 ③ 옷 더미 정리" | 영상 C | C 앞 |
| 5 | 들킴 | 9.9 | 2.4 | D 0.2~2.6 | 복도 불빛이 확 비침, 롤러들 얼어붙음, 고양이는 고개만 돌려 카메라 응시. BGM 정적 9.9~12.3. 스탬프 "들킴" | 영상 D(1동작) | D 단독 |
| 6 | 반전 | 12.3 | 3.4 | A 2.6~4.8 (speed 0.65) | 오프닝 후반 '멈췄다가 다시 폭발' 재사용 슬로모션(다시보기 표시). 자막 "…주인공은 고양이였다 / 작전 성공?" | 영상 A 후반 | A 후반(오프닝과 2.6~3.5초 약 0.9초 겹침, 속도가 달라 허용) |
| 7 | 두루 | 15.7 | 3.2 | - | 소파 틈의 두루(눈알 휴지) 끝에 털뭉치가 붙어 들킨 표정. 자막 "…너는 왜 롤러 줄에?" | 이미지 duru.png + 줌 + question.wav | 무료 |
| 8 | 아침 후일담 | 18.9 | 4.5 | - | 컬러 07:30, 출근하는 집주인 양말 발만 보임, 롤러는 가지런히 서 있고 고양이는 시치미. 자막 "아침 7시 30분, 작전 종료" | 이미지 morning.png + 줌 | 무료 |
| 9 | PPL | 23.4 | 6.4 | - | PPL 카드(master.png dim 0.6). 헤드라인 "털 청소 특공대 채용 (택1)" | 이미지 master.png | 무료 |

합계 3.0+2.3+2.3+2.3+2.4+3.4+3.2+4.5+6.4 = 29.8초.

백업(반전 실패 시): A 후반에 '두 번째 폭발'이 안 나오면 반전을 정지 이미지 EP09_reverse.png(줄무늬 일부만 쓸린 소파 위에 누운 밝은 고양이 + 공중에 떠 있는 털 + 눈알 처진 롤러) + 줌 + hits로 대체. 길이·크레딧 불변, 이미지 1장 추가(무료). 이 이미지는 지금 만들지 않음.

## 이미지 (웹 Nano Banana 2 + Unlimited, 무료) — 파일명은 episode.json과 일치
master.png, EP09_opening_start.png, EP09_attack_start.png, EP09_sweep_start.png, EP09_caught_start.png, duru.png, morning.png (7장, 백업 EP09_reverse.png는 필요 시)

공통 소품 문구(모든 프롬프트에 동일하게 박을 것)
- ROLLER = "generic cylindrical lint roller with a white sticky roll and a black handle, no brand text, one plastic googly eye sticker on the roll"
- CAT = "fluffy light-colored long-haired cat"
- NEG = "no text, no letters, no logos, no watermark, no subtitles, no timestamp"
- 접두(2~7번) = "Edit this exact CCTV image, keep the same camera angle, black and white infrared night vision, fisheye distortion, real photographic props, cute and silly tone, no ghosts, no horror,"
- 레퍼런스: 2~7번 모두 master.png 첨부. 3·4·5번은 EP09_attack_start.png도 추가해 롤러 외형 고정.

1. master.png: A small closet room seen from a fixed ceiling-corner CCTV at night, black and white infrared, fisheye lens, one small armchair against the wall, a pile of dark knit clothes beside it, a sleeping CAT curled on the armchair, door closed. NEG.
2. EP09_opening_start.png: [접두] the CAT on the armchair is mid-shake, body twisted, a big burst of cat fur already exploding into the air and floating over the dark clothes pile, cat wide-eyed. NEG.
3. EP09_attack_start.png: [접두] three ROLLERs lined up on the armchair cushion, the cushion covered in cat fur, one roller leaning forward as if about to roll. NEG.
4. EP09_sweep_start.png: [접두] closer framing on the dark knit clothes pile covered in cat fur, one ROLLER about to roll across the knit, a few clean stripes already visible beside it. NEG.
5. EP09_caught_start.png: [접두] the door is slightly ajar, a thin bright strip of hallway light on the floor, three ROLLERs mid-pose on the armchair looking toward the door, the CAT sitting on the armchair. NEG.
6. duru.png: [접두] a roll of toilet paper with googly eyes (no brand) wedged between the armchair and the wall, a tuft of cat fur stuck on its loose paper tail, looking guilty at the camera. NEG.
7. morning.png (COLOR, not infrared; 접두에서 black and white infrared, fisheye 제외하고 "soft warm morning light, same camera angle"): armchair with three neat ROLLERs standing in a row, the CAT sitting innocently on the cushion looking away, only socked feet of a person walking out the door visible. NEG.

## 영상 프롬프트 (Seedance Mini 480p, generate_audio false, duration 5, 각 2.5크레딧)
공통 앞머리(모든 영상): "Black and white infrared CCTV footage from a fixed ceiling-corner fisheye camera, camera never moves," 공통 끝: NEG.
- A opening(시작 프레임 EP09_opening_start.png): The CAT shakes violently and a huge cloud of cat fur bursts out; it pauses for a moment, then shakes again and the fur bursts a second time, fur drifting over the clothes pile.
- B attack(EP09_attack_start.png): Three ROLLERs charge across the armchair cushion; one rolls forward and the fur on the cushion is swept up in a few clean stripes onto the roller, then another rolls up the armrest and the fur gathers into a clump on the roller.
- C sweep(EP09_sweep_start.png): A ROLLER rolls across the dark knit clothes, cat fur lifts off the fabric and sticks onto the roller in a line, leaving a few clean stripes.
- D caught(EP09_caught_start.png, 들킴 1동작): Hallway light suddenly floods in through the open door, the ROLLERs freeze in place staring at the door, and the CAT slowly turns its head only to look straight at the camera.

## 예상 크레딧
영상 4 x 2.5 = 10 크레딧(한도 12 이내). 이미지 전부 웹 Nano Banana 2 Unlimited = 0. Kling은 Seedance 실패 컷만(그땐 PD 보고).
- 생성 전 `higgsfield generate cost` 확인, A 1컷 테스트(두 번째 폭발 확인) 후 나머지.

## 안전·규정
- 효과 단정 금지: "작전 성공?", "수거" 등 연출어만. '털 0'·'말끔' 류 금지(줄무늬 일부만 쓸림).
- 롤러는 브랜드·로고 없는 일반형 소품. 실제 상품처럼 그리지 않음. 상품명은 PPL 카드에만.
- 유튜브 '변경되거나 합성된 콘텐츠' 체크, AI 연출 표시.
- 대가성 문구 2종(네이버·쿠팡) 고정 댓글/설명란 되읽기(업로드 직전·직후). 업로드 직전 TBD(가격·리뷰·링크)·상품 진행 상태 확인.
