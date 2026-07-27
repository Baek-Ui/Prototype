from workspaces.detector import (
    combine_scores,
    preprocess,
    recommend_actions,
    score_by_rules,
    score_by_similarity,
)
from workspaces.domain import PhishingCase, PhishingCategory, RiskLevel, SimilarCase


def _case(is_phishing: bool) -> PhishingCase:
    return PhishingCase(
        id="x",
        text="t",
        category=PhishingCategory.IMPERSONATION if is_phishing else PhishingCategory.NORMAL,
        is_phishing=is_phishing,
        source="테스트",
        embedding=[],
    )


def test_preprocess_masks_phone_number():
    """전화번호는 마스킹되어야 함"""
    masked = preprocess("연락처는 010-1234-5678 입니다")
    assert "1234" not in masked
    assert "5678" not in masked


def test_preprocess_masks_account_number():
    """계좌번호는 마스킹되어야 함"""
    masked = preprocess("입금 계좌 110-234-567890 로 보내주세요")
    assert "567890" not in masked


def test_preprocess_masks_url():
    """URL은 마스킹되어야 함"""
    masked = preprocess("확인하기 http://bit.ly/ab12cd")
    assert "bit.ly" not in masked


def test_preprocess_keeps_normal_text():
    """일반 텍스트는 보존되어야 함"""
    assert "안전계좌" in preprocess("안전계좌로 이체하세요")


def test_score_by_rules_detects_phishing_keywords():
    """명백한 피싱 문구는 높은 규칙 점수와 근거를 산출해야 함"""
    score, evidences = score_by_rules(
        "서울중앙지검 수사관입니다. 안전계좌로 즉시 이체하지 않으면 계좌가 동결됩니다."
    )
    assert score >= 70
    assert len(evidences) >= 3
    assert all(e.weight > 0 for e in evidences)


def test_score_by_rules_returns_zero_for_normal_text():
    """정상 문구는 0점과 빈 근거를 반환해야 함"""
    score, evidences = score_by_rules("내일 회의 시간 오후 3시로 변경 가능할까요")
    assert score == 0
    assert evidences == []


def test_score_by_rules_is_capped_at_100():
    """규칙 점수는 100을 넘지 않아야 함"""
    score, _ = score_by_rules(
        "검찰 수사관입니다. 안전계좌로 즉시 이체하고 앱 설치 후 원격제어를 허용하세요. "
        "주민등록번호와 OTP를 알려주시고 아무에게도 발설하지 마세요. http://a.co"
    )
    assert score <= 100


def test_score_by_similarity_weights_phishing_cases():
    """피싱 사례와 유사할수록 높은 점수를 반환해야 함"""
    high = score_by_similarity([SimilarCase(_case(True), 0.9)])
    low = score_by_similarity([SimilarCase(_case(True), 0.1)])
    assert high > low


def test_score_by_similarity_ignores_normal_cases():
    """정상 사례와만 유사하면 0점이어야 함"""
    assert score_by_similarity([SimilarCase(_case(False), 0.9)]) == 0


def test_score_by_similarity_handles_empty_list():
    """유사 사례가 없으면 0점이어야 함"""
    assert score_by_similarity([]) == 0


def test_combine_scores_uses_weighted_formula():
    """최종 점수는 규칙 60% + 유사도 40% 가중합이어야 함"""
    assert combine_scores(100, 0) == 60
    assert combine_scores(0, 100) == 40
    assert combine_scores(100, 100) == 100
    assert combine_scores(0, 0) == 0


def test_combine_scores_stays_in_range():
    """결합 점수는 항상 0~100 범위여야 함"""
    for rule_score in (0, 50, 100):
        for similarity_score in (0, 50, 100):
            assert 0 <= combine_scores(rule_score, similarity_score) <= 100


def test_recommend_actions_differ_by_level():
    """위험 등급별로 다른 권장 행동을 반환해야 함"""
    danger = recommend_actions(RiskLevel.DANGER)
    safe = recommend_actions(RiskLevel.SAFE)
    assert danger != safe
    assert len(danger) >= 3
    assert len(safe) >= 1
