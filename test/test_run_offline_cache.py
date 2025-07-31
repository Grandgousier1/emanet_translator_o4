def import_pipeline(monkeypatch):
    import sys
    import types

    sys.modules.setdefault(
        'yt_dlp',
        types.SimpleNamespace(YoutubeDL=lambda *a, **k: None),
    )
    sys.modules.setdefault(
        'faster_whisper',
        types.SimpleNamespace(WhisperModel=object),
    )
    sys.modules.setdefault(
        'ctranslate2',
        types.SimpleNamespace(get_cuda_device_count=lambda: 0),
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


def test_run_offline_cache(monkeypatch, tmp_path):
    pl = import_pipeline(monkeypatch)
    monkeypatch.setattr(pl.settings, 'subs_dir', str(tmp_path))

    # stub heavy operations
    monkeypatch.setattr(
        pl,
        'download_audio',
        lambda url: tmp_path / 'dl.wav',
    )
    monkeypatch.setattr(pl, 'normalize', lambda p: p)
    transcribed = [{'start': 0.0, 'end': 1.0, 'text': 'hi'}]
    translated = [
        {'start': 0.0, 'end': 1.0, 'text': 'hi', 'text_fr': 'bonjour'}
    ]
    t_calls = {'trans': 0, 'translate': 0}

    def fake_transcribe(p):
        t_calls['trans'] += 1
        return list(transcribed)

    def fake_translate(segs):
        t_calls['translate'] += 1
        return list(translated)

    monkeypatch.setattr(pl, 'transcribe', fake_transcribe)
    monkeypatch.setattr(pl, 'translate_segments', fake_translate)
    monkeypatch.setattr(
        pl,
        'build_srt',
        lambda segs, out: out.write_text('ok') or out,
    )

    # cache helpers
    monkeypatch.setattr(
        pl,
        'transcription_cache_path',
        lambda p: tmp_path / 't.json',
    )
    monkeypatch.setattr(
        pl,
        'translation_cache_path',
        lambda p: tmp_path / 'tr.json',
    )
    calls = {'load': [], 'save': []}
    store = {}

    def fake_load(path):
        calls['load'].append(path)
        return store.get(path)

    def fake_save(path, data):
        calls['save'].append(path)
        store[path] = data

    monkeypatch.setattr(pl, 'load_json', fake_load)
    monkeypatch.setattr(pl, 'save_json', fake_save)

    # first run - cache miss triggers save
    result1 = pl.run_offline('http://example.com', force=False)
    assert result1.exists()
    assert calls['load'] == [tmp_path / 't.json', tmp_path / 'tr.json']
    assert calls['save'] == [tmp_path / 't.json', tmp_path / 'tr.json']
    assert t_calls == {'trans': 1, 'translate': 1}

    calls['load'].clear()
    calls['save'].clear()

    # second run - cache hit, no save nor processing
    result2 = pl.run_offline('http://example.com', force=False)
    assert result2.exists()
    assert calls['load'] == [tmp_path / 't.json', tmp_path / 'tr.json']
    assert calls['save'] == []
    assert t_calls == {'trans': 1, 'translate': 1}
