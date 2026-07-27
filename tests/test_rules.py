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


# Regression tests: Benign sentences that previously triggered false positives
def test_settlement_guarantee_word_excludes_daily_guarantees():
    """보증금·보증인·보증서 등 일상 용어는 매칭되지 않아야 함"""
    benign = "전세 보증금 반환 관련해서 집주인과 통화했어요"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "합의금·보증 언급" not in matched


def test_settlement_guarantee_phishing_still_matches():
    """피싱 맥락의 합의금과 보증은 여전히 매칭되어야 함"""
    phishing = "나 지금 친구 보증 때문에 급해. 신분증 사진이랑 계좌 비밀번호 좀 보내줘."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "합의금·보증 언급" in matched


def test_urgency_excludes_workplace_requests():
    """일반 업무 요청의 급함은 매칭되지 않아야 함"""
    benign = "급하게 부탁 좀 할게, 지금 회의실로 와줄 수 있어?"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "긴급성 강조" not in matched


def test_urgency_phishing_still_matches():
    """금전 관련 긴급성은 여전히 매칭되어야 함"""
    phishing = "엄마 나 사고 났어. 합의금이 필요한데 지금 바로 송금해줘."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "긴급성 강조" in matched


def test_agency_excludes_legitimate_notices():
    """기관에서 보내는 정상 공지는 매칭되지 않아야 함"""
    benign = "국세청 종합소득세 신고 기간 안내드립니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "기관 사칭" not in matched


def test_agency_phishing_still_matches():
    """기관을 사칭한 피싱 메시지는 여전히 매칭되어야 함"""
    phishing = "금융감독원입니다. 계좌 동결 방지를 위해 즉시 자산을 안전계좌로 옮기셔야 합니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "기관 사칭" in matched


def test_silence_demand_excludes_generic_nda():
    """일상적 비밀 유지 요청은 매칭되지 않아야 함"""
    benign = "이 프로젝트 관련해서는 비밀 유지 부탁드립니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "함구 요구" not in matched


def test_silence_demand_phishing_still_matches():
    """피싱 맥락의 함구 요구는 여전히 매칭되어야 함"""
    phishing = "경찰청 사이버수사대입니다. 수사 협조를 위해 통화 내용은 절대 발설하지 마십시오."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "함구 요구" in matched


def test_phone_damage_excludes_mundane_statements():
    """단순 휴대폰 고장 신고는 매칭되지 않아야 함"""
    benign = "엄마 폰 액정 깨져서 오늘 수리 맡기고 왔어"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "가족사칭 정황" not in matched


def test_phone_damage_phishing_still_matches():
    """메신저피싱 맥락의 휴대폰 고장은 여전히 매칭되어야 함"""
    phishing = "엄마 나 폰 액정 깨져서 수리 맡겼어. 이 번호로 카톡 줘."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "가족사칭 정황" in matched
