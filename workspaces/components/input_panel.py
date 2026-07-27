import reflex as rx

from .. import styles
from ..state import State

# (분류 라벨, 문구) — 분류는 사용자가 무엇을 시험해 보는지 바로 알 수 있게 붙인다.
EXAMPLES = [
    ("기관사칭", "서울중앙지검 수사관입니다. 안전계좌로 즉시 이체하지 않으면 계좌가 동결됩니다."),
    ("대출사기", "저금리 대환대출 승인되었습니다. 기존 대출 상환을 위해 지정 계좌로 입금하세요."),
    ("정상", "안녕하세요, 내일 회의 시간 오후 3시로 변경 가능할까요?"),
]


def _example_chip(category: str, text: str) -> rx.Component:
    # 정상 예시는 안전 색으로 구분해, 피싱 예시만 있는 것으로 오해하지 않게 한다.
    tag_color = styles.RISK_COLORS["안전"] if category == "정상" else styles.ACCENT

    return rx.flex(
        # 한글은 모노 폰트로 두지 않는다 — Consolas 등에 한글 글리프가 없어
        # 글자별 폴백이 일어나면서 자간이 무너진다. 모노는 숫자·영문 전용.
        rx.text(
            category,
            color=tag_color,
            font_size="0.72rem",
            font_weight="600",
            white_space="nowrap",
        ),
        rx.text(text[:18] + "…", color="inherit", font_size="0.8rem"),
        spacing="2",
        align="center",
        color=styles.TEXT_MUTED,
        background_color=styles.SUBTLE_FILL,
        border=f"1px solid {styles.BORDER_COLOR}",
        padding="0.5rem 1rem",
        border_radius="12px",
        cursor="pointer",
        transition=styles.HOVER_TRANSITION,
        on_click=lambda: State.set_input_text(text),
        _hover={
            "border_color": styles.ACCENT,
            "color": styles.TEXT_INK,
            "transform": "translateY(-1px)",
        },
    )


def input_panel() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text_area(
                placeholder="의심스러운 문자나 메시지를 붙여넣어 주세요...",
                value=State.input_text,
                on_change=State.set_input_text,
                width="100%",
                min_height="9rem",
                background="transparent",
                color=styles.TEXT_INK,
                border="none",
                resize="vertical",
                _placeholder={"color": styles.TEXT_FAINT},
                _focus={"box_shadow": "none"},
            ),
            rx.flex(
                rx.text(
                    "입력한 문구는 저장되지 않습니다",
                    color=styles.TEXT_MUTED,
                    font_size="0.75rem",
                ),
                rx.button(
                    "위험도 분석",
                    rx.icon("arrow-right", size=18),
                    background=styles.PRIMARY_GRADIENT,
                    color=styles.ON_ACCENT,
                    border_radius="full",
                    padding_x="1.5rem",
                    height="2.75rem",
                    cursor="pointer",
                    on_click=State.detect,
                    loading=State.is_detecting,
                    transition=styles.HOVER_TRANSITION,
                    _hover={"filter": "brightness(1.08)", "transform": "translateY(-1px)"},
                ),
                width="100%",
                justify="between",
                align="center",
                wrap="wrap",
                gap="1rem",
            ),
            width="100%",
            spacing="3",
            padding="1.25rem",
        ),
        style=styles.CARD_STYLE,
        width=["95%", "90%", "680px"],
    )


def example_chips() -> rx.Component:
    return rx.flex(
        *[_example_chip(category, text) for category, text in EXAMPLES],
        spacing="3",
        margin_top="1.5rem",
        flex_wrap="wrap",
        justify="center",
    )
