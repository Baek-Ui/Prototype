from dataclasses import dataclass

import reflex as rx


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
    risk_color: str = ""
    masked_text: str = ""
    evidences: list[EvidenceView] = []
    similar_cases: list[SimilarCaseView] = []
    recommended_actions: list[str] = []
    error_message: str = ""

    def set_input_text(self, value: str):
        self.input_text = value
