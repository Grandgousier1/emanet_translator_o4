import types
import sys


def test_gui_debug(monkeypatch):
    import importlib

    yt_mod = types.ModuleType("yt_dlp")
    yt_mod.YoutubeDL = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, "yt_dlp", yt_mod)
    fw_mod = types.ModuleType("faster_whisper")
    fw_mod.WhisperModel = object
    monkeypatch.setitem(sys.modules, "faster_whisper", fw_mod)
    ct_mod = types.ModuleType("ctranslate2")
    ct_mod.get_cuda_device_count = lambda: 0
    monkeypatch.setitem(sys.modules, "ctranslate2", ct_mod)
    tr_mod = types.ModuleType("transformers")
    tr_mod.AutoTokenizer = object
    tr_mod.AutoModelForSeq2SeqLM = object
    monkeypatch.setitem(sys.modules, "transformers", tr_mod)
    config_mod = types.ModuleType("src.config")
    config_mod.settings = types.SimpleNamespace(
        subs_dir="x",
        max_line_chars=42,
    )
    monkeypatch.setitem(sys.modules, "src.config", config_mod)
    logger_mod = types.ModuleType("src.logger")
    logger_mod.logger = types.SimpleNamespace(info=lambda *a, **k: None)
    monkeypatch.setitem(sys.modules, "src.logger", logger_mod)

    called = []

    def start():
        print("start called")
        called.append(True)

    stub = types.SimpleNamespace(start=start)
    monkeypatch.setitem(sys.modules, "src.debug", stub)
    if "src" in sys.modules:
        setattr(sys.modules["src"], "debug", stub)

    gui = importlib.import_module("src.gui")

    app = object.__new__(gui.App)
    app.append = lambda *a: None
    app.debug_var = types.SimpleNamespace(get=lambda: True)

    monkeypatch.setattr(gui, "run_offline", lambda url: "x.srt")
    monkeypatch.setattr(gui.subprocess, "Popen", lambda *a, **k: None)
    monkeypatch.setattr(gui.messagebox, "showerror", lambda *a, **k: None)

    app._do_run("http://x")
    assert called == [True]
