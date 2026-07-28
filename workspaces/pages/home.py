import reflex as rx

from .. import styles
from ..components.input_panel import example_chips, input_panel
from ..components.landing import (
    final_cta_section,
    problem_solution_section,
    process_section,
    trust_section,
)
from ..components.layout import page_shell
from ..components.report_card import report_card
from ..components.skeleton import report_skeleton, stepper
from ..components.vector_graph import vector_graph
from ..state import State


def _hero() -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.box(
                width="0.4rem",
                height="0.4rem",
                border_radius="9999px",
                background=styles.ACCENT_SOFT,
            ),
            rx.text(
                "설치도 가입도 없이, 붙여넣기 한 번",
                font_size="0.8rem",
                font_weight="600",
                color=styles.TEXT_MUTED,
            ),
            spacing="2",
            align="center",
            padding="0.4rem 1rem",
            border_radius="9999px",
            border=f"1px solid {styles.BORDER_COLOR}",
            background=styles.SURFACE,
            margin_bottom="1.5rem",
        ),
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
            # 그라디언트 글자 — 배경을 글자 모양으로 잘라낸다. 버튼용
            # 그라디언트를 쓰면 어두운 바탕에서 글자가 잠기므로 밝은 짝을 쓴다.
            background=styles.TEXT_GRADIENT,
            background_clip="text",
            style={
                "-webkit-background-clip": "text",
                "-webkit-text-fill-color": "transparent",
            },
        ),
        # 두 줄을 각각 텍스트로 둬서 줄바꿈 위치를 폭에 맡기지 않고 고정한다.
        # spacing="0"이라 vstack의 기본 간격 없이 한 문단처럼 붙어 읽힌다.
        rx.vstack(
            rx.text("받은 문구를 붙여넣으면 위험 신호와"),
            rx.text("과거 사기 사례를 대조해 위험도를 알려드립니다."),
            color=styles.TEXT_MUTED,
            text_align="center",
            line_height="1.7",
            spacing="0",
            align="center",
            margin_top="1rem",
            margin_bottom="2.5rem",
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
        # 네비바 로고가 돌아올 자리
        id="hero",
        width="100%",
        align="center",
        padding_top="8.5rem",
        padding_bottom="4rem",
        padding_x="1rem",
    )


def _analysis_section() -> rx.Component:
    """분석을 한 번이라도 시작한 뒤에만 히어로 아래에 열리는 구간."""
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.heading("분석 결과", size="6", color=styles.TEXT_INK),
                    rx.text(
                        "입력한 문구는 저장되지 않으며, 개인정보는 가려서 표시됩니다.",
                        font_size="0.82rem",
                        color=styles.TEXT_MUTED,
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.button(
                    rx.icon("rotate-ccw", size=16),
                    "다른 문구 분석하기",
                    variant="ghost",
                    color=styles.TEXT_MUTED,
                    cursor="pointer",
                    border_radius=styles.RADIUS_FULL,
                    disabled=State.is_detecting,
                    on_click=State.reset_analysis,
                    _hover={"color": styles.ACCENT, "background": styles.SUBTLE_FILL},
                ),
                width="100%",
                justify="between",
                align="center",
                wrap="wrap",
                gap="1rem",
            ),
            stepper(),
            rx.cond(
                State.error_message != "",
                rx.callout(
                    State.error_message,
                    icon="triangle-alert",
                    color_scheme="red",
                    width="100%",
                ),
                rx.fragment(
                    vector_graph(),
                    rx.cond(State.is_detecting, report_skeleton(), report_card()),
                ),
            ),
            width=["95%", "92%", "1080px"],
            align="start",
            spacing="4",
            margin="0 auto",
        ),
        id="analysis",
        width="100%",
        padding_y="2rem",
        padding_x="1rem",
        # 고정 네비바 높이만큼 스크롤 도착점을 내린다
        scroll_margin_top="5.5rem",
    )


def home() -> rx.Component:
    return page_shell(
        # localStorage에 남아 있는 테마 선택을 서버에도 알린다 — 그래프
        # 팔레트가 화면과 어긋나지 않게 하는 유일한 지점이다.
        rx.box(on_mount=State.sync_color_mode(rx.color_mode), display="none"),
        _hero(),
        rx.cond(State.has_started, _analysis_section()),
        problem_solution_section(),
        trust_section(),
        process_section(),
        final_cta_section(),
    )
