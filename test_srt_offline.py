from src.offline.srt_offline import build_srt
from pathlib import Path

def test_srt_build(tmp_path):
    segs=[{'start':0.0,'end':1.2,'text':'Merhaba','text_fr':'Bonjour'}]
    out=tmp_path/'t.srt'
    build_srt(segs,out)
    assert out.exists()
    txt=out.read_text()
    assert 'Bonjour' in txt
