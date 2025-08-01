import sys
import types
from pathlib import Path

# Stub external modules before importing the module under test
trans_mod = types.ModuleType("transformers")
trans_mod.pipeline = object
sys.modules.setdefault("transformers", trans_mod)

config_mod = types.ModuleType("src.config")
config_mod.settings = types.SimpleNamespace(
    merge_gap_seconds=0.5,
    max_segment_chars=10,
    voxtral_model="x",
    voxtral_device="cpu",
)
logger_mod = types.ModuleType("src.logger")
logger_mod.logger = types.SimpleNamespace(info=lambda *a, **k: None)
sys.modules["src.config"] = config_mod
sys.modules["src.logger"] = logger_mod

import src.offline.transcriber_offline as transcriber  # noqa: E402


class DummyPipeline:
    def __init__(self, segments):
        self._segments = segments

    def __call__(self, *a, **k):
        return {"chunks": [
            {"text": s.text, "timestamp": (s.start, s.end)} for s in self._segments
        ]}


def _run_transcribe(monkeypatch, segments, max_chars):
    monkeypatch.setattr(transcriber, "get_model", lambda: DummyPipeline(segments))
    monkeypatch.setattr(transcriber.settings, "max_segment_chars", max_chars)
    return transcriber.transcribe(Path("x.wav"))


def test_no_merge_when_exceeding_limit(monkeypatch):
    segs = [
        types.SimpleNamespace(start=0.0, end=1.0, text="hello"),
        types.SimpleNamespace(start=1.1, end=2.0, text="world"),
    ]
    result = _run_transcribe(monkeypatch, segs, max_chars=9)
    assert result == [
        {"start": 0.0, "end": 1.0, "text": "hello"},
        {"start": 1.1, "end": 2.0, "text": "world"},
    ]


def test_merge_when_within_limit(monkeypatch):
    segs = [
        types.SimpleNamespace(start=0.0, end=1.0, text="abc"),
        types.SimpleNamespace(start=1.1, end=2.0, text="def"),
    ]
    result = _run_transcribe(monkeypatch, segs, max_chars=10)
    assert result == [
        {"start": 0.0, "end": 2.0, "text": "abc def"},
    ]
