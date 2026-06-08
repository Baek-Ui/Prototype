import reflex as rx
from typing import Optional, List
from dataclasses import dataclass
from .domain import AnalysisStatus, AnalysisReport
from .infrastructure import AIPipelineService
from .usecases import AnalyzeVideoUseCase
from . import styles

@dataclass
class FactCheckItem:
    claim: str
    is_true: bool
    evidence: str
    source: str

@dataclass
class ReportData:
    title: str
    platform: str
    url: str
    upload_date: str
    deepfake_score: float
    audio_spoofing_score: float
    fact_check_results: List[FactCheckItem]
    summary: str

@dataclass
class ChatMessage:
    role: str
    content: str
    is_loading: bool = False
    report: Optional[ReportData] = None

class State(rx.State):
    url: str = ""
    is_analyzing: bool = False
    chat_history: List[ChatMessage] = [
        ChatMessage(
            role="assistant",
            content="안녕하세요! 백의(Baek-ui) AI 미디어 무결성 정밀 분석 에이전트입니다. 팩트 체크 및 딥페이크 검증을 원하시는 유튜브 비디오 URL을 입력해 주시면 정밀 분석해 드리겠습니다.",
            report=None,
            is_loading=False
        )
    ]

    def set_url(self, url: str):
        self.url = url

    async def start_analysis(self):
        if not self.url:
            yield rx.window_alert("URL을 입력해주세요.")
            return
            
        current_url = self.url
        self.url = ""
        self.is_analyzing = True
        
        # 1. Append User Message
        self.chat_history.append(
            ChatMessage(
                role="user",
                content=current_url,
                report=None,
                is_loading=False
            )
        )
        
        # 2. Append Assistant Loading Message
        self.chat_history.append(
            ChatMessage(
                role="assistant",
                content="비디오 매칭을 준비하는 중...",
                report=None,
                is_loading=True
            )
        )
        self.chat_history = list(self.chat_history)
        
        # Redirect to the chat page immediately
        yield rx.redirect("/chat")
        yield
        
        # Dependency Injection
        ai_service = AIPipelineService()
        use_case = AnalyzeVideoUseCase(ai_service)
        
        try:
            async for status in use_case.execute(current_url):
                # Update assistant message content during steps
                self.chat_history[-1].content = f"진행 상황: {status.value}"
                self.chat_history = list(self.chat_history)
                yield
            
            report = use_case.last_report
            
            # Serialize the report to strongly typed ReportData
            report_data = ReportData(
                title=report.video.title,
                platform=report.video.platform,
                url=report.video.url,
                upload_date=report.video.upload_date,
                deepfake_score=int(report.deepfake_score * 100) if (report.deepfake_score * 100).is_integer() else round(report.deepfake_score * 100, 2),
                audio_spoofing_score=int(report.audio_spoofing_score * 100) if (report.audio_spoofing_score * 100).is_integer() else round(report.audio_spoofing_score * 100, 2),
                fact_check_results=[
                    FactCheckItem(
                        claim=f.claim,
                        is_true=f.is_true,
                        evidence=f.evidence,
                        source=f.source
                    ) for f in report.fact_check_results
                ],
                summary=report.summary
            )
            
            self.chat_history[-1].is_loading = False
            self.chat_history[-1].content = "분석이 완료되었습니다! 신뢰도 지표와 교차 팩트 체크 테이블을 실시간 연동하여 공유해 드립니다."
            self.chat_history[-1].report = report_data
            self.chat_history = list(self.chat_history)
            yield
            
        except Exception as e:
            self.chat_history[-1].is_loading = False
            self.chat_history[-1].content = f"오류가 발생했습니다: {str(e)}"
            self.chat_history = list(self.chat_history)
            yield
        finally:
            self.is_analyzing = False
            yield

def navbar() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.box(
                rx.image(src="/baek_ui_logo.png", width="160px", height="auto"),
                height="50px",
                overflow="hidden",
                display="flex",
                align_items="center",
                justify_content="center",
                cursor="pointer",
                on_click=rx.redirect("/"),
            ),
            align="center",
        ),
        rx.flex(
            rx.link("Features", href="#", color=styles.TEXT_GRAY, _hover={"color": styles.TEXT_WHITE}),
            rx.link("Technology", href="#", color=styles.TEXT_GRAY, _hover={"color": styles.TEXT_WHITE}),
            rx.link("API Documentation", href="#", color=styles.TEXT_GRAY, _hover={"color": styles.TEXT_WHITE}),
            rx.link("Pricing", href="#", color=styles.TEXT_GRAY, _hover={"color": styles.TEXT_WHITE}),
            spacing="6",
            display=["none", "none", "flex"],
        ),
        rx.flex(
            rx.button("Sign In", variant="ghost", color=styles.TEXT_WHITE),
            rx.button("Get Started", background=styles.PRIMARY_GRADIENT, color="white", border_radius="full", on_click=rx.redirect("/chat")),
            spacing="4",
        ),
        width="100%",
        justify="between",
        align="center",
        padding_x="4rem",
        padding_y="1.5rem",
        position="fixed",
        top="0",
        z_index="100",
        background="rgba(11, 14, 20, 0.8)",
        backdrop_filter="blur(10px)",
    )

def chat_navbar() -> rx.Component:
    return rx.flex(
        rx.button(
            rx.icon("chevron_left", size=18),
            "메인 페이지로 돌아가기",
            variant="ghost",
            color=styles.TEXT_WHITE,
            cursor="pointer",
            on_click=rx.redirect("/"),
            _hover={"color": styles.ACCENT_PURPLE, "background": "rgba(255, 255, 255, 0.05)"},
            border_radius="full",
            padding_x="1rem",
        ),
        width="100%",
        justify="start",
        align="center",
        padding_x="4rem",
        padding_y="1.5rem",
        position="fixed",
        top="0",
        z_index="100",
        background="rgba(11, 14, 20, 0.8)",
        backdrop_filter="blur(10px)",
    )

def render_report_card(report: ReportData) -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.flex(
                rx.vstack(
                    rx.heading("영상 신뢰도 검증 리포트", size="4", color=styles.TEXT_WHITE),
                    rx.text("비디오 제목: ", report.title, color=styles.TEXT_GRAY, font_size="0.85rem"),
                    rx.text("플랫폼: ", report.platform, " | 게시일자: ", report.upload_date, color=styles.TEXT_GRAY, font_size="0.8rem"),
                    align="start",
                    spacing="1",
                ),
                rx.badge("검증 완료", color_scheme="green", variant="surface"),
                width="100%",
                justify="between",
                align="center",
            ),
            rx.divider(margin_y="1rem", border_color=styles.BORDER_COLOR),
            rx.grid(
                rx.vstack(
                    rx.text("중립성 점수", color=styles.TEXT_GRAY, font_size="0.85rem"),
                    rx.heading(report.deepfake_score.to(str), "점", color=styles.ACCENT_PURPLE, size="5"),
                    align="center",
                ),
                rx.vstack(
                    rx.text("맥락 보존율", color=styles.TEXT_GRAY, font_size="0.85rem"),
                    rx.heading(report.audio_spoofing_score.to(str), "%", color=styles.ACCENT_BLUE, size="5"),
                    align="center",
                ),
                columns="2",
                width="100%",
                margin_bottom="1.5rem",
            ),
            rx.vstack(
                rx.heading("교차 팩트 체크 테이블 (정부24 연동)", size="2", color=styles.TEXT_WHITE, margin_bottom="0.5rem"),
                rx.foreach(
                    report.fact_check_results,
                    lambda f: rx.box(
                        rx.flex(
                            rx.box(
                                rx.icon(
                                    rx.cond(f.is_true, "shield-check", "circle-alert"),
                                    color=rx.cond(f.is_true, "green", "red"),
                                    size=16,
                                ),
                                margin_top="0.2rem",
                            ),
                            rx.vstack(
                                rx.flex(
                                    rx.text(f.claim, font_weight="bold", color=styles.TEXT_WHITE, font_size="0.85rem"),
                                    rx.badge(f.source, color_scheme="blue", size="1"),
                                    spacing="2",
                                    align="center",
                                ),
                                rx.text(f.evidence, font_size="0.78rem", color=styles.TEXT_GRAY),
                                align="start",
                                spacing="1",
                            ),
                            spacing="3",
                            align="start",
                        ),
                        padding="0.75rem 1rem",
                        border_radius="8px",
                        background_color="rgba(255, 255, 255, 0.02)",
                        border=f"1px solid {styles.BORDER_COLOR}",
                        width="100%",
                    )
                ),
                width="100%",
                align="start",
                spacing="2",
            ),
            rx.box(
                rx.text(report.summary, color=styles.TEXT_WHITE, font_size="0.85rem", font_weight="500"),
                background="linear-gradient(90deg, rgba(138, 112, 255, 0.1) 0%, rgba(77, 139, 255, 0.1) 100%)",
                border="1px solid rgba(138, 112, 255, 0.2)",
                padding="1rem",
                border_radius="10px",
                margin_top="1rem",
                width="100%",
            ),
            style=styles.GLASS_STYLE,
            padding="1.5rem",
            width="100%",
            border_radius="16px",
            box_shadow="0 4px 30px rgba(0, 0, 0, 0.3)",
        ),
        width="100%",
        align="start",
        margin_top="0.5rem",
    )

def render_message(message: ChatMessage) -> rx.Component:
    return rx.box(
        rx.flex(
            # Assistant Avatar / Icon
            rx.cond(
                message.role == "assistant",
                rx.image(
                    src="/baek_ui_symbol.png",
                    width="32px",
                    height="32px",
                    border_radius="none",
                    margin_top="4px",
                ),
            ),
            # Message Bubble Wrapper
            rx.vstack(
                # Message text content
                rx.box(
                    rx.text(
                        message.content,
                        color=styles.TEXT_WHITE,
                        font_size="0.95rem",
                        line_height="1.5",
                    ),
                    padding="1rem 1.25rem",
                    border_radius="18px",
                    background_color=rx.cond(
                        message.role == "user",
                        "rgba(138, 112, 255, 0.15)",  # User: Glass purple
                        "rgba(255, 255, 255, 0.04)"   # Assistant: Glass grey
                    ),
                    border=rx.cond(
                        message.role == "user",
                        "1px solid rgba(138, 112, 255, 0.3)",
                        f"1px solid {styles.BORDER_COLOR}"
                    ),
                    backdrop_filter="blur(10px)",
                    max_width="85%",
                ),
                # Spinner for loading state
                rx.cond(
                    message.is_loading,
                    rx.flex(
                        rx.spinner(size="1", color=styles.ACCENT_PURPLE),
                        rx.text("AI가 실시간 팩트 DB를 확인하고 있습니다...", color=styles.TEXT_GRAY, font_size="0.75rem"),
                        spacing="2",
                        align="center",
                        margin_left="0.5rem",
                    ),
                ),
                # Report Card if report is ready inside assistant message bubble
                rx.cond(
                    message.report,
                    render_report_card(message.report),
                ),
                align=rx.cond(
                    message.role == "user",
                    "end",
                    "start"
                ),
                spacing="2",
                width="100%",
            ),
            # User Avatar / Icon
            rx.cond(
                message.role == "user",
                rx.avatar(
                    fallback="ME",
                    color_scheme="gray",
                    radius="full",
                    size="2",
                ),
            ),
            spacing="3",
            width="100%",
            justify=rx.cond(
                message.role == "user",
                "end",
                "start"
            ),
            align="start",
        ),
        margin_bottom="1.5rem",
        width="100%",
    )

def chat_section() -> rx.Component:
    return rx.vstack(
        # Unified Glassmorphic Chat Console (Chat History + Input combined)
        rx.box(
            rx.vstack(
                # Internal Top Row: Integrated Back Button
                rx.flex(
                    rx.button(
                        rx.icon("chevron_left", size=18),
                        "메인 페이지로 돌아가기",
                        variant="ghost",
                        color=styles.TEXT_WHITE,
                        cursor="pointer",
                        on_click=rx.redirect("/"),
                        _hover={"color": styles.ACCENT_PURPLE, "background": "rgba(255, 255, 255, 0.05)"},
                        border_radius="full",
                        padding_x="1rem",
                        height="2.25rem",
                    ),
                    width="100%",
                    padding="0.75rem 1.25rem",
                    border_bottom="1px solid rgba(255, 255, 255, 0.06)",
                    justify="start",
                    align="center",
                ),
                # Top part: Scroll area with message logs
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            State.chat_history,
                            render_message
                        ),
                        width="100%",
                        padding="1.5rem",
                    ),
                    width="100%",
                    height="600px",
                    scrollbars="vertical",
                ),
                # Thin divider inside
                rx.box(width="100%", border_top="1px solid rgba(255, 255, 255, 0.08)"),
                # Bottom part: Text input layout (transparent background to match unified console)
                rx.vstack(
                    # Top Row: Search Icon + Input
                    rx.flex(
                        rx.icon("search", size=20, color=styles.TEXT_GRAY, margin_top="0.75rem", margin_left="0.5rem"),
                        rx.input(
                            placeholder="분석할 유튜브 비디오 URL을 입력하고 전송해 보세요...",
                            value=State.url,
                            on_change=State.set_url,
                            variant="soft",
                            width="100%",
                            background="transparent",
                            text_color=styles.TEXT_WHITE,
                            _placeholder={"color": "rgba(255, 255, 255, 0.5)"},
                            border="none",
                            _focus={"box_shadow": "none"},
                            height="3rem",
                        ),
                        align="start",
                        width="100%",
                        spacing="3",
                    ),
                    # Bottom Row: Badges (left) and Action Button (right)
                    rx.flex(
                        # Left side: Badges
                        rx.flex(
                            rx.button(
                                rx.icon("sparkles", size=14, color=styles.ACCENT_PURPLE),
                                "Fast Analysis",
                                variant="outline",
                                size="1",
                                cursor="pointer",
                                background="rgba(255, 255, 255, 0.05)",
                                backdrop_filter="blur(10px)",
                                border="1px solid rgba(255, 255, 255, 0.1)",
                                border_radius="12px",
                                padding="0.5rem 1rem",
                                height="auto",
                                text_align="center",
                                line_height="1",
                                color=styles.TEXT_GRAY,
                                _hover={
                                    "background": "rgba(255, 255, 255, 0.08)",
                                    "color": styles.TEXT_WHITE,
                                    "border_color": styles.ACCENT_PURPLE,
                                },
                            ),
                            rx.button(
                                rx.icon("database", size=14, color=styles.ACCENT_BLUE),
                                "Historical Data",
                                variant="outline",
                                size="1",
                                cursor="pointer",
                                background="rgba(255, 255, 255, 0.05)",
                                backdrop_filter="blur(10px)",
                                border="1px solid rgba(255, 255, 255, 0.1)",
                                border_radius="12px",
                                padding="0.5rem 1rem",
                                height="auto",
                                text_align="center",
                                line_height="1",
                                color=styles.TEXT_GRAY,
                                _hover={
                                    "background": "rgba(255, 255, 255, 0.08)",
                                    "color": styles.TEXT_WHITE,
                                    "border_color": styles.ACCENT_BLUE,
                                },
                            ),
                            spacing="2",
                        ),
                        # Right side: Run/Search Button
                        rx.button(
                            rx.icon("arrow_right", size=20),
                            on_click=State.start_analysis,
                            background=styles.PRIMARY_GRADIENT,
                            color="white",
                            radius="full",
                            width="2.75rem",
                            height="2.75rem",
                            loading=State.is_analyzing,
                        ),
                        width="100%",
                        justify="between",
                        align="center",
                        padding_top="0.5rem",
                    ),
                    width="100%",
                    spacing="3",
                    padding="1.25rem",
                ),
                width="100%",
                spacing="0",
            ),
            style=styles.GLASS_STYLE,
            width=["95%", "95%", "950px"],
            border_radius="28px",
            box_shadow="0 15px 50px rgba(0, 0, 0, 0.5)",
            border="1px solid rgba(255, 255, 255, 0.08)",
            overflow="hidden",
        ),
        width="100%",
        align="center",
        padding_top="2.5rem",
        padding_bottom="3rem",
    )

def landing_hero_section() -> rx.Component:
    return rx.vstack(
        # Page Title Header
        rx.vstack(
            rx.heading(
                "진짜 맥락을 찾아내는",
                size="9",
                color=styles.TEXT_WHITE,
                text_align="center",
                line_height="1.3",
                letter_spacing="-0.02em",
            ),
            rx.heading(
                "가장 완벽한 방법",
                size="9",
                color=styles.ACCENT_PURPLE,
                text_align="center",
                line_height="1.3",
                letter_spacing="-0.02em",
            ),
            spacing="3",
            align="center",
            padding_top="8rem",
            padding_bottom="3rem",
        ),
        # Input box
        rx.box(
            rx.vstack(
                # Top Row: Search Icon + Input
                rx.flex(
                    rx.icon("search", size=20, color=styles.TEXT_GRAY, margin_top="0.75rem", margin_left="0.5rem"),
                    rx.input(
                        placeholder="분석할 유튜브 비디오 URL을 입력해 보세요...",
                        value=State.url,
                        on_change=State.set_url,
                        variant="soft",
                        width="100%",
                        background="transparent",
                        text_color=styles.TEXT_WHITE,
                        _placeholder={"color": "rgba(255, 255, 255, 0.5)"},
                        border="none",
                        _focus={"box_shadow": "none"},
                        height="3rem",
                    ),
                    align="start",
                    width="100%",
                    spacing="3",
                ),
                # Bottom Row: Badges (left) and Action Button (right)
                rx.flex(
                    # Left side: Badges
                    rx.flex(
                        rx.button(
                            rx.icon("sparkles", size=14, color=styles.ACCENT_PURPLE),
                            "Fast Analysis",
                            variant="outline",
                            size="1",
                            cursor="pointer",
                            background="rgba(255, 255, 255, 0.05)",
                            backdrop_filter="blur(10px)",
                            border="1px solid rgba(255, 255, 255, 0.1)",
                            border_radius="12px",
                            padding="0.5rem 1rem",
                            height="auto",
                            text_align="center",
                            line_height="1",
                            color=styles.TEXT_GRAY,
                            _hover={
                                "background": "rgba(255, 255, 255, 0.08)",
                                "color": styles.TEXT_WHITE,
                                "border_color": styles.ACCENT_PURPLE,
                            },
                        ),
                        rx.button(
                            rx.icon("database", size=14, color=styles.ACCENT_BLUE),
                            "Historical Data",
                            variant="outline",
                            size="1",
                            cursor="pointer",
                            background="rgba(255, 255, 255, 0.05)",
                            backdrop_filter="blur(10px)",
                            border="1px solid rgba(255, 255, 255, 0.1)",
                            border_radius="12px",
                            padding="0.5rem 1rem",
                            height="auto",
                            text_align="center",
                            line_height="1",
                            color=styles.TEXT_GRAY,
                            _hover={
                                "background": "rgba(255, 255, 255, 0.08)",
                                "color": styles.TEXT_WHITE,
                                "border_color": styles.ACCENT_BLUE,
                            },
                        ),
                        spacing="2",
                    ),
                    # Right side: Run/Search Button
                    rx.button(
                        rx.icon("arrow_right", size=20),
                        on_click=State.start_analysis,
                        background=styles.PRIMARY_GRADIENT,
                        color="white",
                        radius="full",
                        width="2.75rem",
                        height="2.75rem",
                        loading=State.is_analyzing,
                    ),
                    width="100%",
                    justify="between",
                    align="center",
                    padding_top="0.5rem",
                ),
                width="100%",
                spacing="3",
                padding="1rem",
            ),
            style=styles.GLASS_STYLE,
            width=["95%", "90%", "600px"],
            box_shadow="0 0 30px rgba(138, 112, 255, 0.2)",
            border_radius="24px",
        ),
        # Pinned suggestion tags
        rx.flex(
            rx.text(
                "Deepfake Detection",
                color=styles.TEXT_GRAY,
                font_size="0.85rem",
                font_weight="500",
                display="inline-block",
                text_align="center",
                line_height="1",
                backdrop_filter="blur(10px)",
                background_color="rgba(255, 255, 255, 0.05)",
                border=f"1px solid {styles.BORDER_COLOR}",
                padding="0.5rem 1.25rem",
                border_radius="12px",
                cursor="pointer",
                transition=styles.HOVER_TRANSITION,
                _hover={
                    "border_color": styles.ACCENT_PURPLE,
                    "background_color": "rgba(255, 255, 255, 0.08)",
                    "color": styles.TEXT_WHITE,
                    "transform": "translateY(-1px)",
                },
            ),
            rx.text(
                "Audio Spoofing",
                color=styles.TEXT_GRAY,
                font_size="0.85rem",
                font_weight="500",
                display="inline-block",
                text_align="center",
                line_height="1",
                backdrop_filter="blur(10px)",
                background_color="rgba(255, 255, 255, 0.05)",
                border=f"1px solid {styles.BORDER_COLOR}",
                padding="0.5rem 1.25rem",
                border_radius="12px",
                cursor="pointer",
                transition=styles.HOVER_TRANSITION,
                _hover={
                    "border_color": styles.ACCENT_PURPLE,
                    "background_color": "rgba(255, 255, 255, 0.08)",
                    "color": styles.TEXT_WHITE,
                    "transform": "translateY(-1px)",
                },
            ),
            rx.text(
                "Fact Checking",
                color=styles.TEXT_GRAY,
                font_size="0.85rem",
                font_weight="500",
                display="inline-block",
                text_align="center",
                line_height="1",
                backdrop_filter="blur(10px)",
                background_color="rgba(255, 255, 255, 0.05)",
                border=f"1px solid {styles.BORDER_COLOR}",
                padding="0.5rem 1.25rem",
                border_radius="12px",
                cursor="pointer",
                transition=styles.HOVER_TRANSITION,
                _hover={
                    "border_color": styles.ACCENT_PURPLE,
                    "background_color": "rgba(255, 255, 255, 0.08)",
                    "color": styles.TEXT_WHITE,
                    "transform": "translateY(-1px)",
                },
            ),
            rx.text(
                "Metadata Integrity",
                color=styles.TEXT_GRAY,
                font_size="0.85rem",
                font_weight="500",
                display="inline-block",
                text_align="center",
                line_height="1",
                backdrop_filter="blur(10px)",
                background_color="rgba(255, 255, 255, 0.05)",
                border=f"1px solid {styles.BORDER_COLOR}",
                padding="0.5rem 1.25rem",
                border_radius="12px",
                cursor="pointer",
                transition=styles.HOVER_TRANSITION,
                _hover={
                    "border_color": styles.ACCENT_PURPLE,
                    "background_color": "rgba(255, 255, 255, 0.08)",
                    "color": styles.TEXT_WHITE,
                    "transform": "translateY(-1px)",
                },
            ),
            spacing="3",
            margin_top="2rem",
            flex_wrap="wrap",
            justify="center",
        ),
        width="100%",
        align="center",
        padding_top="2rem",
        padding_bottom="3rem",
    )

def tech_card(icon: str, title: str, description: str) -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.icon(icon, size=30, color=styles.ACCENT_BLUE),
            background="rgba(77, 139, 255, 0.1)",
            padding="1rem",
            border_radius="xl",
        ),
        rx.heading(title, size="4", color=styles.TEXT_WHITE),
        rx.text(description, color=styles.TEXT_GRAY, font_size="0.9rem", line_height="1.5"),
        style=styles.GLASS_STYLE,
        padding="2rem",
        align="start",
        width="100%",
        height="100%",
        transition=styles.HOVER_TRANSITION,
        _hover={"transform": "translateY(-5px)", "border_color": styles.ACCENT_PURPLE},
    )

def tech_section() -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.vstack(
                rx.text("CORE TECHNOLOGY", color=styles.ACCENT_PURPLE, letter_spacing="2px", font_size="0.7rem", font_weight="bold"),
                rx.heading("강력한 멀티모달 AI가 영상의 모든 구성을 정밀 분석합니다.", size="6", color=styles.TEXT_WHITE, max_width="400px"),
                align="start",
            ),
            rx.text(
                "비주얼, 오디오, 텍스트 컨텍스트를 동시에 처리하여 고도화된 가짜 정보와 조작된 미디어를 정확히 식별합니다.",
                color=styles.TEXT_GRAY,
                max_width="400px",
            ),
            width="100%",
            justify="between",
            align="end",
            margin_bottom="3rem",
        ),
        rx.grid(
            tech_card("video", "프레임 정밀 분석", "픽셀 단위의 미세한 왜곡과 딥페이크 아티팩트를 실시간으로 탐지하여 영상 변조 여부를 확인합니다."),
            tech_card("mic", "음성 위조 탐지", "AI로 생성된 가짜 목소리나 변조된 오디오 주파수 패턴을 분석하여 신뢰도를 측정합니다."),
            tech_card("file-text", "메타데이터 검증", "파일 헤더부터 촬영 기기 정보, 게시 이력까지 모든 디지털 발자국을 추적하여 무결성을 보장합니다."),
            columns={"initial": "1", "sm": "1", "md": "3"},
            spacing="6",
            width="100%",
        ),
        width="100%",
        padding_x="4rem",
        padding_y="6rem",
    )

def footer() -> rx.Component:
    return rx.vstack(
        rx.divider(border_color=styles.BORDER_COLOR),
        rx.flex(
            rx.vstack(
                rx.heading("백의", size="4", color=styles.TEXT_WHITE),
                rx.text("© 2024 Baek-ui AI. Protecting digital integrity with advanced multimodal learning.", color=styles.TEXT_GRAY, font_size="0.8rem", max_width="300px"),
                align="start",
            ),
            rx.flex(
                rx.link("Features", color=styles.TEXT_GRAY),
                rx.link("Technology", color=styles.TEXT_GRAY),
                rx.link("API Documentation", color=styles.TEXT_GRAY),
                rx.link("Privacy Policy", color=styles.TEXT_GRAY),
                spacing="6",
                font_size="0.9rem",
            ),
            width="100%",
            justify="between",
            padding_y="3rem",
        ),
        width="100%",
        padding_x="4rem",
    )

def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.scroll_area(
            rx.vstack(
                landing_hero_section(),
                tech_section(),
                footer(),
                width="100%",
                spacing="0",
            ),
            width="100%",
            height="100vh",
        ),
        background=styles.BG_DARK,
        min_height="100vh",
        font_family=styles.FONT_FAMILY,
    )

def chat_page() -> rx.Component:
    return rx.box(
        rx.scroll_area(
            rx.vstack(
                chat_section(),
                footer(),
                width="100%",
                spacing="0",
            ),
            width="100%",
            height="100vh",
        ),
        background=styles.BG_DARK,
        min_height="100vh",
        font_family=styles.FONT_FAMILY,
    )

app = rx.App(
    stylesheets=[
        "styles.css",
    ],
)
app.add_page(index)
app.add_page(chat_page, route="/chat")
