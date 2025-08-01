import sys
import types

trans_mod = types.ModuleType("transformers")
trans_mod.AutoTokenizer = object
trans_mod.AutoModelForCausalLM = object
sys.modules["transformers"] = trans_mod

config_mod = types.ModuleType("src.config")
config_mod.settings = types.SimpleNamespace(
    subs_dir="subs", max_line_chars=42, merge_gap_seconds=0.4, mistral_device="cpu"
)
logger_mod = types.ModuleType("src.logger")
logger_mod.logger = types.SimpleNamespace(info=lambda *a, **k: None)
sys.modules["src.config"] = config_mod
sys.modules["src.logger"] = logger_mod

from src.offline.translator_offline import translate_segments  # noqa: E402


def test_translate_empty():
    assert translate_segments([]) == []
