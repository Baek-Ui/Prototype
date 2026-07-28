import reflex as rx

from .. import styles
from ..state import State

_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": True,
    "responsive": True,
}


def vector_graph() -> rx.Component:
    """입력 문구가 규칙·사례와 이어지는 과정을 보여주는 3D 벡터 그래프."""
    return rx.vstack(
        rx.flex(
            rx.vstack(
                rx.heading("벡터 공간 대조", size="3", color=styles.TEXT_INK),
                rx.text(
                    "입력한 문구를 64차원 벡터로 바꿔 위험 신호 사전 16개, 실제 사례 25건과 나란히 놓았습니다. "
                    "드래그하면 돌려볼 수 있습니다.",
                    font_size="0.82rem",
                    color=styles.TEXT_MUTED,
                    line_height="1.6",
                ),
                align="start",
                spacing="1",
                flex="1 1 18rem",
                min_width="0",
            ),
            rx.text(
                "좌표는 3개 주성분에 투영한 배치이고, 선은 실제 규칙 매칭과 코사인 유사도로만 긋습니다.",
                font_size="0.72rem",
                color=styles.TEXT_FAINT,
                line_height="1.6",
                flex="1 1 14rem",
                min_width="0",
                text_align=["left", "left", "right"],
            ),
            width="100%",
            gap="1rem",
            wrap="wrap",
            align="start",
        ),
        rx.box(
            rx.plotly(
                data=State.graph_figure,
                config=_CONFIG,
                width="100%",
                height="100%",
            ),
            width="100%",
            height=["20rem", "24rem", "28rem"],
            # rx.box는 Radix 컴포넌트가 아니라 border_radius="full"이 먹지 않는다.
            border_radius=styles.RADIUS_MD,
            overflow="hidden",
            background=styles.GRAPH_WASH,
            border=f"1px solid {styles.BORDER_COLOR}",
        ),
        width="100%",
        align="start",
        spacing="3",
        padding="1.35rem",
        style=styles.CARD_STYLE,
    )
