"""Tests for Chameleon Adaptation."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.capabilities.chameleon import ChameleonAdaptation


def test_default_params_when_no_context():
    ch = ChameleonAdaptation()
    ch.set_defaults(temperature=0.7)
    params = ch.adapt({"sentiment": 0.1})
    assert params["temperature"] == 0.7


def test_context_override():
    ch = ChameleonAdaptation()
    ch.set_defaults(temperature=0.7)
    ch.context("angry", lambda s: 1.0 if s.get("sentiment", 0) < -0.5 else 0.0, {"temperature": 0.3})
    params = ch.adapt({"sentiment": -0.9})
    assert params["temperature"] == 0.3
    assert ch.current() == "angry"
