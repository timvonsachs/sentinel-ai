"""Tests for Endocrine System."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.systems.endocrine import EndocrineSystem


def test_hormone_add_and_get():
    endo = EndocrineSystem()
    endo.add_hormone("cortisol", base=0.3, min=0.0, max=1.0, speed=0.1)
    assert 0.0 <= endo.get("cortisol") <= 1.0


def test_regulator_updates_hormone():
    endo = EndocrineSystem()
    endo.add_hormone("cortisol", base=0.3, min=0.0, max=1.0, speed=0.1)
    endo.regulate("cortisol", lambda ctx: ctx.get("pain", 0))
    before = endo.get("cortisol")
    endo.update({"pain": 1.0})
    after = endo.get("cortisol")
    assert after >= before
