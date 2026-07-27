from dataclasses import dataclass
from typing import List

import reflex as rx

from . import styles
from .domain import DetectionStatus
from .repository import MockPhishingRepository
from .usecases import DetectPhishingUseCase

_STEP_INDEX = {
    DetectionStatus.PREPROCESSING: 0,
    DetectionStatus.RULE_SCORING: 1,
    DetectionStatus.SIMILARITY_SEARCH: 2,
    DetectionStatus.JUDGING: 3,
    DetectionStatus.COMPLETED: 4,
}


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


class State(rx.State):
    input_text: str = ""
    is_detecting: bool = False
    current_step: int = 0  # 0~3, 스테퍼용
    risk_score: int = 0
    risk_level: str = ""
    risk_color: str = styles.RISK_COLORS["안전"]
    masked_text: str = ""
    evidences: List[EvidenceView] = []
    similar_cases: List[SimilarCaseView] = []
    recommended_actions: List[str] = []
    error_message: str = ""

    def set_input_text(self, value: str):
        self.input_text = value
        # 입력을 고치는 순간 이전 오류 안내는 더 이상 사실이 아니다
        self.error_message = ""

    def _reset_result(self):
        self.current_step = 0
        self.risk_score = 0
        self.risk_level = ""
        self.masked_text = ""
        self.evidences = []
        self.similar_cases = []
        self.recommended_actions = []
        self.error_message = ""

    async def detect(self):
        if not self.input_text.strip():
            self.error_message = "분석할 문구를 입력해주세요."
            return

        text = self.input_text
        self._reset_result()
        self.is_detecting = True
        yield rx.redirect("/result")
        yield

        use_case = DetectPhishingUseCase(MockPhishingRepository())
        try:
            async for status in use_case.execute(text):
                self.current_step = _STEP_INDEX[status]
                yield

            report = use_case.last_report
            self.risk_score = report.risk_score
            self.risk_level = report.risk_level.value
            self.risk_color = styles.RISK_COLORS[report.risk_level.value]
            self.masked_text = report.input_text
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
        except Exception as error:
            self.error_message = f"분석 중 오류가 발생했습니다: {error}"
        finally:
            self.is_detecting = False
            yield

    def reset_and_go_home(self):
        self.input_text = ""
        self._reset_result()
        return rx.redirect("/")
