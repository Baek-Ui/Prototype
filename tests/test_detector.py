from workspaces.detector import (
    combine_scores,
    find_highlights,
    infer_attack_type,
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


def _categorized(category: PhishingCategory, similarity: float) -> SimilarCase:
    return SimilarCase(
        case=PhishingCase(
            id=f"{category.value}-{similarity}",
            text="t",
            category=category,
            is_phishing=category is not PhishingCategory.NORMAL,
            source="테스트",
            embedding=[],
        ),
        similarity=similarity,
    )


def _highlight(text: str):
    """원문을 마스킹한 뒤, 점수를 낸 근거만으로 부각 구간을 뽑는다."""
    masked = preprocess(text)
    _, evidences = score_by_rules(text)
    return masked, find_highlights(masked, evidences)


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


def test_find_highlights_spans_point_at_real_text():
    """부각 구간은 마스킹된 문구의 실제 위치를 가리켜야 함"""
    masked, highlights = _highlight("안전계좌로 즉시 이체하지 않으면 계좌가 동결됩니다.")

    assert highlights
    assert masked[highlights[0].start : highlights[0].end] == "안전계좌"
    assert all(masked[h.start : h.end] for h in highlights)


def test_find_highlights_never_overlap():
    """구간이 겹치면 같은 글자가 두 번 렌더된다"""
    _, highlights = _highlight(
        "[Web발신] 서울중앙지검 수사관입니다. 안전계좌로 즉시 이체하지 않으면 "
        "계좌가 동결됩니다. 아무에게도 발설하지 마세요. http://bit.ly/x"
    )

    assert len(highlights) >= 5
    for previous, current in zip(highlights, highlights[1:]):
        assert previous.end <= current.start


def test_find_highlights_marks_masked_link_placeholder():
    """원본 URL이 마스킹돼도 링크 신호는 플레이스홀더 위에 남아야 함"""
    masked, highlights = _highlight("택배 조회는 http://bit.ly/ab12cd 에서 확인하세요.")

    assert "[링크]" in masked
    assert any(masked[h.start : h.end] == "[링크]" for h in highlights)


def test_find_highlights_ignores_rules_that_did_not_score():
    """근거 목록에 없는 규칙은 부각하지 않아야 함 — 화면과 근거가 어긋난다"""
    masked = preprocess("안전계좌로 즉시 이체하세요.")
    assert find_highlights(masked, []) == []


def test_find_highlights_leaves_normal_text_untouched():
    """정상 문구에는 부각할 구간이 없어야 함"""
    _, highlights = _highlight("안녕하세요, 내일 회의 시간 오후 3시로 변경 가능할까요?")
    assert highlights == []


def test_infer_attack_type_picks_the_dominant_category():
    """가장 많이 걸린 수법 유형과 그 유형의 최고 유사도를 반환해야 함"""
    category, similarity = infer_attack_type(
        [
            _categorized(PhishingCategory.LOAN, 0.91),
            _categorized(PhishingCategory.LOAN, 0.62),
            _categorized(PhishingCategory.SMISHING, 0.55),
        ],
        RiskLevel.DANGER,
    )
    assert category == PhishingCategory.LOAN.value
    assert similarity == 91


def test_infer_attack_type_returns_none_when_neighbours_are_mostly_normal():
    """이웃의 과반이 정상이면 유형을 단정하지 않아야 함"""
    category, similarity = infer_attack_type(
        [
            _categorized(PhishingCategory.NORMAL, 1.0),
            _categorized(PhishingCategory.NORMAL, 0.50),
            _categorized(PhishingCategory.LOAN, 0.48),
        ],
        RiskLevel.CAUTION,
    )
    assert category == "해당 없음"
    assert similarity == 0


def test_infer_attack_type_survives_a_normal_case_ranking_first():
    """1위가 우연히 정상이어도 이웃 과반이 피싱이면 유형을 밝혀야 함

    해싱 임베딩의 충돌 바닥 탓에 긴 문구에서는 1위 순위 자체가 흔들린다.
    """
    category, similarity = infer_attack_type(
        [
            _categorized(PhishingCategory.NORMAL, 0.63),
            _categorized(PhishingCategory.IMPERSONATION, 0.57),
            _categorized(PhishingCategory.IMPERSONATION, 0.55),
        ],
        RiskLevel.DANGER,
    )
    assert category == PhishingCategory.IMPERSONATION.value
    assert similarity == 57


def test_infer_attack_type_stays_silent_when_the_verdict_is_safe():
    """안전 판정에 수법 유형을 붙이면 바로 옆 타일과 모순된다"""
    neighbours = [
        _categorized(PhishingCategory.LOAN, 0.49),
        _categorized(PhishingCategory.LOAN, 0.47),
        _categorized(PhishingCategory.NORMAL, 0.45),
    ]
    assert infer_attack_type(neighbours, RiskLevel.SAFE) == ("해당 없음", 0)
    assert infer_attack_type(neighbours, RiskLevel.CAUTION)[0] == PhishingCategory.LOAN.value


def test_infer_attack_type_handles_empty_input():
    """유사 사례가 없으면 유형도 없어야 함"""
    assert infer_attack_type([], RiskLevel.DANGER) == ("해당 없음", 0)
