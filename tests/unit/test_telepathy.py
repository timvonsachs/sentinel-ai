"""Tests for Telepathy Bridge."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.transcendence.telepathy import TelepathyBridge


def test_encode_and_recall():
    a = TelepathyBridge("a")
    a.encode_experience("sales", "insight", {"lift": 0.2}, confidence=0.9)
    rec = a.recall("sales")
    assert len(rec) == 1
    assert rec[0].source == "a"


def test_transfer():
    a = TelepathyBridge("a")
    b = TelepathyBridge("b")
    a.encode_experience("sales", "insight", {"lift": 0.2}, confidence=0.9)
    a.transfer_to(b, domain="sales", min_confidence=0.5)
    assert len(b.received) == 1
