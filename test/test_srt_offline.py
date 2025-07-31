import sys
import types

config_mod = types.ModuleType("src.config")
config_mod.settings = types.SimpleNamespace(
    subs_dir="subs", max_line_chars=42, merge_gap_seconds=0.4
)
logger_mod = types.ModuleType("src.logger")
logger_mod.logger = types.SimpleNamespace(info=lambda *a, **k: None)
sys.modules["src.config"] = config_mod
sys.modules["src.logger"] = logger_mod

from src.offline.srt_offline import build_srt  # noqa: E402


def test_srt_build(tmp_path):
    segs = [
        {
            "start": 0.0,
            "end": 1.2,
            "text": "Merhaba",
            "text_fr": "Bonjour",
        }
    ]
    out = tmp_path / "t.srt"
    build_srt(segs, out)
    assert out.exists()
    txt = out.read_text()
    assert "Bonjour" in txt
