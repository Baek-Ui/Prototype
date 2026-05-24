from typing import Callable, Awaitable, AsyncGenerator
from .domain import AnalysisReport, AnalysisStatus, VideoMetadata
from .infrastructure import AIPipelineService

class AnalyzeVideoUseCase:
    def __init__(self, ai_service: AIPipelineService):
        self.ai_service = ai_service
        self.last_report = None

    async def execute(self, url: str) -> AsyncGenerator[AnalysisStatus, None]:
        if not url:
            raise ValueError("URL이 입력되지 않았습니다.")

        # Step 1: Matching
        yield AnalysisStatus.MATCHING
        video = await self.ai_service.match_video(url)

        # Step 2: STT & AV Analysis
        yield AnalysisStatus.STT_ANALYZING
        av_results = await self.ai_service.analyze_audio_visual()

        # Step 3: Fact Checking
        yield AnalysisStatus.FACT_CHECKING
        facts = await self.ai_service.fact_check()

        # Step 4: Finalize
        yield AnalysisStatus.COMPLETED
        
        report = AnalysisReport(
            video=video,
            status=AnalysisStatus.COMPLETED,
            deepfake_score=av_results["deepfake_score"],
            audio_spoofing_score=av_results["audio_spoofing_score"],
            fact_check_results=facts,
            summary="해당 영상은 일부 허위 사실을 포함하고 있을 가능성이 높습니다. 주의가 필요합니다."
        )
        self.last_report = report
