# 글꼴 라이선스 기록 (2026-10-08, editor)

모두 SIL Open Font License 1.1 (OFL). 라이선스 원문은 같은 폴더의 `OFL-*.txt` (각 공식 저장소의 원본 그대로).
원문 허가 조항: "Permission is hereby granted, free of charge, to any person obtaining a copy of the Font Software, to use, study, copy, merge, embed, modify, redistribute, and sell modified and unmodified copies of the Font Software, subject to the following conditions: 1) ... may not be sold by itself."
-> 영상·자막에 사용(상업 이용 포함)과 파일 임베딩은 허용. 금지는 글꼴 파일 자체를 단독 판매하는 것, 예약 글꼴 이름을 단 수정본 배포. 우리는 글꼴을 수정하거나 재배포하지 않고 영상 렌더에만 쓴다.

| 용도 키 | 글꼴 | 파일 | 출처 URL | 라이선스 원문 |
|---|---|---|---|---|
| osd | Galmuri11 Bold (v2.40.4) | Galmuri11-Bold.ttf | https://github.com/quiple/galmuri/releases/tag/v2.40.4 (Galmuri-v2.40.4.zip) | OFL-Galmuri.txt (zip의 LICENSE.txt, Copyright 2019-2025 Lee Minseo) |
| radio | Black Han Sans Regular | BlackHanSans-Regular.ttf | https://github.com/google/fonts/tree/main/ofl/blackhansans | OFL-BlackHanSans.txt (Copyright 2015 The Black Han Sans Project Authors) |
| doc | Nanum Myeongjo ExtraBold | NanumMyeongjo-ExtraBold.ttf | https://github.com/google/fonts/tree/main/ofl/nanummyeongjo | OFL-NanumMyeongjo.txt (Copyright 2010 NHN Corporation, 예약 글꼴 이름 Nanum 계열) |
| info | Pretendard (기존) | Pretendard-*.otf | github.com/orioncactus/pretendard | OFL-Pretendard.txt |

## 글리프 확인 (Pillow로 직접 렌더 비교)
- Galmuri11 Bold: ①②③ ☐ · ※ # 한글 모두 있음.
- Black Han Sans: 한글·# 있음 / **①②③ ☐ · ※ 없음** -> 작전 배지는 노란 원을 직접 그리고 숫자는 ASCII로 쓴다. 자막 문구에 · ※ 는 쓰지 말 것(경고 후 대체).
- Nanum Myeongjo ExtraBold: 한글 · ※ # 있음 / **① ② ③ ☐ 없음** -> 결재 칸 사각형은 직접 그린다.
