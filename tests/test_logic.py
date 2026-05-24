import pytest
import asyncio
from workspaces.usecases import AnalyzeVideoUseCase
from workspaces.infrastructure import AIPipelineService
from workspaces.domain import AnalysisStatus

class MockStatusTracker:
    def __init__(self):
        self.statuses = []
    
    async def track(self, status: AnalysisStatus):
        self.statuses.append(status)

@pytest.mark.asyncio
async def test_analyze_video_success():
    """
    [정상 케이스] 올바른 URL이 입력되었을 때 분석이 성공적으로 완료되는지 확인
    """
    # Given
    ai_service = AIPipelineService()
    use_case = AnalyzeVideoUseCase(ai_service)
    test_url = "https://youtube.com/watch?v=test"
    statuses = []

    # When
    async for status in use_case.execute(test_url):
        statuses.append(status)

    # Then
    assert use_case.last_report is not None, "리포트가 생성되어야 함"
    assert use_case.last_report.status == AnalysisStatus.COMPLETED, "상태가 완료여야 함"
    assert len(use_case.last_report.fact_check_results) > 0, "팩트 체크 결과가 포함되어야 함"
    assert AnalysisStatus.MATCHING in statuses, "매칭 단계가 실행되어야 함"
    assert AnalysisStatus.STT_ANALYZING in statuses, "STT 분석 단계가 실행되어야 함"
    assert AnalysisStatus.FACT_CHECKING in statuses, "팩트 체크 단계가 실행되어야 함"

@pytest.mark.asyncio
async def test_analyze_video_empty_url():
    """
    [엣지 케이스] URL이 비어있을 때 ValueError가 발생하는지 확인
    """
    # Given
    ai_service = AIPipelineService()
    use_case = AnalyzeVideoUseCase(ai_service)

    # When & Then
    with pytest.raises(ValueError) as excinfo:
        # 제너레이터 초기화 시 에러가 발생하므로 첫 요소를 가져올 때 확인
        async for _ in use_case.execute(""):
            pass
    
    assert "URL이 입력되지 않았습니다." in str(excinfo.value), "적절한 예외 메시지가 출력되어야 함"

@pytest.mark.asyncio
async def test_analyze_video_status_sequence():
    """
    [로직 케이스] 분석 단계가 순차적으로 올바르게 변경되는지 확인
    """
    # Given
    ai_service = AIPipelineService()
    use_case = AnalyzeVideoUseCase(ai_service)
    test_url = "https://youtube.com/watch?v=sequence"
    statuses = []

    # When
    async for status in use_case.execute(test_url):
        statuses.append(status)

    # Then
    expected_sequence = [
        AnalysisStatus.MATCHING,
        AnalysisStatus.STT_ANALYZING,
        AnalysisStatus.FACT_CHECKING,
        AnalysisStatus.COMPLETED
    ]
    assert statuses == expected_sequence, "상태 변경 순서가 정확해야 함"

@pytest.mark.asyncio
async def test_analyze_video_report_integrity():
    """
    [정상 케이스] 생성된 리포트의 데이터 무결성(범위 등) 확인
    """
    # Given
    ai_service = AIPipelineService()
    use_case = AnalyzeVideoUseCase(ai_service)
    test_url = "https://youtube.com/watch?v=integrity"

    # When
    async for _ in use_case.execute(test_url):
        pass
    report = use_case.last_report

    # Then
    assert 0.0 <= report.deepfake_score <= 1.0, "딥페이크 점수는 0과 1 사이여야 함"
    assert 0.0 <= report.audio_spoofing_score <= 1.0, "음성 위조 점수는 0과 1 사이여야 함"
    assert report.video.url == test_url, "입력된 URL이 리포트에 반영되어야 함"
