from itertools import groupby

import pytest

from workspaces.domain import DetectionStatus, GraphEdgeKind, GraphNodeKind, RiskLevel
from workspaces.repository import MockPhishingRepository
from workspaces.usecases import INPUT_NODE_ID, DetectPhishingUseCase

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
    """분석 단계가 정해진 순서대로 진행되어야 함

    같은 상태가 연달아 여러 번 나오는 것은 정상이다 — 그래프가 그려지는
    동안 소비자를 다시 깨우기 위한 것이라 횟수는 연출에 따라 달라진다.
    검사할 것은 단계가 건너뛰거나 되돌아가지 않는다는 사실이다.
    """
    use_case = _use_case()
    statuses = await _run(use_case, PHISHING_TEXT)

    assert [key for key, _ in groupby(statuses)] == [
        DetectionStatus.PREPROCESSING,
        DetectionStatus.VECTORIZING,
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


@pytest.mark.asyncio
async def test_graph_grows_monotonically_through_the_pipeline():
    """그래프는 단계가 진행되는 동안 줄어들지 않아야 함"""
    use_case = _use_case()
    counts = []
    async for _ in use_case.execute(PHISHING_TEXT):
        graph = use_case.graph_snapshot
        counts.append((len(graph.nodes), len(graph.edges)))

    assert counts == sorted(counts)
    assert counts[-1][1] > counts[0][1]


@pytest.mark.asyncio
async def test_graph_snapshot_is_not_mutated_by_later_steps():
    """앞 단계에서 받아 둔 스냅샷이 뒤 단계 때문에 바뀌면 안 됨"""
    use_case = _use_case()
    generator = use_case.execute(PHISHING_TEXT)

    await generator.__anext__()  # PREPROCESSING
    early = use_case.graph_snapshot
    early_edges = len(early.edges)

    async for _ in generator:
        pass

    assert len(early.edges) == early_edges
    assert len(use_case.graph_snapshot.edges) > early_edges


@pytest.mark.asyncio
async def test_graph_edges_link_input_to_fired_rules_and_similar_cases():
    """엣지는 입력 노드에서 출발해 실제로 걸린 규칙·검색된 사례로만 이어져야 함"""
    use_case = _use_case()
    await _run(use_case, PHISHING_TEXT)

    graph = use_case.graph_snapshot
    report = use_case.last_report
    node_ids = {node.id for node in graph.nodes}

    assert all(edge.source_id == INPUT_NODE_ID for edge in graph.edges)
    assert all(edge.target_id in node_ids for edge in graph.edges)

    rule_edges = [e for e in graph.edges if e.kind is GraphEdgeKind.RULE]
    active = [n for n in graph.nodes if n.kind is GraphNodeKind.RULE and n.is_active]
    assert len(rule_edges) == len(active) == len(report.evidences)

    case_edges = [e for e in graph.edges if e.kind is GraphEdgeKind.CASE]
    assert {e.target_id for e in case_edges} == {
        item.case.id for item in report.similar_cases
    }


@pytest.mark.asyncio
async def test_normal_text_lights_up_no_rule_nodes():
    """정상 문구는 규칙 노드를 하나도 켜지 않아야 함"""
    use_case = _use_case()
    await _run(use_case, NORMAL_TEXT)

    graph = use_case.graph_snapshot
    assert not [e for e in graph.edges if e.kind is GraphEdgeKind.RULE]
    assert not [n for n in graph.nodes if n.is_active]


@pytest.mark.asyncio
async def test_case_node_layout_is_stable_across_runs():
    """같은 저장소라면 사례 노드의 좌표가 실행마다 같아야 함"""
    first, second = _use_case(), _use_case()
    await _run(first, PHISHING_TEXT)
    await _run(second, NORMAL_TEXT)

    def case_coords(use_case):
        return {
            node.id: (node.x, node.y, node.z)
            for node in use_case.graph_snapshot.nodes
            if node.kind is GraphNodeKind.CASE
        }

    assert case_coords(first) == case_coords(second)
