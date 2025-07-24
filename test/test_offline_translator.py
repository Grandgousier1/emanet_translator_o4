from src.offline.translator_offline import translate_segments

def test_translate_empty():
    assert translate_segments([]) == []

