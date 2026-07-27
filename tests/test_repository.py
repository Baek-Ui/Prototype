import pytest

from workspaces.domain import PhishingCategory
from workspaces.embedding import EMBEDDING_DIM, embed
from workspaces.repository import MockPhishingRepository


@pytest.mark.asyncio
async def test_list_all_cases_returns_seed_data():
    """시드 데이터가 충분히 로드되어야 함"""
    repo = MockPhishingRepository()
    cases = await repo.list_all_cases()
    assert len(cases) >= 20


@pytest.mark.asyncio
async def test_all_cases_have_embeddings():
    """모든 사례는 고정 차원 임베딩을 보유해야 함 (3D 시각화 확장 전제)"""
    repo = MockPhishingRepository()
    for case in await repo.list_all_cases():
        assert len(case.embedding) == EMBEDDING_DIM


@pytest.mark.asyncio
async def test_seed_contains_all_categories():
    """5개 카테고리가 모두 포함되어야 함 (정상 대조군 포함)"""
    repo = MockPhishingRepository()
    categories = {case.category for case in await repo.list_all_cases()}
    assert categories == set(PhishingCategory)


@pytest.mark.asyncio
async def test_normal_cases_are_not_phishing():
    """정상 카테고리 사례는 is_phishing이 False여야 함"""
    repo = MockPhishingRepository()
    for case in await repo.list_all_cases():
        if case.category is PhishingCategory.NORMAL:
            assert case.is_phishing is False
        else:
            assert case.is_phishing is True


@pytest.mark.asyncio
async def test_search_similar_respects_top_k():
    """요청한 개수만큼만 반환해야 함"""
    repo = MockPhishingRepository()
    results = await repo.search_similar(embed("검찰청입니다"), top_k=3)
    assert len(results) == 3


@pytest.mark.asyncio
async def test_search_similar_is_sorted_descending():
    """유사도 내림차순으로 정렬되어야 함"""
    repo = MockPhishingRepository()
    results = await repo.search_similar(embed("안전계좌로 이체하세요"), top_k=5)
    similarities = [r.similarity for r in results]
    assert similarities == sorted(similarities, reverse=True)


@pytest.mark.asyncio
async def test_search_similar_finds_relevant_category():
    """기관사칭 문구를 검색하면 최상위 결과가 보이스피싱 사례여야 함"""
    repo = MockPhishingRepository()
    results = await repo.search_similar(
        embed("서울중앙지검 수사관입니다. 안전계좌로 이체하지 않으면 계좌가 동결됩니다"),
        top_k=1,
    )
    assert results[0].case.is_phishing is True
