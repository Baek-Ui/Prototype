import reflex as rx

from .. import styles
from ..state import State

# 규칙 사전의 최대 가중치. 기여도 막대를 이 값 기준으로 정규화해
# 어느 근거가 점수를 크게 끌어올렸는지 한눈에 비교되게 한다.
_MAX_RULE_WEIGHT = 35


def _score_gauge() -> rx.Component:
    """점수 비율만큼 채워지는 원형 게이지."""
    return rx.box(
        rx.box(
            rx.vstack(
                rx.heading(
                    State.risk_score.to_string(),
                    size="8",
                    color=State.risk_color,
                    font_family=styles.MONO_FAMILY,
                ),
                rx.text("/ 100", font_size="0.66rem", color=styles.TEXT_MUTED,
                        font_family=styles.MONO_FAMILY),
                spacing="0",
                align="center",
                justify="center",
                height="100%",
            ),
            width="calc(100% - 1.25rem)",
            height="calc(100% - 1.25rem)",
            border_radius="full",
            background=styles.SURFACE,
            border=f"1px solid {styles.BORDER_COLOR}",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        width="9.5rem",
        height="9.5rem",
        flex="none",
        border_radius="full",
        display="flex",
        align_items="center",
        justify_content="center",
        background=(
            f"conic-gradient({State.risk_color} 0 {State.risk_score}%, "
            f"{styles.TRACK_COLOR} {State.risk_score}% 100%)"
        ),
    )


def _verdict() -> rx.Component:
    return rx.flex(
        _score_gauge(),
        rx.vstack(
            rx.flex(
                rx.box(width="0.45rem", height="0.45rem", border_radius="full",
                       background=State.risk_color),
                rx.text(State.risk_level, font_size="0.82rem", font_weight="600",
                        color=State.risk_color),
                spacing="2",
                align="center",
                padding="0.3rem 0.85rem",
                border_radius="full",
                border=f"1px solid {State.risk_color}",
                background=styles.SUBTLE_FILL,
            ),
            rx.text(
                State.masked_text,
                font_size="0.9rem",
                color=styles.TEXT_MUTED,
                padding="0.85rem 1.05rem",
                background=styles.SUBTLE_FILL,
                border_left=f"2px solid {State.risk_color}",
                border_radius="0 8px 8px 0",
                width="100%",
            ),
            align="start",
            spacing="3",
            flex="1 1 20rem",
        ),
        spacing="5",
        align="center",
        wrap="wrap",
        width="100%",
    )


def _evidence_item(evidence: rx.Var) -> rx.Component:
    # 가중치가 큰 근거일수록 강한 색으로 — 색만이 아니라 좌측 스트라이프·배지·막대
    # 세 가지 형태로 심각도를 나타내 색을 구분하기 어려운 경우에도 읽히게 한다.
    severity = rx.cond(
        evidence.weight >= 25, styles.RISK_COLORS["위험"], styles.RISK_COLORS["주의"]
    )

    return rx.vstack(
        rx.flex(
            rx.text(evidence.keyword, font_weight="600", font_size="0.9rem",
                    color=styles.TEXT_INK),
            rx.text(
                f"+{evidence.weight}",
                font_family=styles.MONO_FAMILY,
                font_size="0.74rem",
                font_weight="600",
                color=severity,
                padding="0.15rem 0.5rem",
                border_radius="6px",
                background=styles.SUBTLE_FILL,
            ),
            width="100%",
            justify="between",
            align="center",
            gap="0.85rem",
        ),
        rx.text(evidence.description, font_size="0.82rem", color=styles.TEXT_MUTED,
                line_height="1.6"),
        rx.box(
            rx.box(
                width=f"{evidence.weight * 100 / _MAX_RULE_WEIGHT}%",
                height="100%",
                border_radius="2px",
                background=severity,
                opacity="0.85",
            ),
            width="100%",
            height="3px",
            border_radius="2px",
            background=styles.TRACK_COLOR,
            overflow="hidden",
        ),
        spacing="2",
        align="start",
        width="100%",
        padding="0.85rem 0.95rem",
        border_radius="10px",
        background=styles.SUBTLE_FILL,
        border=f"1px solid {styles.BORDER_COLOR}",
        border_left=f"2px solid {severity}",
    )


def _similar_case_item(item: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.text(
                item.category,
                font_size="0.72rem",
                font_weight="600",
                color=styles.ACCENT,
                padding="0.12rem 0.45rem",
                border_radius="5px",
                background=styles.SUBTLE_FILL,
            ),
            rx.text(
                f"{item.similarity_percent}%",
                font_family=styles.MONO_FAMILY,
                font_size="0.78rem",
                font_weight="600",
                color=styles.TEXT_INK,
            ),
            width="100%",
            justify="between",
            align="center",
        ),
        rx.box(
            rx.box(
                width=f"{item.similarity_percent}%",
                height="100%",
                border_radius="2px",
                background=styles.ACCENT,
            ),
            width="100%",
            height="3px",
            border_radius="2px",
            background=styles.TRACK_COLOR,
            overflow="hidden",
        ),
        rx.text(item.text, font_size="0.84rem", color=styles.TEXT_MUTED,
                line_height="1.6", no_of_lines=2),
        spacing="2",
        align="start",
        width="100%",
        padding="0.85rem 0.95rem",
        border_radius="10px",
        background=styles.SUBTLE_FILL,
        border=f"1px solid {styles.BORDER_COLOR}",
    )


def _action_item(index: rx.Var, action: rx.Var) -> rx.Component:
    return rx.flex(
        rx.box(
            rx.text(
                (index + 1).to_string(),
                font_family=styles.MONO_FAMILY,
                font_size="0.7rem",
                font_weight="600",
                color=State.risk_color,
            ),
            width="1.3rem",
            height="1.3rem",
            flex="none",
            border_radius="full",
            display="flex",
            align_items="center",
            justify_content="center",
            background=styles.SURFACE,
            border=f"1px solid {State.risk_color}",
        ),
        rx.text(action, font_size="0.92rem", color=styles.TEXT_INK),
        spacing="3",
        align="start",
    )


def _panel(title: str, count_label: rx.Var | str, body: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.heading(title, size="3", color=styles.TEXT_INK),
            rx.text(count_label, font_family=styles.MONO_FAMILY, font_size="0.72rem",
                    color=styles.TEXT_MUTED),
            width="100%",
            justify="between",
            align="baseline",
        ),
        body,
        align="start",
        spacing="3",
        padding="1.35rem",
        # 넓은 화면에서는 두 패널이 나란히, 좁아지면 자연스럽게 아래로 접힌다
        flex="1 1 22rem",
        min_width="0",
        style=styles.CARD_STYLE,
    )


def report_card() -> rx.Component:
    return rx.vstack(
        rx.box(_verdict(), style=styles.CARD_STYLE, width="100%", padding="1.75rem"),
        rx.flex(
            _panel(
                "탐지된 위험 신호",
                f"{State.evidences.length()}건",
                rx.cond(
                    State.evidences.length() > 0,
                    rx.vstack(rx.foreach(State.evidences, _evidence_item),
                              width="100%", spacing="2"),
                    rx.text("알려진 위험 패턴은 발견되지 않았습니다.",
                            font_size="0.85rem", color=styles.TEXT_MUTED),
                ),
            ),
            _panel(
                "유사한 실제 사례",
                f"상위 {State.similar_cases.length()}건",
                rx.vstack(rx.foreach(State.similar_cases, _similar_case_item),
                          width="100%", spacing="2"),
            ),
            width="100%",
            gap="1rem",
            wrap="wrap",
            align="start",
        ),
        rx.vstack(
            rx.flex(
                rx.icon("triangle-alert", size=17, color=State.risk_color),
                rx.heading("지금 해야 할 일", size="3", color=styles.TEXT_INK),
                spacing="2",
                align="center",
            ),
            rx.vstack(
                rx.foreach(State.recommended_actions,
                           lambda action, index: _action_item(index, action)),
                width="100%",
                align="start",
                spacing="3",
            ),
            width="100%",
            align="start",
            spacing="3",
            padding="1.35rem",
            border_radius="15px",
            background=styles.SURFACE,
            border=f"1px solid {State.risk_color}",
        ),
        width="100%",
        spacing="4",
    )
