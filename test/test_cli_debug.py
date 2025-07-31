from typer.testing import CliRunner
import types
import sys


def test_offline_debug(monkeypatch):
    # Setup minimal stubs before importing CLI
    logger_mod = types.ModuleType("src.logger")
    logger_mod.logger = types.SimpleNamespace(info=lambda *a, **k: None)
    config_mod = types.ModuleType("src.config")
    config_mod.settings = types.SimpleNamespace(
        subs_dir="x",
        max_line_chars=42,
    )
    monkeypatch.setitem(sys.modules, "src.logger", logger_mod)
    monkeypatch.setitem(sys.modules, "src.config", config_mod)
    monkeypatch.setitem(
        sys.modules,
        "yt_dlp",
        types.SimpleNamespace(YoutubeDL=lambda *a, **k: None),
    )
    monkeypatch.setitem(
        sys.modules,
        "faster_whisper",
        types.SimpleNamespace(WhisperModel=object),
    )
    monkeypatch.setitem(
        sys.modules,
        "ctranslate2",
        types.SimpleNamespace(get_cuda_device_count=lambda: 0),
    )
    monkeypatch.setitem(
        sys.modules,
        "transformers",
        types.SimpleNamespace(
            AutoTokenizer=object,
            AutoModelForSeq2SeqLM=object,
        ),
    )
    monkeypatch.setitem(sys.modules, "debugpy", types.ModuleType("debugpy"))

    import importlib
    cli = importlib.import_module("src.cli")

    called = []
    monkeypatch.setattr(cli, "run_offline", lambda url, force=False: "x.srt")
    monkeypatch.setattr(cli.subprocess, "Popen", lambda *a, **k: None)

    class DummyProgress:
        def __init__(self, *a, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        @staticmethod
        def get_default_columns():
            return []

        def add_task(self, *a, **kw):
            return 0

        def update(self, *a, **kw):
            pass

    monkeypatch.setattr(cli, "Progress", DummyProgress)
    import src.debug as debug_module
    monkeypatch.setattr(debug_module, "start", lambda: called.append(True))

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        ["offline", "http://x", "--debug", "--no-cache", "--no-open-vlc"],
    )
    assert result.exit_code == 0
    assert called == [True]
