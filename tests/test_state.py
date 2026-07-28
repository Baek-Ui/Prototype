"""State 계층 테스트 — 도메인 리포트를 UI 모양으로 옮기는 부분.

Reflex는 앱 안에서 State를 직접 생성하는 것을 막지만 테스트 환경에서는
허용한다(BaseState.__init__의 is_testing_env 분기).
"""

import pytest

from workspaces.state import State, _to_segments
from workspaces.domain import TextHighlight

PHISHING_TEXT = (
    "[Web발신] 서울중앙지검 수사관입니다. 안전계좌로 즉시 이체하지 않으면 "
    "계좌가 동결됩니다. http://bit.ly/x 계좌 110-123-456789"
)
NORMAL_TEXT = "안녕하세요, 내일 회의 시간 오후 3시로 변경 가능할까요?"


async def _detect(text: str) -> State:
    state = State()
    state.input_text = text
    async for _ in state.detect():
        pass
    return state


def test_to_segments_round_trips_the_original_text():
    """조각을 도로 이으면 원문이 나와야 함 — 글자가 새거나 겹치면 안 된다"""
    text = "안전계좌로 즉시 이체하세요"
    highlights = [
        TextHighlight(0, 4, "안전계좌", 35),
        TextHighlight(6, 8, "긴급성 강조", 15),
    ]
    segments = _to_segments(text, highlights)

    assert "".join(segment.text for segment in segments) == text
    assert [s.text for s in segments if s.is_flagged] == ["안전계좌", "즉시"]


def test_to_segments_without_highlights_is_one_plain_chunk():
    """부각할 게 없으면 통짜 한 조각이어야 함"""
    segments = _to_segments(NORMAL_TEXT, [])

    assert len(segments) == 1
    assert segments[0].text == NORMAL_TEXT
    assert not segments[0].is_flagged


@pytest.mark.asyncio
async def test_detect_fills_report_and_kpis():
    """분석이 끝나면 리포트와 KPI가 모두 채워져야 함"""
    state = await _detect(PHISHING_TEXT)

    assert state.has_started is True
    assert state.is_detecting is False
    assert state.error_message == ""
    assert state.risk_level == "위험"
    assert state.signal_count == len(state.evidences)
    assert state.max_signal_weight == max(e.weight for e in state.evidences)
    assert state.attack_type == "기관사칭"
    assert 0 < state.attack_similarity <= 100
    assert len(state.similar_cases) == 3
    assert state.recommended_actions


@pytest.mark.asyncio
async def test_detect_leaves_segments_matching_the_masked_text():
    """부각 조각을 이으면 화면에 보이는 마스킹된 문구와 같아야 함"""
    state = await _detect(PHISHING_TEXT)

    assert "".join(s.text for s in state.text_segments) == state.masked_text
    assert any(s.is_flagged for s in state.text_segments)
    # 개인정보는 가려진 채로 부각된다
    assert "456789" not in state.masked_text
    assert any(s.text == "[링크]" and s.is_flagged for s in state.text_segments)


@pytest.mark.asyncio
async def test_detect_builds_a_figure_with_a_stable_trace_count():
    """그래프는 단계와 무관하게 트레이스 수가 고정이어야 함 (plotly 재렌더 튐 방지)"""
    state = await _detect(PHISHING_TEXT)

    assert len(state.graph_figure.data) == 10
    assert state.graph_figure.layout.uirevision == "baekui-vector-graph"
    assert state.current_step == 5


@pytest.mark.asyncio
async def test_normal_text_reports_no_attack_type():
    """정상 문구는 신호도 수법 유형도 없어야 함"""
    state = await _detect(NORMAL_TEXT)

    assert state.risk_level == "안전"
    assert state.signal_count == 0
    assert state.max_signal_weight == 0
    assert state.attack_type == "해당 없음"
    assert state.attack_similarity == 0
    assert not any(s.is_flagged for s in state.text_segments)


@pytest.mark.asyncio
async def test_blank_input_does_not_open_the_analysis_section():
    """빈 입력은 안내만 남기고 결과 섹션을 열지 않아야 함"""
    state = State()
    state.input_text = "   "
    async for _ in state.detect():
        pass

    assert state.has_started is False
    assert state.error_message == "분석할 문구를 입력해주세요."


def test_theme_defaults_to_dark():
    """rxconfig의 appearance='dark'와 서버 쪽 기본값이 어긋나면 안 됨"""
    assert State().is_dark is True


def test_flip_theme_repaints_the_graph():
    """테마를 뒤집으면 그래프도 새 팔레트로 다시 그려져야 함"""
    state = State()
    dark_colors = _legend_font_color(state)

    state.flip_theme()
    assert state.is_dark is False
    light_colors = _legend_font_color(state)

    assert dark_colors != light_colors

    state.flip_theme()
    assert state.is_dark is True
    assert _legend_font_color(state) == dark_colors


def test_flip_theme_returns_no_event():
    """프론트 Var를 백엔드 핸들러 반환값으로 내보내면 안 됨

    rx.toggle_color_mode는 ColorModeContext를 읽는 프론트 Var라 이벤트로
    변환되지 않는다. 여기서 돌려주면 전환할 때마다 오류 팝업이 뜬다 —
    실제 색 전환은 버튼 on_click 체인이 맡는다.
    """
    assert State().flip_theme() is None


def test_sync_color_mode_follows_saved_preference():
    """localStorage에 라이트가 남아 있으면 서버도 라이트로 맞춰야 함"""
    state = State()
    state.sync_color_mode("light")
    assert state.is_dark is False

    state.sync_color_mode("dark")
    assert state.is_dark is True


def _legend_font_color(state: State) -> str:
    return state.graph_figure.layout.legend.font.color


@pytest.mark.asyncio
async def test_detect_uses_the_current_theme_palette():
    """분석 중 만들어지는 그래프도 현재 테마를 따라야 함"""
    state = State()
    state.flip_theme()  # 라이트로
    state.input_text = NORMAL_TEXT
    async for _ in state.detect():
        pass

    light = _legend_font_color(state)
    state.flip_theme()  # 다시 다크
    assert _legend_font_color(state) != light


def test_backend_graph_var_is_not_shared_between_instances():
    """_last_graph 기본값이 인스턴스 간에 공유되면 한 사용자의 그래프가 샌다"""
    first, second = State(), State()
    first._last_graph.nodes.append(object())

    assert second._last_graph.nodes == []


@pytest.mark.asyncio
async def test_reset_analysis_clears_everything():
    """다시 분석하기는 입력과 결과를 모두 비워야 함"""
    state = await _detect(PHISHING_TEXT)
    state.reset_analysis()

    assert state.input_text == ""
    assert state.has_started is False
    assert state.risk_score == 0
    assert state.text_segments == []
    assert state.evidences == []
    assert state.attack_type == ""
