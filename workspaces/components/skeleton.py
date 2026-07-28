import reflex as rx

from .. import styles
from ..state import State

STEP_LABELS = ["전처리", "문구 벡터화", "위험 패턴 대조", "유사 사례 검색", "종합 판정"]


def _step_node(index: int, label: str) -> rx.Component:
    is_done = State.current_step > index
    is_active = State.current_step == index

    return rx.vstack(
        # 진행 막대 — 완료는 채우고, 진행 중은 절반만 채워 "지금 여기"를 보여준다
        rx.box(
            width="100%",
            height="3px",
            border_radius="2px",
            background=rx.cond(
                is_done,
                styles.ACCENT_SOFT,
                rx.cond(
                    is_active,
                    f"linear-gradient(90deg, {styles.ACCENT} 55%, {styles.TRACK_COLOR} 55%)",
                    styles.TRACK_COLOR,
                ),
            ),
        ),
        rx.flex(
            rx.box(
                rx.cond(
                    is_done,
                    rx.icon("check", size=12, color=styles.ON_ACCENT),
                    rx.cond(
                        is_active,
                        rx.spinner(size="1"),
                        rx.text(
                            str(index + 1),
                            font_family=styles.MONO_FAMILY,
                            font_size="0.62rem",
                            color=styles.TEXT_FAINT,
                        ),
                    ),
                ),
                width="1.15rem",
                height="1.15rem",
                flex="none",
                border_radius="9999px",
                display="flex",
                align_items="center",
                justify_content="center",
                background=rx.cond(is_done, styles.ACCENT_SOFT, "transparent"),
                border=rx.cond(
                    is_done,
                    "1px solid transparent",
                    rx.cond(
                        is_active,
                        f"1px solid {styles.ACCENT}",
                        f"1px solid {styles.BORDER_COLOR}",
                    ),
                ),
            ),
            rx.text(
                label,
                font_size="0.83rem",
                color=rx.cond(
                    is_active,
                    styles.TEXT_INK,
                    rx.cond(is_done, styles.TEXT_MUTED, styles.TEXT_FAINT),
                ),
                white_space="nowrap",
            ),
            spacing="2",
            align="center",
        ),
        spacing="2",
        align="start",
        flex="1 1 9rem",
    )


def stepper() -> rx.Component:
    return rx.flex(
        *[_step_node(index, label) for index, label in enumerate(STEP_LABELS)],
        width="100%",
        gap="0.75rem",
        wrap="wrap",
        padding_bottom="1.8rem",
    )


def _bar(width: str, height: str = "14px", radius: str | None = None) -> rx.Component:
    return rx.box(
        class_name="skeleton-block", width=width, height=height, border_radius=radius
    )


def report_skeleton() -> rx.Component:
    """리포트 카드와 동일한 레이아웃의 로딩 플레이스홀더.

    스테퍼는 분석 섹션이 직접 들고 있다 — 진행 상황은 리포트가 아니라
    그 위의 벡터 그래프에도 걸리기 때문이다.
    """
    return rx.vstack(
        rx.flex(
            # 게이지 자리는 원형으로 — 실제 리포트와 형태가 어긋나면 전환이 튄다
            _bar("5.5rem", "5.5rem", radius="9999px"),
            rx.vstack(
                _bar("45%", "1.5rem"),
                _bar("78%"),
                _bar("62%"),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            align="center",
            width="100%",
        ),
        rx.vstack(_bar("34%"), _bar("100%", "3.4rem"), _bar("100%", "3.4rem"),
                  width="100%", spacing="3", margin_top="1.5rem"),
        style=styles.CARD_STYLE,
        width="100%",
        padding="1.75rem",
        spacing="4",
    )
