import reflex as rx

from .. import styles
from ..components.layout import page_shell
from ..components.report_card import report_card
from ..components.skeleton import report_skeleton
from ..state import State


def result() -> rx.Component:
    return page_shell(
        rx.vstack(
            rx.flex(
                rx.button(
                    rx.icon("chevron-left", size=18),
                    "다른 문구 분석하기",
                    variant="ghost",
                    color=styles.TEXT_MUTED,
                    cursor="pointer",
                    border_radius="full",
                    on_click=State.reset_and_go_home,
                    _hover={"color": styles.ACCENT, "background": styles.SUBTLE_FILL},
                ),
                width="100%",
                justify="start",
                margin_bottom="1.5rem",
            ),
            rx.cond(
                State.error_message != "",
                rx.callout(
                    State.error_message,
                    icon="triangle-alert",
                    color_scheme="red",
                    width="100%",
                ),
                rx.cond(State.is_detecting, report_skeleton(), report_card()),
            ),
            width=["95%", "92%", "780px"],
            align="start",
            padding_top="8rem",
            padding_bottom="5rem",
        ),
    )
