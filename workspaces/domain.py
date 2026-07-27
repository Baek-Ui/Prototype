from dataclasses import dataclass, field
from enum import Enum
from typing import List


class DetectionStatus(Enum):
    PREPROCESSING = "문구 전처리 중..."
    RULE_SCORING = "위험 패턴 대조 중..."
    SIMILARITY_SEARCH = "유사 사례 검색 중..."
    JUDGING = "종합 판정 중..."
    COMPLETED = "분석 완료"
    FAILED = "분석 실패"


class RiskLevel(Enum):
    SAFE = "안전"
    CAUTION = "주의"
    DANGER = "위험"

    @classmethod
    def from_score(cls, score: int) -> "RiskLevel":
        if not 0 <= score <= 100:
            raise ValueError(f"위험 점수는 0과 100 사이여야 합니다: {score}")
        if score < 40:
            return cls.SAFE
        if score < 70:
            return cls.CAUTION
        return cls.DANGER


class PhishingCategory(Enum):
    IMPERSONATION = "기관사칭"
    LOAN = "대출사기"
    FAMILY = "가족사칭"
    SMISHING = "스미싱"
    NORMAL = "정상"


@dataclass
class PhishingCase:
    id: str
    text: str
    category: PhishingCategory
    is_phishing: bool
    source: str
    embedding: List[float] = field(default_factory=list)


@dataclass
class DetectionEvidence:
    keyword: str
    description: str
    weight: int


@dataclass
class SimilarCase:
    case: PhishingCase
    similarity: float


@dataclass
class DetectionReport:
    input_text: str
    risk_score: int
    risk_level: RiskLevel
    evidences: List[DetectionEvidence] = field(default_factory=list)
    similar_cases: List[SimilarCase] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
