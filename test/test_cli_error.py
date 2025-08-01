from typer.testing import CliRunner
import types
import sys


def test_offline_error(monkeypatch):
    logger_mod = types.ModuleType("src.logger")
    logger_mod.logger = types.SimpleNamespace(
        info=lambda *a, **k: None,
        error=lambda *a, **k: None,
    )
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
        "transformers",
        types.SimpleNamespace(
            pipeline=object,
            AutoTokenizer=object,
            AutoModelForCausalLM=object,
        ),
    )
    import importlib

    cli = importlib.import_module("src.cli")

    def fail(*a, **k):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "run_offline", fail)
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

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        ["offline", "http://x", "--no-open-vlc"],
    )
    assert result.exit_code == 1
    assert "Erreur: boom" in result.stdout
