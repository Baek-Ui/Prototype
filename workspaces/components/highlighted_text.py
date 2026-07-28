import reflex as rx

from .. import styles
from ..state import State


def _segment(segment: rx.Var) -> rx.Component:
    """부각 구간은 배경으로 표시하고, 무엇 때문에 걸렸는지 툴팁으로 알려준다."""
    return rx.cond(
        segment.is_flagged,
        rx.tooltip(
            rx.text(
                segment.text,
                as_="span",
                color=styles.RISK_COLORS["위험"],
                font_weight="600",
                background=styles.DANGER_WASH,
                border_bottom=f"2px solid {styles.RISK_COLORS['위험']}",
                border_radius="6px",
                padding="0.1rem 0.15rem",
                cursor="help",
            ),
            content=segment.keyword,
        ),
        rx.text(segment.text, as_="span", color=styles.TEXT_INK),
    )


def highlighted_text() -> rx.Component:
    """마스킹된 입력 문구를, 점수를 낸 구간만 색칠해 그대로 보여준다."""
    return rx.vstack(
        rx.flex(
            rx.heading("의심스러운 표현", size="3", color=styles.TEXT_INK),
            rx.text(
                "개인정보는 가려서 표시됩니다",
                font_size="0.72rem",
                color=styles.TEXT_MUTED,
            ),
            width="100%",
            justify="between",
            align="baseline",
            wrap="wrap",
            gap="0.5rem",
        ),
        rx.box(
            rx.cond(
                State.text_segments.length() > 0,
                rx.box(rx.foreach(State.text_segments, _segment)),
                rx.text(
                    State.masked_text,
                    color=styles.TEXT_INK,
                ),
            ),
            width="100%",
            font_size="0.95rem",
            line_height="2.1",
            padding="1rem 1.15rem",
            background=styles.SUBTLE_FILL,
            border_left=f"2px solid {State.risk_color}",
            border_radius=f"0 {styles.RADIUS_MD} {styles.RADIUS_MD} 0",
            # word_break를 여기서 덮으면 body의 keep-all이 무효가 되어 붙여넣은
            # 문구의 어절이 잘린다. 긴 토큰 방어는 overflow_wrap이 맡는다.
            overflow_wrap="break-word",
        ),
        width="100%",
        align="start",
        spacing="3",
        padding="1.35rem",
        style=styles.CARD_STYLE,
    )
