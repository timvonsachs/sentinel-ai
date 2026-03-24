"""Tests for Phoenix Metamorphosis."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.transcendence.phoenix import PhoenixMetamorphosis


def test_form_and_metamorphose():
    p = PhoenixMetamorphosis()
    p.form("chat", {"temperature": 0.7})
    p.form("analysis", {"temperature": 0.2})
    ok = p.metamorphose("analysis", reason="analysis task")
    assert ok is True
    assert p.current_form == "analysis"


def test_best_form():
    p = PhoenixMetamorphosis()
    p.form("a", {"x": 1})
    p.form("b", {"x": 2})
    p.add_evaluator("a", lambda _ctx: 0.2)
    p.add_evaluator("b", lambda _ctx: 0.8)
    assert p.best_form({}) == "b"
