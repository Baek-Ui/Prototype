from workspaces.rules import RULES


def test_rules_are_not_empty():
    """규칙 사전이 비어있지 않아야 함"""
    assert len(RULES) >= 10


def test_rule_keywords_are_unique():
    """키워드 중복이 없어야 함 (근거 목록에 중복 노출 방지)"""
    keywords = [rule.keyword for rule in RULES]
    assert len(keywords) == len(set(keywords))


def test_rule_weights_are_in_valid_range():
    """가중치는 1~40 사이여야 함 (단일 규칙이 점수를 독점하지 않도록)"""
    for rule in RULES:
        assert 1 <= rule.weight <= 40


def test_safe_account_rule_matches():
    """'안전계좌' 규칙이 실제 문구에 매칭되어야 함"""
    matched = [rule.keyword for rule in RULES if rule.pattern.search("안전계좌로 이체하세요")]
    assert "안전계좌" in matched


def test_url_rule_matches_link():
    """URL 규칙이 링크를 탐지해야 함"""
    matched = [rule.keyword for rule in RULES if rule.pattern.search("확인하기 http://bit.ly/ab12cd")]
    assert "의심 링크" in matched


def test_normal_message_matches_no_rule():
    """정상 문구는 어떤 규칙에도 매칭되지 않아야 함"""
    matched = [rule.keyword for rule in RULES if rule.pattern.search("내일 회의 시간 오후 3시로 변경 가능할까요")]
    assert matched == []
