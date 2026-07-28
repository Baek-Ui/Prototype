import math

import pytest

from workspaces.domain import GraphNodeKind
from workspaces.embedding import embed
from workspaces.graph import (
    build_case_nodes,
    build_rule_nodes,
    fit_projection,
    project,
    rule_node_id,
)
from workspaces.repository import MockPhishingRepository
from workspaces.rules import RULES


@pytest.fixture
def cases():
    return MockPhishingRepository()._cases


@pytest.fixture
def projection(cases):
    return fit_projection([case.embedding for case in cases])


def test_fit_projection_yields_three_axes(projection):
    """투영은 3개의 주성분 축을 내놓아야 함"""
    assert len(projection.axes) == 3
    assert all(len(axis) == len(projection.mean) for axis in projection.axes)


def test_fit_projection_is_deterministic(cases):
    """같은 임베딩 집합은 언제나 같은 축을 만들어야 함 (SVD 부호 고정)"""
    embeddings = [case.embedding for case in cases]
    assert fit_projection(embeddings) == fit_projection(embeddings)


def test_axes_are_orthonormal(projection):
    """주성분 축은 정규직교여야 함"""
    for axis in projection.axes:
        assert math.isclose(sum(v * v for v in axis), 1.0, abs_tol=1e-9)

    first, second, third = projection.axes
    for a, b in ((first, second), (first, third), (second, third)):
        assert math.isclose(sum(x * y for x, y in zip(a, b)), 0.0, abs_tol=1e-9)


def test_fit_projection_rejects_too_few_embeddings():
    """주성분 3개를 뽑을 수 없는 입력은 거부해야 함"""
    with pytest.raises(ValueError):
        fit_projection([embed("문구 하나"), embed("문구 둘")])


def test_project_returns_finite_coordinates(projection):
    """투영 좌표는 항상 유한한 실수여야 함"""
    coords = project(projection, embed("안전계좌로 즉시 이체하세요"))
    assert len(coords) == 3
    assert all(math.isfinite(value) for value in coords)


def test_project_is_deterministic(projection):
    """같은 임베딩은 언제나 같은 좌표로 가야 함"""
    embedding = embed("검찰 수사관입니다")
    assert project(projection, embedding) == project(projection, embedding)


def test_identical_texts_land_on_the_same_point(projection, cases):
    """시드 사례와 글자까지 같은 입력은 그 사례 노드 위에 놓여야 함"""
    case = cases[0]
    node = build_case_nodes([case], projection)[0]
    x, y, z = project(projection, embed(case.text))

    assert (
        math.isclose(x, node.x, abs_tol=1e-9)
        and math.isclose(y, node.y, abs_tol=1e-9)
        and math.isclose(z, node.z, abs_tol=1e-9)
    )


def test_build_case_nodes_covers_every_case(projection, cases):
    """사례 하나당 노드 하나가 만들어져야 함"""
    nodes = build_case_nodes(cases, projection)

    assert len(nodes) == len(cases)
    assert {node.id for node in nodes} == {case.id for case in cases}
    assert all(node.kind is GraphNodeKind.CASE for node in nodes)
    assert all(node.detail for node in nodes)


def test_build_rule_nodes_covers_every_rule(projection):
    """규칙 하나당 노드 하나가 만들어지고 처음에는 모두 꺼져 있어야 함"""
    nodes = build_rule_nodes(projection)

    assert len(nodes) == len(RULES)
    assert [node.id for node in nodes] == [rule_node_id(i) for i in range(len(RULES))]
    assert [node.label for node in nodes] == [rule.keyword for rule in RULES]
    assert all(node.kind is GraphNodeKind.RULE for node in nodes)
    assert not any(node.is_active for node in nodes)


def test_rule_and_case_nodes_share_one_coordinate_space(projection, cases):
    """규칙 노드가 사례 구름에서 멀리 튀어나가면 한 화면에 담기지 않는다"""
    case_nodes = build_case_nodes(cases, projection)
    rule_nodes = build_rule_nodes(projection)

    span = max(
        abs(value)
        for node in case_nodes
        for value in (node.x, node.y, node.z)
    )
    assert all(
        abs(value) <= span * 1.5
        for node in rule_nodes
        for value in (node.x, node.y, node.z)
    )
