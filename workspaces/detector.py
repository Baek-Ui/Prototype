"""보이스피싱 탐지 파이프라인의 순수 함수들.

각 단계는 독립적으로 테스트 가능하며, 조율은 usecases.py가 담당한다.
"""

import re
from collections import Counter
from typing import List, Tuple

from .domain import DetectionEvidence, RiskLevel, SimilarCase, TextHighlight
from .rules import RULES

_URL = re.compile(r"https?://[^\s]+")
_PHONE = re.compile(r"01[0-9][-.\s]?\d{3,4}[-.\s]?\d{4}")
_ACCOUNT = re.compile(r"\d{2,6}[-]\d{2,6}[-]\d{2,8}")

# 마스킹을 거치면 원본 토큰이 사라져 규칙이 더는 매칭되지 않는 경우가 있다.
# 점수는 원문으로 이미 매겨졌으므로, 부각 위치만 플레이스홀더로 대신 찾는다.
# 전화번호·계좌번호에는 대응하는 규칙이 없어 항목이 없다 — 규칙이 내지 않은
# 신호를 색칠하면 근거 목록과 화면이 어긋난다.
_MASKED_TOKENS = {"의심 링크": re.compile(r"\[링크\]")}

_NO_ATTACK_TYPE = "해당 없음"

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


def find_highlights(
    masked_text: str, evidences: List[DetectionEvidence]
) -> List[TextHighlight]:
    """마스킹된 문구 안에서 근거가 걸린 구간을 앞에서부터 겹치지 않게 반환한다.

    점수를 낸 규칙(evidences)만 부각한다 — 화면의 색과 근거 목록이 어긋나면
    사용자는 둘 중 무엇을 믿어야 할지 알 수 없다. 규칙의 lookahead는 폭이
    0이라 match.span()이 곧 실제 토큰 구간이다.
    """
    fired = {evidence.keyword for evidence in evidences}
    spans = [
        TextHighlight(match.start(), match.end(), rule.keyword, rule.weight)
        for rule in RULES
        if rule.keyword in fired
        for match in _MASKED_TOKENS.get(rule.keyword, rule.pattern).finditer(masked_text)
    ]

    # 겹치는 구간은 가중치가 큰 쪽을 남긴다. 겹친 채로 렌더하면 같은 글자가
    # 두 번 출력되거나 구간이 잘린다.
    kept: List[TextHighlight] = []
    for span in sorted(spans, key=lambda s: (-s.weight, s.start)):
        if not any(span.start < k.end and k.start < span.end for k in kept):
            kept.append(span)

    return sorted(kept, key=lambda s: s.start)


def infer_attack_type(
    similar_cases: List[SimilarCase], level: RiskLevel
) -> Tuple[str, int]:
    """유사 사례가 가리키는 수법 유형과 그 유형 안에서의 최고 유사도(%).

    두 개의 문을 모두 통과해야 유형을 붙인다.

    첫째, 종합 판정이 '안전'이면 붙일 수법이 없다. 유사도만 보면 정상적인
    은행 입금 알림이 "대출사기 49%"를 달고 나오는데, 바로 옆 타일에는
    "안전 · 신호 0건"이 떠 있다. 근거를 함께 보여주겠다는 서비스가 자기
    화면 안에서 모순되면 사용자는 둘 중 무엇도 믿을 수 없다.

    둘째, 이웃의 과반이 피싱이어야 한다. 한 건이라도 끼면 단정하는 방식은
    정상 문구에 엉뚱한 라벨을 붙였고, 반대로 1위 사례만 보는 방식은 명백한
    기관사칭 문구의 1위가 우연히 정상 사례가 되는 순간 유형을 놓쳤다 —
    embedding.py가 밝힌 충돌 바닥 때문에 긴 문구일수록 1위 순위 자체를
    믿을 수 없다. 유사도 점수도 어차피 이웃의 평균으로 내므로 셈이 일관된다.
    """
    if level is RiskLevel.SAFE or not similar_cases:
        return _NO_ATTACK_TYPE, 0

    phishing = [item for item in similar_cases if item.case.is_phishing]
    if len(phishing) * 2 <= len(similar_cases):
        return _NO_ATTACK_TYPE, 0

    counts = Counter(item.case.category.value for item in phishing)
    top_count = max(counts.values())
    tied = {category for category, count in counts.items() if count == top_count}
    # 최빈 카테고리가 갈리면 유사도가 가장 높은 쪽을 따른다.
    best = max(
        (item for item in phishing if item.case.category.value in tied),
        key=lambda item: item.similarity,
    )
    return best.case.category.value, round(best.similarity * 100)
