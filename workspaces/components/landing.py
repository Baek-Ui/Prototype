"""랜딩 페이지의 설득 구간 — 문제 제기 · 신뢰 요소 · 이용 단계 · 최종 CTA.

수치와 수상 실적은 documents/voicefishingProblem.md와 팀 실적에 근거한 것만
쓴다. 프로토타입이라도 화면에 적힌 숫자가 근거 없이 만들어지면, 정작
"근거를 함께 보여준다"는 이 서비스의 주장 자체가 무너진다.
"""

import reflex as rx

from .. import styles
from ..state import State

_SECTION_PADDING_Y = ["4.5rem", "5.5rem", "7rem"]
_CONTENT_WIDTH = ["95%", "92%", "1080px"]


def _section(anchor: str, *children: rx.Component, background: str = "transparent") -> rx.Component:
    return rx.box(
        rx.vstack(
            *children,
            width=_CONTENT_WIDTH,
            align="center",
            spacing="6",
            margin="0 auto",
        ),
        id=anchor,
        width="100%",
        padding_y=_SECTION_PADDING_Y,
        padding_x="1rem",
        background=background,
        # 고정 네비바 높이만큼 스크롤 지점을 내려 제목이 가려지지 않게 한다
        scroll_margin_top="5.5rem",
    )


def _eyebrow(text: str) -> rx.Component:
    return rx.text(
        text,
        font_size="1.43rem",
        font_weight="700",
        letter_spacing="0.12em",
        color=styles.ACCENT,
    )


def _section_heading(title: str, subtitle) -> rx.Component:
    """부제는 문자열이거나, 강조를 섞은 컴포넌트일 수 있다."""
    body = (
        rx.text(
            subtitle,
            color=styles.TEXT_MUTED,
            text_align="center",
            line_height="1.7",
            max_width="42rem",
        )
        if isinstance(subtitle, str)
        else subtitle
    )

    return rx.vstack(
        rx.heading(
            title,
            size="7",
            color=styles.TEXT_INK,
            text_align="center",
            line_height="1.4",
        ),
        body,
        align="center",
        spacing="3",
        width="100%",
    )


def _highlight(text: str) -> rx.Component:
    """연령층 이름 — 문장에서 가장 먼저 눈에 걸려야 하는 말."""
    return rx.text.strong(text, color=styles.TEXT_INK)


def _risk_term(text: str) -> rx.Component:
    """각 연령층이 실제로 당하는 수법. 연령층 이름보다 한 단계 약하게 둬서
    '누가 → 무엇에'라는 읽는 순서가 생기도록 색으로만 띄운다."""
    return rx.text.span(text, color=styles.ACCENT, font_weight="600")


def _stat_card(value: str, unit: str, label: str, note: str) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.text(
                value,
                # 이 섹션에서 가장 먼저 눈에 들어와야 하는 숫자다
                font_size=["3rem", "3.4rem", "3.8rem"],
                font_weight="700",
                line_height="1.1",
                background=styles.TEXT_GRADIENT,
                background_clip="text",
                style={
                    "-webkit-background-clip": "text",
                    "-webkit-text-fill-color": "transparent",
                },
            ),
            # 단위는 숫자를 따라 키우되 한 단계 작게 둬서 숫자가 주인공으로 남는다
            rx.text(unit, font_size="1.4rem", font_weight="600", color=styles.ACCENT),
            spacing="1",
            align="baseline",
            justify="center",
        ),
        # 줄바꿈된 문장도 가운데로 모이도록 text_align까지 함께 준다 —
        # vstack의 align만으로는 블록 위치만 맞고 안쪽 줄은 왼쪽에 남는다.
        rx.text(
            label,
            font_size="0.92rem",
            font_weight="600",
            color=styles.TEXT_INK,
            text_align="center",
        ),
        rx.text(
            note,
            font_size="0.8rem",
            color=styles.TEXT_MUTED,
            line_height="1.6",
            text_align="center",
        ),
        align="center",
        spacing="2",
        padding="1.5rem",
        flex="1 1 15rem",
        min_width="0",
        class_name="float-card",
        style=styles.CARD_STYLE,
    )


def _solution_card(icon: str, title: str, body: str) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.box(
                rx.icon(icon, size=20, color=styles.ACCENT),
                width="2.6rem",
                height="2.6rem",
                # 제목이 두 줄로 접혀도 아이콘 타일은 찌그러지지 않아야 한다
                flex="none",
                border_radius=styles.RADIUS_MD,
                display="flex",
                align_items="center",
                justify_content="center",
                background=styles.ACCENT_WASH,
                border=f"1px solid {styles.BORDER_COLOR}",
            ),
            rx.heading(title, size="4", color=styles.TEXT_INK, line_height="1.4"),
            width="100%",
            spacing="3",
            align="center",
        ),
        rx.text(body, font_size="0.88rem", color=styles.TEXT_MUTED, line_height="1.8"),
        align="start",
        spacing="3",
        padding="1.6rem",
        flex="1 1 16rem",
        min_width="0",
        class_name="float-card",
        style=styles.CARD_STYLE,
    )


def problem_solution_section() -> rx.Component:
    return _section(
        "problem",
        rx.vstack(
            _eyebrow("WHY NOW"),
            _section_heading(
                "보이스피싱은 더 이상 특정 세대의 문제가 아닙니다",
                # 줄바꿈 위치를 폭에 맡기지 않고 고정한다. spacing="0"이라
                # vstack의 기본 간격 없이 한 문단처럼 이어 읽힌다.
                rx.vstack(
                    rx.text(
                        _highlight("고령층"),
                        "은 ",
                        _risk_term("악성 앱 설치와 원격제어"),
                        "에, ",
                        _highlight("청년층"),
                        "은 ",
                        _risk_term("기관사칭·대출·스미싱"),
                        " 같은 정교한 사칭에",
                    ),
                    rx.text("노출됩니다. 연령이나 디지털 숙련도로 설명할 수 있는 문제가 아닙니다."),
                    color=styles.TEXT_MUTED,
                    text_align="center",
                    line_height="1.7",
                    spacing="0",
                    align="center",
                    width="100%",
                ),
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        rx.flex(
            _stat_card("4.4", "배", "20대 이하 피해액 증가", "2021년 52억 원 → 2023년 231억 원"),
            _stat_card("12.0", "%", "전체 피해액 중 20대 이하 비중", "2021년 3.1%에서 네 배 가까이 확대"),
            _stat_card("61.3", "%", "기관사칭형 피해자 중 20대 이하", "2024년 초 기준"),
            width="100%",
            gap="1rem",
            wrap="wrap",
            align="stretch",
        ),
        rx.text(
            "출처: 금융감독원 보이스피싱 피해 통계",
            font_size="0.74rem",
            color=styles.TEXT_FAINT,
            width="100%",
            text_align="center",
        ),
        rx.divider(border_color=styles.BORDER_COLOR, width="100%"),
        _section_heading(
            "지금의 대응은 대부분 피해가 생긴 뒤에 시작됩니다",
            "신고·지급정지·계좌동결은 모두 사후 조치입니다. 정작 필요한 건 의심 메시지를 받은 그 순간, "
            "송금 버튼을 누르기 전에 판단을 돕는 단계입니다.",
        ),
        rx.flex(
            _solution_card(
                "scan-search",
                "붙여넣기 한 번으로 즉시 판정",
                "받은 문자를 그대로 붙여넣기만 하면 됩니다. 앱 설치도, 회원가입도, 권한 허용도 필요 없습니다. "
                "연령이나 디지털 숙련도와 무관하게 쓸 수 있는 가장 단순한 입력 구조입니다.",
            ),
            _solution_card(
                "list-checks",
                "단정하지 않고 근거를 함께",
                "사기 여부를 단정하는 대신 위험 점수와 그렇게 판단한 근거를 나란히 보여줍니다. "
                "어떤 표현이 왜 걸렸는지 보이기 때문에, 오탐이 나도 사용자가 스스로 걸러낼 수 있습니다.",
            ),
            _solution_card(
                "shield-check",
                "다음에 할 일까지 안내",
                "위험 등급에 맞춰 지금 멈춰야 할 행동과 확인해야 할 공식 창구를 알려줍니다. "
                "이미 송금한 경우의 신고 경로까지 이어집니다.",
            ),
            width="100%",
            gap="1rem",
            wrap="wrap",
            align="stretch",
        ),
    )


def _trust_card(icon: str, title, body: str) -> rx.Component:
    """제목은 문자열 하나, 또는 줄바꿈 위치를 고정하고 싶을 때 문자열 목록."""
    lines = [title] if isinstance(title, str) else list(title)

    return rx.vstack(
        rx.flex(
            # 제목이 여러 줄이어도 아이콘이 눌려 찌그러지지 않게 한다
            rx.icon(icon, size=18, color=styles.ACCENT_SOFT, flex="none"),
            rx.vstack(
                *[
                    rx.heading(line, size="3", color=styles.TEXT_INK, line_height="1.5")
                    for line in lines
                ],
                spacing="0",
                align="start",
            ),
            width="100%",
            spacing="3",
            align="center",
        ),
        rx.text(body, font_size="0.85rem", color=styles.TEXT_MUTED, line_height="1.8"),
        align="start",
        spacing="3",
        padding="1.5rem",
        flex="1 1 16rem",
        min_width="0",
        class_name="float-card",
        style=styles.CARD_STYLE,
    )


def trust_section() -> rx.Component:
    return _section(
        "trust",
        rx.vstack(
            _eyebrow("TRACK RECORD"),
            _section_heading(
                "검증받고 있는 팀이 만듭니다",
                "아이디어 단계에서 멈추지 않고 외부 심사를 통과해 왔습니다.",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        rx.flex(
            _trust_card(
                "trophy",
                "학생 창업 유망팀 300+ 최종 진출",
                "전국 단위 학생 창업 경진 프로그램에서 최종 진출 팀으로 선정되었습니다.",
            ),
            _trust_card(
                "award",
                ["경북대학교 창업 아이템", "경진대회 우수상"],
                "교내 창업 아이템 경진대회에서 우수상을 수상하며 아이템의 실효성을 인정받았습니다.",
            ),
            _trust_card(
                "database",
                "공신력 있는 자료 기반 사례 DB",
                "금융감독원·경찰청·한국인터넷진흥원이 공개한 대표 수법을 참고해 사례 데이터를 구성했습니다.",
            ),
            width="100%",
            gap="1rem",
            wrap="wrap",
            align="stretch",
        ),
        rx.callout(
            "현재 화면은 프로토타입입니다. 탐지는 외부 전송 없이 브라우저 뒤 서버에서 규칙 사전과 "
            "내장 사례 데이터만으로 이뤄지며, 입력한 문구는 저장되지 않습니다.",
            icon="info",
            color_scheme="gray",
            width="100%",
        ),
        background=styles.PANEL_TRANSLUCENT,
    )


def _process_step(index: int, title: str, body: str) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.box(
                rx.text(
                    f"{index:02d}",
                    font_family=styles.MONO_FAMILY,
                    font_size="0.78rem",
                    font_weight="700",
                    color=styles.ON_ACCENT,
                ),
                width="2.2rem",
                height="2.2rem",
                flex="none",
                border_radius="9999px",
                display="flex",
                align_items="center",
                justify_content="center",
                background=styles.PRIMARY_GRADIENT,
            ),
            # 마지막 단계 뒤에는 이어질 곳이 없으므로 선을 넣지 않는다
            rx.box(
                height="1px",
                flex="1 1 auto",
                background=styles.BORDER_COLOR,
                display=["none", "none", "block"] if index < 4 else "none",
            ),
            width="100%",
            align="center",
            gap="0.75rem",
        ),
        rx.heading(title, size="3", color=styles.TEXT_INK, line_height="1.5"),
        rx.text(body, font_size="0.85rem", color=styles.TEXT_MUTED, line_height="1.8"),
        align="start",
        spacing="3",
        flex="1 1 13rem",
        min_width="0",
    )


def process_section() -> rx.Component:
    return _section(
        "process",
        rx.vstack(
            _eyebrow("HOW IT WORKS"),
            _section_heading(
                "네 단계, 5초면 끝납니다",
                "화면 위 진행 표시가 아니라 실제 탐지 파이프라인 그대로입니다.",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        rx.flex(
            _process_step(
                1,
                "문구 붙여넣기",
                "받은 문자나 메신저 메시지를 그대로 붙여넣습니다. 전화번호·계좌번호·링크는 자동으로 가려집니다.",
            ),
            _process_step(
                2,
                "벡터로 변환",
                "문구를 64차원 벡터로 바꿔 위험 신호 사전, 실제 사기 사례와 같은 공간에 놓습니다.",
            ),
            _process_step(
                3,
                "규칙 대조와 사례 검색",
                "16개 위험 신호 규칙을 대조하고, 축적된 실제 사례 중 가장 가까운 3건을 찾아냅니다.",
            ),
            _process_step(
                4,
                "위험도 리포트",
                "위험 점수와 함께 걸린 표현, 닮은 사례, 지금 해야 할 일을 한 화면에 정리해 드립니다.",
            ),
            width="100%",
            gap="1.75rem",
            wrap="wrap",
            align="start",
        ),
    )


def final_cta_section() -> rx.Component:
    return _section(
        "cta",
        rx.vstack(
            rx.flex(
                rx.icon("triangle-alert", size=16, color=styles.RISK_COLORS["위험"]),
                rx.text(
                    "지금 망설이는 그 문자가, 판단할 시간을 주지 않으려고 쓰인 것일 수 있습니다",
                    font_size="0.85rem",
                    font_weight="600",
                    color=styles.RISK_COLORS["위험"],
                    line_height="1.6",
                ),
                spacing="2",
                align="center",
                justify="center",
                wrap="wrap",
                padding="0.5rem 1.1rem",
                border_radius="9999px",
                border=f"1px solid {styles.DANGER_BORDER}",
                background=styles.DANGER_WASH,
            ),
            rx.heading(
                "송금 버튼을 누르기 전 30초",
                size="8",
                color=styles.TEXT_INK,
                text_align="center",
                line_height="1.35",
            ),
            rx.text(
                "한 번 보낸 돈은 되돌리기 어렵습니다. 확인은 지금이 가장 쌉니다.",
                color=styles.TEXT_MUTED,
                text_align="center",
                line_height="1.7",
            ),
            rx.button(
                "문구 검사하러 가기",
                rx.icon("arrow-up", size=18),
                background=styles.PRIMARY_GRADIENT,
                color=styles.ON_ACCENT,
                border_radius=styles.RADIUS_FULL,
                padding_x="2rem",
                height="3rem",
                font_size="1rem",
                cursor="pointer",
                margin_top="0.75rem",
                on_click=State.focus_input,
                transition=styles.HOVER_TRANSITION,
                _hover={"filter": "brightness(1.08)", "transform": "translateY(-2px)"},
            ),
            rx.text(
                "이미 송금하셨다면 지체 없이 은행 1332 또는 경찰 112로 신고하세요.",
                font_size="0.8rem",
                color=styles.TEXT_MUTED,
                text_align="center",
                margin_top="0.5rem",
            ),
            align="center",
            spacing="4",
            width="100%",
        ),
    )
