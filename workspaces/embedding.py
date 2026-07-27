"""외부 API 없이 동작하는 결정론적 텍스트 임베딩.

문자 3-gram을 해싱해 고정 차원 버킷에 누적한 뒤 L2 정규화한다.
동일 입력은 항상 동일 벡터를 반환하며, 유사한 문구는 공유하는
n-gram이 많아 높은 코사인 유사도를 갖는다.
추후 Gemini Embedding 호출로 교체할 때 이 모듈만 수정하면 된다.
"""

import hashlib
import math
import re
from typing import List

EMBEDDING_DIM = 64
_NGRAM_SIZE = 3
_NON_WORD = re.compile(r"[^0-9a-z가-힣]+")


def _normalize(text: str) -> str:
    return _NON_WORD.sub("", text.lower())


def _bucket(ngram: str) -> int:
    digest = hashlib.md5(ngram.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % EMBEDDING_DIM


def embed(text: str) -> List[float]:
    """텍스트를 L2 정규화된 EMBEDDING_DIM 차원 벡터로 변환한다."""
    normalized = _normalize(text)
    vector = [0.0] * EMBEDDING_DIM

    for i in range(len(normalized) - _NGRAM_SIZE + 1):
        vector[_bucket(normalized[i : i + _NGRAM_SIZE])] += 1.0

    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0.0:
        return vector
    return [v / norm for v in vector]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """두 벡터의 코사인 유사도를 반환한다. 영벡터가 있으면 0.0."""
    norm_a = math.sqrt(sum(v * v for v in a))
    norm_b = math.sqrt(sum(v * v for v in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)
