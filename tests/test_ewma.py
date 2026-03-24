from sentinel.core.ewma import EWMABaseline


def test_ewma_initial_observation_has_zero_zscore():
    ewma = EWMABaseline()
    obs = ewma.observe(1.0)
    assert obs.z_score == 0.0
