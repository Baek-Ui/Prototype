import reflex as rx

from .. import styles


def _nav_link(label: str) -> rx.Component:
    return rx.link(
        label,
        href="#",
        color=styles.TEXT_MUTED,
        text_decoration="none",
        transition=styles.HOVER_TRANSITION,
        _hover={"color": styles.TEXT_INK},
    )


def navbar() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.icon("shield-check", size=24, color=styles.ACCENT),
            rx.heading("백의", size="5", color=styles.TEXT_INK),
            spacing="2",
            align="center",
            cursor="pointer",
            on_click=rx.redirect("/"),
        ),
        rx.flex(
            _nav_link("서비스 소개"),
            _nav_link("탐지 원리"),
            _nav_link("신고 안내"),
            spacing="6",
            display=["none", "none", "flex"],
        ),
        width="100%",
        justify="between",
        align="center",
        padding_x=["1.5rem", "2rem", "4rem"],
        padding_y="1.5rem",
        position="fixed",
        top="0",
        z_index="100",
        # 밝은 바탕에서는 반투명 흰색 + 하단 경계선이 스크롤 시 내용과 겹치지 않게 막아준다
        background="rgba(255, 255, 255, 0.82)",
        backdrop_filter="blur(10px)",
        border_bottom=f"1px solid {styles.BORDER_COLOR}",
    )


def footer() -> rx.Component:
    return rx.vstack(
        rx.divider(border_color=styles.BORDER_COLOR),
        rx.flex(
            rx.text(
                "본 서비스는 사기 여부를 단정하지 않습니다. 최종 판단 전 반드시 공식 기관에 확인하세요.",
                color=styles.TEXT_MUTED,
                font_size="0.8rem",
            ),
            rx.text(
                "보이스피싱 신고 112 · 금융감독원 1332",
                color=styles.TEXT_MUTED,
                font_size="0.8rem",
            ),
            width="100%",
            justify="between",
            wrap="wrap",
            gap="1rem",
            padding_y="2.5rem",
        ),
        width="100%",
        padding_x=["1.5rem", "2rem", "4rem"],
    )


def page_shell(*children: rx.Component) -> rx.Component:
    """모든 페이지가 공유하는 배경·폰트·스크롤 컨테이너."""
    return rx.box(
        navbar(),
        rx.scroll_area(
            rx.vstack(*children, footer(), width="100%", spacing="0"),
            width="100%",
            height="100vh",
        ),
        background=styles.BG_BASE,
        background_image=styles.BG_WASH,
        background_attachment="fixed",
        color=styles.TEXT_INK,
        min_height="100vh",
        font_family=styles.FONT_FAMILY,
    )
