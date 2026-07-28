from dataclasses import dataclass
from typing import List

import plotly.graph_objects as go
import reflex as rx

from . import styles
from .domain import DetectionStatus, TextHighlight, VectorGraph
from .figure import build_figure, empty_figure
from .repository import MockPhishingRepository
from .rules import RULES
from .usecases import DetectPhishingUseCase

_STEP_INDEX = {
    DetectionStatus.PREPROCESSING: 0,
    DetectionStatus.VECTORIZING: 1,
    DetectionStatus.RULE_SCORING: 2,
    DetectionStatus.SIMILARITY_SEARCH: 3,
    DetectionStatus.JUDGING: 4,
    DetectionStatus.COMPLETED: 5,
}

# 분석 결과가 열리는 자리. detect가 끝나기를 기다리지 않고 바로 스크롤한다.
ANALYSIS_ANCHOR = "analysis"
INPUT_ANCHOR = "input-panel"

TOTAL_RULE_COUNT = len(RULES)


# Reflex state var로 쓰려면 도메인 객체가 아니라 평범한 dataclass여야 한다
# (rx.Base는 0.9에서 제거됨).
@dataclass
class EvidenceView:
    keyword: str
    description: str
    weight: int


@dataclass
class SimilarCaseView:
    text: str
    category: str
    similarity_percent: int
    is_phishing: bool


@dataclass
class TextSegmentView:
    """마스킹된 입력을 부각 구간 기준으로 자른 조각."""

    text: str
    keyword: str
    is_flagged: bool


def _to_segments(text: str, highlights: List[TextHighlight]) -> List[TextSegmentView]:
    """겹치지 않는 부각 구간을 기준으로 문구를 조각낸다.

    detector.find_highlights가 비중첩·오름차순을 보장하므로 커서를 앞으로만
    옮기면 된다.
    """
    segments: List[TextSegmentView] = []
    cursor = 0

    for highlight in highlights:
        if highlight.start > cursor:
            segments.append(TextSegmentView(text[cursor : highlight.start], "", False))
        segments.append(
            TextSegmentView(text[highlight.start : highlight.end], highlight.keyword, True)
        )
        cursor = highlight.end

    if cursor < len(text):
        segments.append(TextSegmentView(text[cursor:], "", False))

    return segments


class State(rx.State):
    input_text: str = ""
    is_detecting: bool = False
    # 컴포넌트 색은 CSS 변수라 테마를 따라 저절로 바뀌지만, Plotly Figure만은
    # 파이썬에서 색을 구워 만들기 때문에 서버도 현재 모드를 알아야 한다.
    # 기본값은 rxconfig.py의 appearance="dark"와 맞춘다.
    is_dark: bool = True
    # 테마가 바뀌면 이 그래프로 Figure를 다시 만든다. 밑줄로 시작하는 backend
    # var라 프론트로 전송되지 않는다.
    _last_graph: VectorGraph = VectorGraph()
    # 한 번이라도 분석을 시작했는지. 그 전에는 결과 섹션을 렌더하지 않아
    # 랜딩이 처음 방문자에게 깔끔하게 읽힌다.
    has_started: bool = False
    current_step: int = 0  # 0~4, 스테퍼용
    risk_score: int = 0
    risk_level: str = ""
    risk_color: str = styles.RISK_COLORS["안전"]
    masked_text: str = ""
    text_segments: List[TextSegmentView] = []
    evidences: List[EvidenceView] = []
    similar_cases: List[SimilarCaseView] = []
    recommended_actions: List[str] = []
    graph_figure: go.Figure = empty_figure()
    signal_count: int = 0
    max_signal_weight: int = 0
    attack_type: str = ""
    attack_similarity: int = 0
    error_message: str = ""

    def set_input_text(self, value: str):
        self.input_text = value
        # 입력을 고치는 순간 이전 오류 안내는 더 이상 사실이 아니다
        self.error_message = ""

    def sync_color_mode(self, mode: str):
        """페이지가 뜰 때 localStorage에 저장된 테마를 서버에 맞춘다.

        기본은 다크지만 사용자가 지난번에 라이트를 골랐다면 프론트만 라이트로
        복원되어, 이걸 하지 않으면 그래프만 다크 팔레트로 남는다.
        """
        is_dark = mode != "light"
        if is_dark == self.is_dark:
            return
        self.is_dark = is_dark
        self.graph_figure = build_figure(self._last_graph, self.is_dark)

    def flip_theme(self):
        """서버가 아는 테마를 뒤집고 그래프를 새 팔레트로 다시 그린다.

        실제 화면 전환은 프론트의 `rx.toggle_color_mode`가 맡는다 — 그건
        ColorModeContext를 읽는 프론트 Var라 백엔드 핸들러의 반환값으로는
        쓸 수 없다(이벤트로 변환되지 않고 오류가 난다). 그래서 버튼의
        on_click에서 둘을 나란히 실행하고, 여기서는 거울만 맞춘다.
        """
        self.is_dark = not self.is_dark
        self.graph_figure = build_figure(self._last_graph, self.is_dark)

    def _reset_result(self):
        self.current_step = 0
        self.risk_score = 0
        self.risk_level = ""
        self.masked_text = ""
        self.text_segments = []
        self.evidences = []
        self.similar_cases = []
        self.recommended_actions = []
        self._last_graph = VectorGraph()
        self.graph_figure = build_figure(self._last_graph, self.is_dark)
        self.signal_count = 0
        self.max_signal_weight = 0
        self.attack_type = ""
        self.attack_similarity = 0
        self.error_message = ""

    async def detect(self):
        if not self.input_text.strip():
            self.error_message = "분석할 문구를 입력해주세요."
            return

        text = self.input_text
        self._reset_result()
        self.is_detecting = True
        self.has_started = True
        # 결과가 나오길 기다리지 않고 먼저 자리로 데려간다 — 분석 과정 자체가
        # 보여줄 내용이다.
        yield rx.scroll_to(ANALYSIS_ANCHOR)
        yield

        use_case = DetectPhishingUseCase(MockPhishingRepository())
        try:
            async for status in use_case.execute(text):
                self.current_step = _STEP_INDEX[status]
                # 같은 단계가 여러 번 와도 그래프는 매번 다시 그린다 — 노드와
                # 엣지가 붙는 과정이 곧 이 화면의 내용이다.
                self._last_graph = use_case.graph_snapshot
                self.graph_figure = build_figure(self._last_graph, self.is_dark)
                yield

            report = use_case.last_report
            self.risk_score = report.risk_score
            self.risk_level = report.risk_level.value
            self.risk_color = styles.RISK_COLORS[report.risk_level.value]
            self.masked_text = report.input_text
            self.text_segments = _to_segments(report.input_text, report.highlights)
            self.evidences = [
                EvidenceView(
                    keyword=e.keyword, description=e.description, weight=e.weight
                )
                for e in report.evidences
            ]
            self.similar_cases = [
                SimilarCaseView(
                    text=item.case.text,
                    category=item.case.category.value,
                    similarity_percent=round(item.similarity * 100),
                    is_phishing=item.case.is_phishing,
                )
                for item in report.similar_cases
            ]
            self.recommended_actions = report.recommended_actions
            self.signal_count = len(report.evidences)
            self.max_signal_weight = max(
                (e.weight for e in report.evidences), default=0
            )
            self.attack_type = report.attack_type
            self.attack_similarity = report.attack_similarity
        except Exception as error:
            self.error_message = f"분석 중 오류가 발생했습니다: {error}"
        finally:
            self.is_detecting = False
            yield

    def reset_analysis(self):
        """결과를 접고 입력 패널로 되돌아간다."""
        self.input_text = ""
        self._reset_result()
        self.has_started = False
        return rx.scroll_to(INPUT_ANCHOR)

    def focus_input(self):
        """랜딩 아래쪽 CTA에서 히어로의 입력 패널로 데려간다."""
        return rx.scroll_to(INPUT_ANCHOR)
