"""디자인 토큰 — 라이트 테마 단일 팔레트.

Task 7에서 승인된 시안의 값을 그대로 옮긴다. 액센트와 위험도 색은
다크 팔레트를 밝기만 뒤집은 것이 아니라, 흰 바탕에서 본문 크기로도
읽히도록 명도 대비를 따로 확보한 값이다.
"""

# Surfaces
BG_BASE = "#EEF2F6"  # 페이지 바탕
SURFACE = "#FFFFFF"  # 카드·패널 표면

# Accents
ACCENT = "#2F7CA8"
ACCENT_SOFT = "#3E8C76"
ON_ACCENT = "#FFFFFF"

# Text
TEXT_INK = "#1B2733"
TEXT_MUTED = "#5C6B7A"
TEXT_FAINT = "rgba(92, 107, 122, 0.68)"

# Lines & fills
BORDER_COLOR = "rgba(27, 39, 51, 0.13)"
SUBTLE_FILL = "rgba(27, 39, 51, 0.03)"
TRACK_COLOR = "rgba(27, 39, 51, 0.10)"

# Elevation — 밝은 바탕에서는 얕고 서늘한 그림자가 카드 경계를 만든다
CARD_SHADOW = "0 0.75rem 2rem rgba(27, 39, 51, 0.09)"

CARD_STYLE = {
    "background_color": SURFACE,
    "border": f"1px solid {BORDER_COLOR}",
    "border_radius": "15px",
    "box_shadow": CARD_SHADOW,
}

# Typography
FONT_FAMILY = (
    'Inter, "Pretendard", system-ui, -apple-system, "Segoe UI", '
    '"Malgun Gothic", sans-serif'
)
MONO_FAMILY = 'ui-monospace, "Cascadia Mono", "Consolas", "D2Coding", monospace'

# Gradients
PRIMARY_GRADIENT = f"linear-gradient(90deg, {ACCENT} 0%, {ACCENT_SOFT} 100%)"

# 배경 워시 — 눈에 거의 걸리지 않을 만큼만
BG_WASH = (
    "radial-gradient(58rem 30rem at 15% -10%, rgba(47, 124, 168, 0.08), transparent 64%)"
)

# Hover Effects
HOVER_TRANSITION = "all 0.3s ease-in-out"

# Risk Levels (RiskLevel.value를 키로 사용)
RISK_COLORS = {
    "안전": "#227A54",
    "주의": "#9A6A12",
    "위험": "#C0503F",
}
