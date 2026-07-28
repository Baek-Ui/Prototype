"""보이스피싱 탐지 유즈케이스.

각 단계 완료 시 DetectionStatus를 yield해 UI가 진행 상황을 실시간으로
표시할 수 있게 한다. async generator는 async for 소비자에게 반환값을
전달할 수 없으므로 최종 리포트는 last_report에, 그때까지 조립된 벡터
그래프는 graph_snapshot에 담아 둔다.
"""

import asyncio
import copy
from typing import AsyncGenerator, List, Optional

from .detector import (
    combine_scores,
    find_highlights,
    infer_attack_type,
    preprocess,
    recommend_actions,
    score_by_rules,
    score_by_similarity,
)
from .domain import (
    DetectionReport,
    DetectionStatus,
    GraphEdge,
    GraphEdgeKind,
    GraphNode,
    GraphNodeKind,
    RiskLevel,
    VectorGraph,
)
from .embedding import embed
from .graph import build_case_nodes, build_rule_nodes, fit_projection, project, rule_node_id
from .repository import PhishingRepository
from .rules import RULES

_STEP_DELAY = 0.4  # 단계별 진행 상황을 사용자가 인지할 수 있게 하는 최소 지연
_EDGE_DELAY = 0.35  # 유사 사례 엣지가 한 줄씩 그어지는 간격

INPUT_NODE_ID = "input"


class DetectPhishingUseCase:
    def __init__(self, repository: PhishingRepository):
        self.repository = repository
        self.last_report: Optional[DetectionReport] = None
        self._graph = VectorGraph()
        self._base_nodes: Optional[List[GraphNode]] = None
        self._projection = None

    @property
    def graph_snapshot(self) -> VectorGraph:
        """지금까지 조립된 그래프의 사본.

        소비자가 매 단계 화면을 다시 그리는 동안 다음 단계가 같은 객체를
        수정하면 이전 프레임까지 소급해 바뀐다. 그래서 복사본을 준다.
        """
        return copy.deepcopy(self._graph)

    async def _ensure_layout(self) -> None:
        """사례·규칙 노드의 고정 배치를 한 번만 계산한다.

        생성자를 async로 만들 수 없어 첫 실행 때 지연 준비한다.
        """
        if self._base_nodes is not None:
            return
        cases = await self.repository.list_all_cases()
        self._projection = fit_projection([case.embedding for case in cases])
        self._base_nodes = build_case_nodes(cases, self._projection) + build_rule_nodes(
            self._projection
        )

    async def execute(self, text: str) -> AsyncGenerator[DetectionStatus, None]:
        if not text or not text.strip():
            raise ValueError("분석할 문구를 입력해주세요.")

        await self._ensure_layout()
        self._graph = VectorGraph(nodes=copy.deepcopy(self._base_nodes))

        yield DetectionStatus.PREPROCESSING
        await asyncio.sleep(_STEP_DELAY)
        masked = preprocess(text)

        # 그래프를 바꾸는 단계는 상태를 두 번 yield한다. 먼저 "이 단계 진행 중"을
        # 알려 스테퍼를 움직이고, 작업을 끝낸 뒤 같은 상태를 다시 보내 그래프가
        # 아직 그 단계에 머무는 동안 갱신되게 한다. 한 번만 yield하면 노드가
        # 다음 단계 이름표 아래에서 나타나 화면과 설명이 어긋난다.
        yield DetectionStatus.VECTORIZING
        await asyncio.sleep(_STEP_DELAY)
        embedding = embed(text)
        x, y, z = project(self._projection, embedding)
        self._graph.nodes.append(
            GraphNode(
                id=INPUT_NODE_ID,
                label="입력 문구",
                kind=GraphNodeKind.INPUT,
                x=x,
                y=y,
                z=z,
                detail=masked,
            )
        )
        yield DetectionStatus.VECTORIZING
        await asyncio.sleep(_STEP_DELAY)

        yield DetectionStatus.RULE_SCORING
        await asyncio.sleep(_STEP_DELAY)
        rule_score, evidences = score_by_rules(text)
        self._connect_rules(evidences)
        yield DetectionStatus.RULE_SCORING
        await asyncio.sleep(_STEP_DELAY)

        yield DetectionStatus.SIMILARITY_SEARCH
        await asyncio.sleep(_STEP_DELAY)
        similar_cases = await self.repository.search_similar(embedding, top_k=3)
        # 엣지를 한 줄씩 그으며 같은 상태를 다시 yield한다 — 소비자는 매번
        # graph_snapshot을 다시 읽으므로 연결되는 과정이 그대로 화면에 흐른다.
        for item in similar_cases:
            self._graph.edges.append(
                GraphEdge(
                    source_id=INPUT_NODE_ID,
                    target_id=item.case.id,
                    kind=GraphEdgeKind.CASE,
                    strength=item.similarity,
                )
            )
            yield DetectionStatus.SIMILARITY_SEARCH
            await asyncio.sleep(_EDGE_DELAY)

        yield DetectionStatus.JUDGING
        await asyncio.sleep(_STEP_DELAY)
        risk_score = combine_scores(rule_score, score_by_similarity(similar_cases))
        risk_level = RiskLevel.from_score(risk_score)
        attack_type, attack_similarity = infer_attack_type(similar_cases, risk_level)

        self.last_report = DetectionReport(
            input_text=masked,
            risk_score=risk_score,
            risk_level=risk_level,
            evidences=evidences,
            similar_cases=similar_cases,
            recommended_actions=recommend_actions(risk_level),
            highlights=find_highlights(masked, evidences),
            attack_type=attack_type,
            attack_similarity=attack_similarity,
        )

        yield DetectionStatus.COMPLETED

    def _connect_rules(self, evidences) -> None:
        """걸린 규칙 노드를 켜고 입력 노드와 잇는다."""
        fired = {evidence.keyword for evidence in evidences}
        by_id = {node.id: node for node in self._graph.nodes}

        for index, rule in enumerate(RULES):
            if rule.keyword not in fired:
                continue
            node = by_id[rule_node_id(index)]
            node.is_active = True
            self._graph.edges.append(
                GraphEdge(
                    source_id=INPUT_NODE_ID,
                    target_id=node.id,
                    kind=GraphEdgeKind.RULE,
                    strength=rule.weight,
                )
            )
