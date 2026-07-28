import reflex as rx

from .. import styles
from ..state import State


def _theme_toggle() -> rx.Component:
    """라이트/다크 전환. 프론트의 색은 CSS 변수가 알아서 바뀌지만 Plotly
    그래프는 서버가 다시 만들어야 하므로 State를 거쳐 둘을 함께 뒤집는다."""
    return rx.button(
        rx.cond(
            State.is_dark,
            rx.icon("sun", size=18),
            rx.icon("moon", size=18),
        ),
        aria_label=rx.cond(State.is_dark, "라이트 모드로 전환", "다크 모드로 전환"),
        variant="ghost",
        color=styles.TEXT_MUTED,
        cursor="pointer",
        padding="0.5rem",
        border_radius="9999px",
        # 프론트(실제 색 전환)와 백엔드(Plotly 팔레트)를 나란히 돌린다.
        on_click=[rx.toggle_color_mode, State.flip_theme],
        transition=styles.HOVER_TRANSITION,
        _hover={"color": styles.TEXT_INK, "background": styles.SUBTLE_FILL},
    )


def _nav_link(label: str, anchor: str) -> rx.Component:
    return rx.link(
        label,
        href=f"#{anchor}",
        color=styles.TEXT_MUTED,
        text_decoration="none",
        transition=styles.HOVER_TRANSITION,
        _hover={"color": styles.TEXT_INK},
    )


def navbar() -> rx.Component:
    return rx.flex(
        rx.image(
            # 원본 baek_ui_logo.png는 500x500 정사각형인데 실제 글자는 세로
            # 22.8%뿐이라, 높이를 키워도 로고는 그대로 작아 보였다. 투명
            # 여백을 잘라낸 387x114(비율 3.39) 판을 쓴다 — 지정한 높이가
            # 곧 글자 높이가 된다.
            src="/baek_ui_logo_trimmed.png",
            alt="Baek-ui 백의",
            # 워드마크가 짙은 남보라 단색이라 다크에서는 그대로 두면 묻힌다.
            # 밝기 보정은 assets/styles.css의 .brand-logo가 담당한다.
            class_name="brand-logo",
            height=["1.9rem", "2.1rem", "2.4rem"],
            width="auto",
            flex="none",
            cursor="pointer",
            # 페이지를 다시 부르지 않고 히어로로 미끄러져 올라간다. redirect는
            # 새로고침이라 입력해 둔 문구와 분석 결과가 날아간다.
            on_click=rx.scroll_to("hero"),
        ),
        rx.flex(
            rx.flex(
                # 페이지에 놓인 순서(problem → trust → process)와 같게 둔다.
                # 메뉴가 실제 스크롤 순서와 어긋나면 클릭할 때마다 위아래로
                # 튀는 것처럼 느껴진다.
                _nav_link("문제 인식", "problem"),
                _nav_link("팀 실적", "trust"),
                _nav_link("탐지 원리", "process"),
                # Radix 간격 척도(spacing="6" = 2rem) 대신 값을 직접 준다 —
                # 척도는 단계가 듬성해서 50%씩 정확히 늘릴 수가 없다.
                gap="5.1rem",
                align="center",
                # 좁은 화면에서는 섹션 링크만 접고 테마 버튼은 남긴다
                display=["none", "none", "flex"],
            ),
            _theme_toggle(),
            gap="3.83rem",
            align="center",
        ),
        width="100%",
        # 로고와 메뉴를 화면 양끝으로 벌리지 않고 가운데에 한 덩어리로 모은다
        justify="center",
        align="center",
        gap=["3.83rem", "5.1rem", "7.65rem"],
        wrap="wrap",
        padding_x=["1.5rem", "2rem", "4rem"],
        # 로고 2.4rem + 상하 여백 = 약 4.6rem. 아래 앵커들의
        # scroll_margin_top(5.5rem)이 이보다 커야 제목이 가려지지 않는다.
        padding_y="1.1rem",
        position="fixed",
        top="0",
        z_index="100",
        # 반투명 바탕 + 하단 경계선이 스크롤 시 내용과 겹치지 않게 막아준다
        background=styles.NAVBAR_BG,
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
