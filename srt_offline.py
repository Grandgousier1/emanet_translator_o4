from pathlib import Path
from textwrap import wrap
from ..config import settings
from ..logger import logger

def _fmt(ts: float):
    ms = int(ts*1000)
    h=ms//3600000; m=(ms%3600000)//60000; s=(ms%60000)//1000; msr=ms%1000
    return f"{h:02}:{m:02}:{s:02},{msr:03}"

def _wrap_lines(text: str):
    lines = []
    for para in text.strip().split('
'):
        current = wrap(para, width=settings.max_line_chars) or ['']
        lines.extend(current)
    return '
'.join(lines)

def build_srt(translated_segments, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        for i, seg in enumerate(translated_segments, 1):
            txt = seg.get('text_fr') or seg['text']
            txt = _wrap_lines(txt)
            f.write(f"{i}
{_fmt(seg['start'])} --> {_fmt(seg['end'])}
{txt}

")
    logger.info('srt.write', path=str(out_path), count=len(translated_segments))
    return out_path

