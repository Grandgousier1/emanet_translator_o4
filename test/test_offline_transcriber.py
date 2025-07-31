import sys
import types
from pathlib import Path

# Stub external modules before importing the module under test
fw_mod = types.ModuleType("faster_whisper")
fw_mod.WhisperModel = object
sys.modules.setdefault("faster_whisper", fw_mod)

ct_mod = types.ModuleType("ctranslate2")
ct_mod.get_cuda_device_count = lambda: 0
sys.modules.setdefault("ctranslate2", ct_mod)

config_mod = types.ModuleType("src.config")
config_mod.settings = types.SimpleNamespace(
    merge_gap_seconds=0.5,
    max_segment_chars=10,
    whisper_model_size="tiny",
    whisper_device="cpu",
    whisper_compute_type="int8",
)
logger_mod = types.ModuleType("src.logger")
logger_mod.logger = types.SimpleNamespace(info=lambda *a, **k: None)
sys.modules["src.config"] = config_mod
sys.modules["src.logger"] = logger_mod

import src.offline.transcriber_offline as transcriber  # noqa: E402


class DummyModel:
    def __init__(self, segments):
        self._segments = segments

    def transcribe(self, *a, **k):
        return self._segments, {}


def _run_transcribe(monkeypatch, segments, max_chars):
    monkeypatch.setattr(transcriber, "get_model", lambda: DummyModel(segments))
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
