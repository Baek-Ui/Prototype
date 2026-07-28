from dataclasses import dataclass, field
from enum import Enum
from typing import List


class DetectionStatus(Enum):
    PREPROCESSING = "문구 전처리 중..."
    VECTORIZING = "문구 벡터화 중..."
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
        # 주의 경계 35: 가중치 25짜리 규칙 하나만 걸린 문구가 결합식(규칙 0.6 +
        # 유사도 0.4)을 거치면 35점대에 모이는데, 정상 문구는 홀드아웃 측정에서
        # 최고 22점에 그쳐 두 분포가 이 지점에서 분리된다.
        if score < 35:
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
class TextHighlight:
    """입력 문구 안에서 위험 신호가 걸린 구간. 반드시 서로 겹치지 않는다."""

    start: int
    end: int
    keyword: str
    weight: int


class GraphNodeKind(Enum):
    INPUT = "입력 문구"
    CASE = "실제 사례"
    RULE = "위험 신호"


class GraphEdgeKind(Enum):
    RULE = "규칙"
    CASE = "사례"


@dataclass
class GraphNode:
    id: str
    label: str
    kind: GraphNodeKind
    x: float
    y: float
    z: float
    # CASE 노드만 채운다. RULE·INPUT 노드에서는 각각 신호 설명과 빈 문자열.
    detail: str = ""
    is_phishing: bool = False
    # 이번 분석에서 실제로 걸린 규칙인지. 켜진 노드만 강조해 그린다.
    is_active: bool = False


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    kind: GraphEdgeKind
    # RULE 엣지는 규칙 가중치, CASE 엣지는 코사인 유사도(0~1)를 굵기 근거로 쓴다.
    strength: float = 0.0


@dataclass
class VectorGraph:
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)


@dataclass
class DetectionReport:
    input_text: str
    risk_score: int
    risk_level: RiskLevel
    evidences: List[DetectionEvidence] = field(default_factory=list)
    similar_cases: List[SimilarCase] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    highlights: List[TextHighlight] = field(default_factory=list)
    attack_type: str = ""
    attack_similarity: int = 0
