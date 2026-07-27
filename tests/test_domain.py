import pytest
from workspaces.domain import RiskLevel


@pytest.mark.parametrize(
    "score,expected",
    [
        (0, RiskLevel.SAFE),
        (39, RiskLevel.SAFE),
        (40, RiskLevel.CAUTION),
        (69, RiskLevel.CAUTION),
        (70, RiskLevel.DANGER),
        (100, RiskLevel.DANGER),
    ],
)
def test_risk_level_from_score(score, expected):
    """점수 구간에 따라 위험 등급이 정확히 매핑되어야 함"""
    assert RiskLevel.from_score(score) == expected


def test_risk_level_rejects_out_of_range():
    """0~100 범위를 벗어난 점수는 거부되어야 함"""
    with pytest.raises(ValueError):
        RiskLevel.from_score(101)
    with pytest.raises(ValueError):
        RiskLevel.from_score(-1)
