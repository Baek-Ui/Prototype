import reflex as rx

from .. import styles
from ..components.layout import page_shell


def home() -> rx.Component:
    return page_shell(
        rx.center(
            rx.heading("보이스피싱 문구 탐지", size="8", color=styles.TEXT_INK),
            width="100%",
            padding_top="10rem",
            padding_bottom="6rem",
        )
    )
