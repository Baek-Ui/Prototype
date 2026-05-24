from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

class AnalysisStatus(Enum):
    IDLE = "대기 중"
    MATCHING = "원본 영상 매칭 중..."
    STT_ANALYZING = "STT 타임스탬프 분석 중..."
    FACT_CHECKING = "정부24 팩트 대조 중..."
    COMPLETED = "분석 완료"
    FAILED = "분석 실패"

@dataclass
class FactCheckResult:
    claim: str
    is_true: bool
    evidence: str
    source: str = "정부24"

@dataclass
class VideoMetadata:
    title: str
    platform: str
    url: str
    upload_date: str

@dataclass
class AnalysisReport:
    video: VideoMetadata
    status: AnalysisStatus
    deepfake_score: float  # 0.0 to 1.0
    audio_spoofing_score: float # 0.0 to 1.0
    fact_check_results: List[FactCheckResult] = field(default_factory=list)
    summary: str = ""
