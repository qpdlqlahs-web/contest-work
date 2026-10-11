#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
쇼핑 쇼츠 자동 생성기 (3040 선물 큐레이션)

shopping_shorts.xlsx 의 '영상' / '상품' 시트를 읽어서 아래 파일을 만든다.
  output/<영상ID>/<영상ID>_youtube.mp4   유튜브 쇼츠·인스타 릴스·틱톡용 (프로필 링크 안내)
  output/<영상ID>/<영상ID>_clip.mp4      네이버 클립용 (쇼핑커넥트 스티커 안내)
  output/<영상ID>/<영상ID>_<플랫폼>.txt  제목·설명란·링크·업로드 체크리스트
  output/<영상ID>/<영상ID>_preview.png   장면별 미리보기 (UI 가림 영역 표시)

영상 시트 '형식'이 '숫자'면 상품 사진 없이 리뷰 수·평점·가격 비교로 만든다
(사진 허락이 필요 없음. 상품 시트 '리뷰 수'·'평점'은 상품 페이지 표시값 그대로).

사용법
  python make_short.py --check                 시트 전체 검사만 (영상 안 만듦)
  python make_short.py --id DEMO               한 개 제작 (유튜브 + 클립 버전)
  python make_short.py --id V01 --id V02       여러 개 제작
  python make_short.py --ready                 상태가 '제작대기'인 영상 전부 제작
  python make_short.py --id V01 --platform youtube
  옵션: --no-motion  확대 효과 끄기 / --keep-temp  중간 파일 보존
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

try:
    import openpyxl
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
except ImportError:
    print("필요한 패키지가 없어요. 먼저 실행하세요:  pip install -r requirements.txt")
    sys.exit(1)

try:  # Windows 콘솔에서 한글 출력 깨짐 방지
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
W, H = 1080, 1920

# 쇼츠·클립·릴스 UI가 덮는 영역. 중요한 글자와 상품은 이 밖에 둔다 (미리보기에 빨갛게 표시).
UI_ZONES = [
    (0, 0, W, 150),        # 상단: 검색·카메라 아이콘
    (0, 1500, W, H),       # 하단: 제목·채널명·설명
    (950, 850, W, 1500),   # 오른쪽: 좋아요·댓글·공유 버튼
]

STATUS_READY = "제작대기"
ACTIVE_STATUSES = {"상품선정", "허락대기", STATUS_READY, "제작완료"}
PLATFORMS = ("youtube", "clip")
PLATFORM_LABEL = {"youtube": "유튜브 쇼츠·릴스·틱톡용", "clip": "네이버 클립용"}
AFF_TYPES = ("쇼핑커넥트", "쿠팡파트너스")
FMT_DATA = "숫자"  # 영상 시트 '형식': 비우면 사진형, '숫자'면 사진 없는 리뷰·평점 비교형
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")

TEACHER = "교사 대상 선물은 청탁금지법 문제가 있어요. 주제에서 빼는 걸 권해요."
HEALTH = "건강 효능처럼 읽히는 표현은 건강기능식품·의약품 광고 규정에 걸릴 수 있어요."
ALCOHOL = "주류는 온라인 판매·광고 제한이 있어서 피하는 게 안전해요."
RISK_WORDS = {
    "선생님": TEACHER, "담임": TEACHER, "교사": TEACHER, "어린이집 선생": TEACHER,
    "면역": HEALTH, "효능": HEALTH, "치료": HEALTH, "예방": HEALTH, "다이어트": HEALTH,
    "혈압": HEALTH, "혈당": HEALTH, "관절": HEALTH,
    "와인": ALCOHOL, "위스키": ALCOHOL, "소주": ALCOHOL, "맥주": ALCOHOL,
    "샴페인": ALCOHOL, "막걸리": ALCOHOL, "전통주": ALCOHOL,
}
FAKE_REVIEW_PATTERNS = ("써보니", "써봤는데", "직접 써", "받고 울", "진짜 좋아했")


# ----------------------------------------------------------------------------- 데이터

@dataclass
class Product:
    order: int
    name: str
    price: int | None
    reason: str
    image: str
    aff_type: str
    link: str
    seller: str
    permission: str
    row: int
    image_path: Path | None = None
    reviews: int | None = None
    rating: float | None = None


@dataclass
class Video:
    vid: str
    status: str
    upload_date: object
    occasion: str
    target: str
    budget: str
    title: str
    hook: str
    link_no: str
    price_date: object
    hashtags: str
    row: int
    products: list = field(default_factory=list)
    fmt: str = ""

    @property
    def is_data(self) -> bool:
        return self.fmt == FMT_DATA


def s(v) -> str:
    """셀 값을 깔끔한 문자열로."""
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def parse_price(v) -> int | None:
    if v is None or s(v) == "":
        return None
    if isinstance(v, (int, float)):
        return int(round(v))
    digits = re.sub(r"[^0-9]", "", str(v))
    return int(digits) if digits else None


def parse_rating(v) -> float | None:
    try:
        return float(re.sub(r"[^0-9.]", "", s(v)))
    except ValueError:
        return None


def fmt_count(n: int) -> str:
    """12384 -> '1.2만', 8210 -> '8,210'"""
    if n >= 10000:
        return f"{n / 10000:.1f}".rstrip("0").rstrip(".") + "만"
    return f"{n:,}"


def fmt_md(d) -> str:
    if isinstance(d, (dt.datetime, dt.date)):
        return f"{d.month}/{d.day}"
    text = s(d)
    m = re.match(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", text)
    if m:
        return f"{int(m.group(2))}/{int(m.group(3))}"
    return text or f"{dt.date.today().month}/{dt.date.today().day}"


def load_config() -> dict:
    with open(ROOT / "config.json", encoding="utf-8") as f:
        return json.load(f)


def read_table(ws) -> list[dict]:
    """'영상ID' 또는 첫 머리글 행을 찾아 dict 목록으로 읽는다."""
    rows = list(ws.iter_rows(values_only=True))
    for i, r in enumerate(rows):
        header = [s(c) for c in (r or [])]
        if "영상ID" in header or "판매자명" in header:
            out = []
            for j, rr in enumerate(rows[i + 1:], start=i + 2):
                if rr is None or all(s(c) == "" for c in rr):
                    continue
                rec = {header[k]: rr[k] for k in range(min(len(header), len(rr))) if header[k]}
                rec["_row"] = j
                out.append(rec)
            return out
    raise ValueError(f"'{ws.title}' 시트에서 머리글 행을 찾지 못했어요.")


def find_image(name: str) -> Path | None:
    if not name:
        return None
    base = ROOT / "assets" / "products"
    p = base / name
    if p.suffix and p.exists():
        return p
    for ext in IMAGE_EXTS:
        q = base / f"{name}{ext}"
        if q.exists():
            return q
    return p if p.exists() else None


def load_sheet(path: Path) -> dict[str, Video]:
    try:
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    except PermissionError:
        print(f"[오류] {path.name} 파일을 열 수 없어요. 엑셀에서 열려 있으면 닫고 다시 실행하세요.")
        sys.exit(1)
    try:
        vids = read_table(wb["영상"])
        prods = read_table(wb["상품"])
    finally:
        wb.close()

    videos: dict[str, Video] = {}
    for r in vids:
        vid = s(r.get("영상ID"))
        if not vid:
            continue
        videos[vid] = Video(
            vid=vid, status=s(r.get("상태")), upload_date=r.get("업로드 예정일"),
            occasion=s(r.get("상황")), target=s(r.get("대상")), budget=s(r.get("예산")),
            title=s(r.get("제목")), hook=s(r.get("훅 문구")), link_no=s(r.get("링크 번호")),
            price_date=r.get("가격 확인일"), hashtags=s(r.get("해시태그")), row=r["_row"],
            fmt=s(r.get("형식")),
        )
    for r in prods:
        vid = s(r.get("영상ID"))
        if not vid:
            continue
        order_text = s(r.get("순서"))
        p = Product(
            order=int(order_text) if order_text.isdigit() else 99,
            name=s(r.get("상품명")), price=parse_price(r.get("가격")),
            reason=s(r.get("고른 이유")), image=s(r.get("이미지 파일")),
            aff_type=s(r.get("제휴 종류")), link=s(r.get("제휴 링크")),
            seller=s(r.get("판매처")), permission=s(r.get("사진 허락")).upper(),
            row=r["_row"], reviews=parse_price(r.get("리뷰 수")), rating=parse_rating(r.get("평점")),
        )
        p.image_path = find_image(p.image)
        if vid in videos:
            videos[vid].products.append(p)
        else:
            videos.setdefault("_orphans", Video("_orphans", "", None, "", "", "", "", "", "", None, "", 0)).products.append(p)
    for v in videos.values():
        v.products.sort(key=lambda p: p.order)
    return videos


# ----------------------------------------------------------------------------- 검사

def validate(v: Video, cfg: dict, platforms: tuple[str, ...]) -> tuple[list[str], list[str], tuple[str, ...]]:
    """(오류, 경고, 실제로 만들 플랫폼). 오류가 있으면 제작하지 않는다."""
    errors, warns = [], []
    n = len(v.products)
    if n == 0:
        errors.append("'상품' 시트에 이 영상의 상품이 없어요.")
    elif not 2 <= n <= 4:
        errors.append(f"상품은 2~4개여야 해요 (지금 {n}개). 3개를 권장해요.")
    if not v.title:
        errors.append("제목이 비어 있어요.")
    if not v.hook:
        warns.append("훅 문구가 비어 있어서 제목을 첫 화면에 써요.")
    elif len(v.hook) > 28:
        warns.append(f"훅 문구가 {len(v.hook)}자예요. 첫 화면은 20자 안팎이 잘 읽혀요.")
    if v.fmt and not v.is_data:
        errors.append(f"'형식'은 비우거나(사진형) '{FMT_DATA}'만 쓸 수 있어요 (지금 '{v.fmt}').")
    if v.is_data and not s(v.price_date):
        warns.append("숫자형은 '가격 확인일'에 리뷰 수·평점을 확인한 날짜를 꼭 적어요 (영상에 기준일로 나가요).")
    if v.title and not re.search(r"\d", v.title):
        warns.append("제목에 예산(숫자)이 없어요. '3만 원대'처럼 넣으면 클릭이 잘 나와요.")

    for p in v.products:
        tag = f"상품 {p.order}({p.name or '이름 없음'}, 상품 시트 {p.row}행)"
        if not p.name:
            errors.append(f"{tag}: 상품명이 비어 있어요.")
        elif len(p.name) > 22:
            warns.append(f"{tag}: 상품명이 길어요. 영상에는 짧은 이름(22자 이내)이 좋아요.")
        if p.price is None:
            errors.append(f"{tag}: 가격이 비어 있어요.")
        if not p.reason:
            errors.append(f"{tag}: '고른 이유'가 비어 있어요. 이 한 줄은 직접 써야 해요.")
        elif len(p.reason) > 32:
            warns.append(f"{tag}: 고른 이유가 {len(p.reason)}자예요. 32자 이내가 잘 읽혀요.")
        if v.is_data:
            if not p.reviews:
                errors.append(f"{tag}: 숫자형은 '리뷰 수'가 필요해요 (상품 페이지 표시값 그대로).")
            if p.rating is None or not 0 < p.rating <= 5:
                errors.append(f"{tag}: 숫자형은 '평점'이 필요해요 (0~5, 예: 4.8).")
        else:
            if p.permission != "O":
                errors.append(f"{tag}: 사진 허락이 'O'가 아니에요. 허락받은 사진만 쓸 수 있어요.")
            if not p.image:
                errors.append(f"{tag}: 이미지 파일 이름이 비어 있어요.")
            elif p.image_path is None:
                errors.append(f"{tag}: assets/products/{p.image} 파일을 찾을 수 없어요.")
        if p.aff_type not in AFF_TYPES:
            errors.append(f"{tag}: 제휴 종류는 {' 또는 '.join(AFF_TYPES)} 중 하나여야 해요.")
        if not p.link.startswith("http"):
            errors.append(f"{tag}: 제휴 링크가 비어 있거나 http로 시작하지 않아요.")
        for text in (p.name, p.reason):
            for pat in FAKE_REVIEW_PATTERNS:
                if pat in text:
                    warns.append(f"{tag}: '{pat}' 같은 체험 표현은 실제로 써본 게 아니면 빼야 해요 (표시광고법).")

    joined = " ".join([v.title, v.hook, v.occasion, v.target] + [p.name + " " + p.reason for p in v.products])
    seen = set()
    for word, msg in RISK_WORDS.items():
        if word in joined and msg not in seen:
            warns.append(f"'{word}' 포함: {msg}")
            seen.add(msg)

    build = list(platforms)
    if "youtube" in build and not v.link_no:
        errors.append("'링크 번호'가 비어 있어요. 유튜브 버전 마지막 화면에 들어가요.")
    if "clip" in build and v.products and any(p.aff_type != "쇼핑커넥트" for p in v.products):
        warns.append("쿠팡파트너스 상품이 섞여 있어서 클립 버전은 건너뛰어요 (클립 스티커는 쇼핑커넥트 상품만 연결돼요).")
        build.remove("clip")
    return errors, warns, tuple(build)


def check_all(videos: dict[str, Video], cfg: dict) -> int:
    print("시트 검사 결과")
    print("-" * 50)
    planned = 0
    problems = 0
    link_owner: dict[str, str] = {}
    for vid, v in videos.items():
        if vid == "_orphans":
            for p in v.products:
                print(f"[경고] 상품 시트 {p.row}행: '영상' 시트에 없는 영상ID예요.")
            continue
        if v.status not in ACTIVE_STATUSES and not v.products:
            planned += 1
            continue
        if v.link_no:
            if v.link_no in link_owner:
                print(f"[경고] {vid}: 링크 번호 {v.link_no}번이 {link_owner[v.link_no]}와 겹쳐요.")
            link_owner[v.link_no] = vid
        errors, warns, _ = validate(v, cfg, PLATFORMS)
        mark = "OK" if not errors else "수정 필요"
        print(f"{vid} [{v.status or '상태 없음'}] {v.title}  ->  {mark}")
        for e in errors:
            print(f"   오류: {e}")
        for w_ in warns:
            print(f"   참고: {w_}")
        problems += bool(errors)
    print("-" * 50)
    print(f"상품을 아직 안 채운 기획 단계 영상: {planned}개 (검사 생략)")
    return 1 if problems else 0


# ----------------------------------------------------------------------------- 그리기

class Fonts:
    def __init__(self, cfg: dict):
        self.paths = {k: self._find(k, v) for k, v in cfg["fonts"].items()}
        self._cache: dict = {}

    @staticmethod
    def _find(kind: str, candidates: list[str]) -> str:
        for c in candidates:
            p = Path(c)
            if not p.is_absolute():
                p = ROOT / p
            if p.exists():
                return str(p)
        raise FileNotFoundError(f"'{kind}' 폰트를 찾지 못했어요. config.json의 fonts 경로를 확인하세요.")

    def get(self, kind: str, size: int):
        key = (kind, size)
        if key not in self._cache:
            self._cache[key] = ImageFont.truetype(self.paths[kind], size)
        return self._cache[key]


def wrap(draw, text: str, font, max_w: int) -> list[str]:
    lines: list[str] = []
    for para in str(text).split("\n"):
        cur = ""
        for word in para.split(" "):
            if not word:
                continue
            trial = f"{cur} {word}" if cur else word
            if draw.textlength(trial, font=font) <= max_w:
                cur = trial
                continue
            if cur:
                lines.append(cur)
            if draw.textlength(word, font=font) <= max_w:
                cur = word
            else:  # 띄어쓰기 없는 긴 단어는 글자 단위로 자른다
                piece = ""
                for ch in word:
                    if draw.textlength(piece + ch, font=font) <= max_w:
                        piece += ch
                    else:
                        lines.append(piece)
                        piece = ch
                cur = piece
        if cur:
            lines.append(cur)
    return lines or [""]


def balance(draw, text: str, font, max_w: int, lines: list[str]) -> list[str]:
    """줄 수는 그대로 두고 줄 길이를 고르게 (한 단어만 덩그러니 남는 줄 방지)."""
    if len(lines) < 2:
        return lines
    lo, hi, best = int(max_w * 0.45), max_w, lines
    while lo <= hi:
        mid = (lo + hi) // 2
        trial = wrap(draw, text, font, mid)
        if len(trial) <= len(lines):
            best, hi = trial, mid - 1
        else:
            lo = mid + 1
    return best


def fit(draw, fonts: Fonts, kind: str, text: str, max_w: int, max_lines: int,
        size_max: int, size_min: int, notes: list[str] | None = None, label: str = ""):
    size = size_max
    while True:
        font = fonts.get(kind, size)
        lines = wrap(draw, text, font, max_w)
        if len(lines) <= max_lines:
            # 글자를 조금(최대 14%) 줄여서 한 줄을 아낄 수 있으면 그쪽이 더 빨리 읽힌다
            floor = max(size_min, int(size * 0.86))
            smaller = size - 4
            while len(lines) > 1 and smaller >= floor:
                f2 = fonts.get(kind, smaller)
                l2 = wrap(draw, text, f2, max_w)
                if len(l2) < len(lines):
                    font, lines = f2, l2
                    break
                smaller -= 4
            return font, balance(draw, text, font, max_w, lines)
        if size - 4 < size_min:
            if notes is not None:
                notes.append(f"{label} 글자가 길어서 {max_lines}줄로 잘랐어요: '{text}'")
            kept = lines[:max_lines]
            last = kept[-1]
            while last and draw.textlength(last + "…", font=font) > max_w:
                last = last[:-1]
            kept[-1] = last + "…"
            return font, kept
        size -= 4


def draw_lines(draw, lines, font, x, top, fill, anchor="ma", spacing=1.24) -> int:
    lh = int(font.size * spacing)
    y = top
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill, anchor=anchor)
        y += lh
    return y


def chip(draw, text: str, font, cx: int, top: int, bg: str, fg: str, pad_x=34, pad_y=16) -> int:
    tw = draw.textlength(text, font=font)
    h = font.size + pad_y * 2
    w = int(tw) + pad_x * 2
    x0 = int(cx - w / 2)
    draw.rounded_rectangle([x0, top, x0 + w, top + h], radius=h // 2, fill=bg)
    draw.text((cx, top + h / 2), text, font=font, fill=fg, anchor="mm")
    return top + h


def load_rgba(path: Path) -> Image.Image:
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGBA")


def product_card(path: Path, size: int, radius=36, pad=36, shadow=True) -> tuple[Image.Image, int]:
    """흰 둥근 카드 위에 상품 사진을 잘리지 않게 넣는다. (이미지, 그림자 여백)"""
    m = 44 if shadow else 0
    canvas = Image.new("RGBA", (size + 2 * m, size + 2 * m), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([m, m + 14, m + size, m + size + 14], radius=radius, fill=(0, 0, 0, 60))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=(255, 255, 255, 255))
    photo = ImageOps.contain(load_rgba(path), (size - 2 * pad, size - 2 * pad), Image.LANCZOS)
    card.alpha_composite(photo, ((size - photo.width) // 2, (size - photo.height) // 2))
    canvas.alpha_composite(card, (m, m))
    return canvas, m


def ease(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def prog(t: float, start: float, dur: float) -> float:
    """t초 시점에 start초부터 dur초 동안 진행되는 움직임의 진행률 (0~1, 감속)."""
    return ease((t - start) / dur)


def fade(layer: Image.Image, k: float) -> Image.Image:
    if k < 1:
        layer.putalpha(layer.getchannel("A").point(lambda a_: int(a_ * k)))
    return layer


@lru_cache(maxsize=8)
def card_shadow(size: int, radius: int, m: int) -> Image.Image:
    canvas = Image.new("RGBA", (size + 2 * m, size + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([m, m + 14, m + size, m + size + 14], radius=radius, fill=(0, 0, 0, 60))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    return canvas


def star(draw, cx: float, cy: float, r: float, fill: str) -> None:
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill)


def review_rank(v: Video, p: Product) -> int:
    return 1 + sum(1 for q in v.products if (q.reviews or 0) > (p.reviews or 0))


def data_card(v: Video, p: Product, size: int, fonts: Fonts, cfg: dict, radius=36,
              t: float | None = None) -> tuple[Image.Image, int]:
    """사진 대신 쓰는 리뷰 수·평점 카드. 680px로 그린 뒤 size로 줄인다. (이미지, 그림자 여백)"""
    c = cfg["colors"]
    line_c = c.get("line", "#E8E2D8")
    B, pad = 680, 60
    card = Image.new("RGBA", (B, B), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, B - 1, B - 1], radius=radius, fill=(255, 255, 255, 255))

    d.text((B // 2, 58), "리뷰", font=fonts.get("bold", 40), fill=c["muted"], anchor="ma")
    font, _ = fit(d, fonts, "heavy", f"{p.reviews:,}개", B - 2 * pad, 1, 112, 64)
    k = 1.0 if t is None else prog(t, 0.3, 1.0)
    draw_lines(d, [f"{round(p.reviews * k):,}개"], font, B // 2, 116, c["ink"])
    d.line([(pad, 286), (B - pad, 286)], fill=line_c, width=3)

    d.text((B // 2, 314), "평점", font=fonts.get("bold", 40), fill=c["muted"], anchor="ma")
    num_f, tail_f = fonts.get("heavy", 104), fonts.get("bold", 46)
    num, tail = f"{p.rating:.1f}", " / 5"
    sr, gap = 44, 22
    total = 2 * sr + gap + d.textlength(num, font=num_f) + d.textlength(tail, font=tail_f)
    x = (B - total) / 2
    base = 470
    star(d, x + sr, base - 38, sr, c.get("star", "#F2A900"))
    x += 2 * sr + gap
    kr = 1.0 if t is None else prog(t, 0.5, 1.0)
    d.text((x, base), f"{p.rating * kr:.1f}", font=num_f, fill=c["ink"], anchor="ls")
    d.text((x + d.textlength(num, font=num_f), base), tail, font=tail_f, fill=c["muted"], anchor="ls")

    rank = review_rank(v, p)
    top = max(q.reviews or 0 for q in v.products) or 1
    d.text((B // 2, 528), f"{len(v.products)}개 중 리뷰 수 {rank}위", font=fonts.get("bold", 36),
           fill=c["ink"], anchor="ma")
    d.rounded_rectangle([pad, 596, B - pad, 622], radius=13, fill=line_c)
    kb = 1.0 if t is None else prog(t, 1.0, 0.6)
    fill_w = max(26, int((B - 2 * pad) * (p.reviews or 0) / top * kb))
    if kb > 0:
        d.rounded_rectangle([pad, 596, pad + fill_w, 622], radius=13, fill=c["accent"] if rank == 1 else c["muted"])

    if size != B:
        card = card.resize((size, size), Image.LANCZOS)
    m = 44
    canvas = card_shadow(size, radius, m).copy()
    canvas.alpha_composite(card, (m, m))
    return canvas, m


def hook_bars_h(n: int) -> int:
    return 120 + n * 64 + (n - 1) * 26 + 44


def hook_bars(im: Image.Image, v: Video, fonts: Fonts, cfg: dict, top: int, t: float | None = None) -> None:
    """숫자형 첫 화면: 상품 이름 없이 리뷰 수 막대만 보여 줘서 궁금하게 만든다."""
    c = cfg["colors"]
    d = ImageDraw.Draw(im)
    n = len(v.products)
    x0, x1 = 130, 950
    d.rounded_rectangle([x0, top, x1, top + hook_bars_h(n)], radius=32, fill=c.get("dark_panel", "#2A3756"))
    d.text((W // 2, top + 40), "리뷰 수 비교", font=fonts.get("bold", 38), fill=c["dark_muted"], anchor="ma")
    best = max(q.reviews or 0 for q in v.products) or 1
    y = top + 120
    for i, p in enumerate(v.products, 1):
        cy = y + 32
        d.ellipse([x0 + 40, cy - 28, x0 + 96, cy + 28], fill=c["highlight"])
        d.text((x0 + 68, cy), str(i), font=fonts.get("heavy", 34), fill=c["chip_ink"], anchor="mm")
        bx0, bx1 = x0 + 124, x1 - 50
        d.rounded_rectangle([bx0, cy - 18, bx1, cy + 18], radius=18, fill=c["dark_bg"])
        grow = 1.0 if t is None else prog(t, 0.4 + (i - 1) * 0.15, 0.6)
        w_ = max(36, int((bx1 - bx0) * (p.reviews or 0) / best * grow))
        is_top = (p.reviews or 0) == best
        if grow > 0:
            d.rounded_rectangle([bx0, cy - 18, bx0 + w_, cy + 18], radius=18,
                                fill=c["highlight"] if is_top else c["dark_muted"])
        y += 64 + 26


def render_hook(v: Video, fonts: Fonts, cfg: dict, notes: list[str], t: float | None = None) -> Image.Image:
    """t(초)가 있으면 그 시점의 움직임 프레임(숫자형), 없으면 마지막 모습."""
    c = cfg["colors"]
    im = Image.new("RGB", (W, H), c["dark_bg"])
    text_k = 1.0 if t is None else prog(t, 0, 0.35)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    chip_text = " · ".join(x for x in (v.occasion, v.budget) if x) or "선물 추천"
    chip_font = fonts.get("bold", 42)
    font, lines = fit(d, fonts, "heavy", v.hook or v.title, 840, 3, 112, 72, notes, "훅 문구")
    lh = int(font.size * 1.24)

    n = len(v.products)
    gap = 24
    size = min(320 if n == 2 else 254, (820 - (n - 1) * gap) // n)  # 오른쪽 버튼 영역(x>950)을 피하는 폭
    if v.is_data:
        size = hook_bars_h(n)
    chip_h = chip_font.size + 32
    block_h = chip_h + 56 + len(lines) * lh + 70 + size
    top = max(190, (150 + 1370) // 2 - block_h // 2)  # 화면 안전 영역 가운데 정렬

    shift = int(40 * (1 - text_k))
    y = chip(d, chip_text, chip_font, W // 2, top + shift, c["highlight"], c["chip_ink"])
    y = draw_lines(d, lines, font, W // 2, y + 56, c["dark_ink"]) - shift
    row_w = n * size + (n - 1) * gap
    x = (W - row_w) // 2
    ty = y + 70
    if v.is_data:
        hook_bars(im, v, fonts, cfg, ty, t)
    for p in ([] if v.is_data else v.products):
        card, _ = product_card(p.image_path, size, radius=28, pad=20, shadow=False)
        im.paste(card, (x, ty), card)
        x += size + gap
    im.paste(fade(layer, text_k), (0, 0), layer)
    ImageDraw.Draw(im).text((W // 2, 1400), cfg["disclosure_on_video"], font=fonts.get("regular", 32),
                            fill=c["dark_muted"], anchor="ma")  # 광고 표시는 첫 프레임부터
    return im


def render_product(v: Video, p: Product, idx: int, fonts: Fonts, cfg: dict, price_date: str,
                   notes: list[str], t: float | None = None) -> tuple[Image.Image, Image.Image, tuple[int, int]]:
    """(배경, 상품 카드, 카드 중심). 카드만 천천히 커지는 효과를 위해 따로 만든다."""
    c = cfg["colors"]
    bg = Image.new("RGB", (W, H), c["bg"])
    d = ImageDraw.Draw(bg)
    label = f"리뷰 수 {review_rank(v, p)}위" if v.is_data else f"{idx} / {len(v.products)}"
    y = chip(d, label, fonts.get("bold", 38), W // 2, 190, c["dark_bg"], c["dark_ink"])
    font, lines = fit(d, fonts, "heavy", p.name, 860, 2, 78, 56, notes, f"상품 {idx} 이름")
    y = draw_lines(d, lines, font, W // 2, y + 36, c["ink"])
    font, lines = fit(d, fonts, "bold", p.reason, 860, 2, 50, 38, notes, f"상품 {idx} 고른 이유")
    y = draw_lines(d, lines, font, W // 2, y + 6, c["muted"])

    card_top = max(y + 36, 560)
    size = min(680, 1262 - card_top)
    if v.is_data:
        card, _ = data_card(v, p, size, fonts, cfg, t=t)
        basis = f"{price_date} 상품 페이지 기준 (가격·리뷰·평점)"
    else:
        card, _ = product_card(p.image_path, size)
        basis = f"{price_date} 기준 가격"
    center = (W // 2, card_top + size // 2)

    kp = 1.0 if t is None else prog(t, 1.4, 0.35)
    if kp > 0:
        pl = Image.new("RGBA", (W, 140), (0, 0, 0, 0))
        ImageDraw.Draw(pl).text((W // 2, 0), f"{p.price:,}원", font=fonts.get("heavy", 100), fill=c["accent"], anchor="ma")
        bg.paste(fade(pl, kp), (0, 1296 + int(30 * (1 - kp))), pl)
    d.text((W // 2, 1420), basis, font=fonts.get("regular", 30), fill=c["muted"], anchor="ma")
    return bg, card, center


def data_product_frame(v: Video, p: Product, idx: int, fonts: Fonts, cfg: dict, price_date: str,
                       t: float) -> Image.Image:
    """숫자형 상품 장면의 t초 프레임: 카드가 아래에서 올라오며 나타난다."""
    bg, card, center = render_product(v, p, idx, fonts, cfg, price_date, [], t)
    k = prog(t, 0, 0.4)
    return compose(bg, fade(card, k), (center[0], center[1] + int(80 * (1 - k))))


def compose(bg: Image.Image, card: Image.Image, center: tuple[int, int]) -> Image.Image:
    frame = bg.convert("RGBA")
    frame.alpha_composite(card, (center[0] - card.width // 2, center[1] - card.height // 2))
    return frame.convert("RGB")


def render_outro(v: Video, platform: str, fonts: Fonts, cfg: dict, notes: list[str],
                 t: float | None = None) -> Image.Image:
    c = cfg["colors"]
    im = Image.new("RGB", (W, H), c["dark_bg"])
    d = ImageDraw.Draw(im)
    y = chip(d, "오늘의 선물 정리", fonts.get("bold", 40), W // 2, 200, c["highlight"], c["chip_ink"]) + 50

    n = len(v.products)
    gap = 24
    row_h = min(190, (660 - (n - 1) * gap) // n)
    x0 = 110
    for i, p in enumerate(v.products, 1):
        row = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(row)
        if v.is_data:
            r = 40
            d.ellipse([x0, y + 20, x0 + 2 * r, y + 20 + 2 * r], fill=c["highlight"])
            d.text((x0 + r, y + 20 + r), str(i), font=fonts.get("heavy", 44), fill=c["chip_ink"], anchor="mm")
            tx = x0 + 2 * r + 36
        else:
            card, _ = product_card(p.image_path, row_h, radius=24, pad=14, shadow=False)
            row.paste(card, (x0, y), card)
            tx = x0 + row_h + 36
        name_font, name_lines = fit(d, fonts, "bold", p.name, 940 - tx, 2, 44, 34)
        ny = draw_lines(d, name_lines, name_font, tx, y + 8, c["dark_muted"], anchor="la", spacing=1.18)
        price, price_f = f"{p.price:,}원", fonts.get("heavy", 48)
        d.text((tx, ny + 6), price, font=price_f, fill=c["dark_ink"], anchor="la")
        if v.is_data:
            d.text((tx + d.textlength(price, font=price_f) + 24, ny + 6 + 48),
                   f"리뷰 {fmt_count(p.reviews)} · 평점 {p.rating:.1f}",
                   font=fonts.get("bold", 36), fill=c["highlight"], anchor="ls")
        k = 1.0 if t is None else prog(t, 0.1 + (i - 1) * 0.12, 0.45)
        if k > 0:
            im.paste(fade(row, k), (int(120 * (1 - k)), 0), row)
        y += row_h + gap

    d = ImageDraw.Draw(im)
    cta = cfg["cta"][platform].format(link_no=v.link_no or "?", n=n)
    font, lines = fit(d, fonts, "heavy", cta, 820, 3, 76, 54, notes, "마지막 안내 문구")
    kc = 1.0 if t is None else prog(t, 0.55, 0.4)
    if kc > 0:
        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_lines(ImageDraw.Draw(cl), lines, font, W // 2, max(y + 60, 1010), c["highlight"])
        im.paste(fade(cl, kc), (0, 0), cl)
    d.text((W // 2, 1400), cfg["disclosure_on_video"], font=fonts.get("regular", 32),
           fill=c["dark_muted"], anchor="ma")
    return im


def make_preview(frames: list[tuple[str, Image.Image]], fonts: Fonts, out: Path) -> None:
    tw, th, gap, label_h = 270, 480, 20, 44
    sheet = Image.new("RGB", (len(frames) * (tw + gap) + gap, th + label_h + gap * 2), "#FFFFFF")
    d = ImageDraw.Draw(sheet)
    font = fonts.get("bold", 22)
    for i, (label, frame) in enumerate(frames):
        f = frame.convert("RGBA")
        overlay = Image.new("RGBA", f.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        for zone in UI_ZONES:
            od.rectangle(zone, fill=(230, 40, 40, 70))
        f = Image.alpha_composite(f, overlay).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = gap + i * (tw + gap)
        sheet.paste(f, (x, gap))
        d.text((x + tw // 2, gap + th + 10), label, font=font, fill="#333333", anchor="ma")
    sheet.save(out)


# ----------------------------------------------------------------------------- ffmpeg

def find_ffmpeg(cfg: dict) -> str:
    ff = shutil.which(cfg.get("ffmpeg", "ffmpeg")) or shutil.which("ffmpeg")
    if not ff:
        print("[오류] ffmpeg를 찾을 수 없어요. 설치 후 PATH에 등록하거나 config.json의 ffmpeg에 전체 경로를 적으세요.")
        print("       Windows 설치 예:  winget install Gyan.FFmpeg")
        sys.exit(1)
    return ff


def run(cmd: list[str], cwd: Path) -> None:
    r = subprocess.run(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace")[-1500:])


def enc(fps: int) -> list[str]:
    return ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps)]


def seg_static(ff: str, png: str, dur: float, out: str, fps: int, cwd: Path) -> None:
    run([ff, "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(fps), "-t", f"{dur}",
         "-i", png, *enc(fps), "-an", out], cwd)


def render_anim(ff: str, out: str, dur: float, fps: int, frame_at, cwd: Path) -> None:
    """frame_at(t초) -> 1080x1920 RGB 이미지를 프레임마다 그려 ffmpeg로 바로 인코딩."""
    proc = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", *enc(fps), "-an", out],
                            cwd=str(cwd), stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for k in range(round(dur * fps)):
            proc.stdin.write(frame_at(k / fps).convert("RGB").tobytes())
    finally:
        proc.stdin.close()
    err = proc.stderr.read()
    if proc.wait() != 0:
        raise RuntimeError(err.decode("utf-8", "replace")[-1500:])


def seg_motion(ff: str, bg: str, card: str, center: tuple[int, int], dur: float, zoom: float,
               out: str, fps: int, cwd: Path) -> None:
    cx, cy = center
    filt = (f"[1:v]scale=w='trunc(iw*(1+{zoom}*t/{dur})/2)*2':h=-2:eval=frame[c];"
            f"[0:v][c]overlay=x='{cx}-w/2':y='{cy}-h/2':eval=frame:shortest=1,format=yuv420p[v]")
    run([ff, "-y", "-loglevel", "error",
         "-loop", "1", "-framerate", str(fps), "-t", f"{dur}", "-i", bg,
         "-loop", "1", "-framerate", str(fps), "-t", f"{dur}", "-i", card,
         "-filter_complex", filt, "-map", "[v]", *enc(fps), "-an", out], cwd)


# ----------------------------------------------------------------------------- 설명란

def hashtags(v: Video, cfg: dict) -> str:
    if v.hashtags:
        return v.hashtags
    tags = list(cfg.get("default_hashtags", []))
    if v.occasion:
        tags.insert(0, "#" + re.sub(r"[\s·,/]", "", v.occasion) + "선물")
    return " ".join(dict.fromkeys(tags))


def write_upload_text(v: Video, platform: str, cfg: dict, price_date: str, out: Path) -> None:
    types = [t for t in AFF_TYPES if any(p.aff_type == t for p in v.products)]
    L = ["[제목]", v.title, "", "[설명란에 붙여넣기]"]
    L += [cfg["disclosure_text"][t] for t in types]
    if v.is_data:
        L += [f"※ 가격·리뷰 수·평점은 {price_date} 상품 페이지 기준이며 변동될 수 있어요.", "", "오늘 비교한 선물"]
        L += [f"{i}. {p.name} | {p.price:,}원 | 리뷰 {p.reviews:,}개 · 평점 {p.rating:.1f}"
              for i, p in enumerate(v.products, 1)]
    else:
        L += [f"※ 가격은 {price_date} 기준이며 변동될 수 있어요.", "", "오늘 소개한 선물"]
        L += [f"{i}. {p.name} | {p.price:,}원" for i, p in enumerate(v.products, 1)]
    L.append("")
    if platform == "youtube":
        L.append(f"▶ 상품 링크는 프로필 링크 {v.link_no}번에 있어요")
    else:
        L.append("▶ 화면의 상품 스티커를 누르면 바로 볼 수 있어요")
    L += ["", hashtags(v, cfg), "", "=" * 40]
    if platform == "youtube":
        L.append(f"[프로필 링크 페이지 {v.link_no}번에 등록할 링크]")
    else:
        L.append("[쇼핑커넥트 스티커로 연결할 상품]")
    L += [f"{i}. {p.name}: {p.link}" for i, p in enumerate(v.products, 1)]
    L += ["", "[업로드 전 체크]",
          "- 첫 화면과 마지막 화면의 광고 표시가 잘 보이는지",
          "- 가격이 지금도 같은지 (바뀌었으면 시트 수정 후 다시 제작)"]
    if v.is_data:
        L += ["- 리뷰 수·평점이 상품 페이지 표시값과 같은지 (리뷰 문장은 인용하지 않기)"]
    if platform == "youtube":
        L += ["- 설명란 첫 줄 대가성 문구를 고정 댓글로도 달고 맨 위에 고정 (쇼츠 필수)",
              "- 유튜브 업로드 시 '유료 프로모션 포함' 체크",
              f"- 프로필 링크 {v.link_no}번에 위 링크를 먼저 등록",
              "- 릴스·틱톡에 올릴 때도 이 파일을 그대로 사용"]
    else:
        L += ["- 클립 업로드 시 상품마다 쇼핑커넥트 스티커(태그) 연결 → 본문 맨 앞 [광고] 자동 표시 확인 (없으면 직접 입력)",
              "- 설명란 첫 줄 대가성 문구를 첫 번째 댓글로 달고 고정 (문구 그대로)"]
    out.write_text("\n".join(L) + "\n", encoding="utf-8-sig")


# ----------------------------------------------------------------------------- 제작

def build(v: Video, platforms: tuple[str, ...], cfg: dict, fonts: Fonts, ff: str,
          motion: bool, keep_temp: bool) -> bool:
    print(f"\n=== {v.vid} | {v.title}")
    errors, warns, platforms = validate(v, cfg, platforms)
    for w_ in warns:
        print(f"   참고: {w_}")
    if errors:
        for e in errors:
            print(f"   오류: {e}")
        print("   -> 오류를 고친 뒤 다시 실행하세요. (python make_short.py --check)")
        return False
    if not platforms:
        print("   -> 만들 플랫폼 버전이 없어요.")
        return False
    if v.is_data:  # 숫자형은 리뷰 수 순위대로 (1위가 1번)
        v.products.sort(key=lambda p: -(p.reviews or 0))

    fps = int(cfg["fps"])
    dur = cfg["durations"]
    price_date = fmt_md(v.price_date) if s(v.price_date) else fmt_md(dt.date.today())
    out_dir = ROOT / "output" / v.vid
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="shopshorts_"))
    notes: list[str] = []
    try:
        hook = render_hook(v, fonts, cfg, notes)
        hook.save(tmp / "hook.png")
        if v.is_data:
            render_anim(ff, "seg_00.mp4", dur["hook"], fps, lambda t: render_hook(v, fonts, cfg, [], t), tmp)
        else:
            seg_static(ff, "hook.png", dur["hook"], "seg_00.mp4", fps, tmp)
        segments = ["seg_00.mp4"]
        preview = [("훅", hook)]

        order = list(enumerate(v.products, 1))
        if v.is_data:  # 3위 -> 1위 순서로 공개
            order.reverse()
        for i, p in order:
            bg, card, center = render_product(v, p, i, fonts, cfg, price_date, notes)
            static = compose(bg, card, center)
            preview.append((f"{review_rank(v, p)}위" if v.is_data else f"상품 {i}", static))
            name = f"seg_{len(segments):02d}.mp4"
            if v.is_data:
                render_anim(ff, name, dur["product"], fps,
                            lambda t, p=p, i=i: data_product_frame(v, p, i, fonts, cfg, price_date, t), tmp)
                segments.append(name)
                continue
            bg.save(tmp / f"p{i}_bg.png")
            card.save(tmp / f"p{i}_card.png")
            static.save(tmp / f"p{i}_static.png")
            done = False
            if motion:
                try:
                    seg_motion(ff, f"p{i}_bg.png", f"p{i}_card.png", center, dur["product"],
                               cfg["zoom"], name, fps, tmp)
                    done = True
                except RuntimeError:
                    print("   참고: 이 ffmpeg에서는 확대 효과가 안 돼서 정지 화면으로 만들어요.")
                    motion = False
            if not done:
                seg_static(ff, f"p{i}_static.png", dur["product"], name, fps, tmp)
            segments.append(name)

        total = dur["hook"] + dur["product"] * len(v.products) + dur["outro"]
        bgm_cfg = ROOT / cfg.get("bgm", "")
        bgm = None
        if cfg.get("bgm") and bgm_cfg.exists():
            bgm = "bgm" + bgm_cfg.suffix
            shutil.copy(bgm_cfg, tmp / bgm)
        else:
            print("   참고: 배경음악(assets/bgm/jingle.mp3)이 없어서 무음으로 만들어요.")

        for platform in platforms:
            outro = render_outro(v, platform, fonts, cfg, notes)
            outro.save(tmp / f"outro_{platform}.png")
            if v.is_data:
                render_anim(ff, f"outro_{platform}.mp4", dur["outro"], fps,
                            lambda t, pf=platform: render_outro(v, pf, fonts, cfg, [], t), tmp)
            else:
                seg_static(ff, f"outro_{platform}.png", dur["outro"], f"outro_{platform}.mp4", fps, tmp)
            preview.append((f"마지막({platform})", outro))
            (tmp / f"list_{platform}.txt").write_text(
                "".join(f"file '{x}'\n" for x in segments + [f"outro_{platform}.mp4"]), encoding="utf-8")
            run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"list_{platform}.txt",
                 "-c", "copy", f"video_{platform}.mp4"], tmp)
            final = f"final_{platform}.mp4"
            if bgm:
                fade = float(cfg.get("bgm_fade_out", 1.2))
                run([ff, "-y", "-loglevel", "error", "-i", f"video_{platform}.mp4", "-stream_loop", "-1", "-i", bgm,
                     "-filter_complex", f"[1:a]volume={cfg.get('bgm_volume', 0.9)},"
                                        f"afade=t=out:st={total - fade:.2f}:d={fade}[a]",
                     "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                     "-t", f"{total:.2f}", "-movflags", "+faststart", final], tmp)
            else:
                run([ff, "-y", "-loglevel", "error", "-i", f"video_{platform}.mp4",
                     "-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=48000:cl=stereo",
                     "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                     "-t", f"{total:.2f}", "-movflags", "+faststart", final], tmp)
            target = out_dir / f"{v.vid}_{platform}.mp4"
            shutil.move(str(tmp / final), str(target))
            write_upload_text(v, platform, cfg, price_date, out_dir / f"{v.vid}_{platform}.txt")
            print(f"   완료: {target.relative_to(ROOT)}  ({PLATFORM_LABEL[platform]}, {total:.1f}초)")

        make_preview(preview, fonts, out_dir / f"{v.vid}_preview.png")
        print(f"   미리보기: {(out_dir / f'{v.vid}_preview.png').relative_to(ROOT)}  (빨간 영역 = 앱 UI가 가리는 곳)")
        for n_ in notes:
            print(f"   참고: {n_}")
        return True
    except RuntimeError as e:
        print(f"   [ffmpeg 오류]\n{e}")
        return False
    finally:
        if keep_temp:
            print(f"   중간 파일: {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="쇼핑 쇼츠 자동 생성기")
    ap.add_argument("--id", action="append", help="만들 영상ID (여러 번 쓸 수 있음)")
    ap.add_argument("--ready", action="store_true", help="상태가 '제작대기'인 영상 전부 제작")
    ap.add_argument("--check", action="store_true", help="시트 검사만")
    ap.add_argument("--platform", choices=["all", *PLATFORMS], default="all")
    ap.add_argument("--no-motion", action="store_true", help="상품 확대 효과 끄기")
    ap.add_argument("--keep-temp", action="store_true", help="중간 파일 보존")
    ap.add_argument("--sheet", help="시트 파일 경로 (기본: config.json의 sheet)")
    args = ap.parse_args()

    cfg = load_config()
    sheet = Path(args.sheet) if args.sheet else ROOT / cfg["sheet"]
    if not sheet.exists():
        print(f"[오류] 시트 파일이 없어요: {sheet}")
        return 1
    videos = load_sheet(sheet)

    if args.check:
        return check_all(videos, cfg)

    if args.ready:
        targets = [v for k, v in videos.items() if k != "_orphans" and v.status == STATUS_READY]
        if not targets:
            print("상태가 '제작대기'인 영상이 없어요.")
            return 0
    elif args.id:
        missing = [i for i in args.id if i not in videos]
        if missing:
            print(f"[오류] '영상' 시트에 없는 영상ID: {', '.join(missing)}")
            return 1
        targets = [videos[i] for i in args.id]
    else:
        ap.print_help()
        return 0

    platforms = PLATFORMS if args.platform == "all" else (args.platform,)
    fonts = Fonts(cfg)
    ff = find_ffmpeg(cfg)
    ok = 0
    for v in targets:
        ok += build(v, platforms, cfg, fonts, ff, motion=not args.no_motion, keep_temp=args.keep_temp)
    print(f"\n완료 {ok}개 / 요청 {len(targets)}개")
    return 0 if ok == len(targets) else 1


if __name__ == "__main__":
    sys.exit(main())
