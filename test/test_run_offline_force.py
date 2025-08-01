def import_pipeline(monkeypatch):
    import sys
    import types

    sys.modules.setdefault(
        'yt_dlp', types.SimpleNamespace(YoutubeDL=lambda *a, **k: None)
    )
    sys.modules.setdefault(
        'faster_whisper', types.SimpleNamespace(WhisperModel=object)
    )
    sys.modules.setdefault(
        'ctranslate2', types.SimpleNamespace(get_cuda_device_count=lambda: 0)
    )
    sys.modules.setdefault(
        'transformers',
        types.SimpleNamespace(
            AutoTokenizer=object,
            AutoModelForSeq2SeqLM=object,
        ),
    )
    structlog_mod = types.ModuleType('structlog')
    structlog_mod.configure = lambda **kw: None
    structlog_mod.processors = types.SimpleNamespace(
        TimeStamper=lambda fmt=None: None,
        add_log_level=lambda *a, **k: None,
        JSONRenderer=lambda *a, **k: None,
    )
    structlog_mod.get_logger = lambda: types.SimpleNamespace(
        info=lambda *a, **k: None,
        warning=lambda *a, **k: None,
        error=lambda *a, **k: None,
    )
    stdlib_mod = types.ModuleType('structlog.stdlib')
    stdlib_mod.LoggerFactory = object
    sys.modules.setdefault('structlog', structlog_mod)
    sys.modules.setdefault('structlog.stdlib', stdlib_mod)
    config_mod = types.ModuleType('src.config')
    config_mod.settings = types.SimpleNamespace(subs_dir='subs')
    sys.modules.setdefault('src.config', config_mod)

    from src.offline import pipeline_offline as pl
    return pl


def test_run_offline_force(monkeypatch, tmp_path):
    pl = import_pipeline(monkeypatch)
    # output directory for SRT
    monkeypatch.setattr(pl.settings, "subs_dir", str(tmp_path))

    # stub heavy operations
    monkeypatch.setattr(pl, "download_audio", lambda url: tmp_path / "dl.wav")
    monkeypatch.setattr(pl, "normalize", lambda p: p)
    monkeypatch.setattr(
        pl,
        "transcribe",
        lambda p, progress=None: [{"start": 0.0, "end": 1.0, "text": "hi"}],
    )
    monkeypatch.setattr(
        pl,
        "translate_segments",
        lambda segs, progress=None: [
            {"start": 0.0, "end": 1.0, "text": "hi", "text_fr": "bonjour"}
        ],
    )
    monkeypatch.setattr(
        pl,
        "build_srt",
        lambda segs, out: out.write_text("ok") or out,
    )

    # stub cache helpers and record usage
    monkeypatch.setattr(
        pl, "transcription_cache_path", lambda p: tmp_path / "t.json"
    )
    monkeypatch.setattr(
        pl, "translation_cache_path", lambda p: tmp_path / "tr.json"
    )
    load_called = []
    save_called = []

    def fake_load(path):
        load_called.append(path)
        return None

    def fake_save(path, data):
        save_called.append(path)

    monkeypatch.setattr(pl, "load_json", fake_load)
    monkeypatch.setattr(pl, "save_json", fake_save)

    result = pl.run_offline("http://example.com", force=True)

    assert result.exists()
    assert load_called == []
    assert save_called == []
