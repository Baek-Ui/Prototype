"""디자인 토큰.

두 갈래로 나뉜다.

1. **컴포넌트용 토큰** — 전부 `var(--bu-*)` CSS 변수다. 실제 값은
   `assets/styles.css`가 `<html class="dark">` / `.light`에 따라 바꿔 끼운다.
   테마를 바꿔도 서버가 다시 렌더할 필요가 없다는 게 이 방식의 요점이다.
2. **`GRAPH_PALETTES`** — 리터럴 hex. Plotly는 파이썬에서 Figure를 만들고
   색을 그대로 굽기 때문에 CSS 변수를 해석하지 못한다. 그래서 그래프만은
   현재 모드에 맞는 hex를 State가 골라 넘긴다(`figure.build_figure`).

색은 design/DESIGN.md의 다크 팔레트를 따른다 — 인디고/퍼플 계열이
baek_ui 심볼의 그라디언트와 같은 색계라 브랜드가 맞아떨어진다. 라이트
모드는 같은 정체성을 흰 바탕에서 읽히도록 명도만 다시 잡은 짝이다.

CSS 변수는 `#RRGGBB` + 알파 접미사 같은 문자열 조작이 불가능하다. 반투명이
필요한 자리는 여기서 별도 토큰(`*_WASH`, `SUBTLE_FILL` 등)으로 뽑아 둔다.
"""

# Surfaces
BG_BASE = "var(--bu-bg-base)"  # 페이지 바탕
SURFACE = "var(--bu-surface)"  # 카드·패널 표면
NAVBAR_BG = "var(--bu-navbar-bg)"  # 반투명 네비바
PANEL_TRANSLUCENT = "var(--bu-panel-translucent)"  # 섹션 배경용 반투명 표면

# Accents
ACCENT = "var(--bu-accent)"
ACCENT_SOFT = "var(--bu-accent-soft)"
ON_ACCENT = "var(--bu-on-accent)"
ACCENT_WASH = "var(--bu-accent-wash)"  # 아이콘 타일 등 옅은 액센트 바탕

# Text
TEXT_INK = "var(--bu-text-ink)"
TEXT_MUTED = "var(--bu-text-muted)"
TEXT_FAINT = "var(--bu-text-faint)"

# Lines & fills
BORDER_COLOR = "var(--bu-border)"
SUBTLE_FILL = "var(--bu-subtle-fill)"
TRACK_COLOR = "var(--bu-track)"

# Elevation
CARD_SHADOW = "var(--bu-card-shadow)"

# 모서리 — DESIGN.md의 "Rounded" 언어. 작은 요소일수록 작게 줘야 같은
# 곡률로 보인다(큰 카드에 12px을 주면 각져 보이고, 칩에 24px을 주면 알약이 된다).
RADIUS_SM = "10px"  # 칩, 배지, 작은 태그
RADIUS_MD = "14px"  # 리포트 안쪽 항목, 아이콘 타일
RADIUS_LG = "20px"  # 카드·패널
RADIUS_XL = "26px"  # 입력 패널처럼 화면의 주인공이 되는 큰 표면
RADIUS_FULL = "9999px"  # rx.box 등 Radix가 아닌 요소의 알약 모양

CARD_STYLE = {
    "background_color": SURFACE,
    "border": f"1px solid {BORDER_COLOR}",
    "border_radius": RADIUS_LG,
    "box_shadow": CARD_SHADOW,
}

# Typography — 한글은 모노 스택에 넣지 않는다(Consolas 등에 한글 글리프가
# 없어 글자별 폴백이 일어나면 자간이 무너진다). MONO는 숫자·영문 전용.
FONT_FAMILY = (
    'Inter, "Pretendard", system-ui, -apple-system, "Segoe UI", '
    '"Malgun Gothic", sans-serif'
)
MONO_FAMILY = 'ui-monospace, "Cascadia Mono", "Consolas", "D2Coding", monospace'

# Gradients — 채워진 버튼용(흰 글자가 얹힌다)과 글자 자체를 칠하는 용도를
# 나눈다. 버튼 그라디언트를 어두운 바탕 위 헤드라인에 그대로 쓰면 글자가
# 배경에 잠긴다.
PRIMARY_GRADIENT = "var(--bu-primary-gradient)"
TEXT_GRADIENT = "var(--bu-text-gradient)"

# 배경 워시 — 눈에 거의 걸리지 않을 만큼만
BG_WASH = "var(--bu-bg-wash)"
GRAPH_WASH = "var(--bu-graph-wash)"

# Hover Effects
HOVER_TRANSITION = "all 0.3s ease-in-out"

# Risk Levels (RiskLevel.value를 키로 사용)
RISK_COLORS = {
    "안전": "var(--bu-risk-safe)",
    "주의": "var(--bu-risk-caution)",
    "위험": "var(--bu-risk-danger)",
}

# 위험 강조용 반투명 — 하이라이트 배경, 긴급 배너 등
DANGER_WASH = "var(--bu-danger-wash)"
DANGER_BORDER = "var(--bu-danger-border)"


# --- Plotly 전용 리터럴 팔레트 -------------------------------------------
# CSS 변수를 쓸 수 없는 유일한 자리. 키는 PhishingCategory.value.

_DARK_CATEGORIES = {
    "기관사칭": "#FF9E93",
    "대출사기": "#FFB783",
    "가족사칭": "#D0BCFF",
    "스미싱": "#8FB8FF",
    "정상": "#5BD6A0",
}

_LIGHT_CATEGORIES = {
    "기관사칭": "#C0503F",
    "대출사기": "#B26A1F",
    "가족사칭": "#7B3FD4",
    "스미싱": "#3A63C4",
    "정상": "#227A54",
}

GRAPH_PALETTES = {
    "dark": {
        "categories": _DARK_CATEGORIES,
        "rule_edge": "#FF9E93",
        "case_edge": "#8083FF",
        "rule_inactive": "#908FA0",
        "rule_active": "#FF9E93",
        # 입력 노드는 다섯 카테고리 색 어디에도 속하지 않아야 "내가 지금
        # 여기"로 읽힌다. 어두운 바탕에서는 잉크색 대신 가장 밝은 흰빛.
        "input_node": "#F4F2FA",
        "marker_outline": "#13131B",
        "legend_bg": "rgba(19, 19, 27, 0.72)",
        "text": "#C7C4D7",
        "hover_bg": "#1F1F27",
        "hover_border": "#464554",
        "hover_text": "#E4E1ED",
    },
    "light": {
        "categories": _LIGHT_CATEGORIES,
        "rule_edge": "#C0503F",
        "case_edge": "#4B4ACF",
        "rule_inactive": "#55556B",
        "rule_active": "#C0503F",
        "input_node": "#14141C",
        "marker_outline": "#FFFFFF",
        "legend_bg": "rgba(255, 255, 255, 0.78)",
        "text": "#55556B",
        "hover_bg": "#FFFFFF",
        "hover_border": "rgba(20, 20, 28, 0.14)",
        "hover_text": "#14141C",
    },
}


def graph_palette(is_dark: bool) -> dict:
    return GRAPH_PALETTES["dark" if is_dark else "light"]
