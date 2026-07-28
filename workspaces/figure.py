"""벡터 그래프를 Plotly Figure로 조립한다.

reflex를 import하지 않는다 — state.py가 이 모듈을 쓰고, 그래프 컴포넌트가
state.py를 쓰기 때문에 여기서 컴포넌트 쪽을 참조하면 순환 import가 된다.

좌표는 graph.py가 만든 3성분 투영값이다(설명분산 약 27%). 눈에 보이는
거리는 근거가 아니므로, 두 노드를 잇는 선은 오직 실제로 걸린 규칙과
코사인 검색 결과로만 그린다.

색만은 CSS 변수를 쓸 수 없다 — Plotly는 파이썬에서 Figure를 만들 때 색을
그대로 굽는다. 그래서 현재 테마의 리터럴 팔레트(styles.GRAPH_PALETTES)를
인자로 받고, 테마가 바뀌면 State가 Figure를 다시 만든다.
"""

from typing import List, Optional

import plotly.graph_objects as go

from . import styles
from .domain import GraphEdgeKind, GraphNode, GraphNodeKind, VectorGraph

_HOVER_WRAP = 26

_CASE_SIZE = 5
_CASE_LINKED_SIZE = 13
_RULE_SIZE = 6
_RULE_ACTIVE_SIZE = 13
_INPUT_SIZE = 18


def _wrap(text: str) -> str:
    """호버 툴팁은 자동 줄바꿈이 없어 직접 끊어 준다."""
    lines = [text[i : i + _HOVER_WRAP] for i in range(0, len(text), _HOVER_WRAP)]
    return "<br>".join(lines)


def _node_trace(
    nodes: List[GraphNode],
    name: str,
    color: str,
    size,
    symbol: str,
    opacity: float,
    line_color: str,
    line_width: float,
    hover_titles: List[str],
) -> go.Scatter3d:
    return go.Scatter3d(
        x=[node.x for node in nodes],
        y=[node.y for node in nodes],
        z=[node.z for node in nodes],
        mode="markers",
        name=name,
        marker={
            "size": size,
            "color": color,
            "symbol": symbol,
            "opacity": opacity,
            "line": {"color": line_color, "width": line_width},
        },
        customdata=[
            [title, _wrap(node.detail)] for title, node in zip(hover_titles, nodes)
        ],
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
        # 아직 등장하지 않은 노드 종류는 범례에서도 빼되 트레이스 자리는 남긴다.
        # 트레이스 순서가 단계마다 바뀌면 plotly가 다시 그릴 때 화면이 튄다.
        showlegend=bool(nodes),
    )


def _edge_trace(
    graph: VectorGraph, kind: GraphEdgeKind, name: str, color: str, width: float
) -> go.Scatter3d:
    """엣지는 좌표 사이에 None을 끼워 하나의 선 트레이스로 묶는다."""
    positions = {node.id: node for node in graph.nodes}
    x: List[Optional[float]] = []
    y: List[Optional[float]] = []
    z: List[Optional[float]] = []

    for edge in graph.edges:
        if edge.kind is not kind:
            continue
        source, target = positions.get(edge.source_id), positions.get(edge.target_id)
        if source is None or target is None:
            continue
        x += [source.x, target.x, None]
        y += [source.y, target.y, None]
        z += [source.z, target.z, None]

    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        name=name,
        line={"color": color, "width": width},
        hoverinfo="skip",
        showlegend=False,
    )


def build_figure(graph: VectorGraph, is_dark: bool = True) -> go.Figure:
    """현재까지 조립된 그래프를 그대로 그린다.

    엣지가 하나 추가될 때마다 Figure를 새로 만들지만, 트레이스 순서를 항상
    같게 유지하고 layout.uirevision을 고정해 두었기 때문에 사용자가 돌려놓은
    카메라 각도는 그대로 남는다. 테마를 바꿔 다시 그릴 때도 마찬가지다.
    """
    palette = styles.graph_palette(is_dark)
    linked = {edge.target_id for edge in graph.edges}

    # 선이 노드 뒤로 가도록 엣지를 먼저 깐다.
    traces: List[go.Scatter3d] = [
        _edge_trace(graph, GraphEdgeKind.RULE, "규칙 연결", palette["rule_edge"], 3),
        _edge_trace(graph, GraphEdgeKind.CASE, "사례 연결", palette["case_edge"], 4),
    ]

    for category, color in palette["categories"].items():
        nodes = [
            node
            for node in graph.nodes
            if node.kind is GraphNodeKind.CASE and node.label == category
        ]
        traces.append(
            _node_trace(
                nodes,
                name=category,
                color=color,
                # 연결된 사례만 키워, 25개 구름 속에서 어디가 근거인지 드러낸다.
                size=[
                    _CASE_LINKED_SIZE if node.id in linked else _CASE_SIZE
                    for node in nodes
                ],
                symbol="circle",
                opacity=0.9,
                line_color=palette["marker_outline"],
                line_width=1,
                hover_titles=[f"{category} 사례" for _ in nodes],
            )
        )

    rules = [node for node in graph.nodes if node.kind is GraphNodeKind.RULE]
    traces.append(
        _node_trace(
            [node for node in rules if not node.is_active],
            name="위험 신호 사전",
            color=palette["rule_inactive"],
            size=_RULE_SIZE,
            symbol="diamond",
            opacity=0.3,
            line_color="rgba(0,0,0,0)",
            line_width=0,
            hover_titles=[node.label for node in rules if not node.is_active],
        )
    )
    traces.append(
        _node_trace(
            [node for node in rules if node.is_active],
            name="걸린 위험 신호",
            color=palette["rule_active"],
            size=_RULE_ACTIVE_SIZE,
            symbol="diamond",
            opacity=1.0,
            line_color=palette["marker_outline"],
            line_width=1,
            hover_titles=[node.label for node in rules if node.is_active],
        )
    )

    user_input = [node for node in graph.nodes if node.kind is GraphNodeKind.INPUT]
    traces.append(
        _node_trace(
            user_input,
            name="입력 문구",
            color=palette["input_node"],
            size=_INPUT_SIZE,
            symbol="circle",
            opacity=1.0,
            line_color=palette["marker_outline"],
            line_width=2,
            hover_titles=["입력 문구" for _ in user_input],
        )
    )

    figure = go.Figure(data=traces)
    figure.update_layout(_layout(palette))
    return figure


_HIDDEN_AXIS = {
    "visible": False,
    "showgrid": False,
    "zeroline": False,
    "showspikes": False,
}

def _layout(palette: dict) -> dict:
    return {
        "scene": {
            "xaxis": _HIDDEN_AXIS,
            "yaxis": _HIDDEN_AXIS,
            "zaxis": _HIDDEN_AXIS,
            # 바탕을 비워 페이지의 테마 색이 그대로 비치게 한다.
            "bgcolor": "rgba(0,0,0,0)",
            "aspectmode": "cube",
            "camera": {"eye": {"x": 1.45, "y": 1.45, "z": 1.0}},
            "dragmode": "orbit",
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
        "showlegend": True,
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 0,
            "xanchor": "center",
            "x": 0.5,
            "font": {
                "size": 11,
                "color": palette["text"],
                "family": styles.FONT_FAMILY,
            },
            "bgcolor": palette["legend_bg"],
            "borderwidth": 0,
            "itemsizing": "constant",
        },
        "hoverlabel": {
            "bgcolor": palette["hover_bg"],
            "bordercolor": palette["hover_border"],
            "font": {
                "size": 12,
                "color": palette["hover_text"],
                "family": styles.FONT_FAMILY,
            },
            "align": "left",
        },
        "font": {"family": styles.FONT_FAMILY, "color": palette["text"]},
        # 단계마다, 그리고 테마를 바꿔 다시 그릴 때도 카메라·범례 상태를
        # 유지시키는 열쇠.
        "uirevision": "baekui-vector-graph",
    }


def empty_figure(is_dark: bool = True) -> go.Figure:
    """노드도 엣지도 없는, 그러나 레이아웃은 갖춘 그래프.

    State의 초기값으로 쓴다. 맨 go.Figure()를 두면 아직 아무것도 안 그린
    시점에 레이아웃 없는 Figure가 남아, 테마와 무관한 기본 흰 배경이 잠깐
    비칠 수 있다.
    """
    return build_figure(VectorGraph(), is_dark)
