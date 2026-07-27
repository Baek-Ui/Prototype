import reflex as rx

from .. import styles
from ..components.input_panel import example_chips, input_panel
from ..components.layout import page_shell
from ..state import State


def home() -> rx.Component:
    return page_shell(
        rx.vstack(
            rx.heading(
                "의심스러운 문자,",
                size="9",
                color=styles.TEXT_INK,
                text_align="center",
                line_height="1.3",
            ),
            rx.heading(
                "보내기 전에 확인하세요",
                size="9",
                text_align="center",
                line_height="1.3",
                # 그라디언트 글자 — 배경을 글자 모양으로 잘라낸다
                background=styles.PRIMARY_GRADIENT,
                background_clip="text",
                style={
                    "-webkit-background-clip": "text",
                    "-webkit-text-fill-color": "transparent",
                },
            ),
            rx.text(
                "받은 문구를 붙여넣으면 위험 신호와 과거 사기 사례를 대조해 위험도를 알려드립니다.",
                color=styles.TEXT_MUTED,
                text_align="center",
                margin_top="1rem",
                margin_bottom="3rem",
            ),
            input_panel(),
            # 빈 입력 등의 안내는 네이티브 alert 대신 화면 안에서 보여준다
            rx.cond(
                State.error_message != "",
                rx.callout(
                    State.error_message,
                    icon="triangle-alert",
                    color_scheme="red",
                    margin_top="1rem",
                    width=["95%", "90%", "680px"],
                ),
            ),
            example_chips(),
            width="100%",
            align="center",
            padding_top="9rem",
            padding_bottom="5rem",
            padding_x="1rem",
        )
    )
