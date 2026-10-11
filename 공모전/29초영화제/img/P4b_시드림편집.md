# P4b 낙산 — 근경 수면·부두 제거 (Seedream 4.5 편집, 0cr)

편집 항목: P4-01(수면 x0–314 y1261–1440), P4-02(부두 선 x0–422 y1216–1280). 좌표는 원본 1440×2560.
사실 근거: 낙산 성곽길 아래에는 수면이 없다. 이 자리는 성곽 너머 **어두운 숲 사면 + 멀리 시가지 불빛**이어야 한다.
로컬 처리(edit_plates.py `LOCAL_COVER`)는 타일 이음·평평한 검은 덩어리·인공적인 수관선 때문에 탈락했다.

## 1. 생성 (사용자, Higgsfield 웹)
- 모델: Seedream 4.5 **Unlimited**(0cr인지 생성 버튼에서 확인. 크레딧이 표시되면 멈추고 알린다)
- 참조 이미지 1장: `img\fix\P4b_1_fix.png` (안내판 블러와 하늘 통일이 들어간 판. 없으면 `img\P4b_1.png`)
- 비율 9:16, 해상도는 가장 큰 값(1440×2560 또는 2K)
- 2장 생성. 둘 다 마음에 안 들면 프롬프트 B로 2장 더 만든다(최대 4장)

**프롬프트 A**
```
Edit the reference image. Keep the exact same composition, camera angle, lighting, colors and every detail identical, except one area: in the lower left part of the image, beyond the stone fortress wall, there is a body of water with reflections and a straight pier line. Remove the water and the pier completely. Replace that area with a dark forested hillside slope that falls away below the wall, with dense dark tree canopy, and far beyond it the small scattered warm lights of the city (#FFB15C) continuing the existing city lights. No water, no reflections, no lake, no river, no pier, no boats. Do not change the fortress wall, the path, the people, the sky or the signboard. No text, no letters, no logos.
```

**프롬프트 B** (A가 수면을 남기거나 성곽까지 바꿀 때)
```
Same image as the reference, pixel-for-pixel identical everywhere except the bottom-left corner below the fortress wall. In that corner only: a steep dark wooded hillside covered with trees, seen from above at night, with tiny distant city lights between the trees. There is no water anywhere in the image. Everything else unchanged.
```

- 저장 이름: `img\P4b_sd_1.png`, `img\P4b_sd_2.png` … (번호 순서대로)

## 2. 합성 (무료, 로컬)
```
cd 29초영화제\img\fix
python merge_p4b.py            # 후보 전부 합성 + 수치 + 비교 이미지
python merge_p4b.py --pick 2   # 고른 번호를 채택본 P4b_1_sdfix.png로 저장
```
- Seedream 결과를 통째로 쓰지 않는다. 기준 판에 정렬(편집 영역 밖에서 ECC) → 주변 60px 고리로 색 맞춤 → **편집 영역(+24px, 페더 16px)만** 합친다 → 그레인 맞춤. 그래서 영역 밖은 기준 판과 비트 단위로 같다.
- 결과: `img\fix\compare\P4b_sd<n>_crop.png`(기준 | Seedream 정렬 | 합성, 2배), `_full.png`, `_phone.png`(1080 축소본을 폰 너비 405px로), 수치 `P4b_sd_report.txt`

## 3. 합격 기준 (만든 사람이 1차 판정, 독립 검수자가 재판정)
| # | 기준 | 확인 방법 |
|---|---|---|
| 1 | 수면·반사·부두 선이 남지 않는다 | crop 이미지 + 가로 줄무늬 지표 1.3 이하(참고값) |
| 2 | 숲 사면이 기존 숲(x≥430)과 이어지고 타일 반복·검은 덩어리가 없다 | crop 이미지 |
| 3 | 경계가 보이지 않는다 | 경계 단차 6 이하 + phone 이미지 |
| 4 | 시가지 불빛이 기존 불빛과 크기·색이 같다(새로 생긴 불빛이 더 크거나 하얗지 않다) | 밝은 점 수·크기, crop 이미지 |
| 5 | 성곽·길·인물·하늘·안내판이 바뀌지 않았다 | 영역 밖 최대 변화 0(구조상 보장), full 이미지 |
| 6 | 가짜 글자·로고가 새로 생기지 않았다 | 1080·폰 크기 확인 |
| 7 | 정렬이 맞다: ECC 상관 0.95 이상, 배율 1±0.01 | report |

- 색 맞춤 gain이 0.85~1.15를 벗어나면 Seedream이 톤을 크게 바꾼 것이다. 합성 경계에서 색 차이가 보이는지 더 꼼꼼히 본다.
- 채택 후 `plate_edits.json`의 P4-01·P4-02 상태를 `done_seedream`으로 바꾸고, 결과 파일을 `P4b_1_sdfix.png`로 적는다. 이후 독립 검수(`review_plates.py`)는 이 파일을 쓴다.
