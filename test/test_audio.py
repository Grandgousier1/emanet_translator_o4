import sys, types, subprocess
import pytest
from pathlib import Path

# stub logger and config before importing the module under test
logger_mod = types.ModuleType("src.logger")
logger_mod.logger = types.SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None)
sys.modules["src.logger"] = logger_mod

config_mod = types.ModuleType("src.config")
config_mod.settings = types.SimpleNamespace(audio_dir="x")
sys.modules["src.config"] = config_mod

import src.util.audio as audio


def test_normalize_error(monkeypatch, tmp_path):
    stderr_calls = []
    monkeypatch.setattr(audio.logger, "error", lambda *a, **k: stderr_calls.append(k.get("stderr")))
    monkeypatch.setattr(audio.settings, "audio_dir", str(tmp_path))

    def fake_run(cmd, capture_output=True, check=True):
        raise subprocess.CalledProcessError(1, cmd, stderr=b"fail")

    monkeypatch.setattr(audio.subprocess, "run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        audio.normalize(tmp_path / "in.wav")

    assert stderr_calls == ["fail"]
