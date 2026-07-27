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


# Round 2 regression tests: More specific lookahead word validation
def test_urgency_excludes_generic_confirmation_request():
    """일반 확인 요청(금전 무관)은 긴급성 강조로 매칭되지 않아야 함"""
    benign = "고객님의 정기예금 이자가... 즉시 확인 바랍니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "긴급성 강조" not in matched


def test_urgency_with_financial_action_still_matches():
    """금전 행동(송금, 이체 등)과 함께하는 긴급성은 매칭되어야 함"""
    phishing = "지금 즉시 본인인증을 완료해서 계좌로 200만원을 보내주세요"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "긴급성 강조" in matched


def test_investigative_agency_excludes_legitimate_traffic_info():
    """교통사고 정보 안내는 수사기관 사칭으로 매칭되지 않아야 함"""
    benign = "관할 경찰서에서 교통사고 관련 정보 안내드립니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "수사기관 사칭" not in matched


def test_investigative_agency_excludes_legitimate_recruitment_info():
    """채용 정보 안내는 검찰 사칭으로 매칭되지 않아야 함"""
    benign = "검찰청 홈페이지에서 채용 정보를 확인하실 수 있습니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "수사기관 사칭" not in matched


def test_investigative_agency_with_personal_info_demand_matches():
    """개인정보 요구와 함께하는 수사기관 사칭은 매칭되어야 함"""
    phishing = "경찰청입니다. 귀하의 개인정보 본인확인이 필요합니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "수사기관 사칭" in matched


def test_agency_excludes_legitimate_tax_info():
    """세금 정보 안내는 기관 사칭으로 매칭되지 않아야 함"""
    benign = "국세청에서 연말정산 세금 정보 안내드립니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "기관 사칭" not in matched


def test_agency_excludes_legitimate_finance_info():
    """금융 정보 안내는 기관 사칭으로 매칭되지 않아야 함"""
    benign = "금융감독원 홈페이지에서 금융 정보를 확인하실 수 있습니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "기관 사칭" not in matched


def test_agency_with_personal_info_demand_matches():
    """개인정보 요구와 함께하는 기관 사칭은 매칭되어야 함"""
    phishing = "국세청입니다. 개인정보 본인확인을 위해 주민등록번호를 알려주세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "기관 사칭" in matched


def test_account_freeze_with_particle_matches():
    """한국어 조사를 포함한 계좌 동결 표현은 매칭되어야 함"""
    phishing = "계좌가 동결됩니다"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "계좌 동결 위협" in matched


def test_account_freeze_various_particles_match():
    """다양한 조사를 포함한 계좌 동결 표현들이 매칭되어야 함"""
    test_cases = [
        "당신의 계좌는 동결됩니다",
        "계좌를 동결하겠습니다",
        "계좌가 정지됩니다",
        "계좌 동결 예정입니다"
    ]
    for case in test_cases:
        matched = [rule.keyword for rule in RULES if rule.pattern.search(case)]
        assert "계좌 동결 위협" in matched, f"Failed to match: {case}"


# Round 3 regression tests: Bare nouns to action forms (11 false positives + 계좌동결 regression)
def test_agency_excludes_app_mention_without_installation_demand():
    """기관 앱 소개는 기관 사칭으로 매칭되지 않아야 함"""
    benign = "국세청 앱에서 연말정산 신고를 편리하게 하실 수 있습니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "기관 사칭" not in matched


def test_agency_app_installation_demand_matches():
    """앱 설치 요구와 함께하는 기관 사칭은 매칭되어야 함"""
    phishing = "국세청입니다. 앱을 설치하고 본인인증하세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "기관 사칭" in matched


def test_agency_excludes_account_mention_without_transfer_demand():
    """기관의 계좌 안내는 기관 사칭으로 매칭되지 않아야 함"""
    benign = "국세청에서 계좌 환급 절차 안내드립니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "기관 사칭" not in matched


def test_agency_account_demand_matches():
    """계좌 요구와 함께하는 기관 사칭은 매칭되어야 함"""
    phishing = "국세청입니다. 계좌번호를 알려주세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "기관 사칭" in matched


def test_agency_excludes_password_advice_without_demand():
    """기관의 비밀번호 변경 권고는 기관 사칭으로 매칭되지 않아야 함"""
    benign = "금융감독원에서 비밀번호를 주기적으로 변경하라고 권고합니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "기관 사칭" not in matched


def test_agency_password_disclosure_demand_matches():
    """비밀번호 공개 요구와 함께하는 기관 사칭은 매칭되어야 함"""
    phishing = "금융감독원입니다. 비밀번호를 입력해주세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "기관 사칭" in matched


def test_agency_excludes_id_request_in_legitimate_context():
    """기관 방문 시 신분증 지참은 기관 사칭으로 매칭되지 않아야 함"""
    benign = "건강보험공단 방문 시 신분증을 지참해주세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "기관 사칭" not in matched


def test_agency_id_copy_demand_matches():
    """신분증 사본 요구와 함께하는 기관 사칭은 매칭되어야 함"""
    phishing = "금융감독원입니다. 신분증 사본을 보내주세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "기관 사칭" in matched


def test_investigative_agency_excludes_app_mention_without_installation_demand():
    """경찰청 안전신문고 앱 소개는 수사기관 사칭으로 매칭되지 않아야 함"""
    benign = "경찰청 안전신문고 앱에서 민원을 신청할 수 있습니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "수사기관 사칭" not in matched


def test_investigative_agency_excludes_account_mention_without_transfer_demand():
    """경찰서의 계좌 신고 안내는 수사기관 사칭으로 매칭되지 않아야 함"""
    benign = "경찰서에서 사기 피해 계좌 신고 접수 안내드립니다."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "수사기관 사칭" not in matched


def test_investigative_agency_account_demand_matches():
    """계좌 요구와 함께하는 수사기관 사칭은 매칭되어야 함"""
    phishing = "경찰청입니다. 피해 계좌번호를 알려주세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "수사기관 사칭" in matched


def test_urgency_excludes_password_change_advice():
    """보안을 위한 비밀번호 변경 권고는 긴급성 강조로 매칭되지 않아야 함"""
    benign = "보안을 위해 즉시 비밀번호를 변경해 주세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "긴급성 강조" not in matched


def test_urgency_password_demand_matches():
    """비밀번호 입력 요구와 함께하는 긴급성은 매칭되어야 함"""
    phishing = "지금 즉시 비밀번호를 입력해주세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "긴급성 강조" in matched


def test_urgency_excludes_app_update_advice():
    """앱 업데이트 권고는 긴급성 강조로 매칭되지 않아야 함"""
    benign = "지금 바로 앱 업데이트를 진행해 주세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "긴급성 강조" not in matched


def test_urgency_app_installation_demand_matches():
    """앱 설치 요구와 함께하는 긴급성은 매칭되어야 함"""
    phishing = "지금 바로 앱을 설치해서 본인인증하세요."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "긴급성 강조" in matched


def test_phone_damage_excludes_money_mention_without_transfer_demand():
    """휴대폰 고장 후 금전 소비는 가족사칭 정황으로 매칭되지 않아야 함"""
    benign = "엄마 폰 액정 깨져서 수리비로 돈 좀 썼어"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "가족사칭 정황" not in matched


def test_phone_damage_money_transfer_demand_matches():
    """돈 송금 요구와 함께하는 폰 고장은 가족사칭으로 매칭되어야 함"""
    phishing = "엄마 폰 액정 깨졌어, 돈을 보내줄래?"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "가족사칭 정황" in matched


def test_phone_damage_excludes_number_mention_without_contact_demand():
    """폰 고장 후 전화번호 언급은 가족사칭 정황으로 매칭되지 않아야 함"""
    benign = "엄마 폰 액정 깨졌어, 전화번호 저장해놨으니 걱정마"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "가족사칭 정황" not in matched


def test_phone_damage_new_contact_channel_matches():
    """새 번호로의 연락 요구와 함께하는 폰 고장은 가족사칭으로 매칭되어야 함"""
    phishing = "엄마 폰 액정 깨졌어, 이 번호로 카톡 줘."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "가족사칭 정황" in matched


def test_phone_damage_excludes_message_mention_without_contact_demand():
    """폰 고장 후 문자 언급은 가족사칭 정황으로 매칭되지 않아야 함"""
    benign = "엄마 폰 액정 깨졌어, 문자는 나중에 확인할게"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(benign)]
    assert "가족사칭 정황" not in matched


def test_phone_damage_message_contact_demand_matches():
    """문자로 연락 요청과 함께하는 폰 고장은 가족사칭으로 매칭되어야 함"""
    phishing = "엄마 폰 액정 깨졌어, 문자 줘."
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "가족사칭 정황" in matched


def test_account_freeze_no_separator_matches():
    """공백 없는 계좌동결도 매칭되어야 함"""
    phishing = "계좌동결됩니다"
    matched = [rule.keyword for rule in RULES if rule.pattern.search(phishing)]
    assert "계좌 동결 위협" in matched
