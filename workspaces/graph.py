"""64차원 임베딩을 3차원으로 투영해 벡터 그래프 좌표를 만든다.

투영 축은 시드 **사례** 임베딩만으로 적합한 상위 3개 주성분이다. 규칙
키워드와 사용자 입력은 같은 축에 얹기만 한다 — 입력이 들어올 때마다
축이 흔들리면 같은 사례가 매번 다른 자리로 튀기 때문이다.

이 좌표가 무엇이 아닌지 알고 쓸 것: 25개 시드로 적합한 상위 3성분의
설명분산은 약 27%다. embedding.py가 밝힌 대로 64개 버킷에 636개
3-gram이 충돌하면서 생긴 0.35 근처의 유사도 바닥이 여기에도 그대로
남아 있어, **3D 거리 순서는 실제 64차원 코사인 순서와 일치하지 않는다.**
그래서 노드 사이의 엣지는 눈에 보이는 거리가 아니라 repository의
코사인 검색 결과로만 그린다. 좌표는 배치이고, 엣지가 판단이다.
"""

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np

from .domain import GraphNode, GraphNodeKind, PhishingCase
from .embedding import embed
from .rules import RULES

_COMPONENTS = 3


@dataclass(frozen=True)
class Projection:
    """시드 코퍼스에 적합된 PCA 축."""

    mean: List[float]
    axes: List[List[float]]  # _COMPONENTS x EMBEDDING_DIM
    explained_variance: float


def fit_projection(embeddings: Sequence[Sequence[float]]) -> Projection:
    """임베딩 집합의 상위 3개 주성분을 구한다."""
    matrix = np.asarray(embeddings, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] < _COMPONENTS:
        raise ValueError(f"주성분 {_COMPONENTS}개를 뽑으려면 최소 {_COMPONENTS}개의 임베딩이 필요합니다.")

    mean = matrix.mean(axis=0)
    centered = matrix - mean
    _, singular, components = np.linalg.svd(centered, full_matrices=False)

    axes = components[:_COMPONENTS]
    # SVD는 성분의 부호를 보장하지 않는다. 같은 입력에 같은 좌표가 나오도록
    # 절댓값이 가장 큰 성분이 양수가 되게 고정한다.
    signs = np.sign(axes[np.arange(_COMPONENTS), np.abs(axes).argmax(axis=1)])
    signs[signs == 0] = 1.0
    axes = axes * signs[:, np.newaxis]

    variance = singular**2
    explained = float(variance[:_COMPONENTS].sum() / variance.sum()) if variance.sum() else 0.0

    return Projection(
        mean=mean.tolist(),
        axes=axes.tolist(),
        explained_variance=explained,
    )


def project(projection: Projection, embedding: Sequence[float]) -> Tuple[float, float, float]:
    """임베딩 하나를 적합된 축 위의 3차원 좌표로 옮긴다."""
    centered = np.asarray(embedding, dtype=float) - np.asarray(projection.mean)
    x, y, z = np.asarray(projection.axes) @ centered
    return float(x), float(y), float(z)


def build_case_nodes(
    cases: Sequence[PhishingCase], projection: Projection
) -> List[GraphNode]:
    """시드 사례 하나당 노드 하나. 라벨은 카테고리, 상세는 원문."""
    nodes = []
    for case in cases:
        x, y, z = project(projection, case.embedding)
        nodes.append(
            GraphNode(
                id=case.id,
                label=case.category.value,
                kind=GraphNodeKind.CASE,
                x=x,
                y=y,
                z=z,
                detail=case.text,
                is_phishing=case.is_phishing,
            )
        )
    return nodes


def build_rule_nodes(projection: Projection) -> List[GraphNode]:
    """규칙 사전의 신호 하나당 노드 하나.

    키워드는 문장보다 훨씬 짧아 3-gram이 몇 개 되지 않는다. 그래서 규칙
    노드는 사례 구름의 바깥 언저리에 성기게 흩어지는데, 이 배치 자체가
    "신호는 문구가 아니라 문구를 재는 잣대"라는 걸 보여줘서 그대로 둔다.
    """
    nodes = []
    for index, rule in enumerate(RULES):
        x, y, z = project(projection, embed(rule.keyword))
        nodes.append(
            GraphNode(
                id=rule_node_id(index),
                label=rule.keyword,
                kind=GraphNodeKind.RULE,
                x=x,
                y=y,
                z=z,
                detail=rule.description,
            )
        )
    return nodes


def rule_node_id(index: int) -> str:
    """규칙 노드 id는 RULES의 순번으로 만든다 — 키워드 중복에 흔들리지 않는다."""
    return f"rule-{index:02d}"
