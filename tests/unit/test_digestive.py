"""Tests for Digestive System."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.systems.digestive import DigestiveSystem


def test_digest_returns_processed_payload():
    ds = DigestiveSystem()
    res = ds.digest("hello world")
    assert res.safe is True
    assert res.processed == "hello world"


def test_filter_can_modify_text():
    ds = DigestiveSystem()
    ds.add_filter("redact", lambda t: (t.replace("secret", "[REDACTED]"), ["redacted"]))
    res = ds.digest("this is secret")
    assert "[REDACTED]" in res.processed
    assert "redacted" in res.waste
