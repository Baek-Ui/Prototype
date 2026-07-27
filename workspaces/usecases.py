"""보이스피싱 탐지 유즈케이스.

각 단계 완료 시 DetectionStatus를 yield해 UI가 진행 상황을 실시간으로
표시할 수 있게 한다. async generator는 async for 소비자에게 반환값을
전달할 수 없으므로 최종 리포트는 last_report 속성에 저장한다.
"""

import asyncio
from typing import AsyncGenerator, Optional

from .detector import (
    combine_scores,
    preprocess,
    recommend_actions,
    score_by_rules,
    score_by_similarity,
)
from .domain import DetectionReport, DetectionStatus, RiskLevel
from .embedding import embed
from .repository import PhishingRepository

_STEP_DELAY = 0.4  # 단계별 진행 상황을 사용자가 인지할 수 있게 하는 최소 지연


class DetectPhishingUseCase:
    def __init__(self, repository: PhishingRepository):
        self.repository = repository
        self.last_report: Optional[DetectionReport] = None

    async def execute(self, text: str) -> AsyncGenerator[DetectionStatus, None]:
        if not text or not text.strip():
            raise ValueError("분석할 문구를 입력해주세요.")

        yield DetectionStatus.PREPROCESSING
        await asyncio.sleep(_STEP_DELAY)
        masked = preprocess(text)

        yield DetectionStatus.RULE_SCORING
        await asyncio.sleep(_STEP_DELAY)
        rule_score, evidences = score_by_rules(text)

        yield DetectionStatus.SIMILARITY_SEARCH
        await asyncio.sleep(_STEP_DELAY)
        similar_cases = await self.repository.search_similar(embed(text), top_k=3)

        yield DetectionStatus.JUDGING
        await asyncio.sleep(_STEP_DELAY)
        risk_score = combine_scores(rule_score, score_by_similarity(similar_cases))
        risk_level = RiskLevel.from_score(risk_score)

        self.last_report = DetectionReport(
            input_text=masked,
            risk_score=risk_score,
            risk_level=risk_level,
            evidences=evidences,
            similar_cases=similar_cases,
            recommended_actions=recommend_actions(risk_level),
        )

        yield DetectionStatus.COMPLETED
