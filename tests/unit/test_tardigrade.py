"""Tests for Tardigrade Hibernation."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism
from sentinel.capabilities.tardigrade import TardigradeHibernation


def test_enter_and_exit_hibernation():
    t = TardigradeHibernation()
    body = Organism("hib-test")
    t.enter(body)
    assert t.is_hibernating is True
    restored = t.exit()
    assert t.is_hibernating is False
    assert isinstance(restored, dict)


def test_should_hibernate_condition():
    t = TardigradeHibernation()
    t.hibernate_when(lambda org: org.name == "x")
    assert t.should_hibernate(Organism("x")) is True
