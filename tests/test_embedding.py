import math

from workspaces.embedding import EMBEDDING_DIM, cosine_similarity, embed


def test_embed_returns_fixed_dimension():
    """임베딩은 항상 고정 차원을 반환해야 함"""
    assert len(embed("정부지원금 신청하세요")) == EMBEDDING_DIM


def test_embed_is_deterministic():
    """동일 입력은 항상 동일 벡터를 반환해야 함"""
    assert embed("안전계좌로 이체하세요") == embed("안전계좌로 이체하세요")


def test_embed_is_l2_normalized():
    """벡터는 L2 정규화되어 크기가 1이어야 함"""
    vector = embed("검찰청 수사관입니다")
    norm = math.sqrt(sum(v * v for v in vector))
    assert math.isclose(norm, 1.0, rel_tol=1e-6)


def test_embed_empty_text_returns_zero_vector():
    """빈 문자열은 영벡터를 반환해야 함 (0으로 나누기 방지)"""
    assert embed("") == [0.0] * EMBEDDING_DIM


def test_similar_texts_have_higher_similarity():
    """유사한 문구가 무관한 문구보다 높은 유사도를 가져야 함"""
    base = embed("안전계좌로 즉시 이체하지 않으면 계좌가 동결됩니다")
    similar = embed("안전계좌로 이체하지 않으면 계좌가 동결될 수 있습니다")
    unrelated = embed("오늘 점심은 김치찌개 어떠신가요")

    assert cosine_similarity(base, similar) > cosine_similarity(base, unrelated)


def test_cosine_similarity_of_identical_vectors_is_one():
    """동일 벡터의 코사인 유사도는 1이어야 함"""
    vector = embed("대출 승인되었습니다")
    assert math.isclose(cosine_similarity(vector, vector), 1.0, rel_tol=1e-6)


def test_cosine_similarity_with_zero_vector_is_zero():
    """영벡터와의 유사도는 0이어야 함"""
    assert cosine_similarity(embed("대출"), [0.0] * EMBEDDING_DIM) == 0.0
