# 쇼핑 쇼츠 키트

시트에 상품만 채우면 세로 쇼핑 쇼츠(유튜브용·네이버 클립용), 설명란 텍스트, 미리보기 이미지를 자동으로 만들어 주는 작업 폴더예요.
자세한 운영 원칙과 작업 흐름은 `CLAUDE.md`에 있어요 (Claude Code가 자동으로 읽어요).

## 처음 한 번만
1. 이 폴더를 원하는 곳에 둬요. 예: `C:\Users\one\Desktop\일\2026\쇼핑쇼츠`
2. 패키지 설치: `pip install -r requirements.txt`
3. ffmpeg 확인: `ffmpeg -version` (없으면 `winget install Gyan.FFmpeg` 후 터미널 다시 열기)
4. 샘플 만들기: `python make_short.py --id DEMO` → `output\DEMO` 폴더에 영상 2개, 설명란 txt, 미리보기 png

## Claude Code로 이어서 작업하기
폴더에서 `claude`를 실행하고 이렇게 시작하면 돼요.

> CLAUDE.md 읽고 DEMO 영상 만들어서 미리보기 검수해줘. 그다음 V01부터 상품 채우는 거 같이 하자.

## 파일
- `shopping_shorts.xlsx` 운영 시트 (안내 시트부터 읽어 보세요)
- `make_short.py` 생성 스크립트 / `config.json` 색·폰트·길이·문구 설정
- `templates/` 판매자에게 보낼 메시지 2종
- `assets/fonts/` Pretendard 폰트 (SIL Open Font License, `OFL-Pretendard.txt`)
