import pytest

from workspaces.domain import DetectionStatus, RiskLevel
from workspaces.repository import MockPhishingRepository
from workspaces.usecases import DetectPhishingUseCase

PHISHING_TEXT = (
    "서울중앙지검 수사관입니다. 귀하 명의 계좌가 범죄에 연루되어 "
    "안전계좌로 즉시 이체하지 않으면 계좌가 동결됩니다. 아무에게도 발설하지 마세요."
)
NORMAL_TEXT = "안녕하세요, 내일 회의 시간 오후 3시로 변경 가능할까요?"


def _use_case() -> DetectPhishingUseCase:
    return DetectPhishingUseCase(MockPhishingRepository())


async def _run(use_case: DetectPhishingUseCase, text: str) -> list:
    return [status async for status in use_case.execute(text)]


@pytest.mark.asyncio
async def test_status_sequence_is_ordered():
    """분석 단계가 정해진 순서대로 진행되어야 함"""
    use_case = _use_case()
    statuses = await _run(use_case, PHISHING_TEXT)
    assert statuses == [
        DetectionStatus.PREPROCESSING,
        DetectionStatus.RULE_SCORING,
        DetectionStatus.SIMILARITY_SEARCH,
        DetectionStatus.JUDGING,
        DetectionStatus.COMPLETED,
    ]


@pytest.mark.asyncio
async def test_phishing_text_is_flagged_as_danger():
    """명백한 피싱 문구는 위험 등급으로 판정되어야 함"""
    use_case = _use_case()
    await _run(use_case, PHISHING_TEXT)
    report = use_case.last_report

    assert report is not None
    assert report.risk_level is RiskLevel.DANGER
    assert len(report.evidences) >= 3


@pytest.mark.asyncio
async def test_normal_text_is_flagged_as_safe():
    """정상 문구는 안전 등급으로 판정되어야 함"""
    use_case = _use_case()
    await _run(use_case, NORMAL_TEXT)
    assert use_case.last_report.risk_level is RiskLevel.SAFE


@pytest.mark.asyncio
async def test_empty_input_raises_value_error():
    """빈 입력은 ValueError를 발생시켜야 함"""
    use_case = _use_case()
    with pytest.raises(ValueError):
        await _run(use_case, "   ")


@pytest.mark.asyncio
async def test_report_score_is_in_range():
    """위험 점수는 0~100 범위여야 함"""
    use_case = _use_case()
    await _run(use_case, PHISHING_TEXT)
    assert 0 <= use_case.last_report.risk_score <= 100


@pytest.mark.asyncio
async def test_report_text_is_masked():
    """리포트에 담긴 입력은 개인정보가 마스킹되어야 함"""
    use_case = _use_case()
    await _run(use_case, "안전계좌 110-234-567890 로 010-1234-5678 연락주세요")
    masked = use_case.last_report.input_text

    assert "567890" not in masked
    assert "5678" not in masked


@pytest.mark.asyncio
async def test_report_includes_similar_cases_and_actions():
    """리포트는 유사 사례 3건과 권장 행동을 포함해야 함"""
    use_case = _use_case()
    await _run(use_case, PHISHING_TEXT)
    report = use_case.last_report

    assert len(report.similar_cases) == 3
    assert len(report.recommended_actions) >= 1
