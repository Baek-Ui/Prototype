import reflex as rx

from .. import styles
from ..state import TOTAL_RULE_COUNT, State


def _score_gauge() -> rx.Component:
    """점수 비율만큼 채워지는 원형 게이지."""
    return rx.box(
        rx.box(
            rx.vstack(
                rx.heading(
                    State.risk_score.to_string(),
                    size="7",
                    color=State.risk_color,
                    font_family=styles.MONO_FAMILY,
                ),
                rx.text(
                    "/ 100",
                    font_size="0.62rem",
                    color=styles.TEXT_MUTED,
                    font_family=styles.MONO_FAMILY,
                ),
                spacing="0",
                align="center",
                justify="center",
                height="100%",
            ),
            width="calc(100% - 1.1rem)",
            height="calc(100% - 1.1rem)",
            border_radius="9999px",
            background=styles.SURFACE,
            border=f"1px solid {styles.BORDER_COLOR}",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        width="7.5rem",
        height="7.5rem",
        flex="none",
        border_radius="9999px",
        display="flex",
        align_items="center",
        justify_content="center",
        background=(
            f"conic-gradient({State.risk_color} 0 {State.risk_score}%, "
            f"{styles.TRACK_COLOR} {State.risk_score}% 100%)"
        ),
    )


def _tile(label: str, body: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.text(
            label,
            font_size="0.72rem",
            font_weight="600",
            color=styles.TEXT_MUTED,
            letter_spacing="0.02em",
        ),
        body,
        align="start",
        justify="between",
        spacing="3",
        padding="1.25rem",
        # 세 타일이 나란히 서다가 좁아지면 자연스럽게 아래로 접힌다
        flex="1 1 13rem",
        min_width="0",
        min_height="11rem",
        style=styles.CARD_STYLE,
    )


def _headline(value: rx.Var | str, color: rx.Var | str) -> rx.Component:
    return rx.text(
        value,
        font_size="1.65rem",
        font_weight="700",
        color=color,
        line_height="1.2",
    )


def _caption(text: rx.Var | str) -> rx.Component:
    return rx.text(text, font_size="0.8rem", color=styles.TEXT_MUTED, line_height="1.5")


def kpi_row() -> rx.Component:
    """종합 위험도 · 탐지된 신호 · 추정 수법 유형."""
    return rx.flex(
        _tile(
            "종합 위험도",
            rx.flex(
                _score_gauge(),
                rx.vstack(
                    rx.flex(
                        rx.box(
                            width="0.45rem",
                            height="0.45rem",
                            border_radius="9999px",
                            background=State.risk_color,
                        ),
                        rx.text(
                            State.risk_level,
                            font_size="0.82rem",
                            font_weight="600",
                            color=State.risk_color,
                        ),
                        spacing="2",
                        align="center",
                        padding="0.3rem 0.85rem",
                        border_radius="9999px",
                        border=f"1px solid {State.risk_color}",
                        background=styles.SUBTLE_FILL,
                    ),
                    _caption("위험 신호 60% + 사례 유사도 40%"),
                    align="start",
                    spacing="2",
                    flex="1 1 8rem",
                    min_width="0",
                ),
                gap="1rem",
                align="center",
                wrap="wrap",
                width="100%",
            ),
        ),
        _tile(
            "탐지된 위험 신호",
            rx.vstack(
                rx.flex(
                    _headline(State.signal_count.to_string(), State.risk_color),
                    rx.text(
                        f"/ {TOTAL_RULE_COUNT}건",
                        font_size="0.8rem",
                        color=styles.TEXT_MUTED,
                        font_family=styles.MONO_FAMILY,
                    ),
                    spacing="2",
                    align="baseline",
                ),
                rx.box(
                    rx.box(
                        width=f"{State.signal_count * 100 / TOTAL_RULE_COUNT}%",
                        height="100%",
                        border_radius="2px",
                        background=State.risk_color,
                    ),
                    width="100%",
                    height="4px",
                    border_radius="2px",
                    background=styles.TRACK_COLOR,
                    overflow="hidden",
                ),
                rx.cond(
                    State.signal_count > 0,
                    _caption(f"가장 무거운 신호 +{State.max_signal_weight}점"),
                    _caption("규칙 사전에 걸린 신호가 없습니다"),
                ),
                align="start",
                spacing="2",
                width="100%",
            ),
        ),
        _tile(
            "추정 수법 유형",
            rx.vstack(
                _headline(
                    State.attack_type,
                    rx.cond(
                        State.attack_similarity > 0, styles.TEXT_INK, styles.TEXT_MUTED
                    ),
                ),
                rx.cond(
                    State.attack_similarity > 0,
                    rx.vstack(
                        rx.box(
                            rx.box(
                                width=f"{State.attack_similarity}%",
                                height="100%",
                                border_radius="2px",
                                background=styles.ACCENT,
                            ),
                            width="100%",
                            height="4px",
                            border_radius="2px",
                            background=styles.TRACK_COLOR,
                            overflow="hidden",
                        ),
                        _caption(f"가장 가까운 사례와 {State.attack_similarity}% 일치"),
                        align="start",
                        spacing="2",
                        width="100%",
                    ),
                    _caption("가장 가까운 사례가 정상 문구입니다"),
                ),
                align="start",
                spacing="2",
                width="100%",
            ),
        ),
        width="100%",
        gap="1rem",
        wrap="wrap",
        align="stretch",
    )
