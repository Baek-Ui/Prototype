"""보이스피싱 탐지 파이프라인의 순수 함수들.

각 단계는 독립적으로 테스트 가능하며, 조율은 usecases.py가 담당한다.
"""

import re
from typing import List, Tuple

from .domain import DetectionEvidence, RiskLevel, SimilarCase
from .rules import RULES

_URL = re.compile(r"https?://[^\s]+")
_PHONE = re.compile(r"01[0-9][-.\s]?\d{3,4}[-.\s]?\d{4}")
_ACCOUNT = re.compile(r"\d{2,6}[-]\d{2,6}[-]\d{2,8}")

_RULE_SCORE_CAP = 100
_RULE_WEIGHT = 0.6
_SIMILARITY_WEIGHT = 0.4

_ACTIONS = {
    RiskLevel.DANGER: [
        "송금이나 개인정보 입력을 즉시 중단하세요.",
        "문자 속 링크를 절대 클릭하지 마세요.",
        "해당 기관의 공식 대표번호로 직접 전화해 사실을 확인하세요.",
        "이미 송금했다면 즉시 은행(1332) 또는 경찰(112)에 신고하세요.",
    ],
    RiskLevel.CAUTION: [
        "송금이나 개인정보 제공을 잠시 보류하세요.",
        "발신자가 주장하는 기관의 공식 번호로 직접 확인하세요.",
        "가족이나 지인에게 내용을 공유해 함께 판단하세요.",
    ],
    RiskLevel.SAFE: [
        "명백한 위험 신호는 발견되지 않았습니다.",
        "다만 금전 요구나 링크 접속 요청이 있다면 반드시 공식 경로로 확인하세요.",
    ],
}


def preprocess(text: str) -> str:
    """개인정보·링크를 마스킹한 텍스트를 반환한다."""
    masked = _URL.sub("[링크]", text)
    masked = _PHONE.sub("[전화번호]", masked)
    masked = _ACCOUNT.sub("[계좌번호]", masked)
    return re.sub(r"\s+", " ", masked).strip()


def score_by_rules(text: str) -> Tuple[int, List[DetectionEvidence]]:
    """규칙 사전 매칭 결과로 0~100 점수와 근거 목록을 반환한다."""
    evidences = [
        DetectionEvidence(rule.keyword, rule.description, rule.weight)
        for rule in RULES
        if rule.pattern.search(text)
    ]
    total = min(sum(e.weight for e in evidences), _RULE_SCORE_CAP)
    evidences.sort(key=lambda e: e.weight, reverse=True)
    return total, evidences


def score_by_similarity(similar_cases: List[SimilarCase]) -> int:
    """피싱으로 라벨된 유사 사례의 유사도 평균을 0~100 점수로 환산한다."""
    if not similar_cases:
        return 0
    phishing_similarity = sum(
        item.similarity for item in similar_cases if item.case.is_phishing
    )
    average = phishing_similarity / len(similar_cases)
    return max(0, min(round(average * 100), 100))


def combine_scores(rule_score: int, similarity_score: int) -> int:
    """규칙 60% + 유사도 40% 가중합을 정수 점수로 반환한다."""
    combined = rule_score * _RULE_WEIGHT + similarity_score * _SIMILARITY_WEIGHT
    return max(0, min(round(combined), 100))


def recommend_actions(level: RiskLevel) -> List[str]:
    """위험 등급에 맞는 권장 행동 목록을 반환한다."""
    return list(_ACTIONS[level])
