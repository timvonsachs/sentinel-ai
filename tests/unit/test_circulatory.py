"""Tests for Circulatory System."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.systems.circulatory import CirculatorySystem, StatePacket


def test_pump_updates_state():
    circ = CirculatorySystem()
    circ.pump(StatePacket(source="immune", type="alert", data={"x": 1}, priority=2))
    st = circ.state()
    assert "immune.alert" in st
    assert st["immune.alert"]["data"]["x"] == 1


def test_subscribe_receives_packet():
    circ = CirculatorySystem()
    hit = {"ok": False}

    def handler(_packet):
        hit["ok"] = True

    circ.subscribe("endo", handler, filter_type="alert")
    circ.pump(StatePacket(source="immune", type="alert", data={}))
    assert hit["ok"] is True
