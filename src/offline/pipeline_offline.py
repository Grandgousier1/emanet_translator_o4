from pathlib import Path
from typing import Callable, Optional

from ..util.downloader import download_audio
from ..util.audio import normalize
from .transcriber_offline import transcribe
from .translator_offline import translate_segments
from .srt_offline import build_srt
from .cache import (
    transcription_cache_path,
    translation_cache_path,
    load_json,
    save_json,
)
from ..config import settings
from ..logger import logger


def run_offline(
    url: str,
    *,
    force: bool = False,
    progress: Optional[Callable[[int, int], None]] = None,
) -> Path:
    """Run the offline pipeline for a single YouTube URL.

    Parameters
    ----------
    url: str
        Youtube URL to process.
    force: bool, default ``False``
        When ``True`` the transcription and translation caches are
        completely bypassed (neither read nor written).
    """
    total_pct = 100
    current = 0.0
    if progress:
        progress(int(current), total_pct)

    # weight of each stage in percentage points
    w_dl = 5
    w_norm = 5
    w_transcribe = 60
    w_translate = 20
    w_srt = 10

    audio = download_audio(url)
    current += w_dl
    if progress:
        progress(int(current), total_pct)

    norm = normalize(audio)
    current += w_norm
    if progress:
        progress(int(current), total_pct)

    t_cache = transcription_cache_path(norm)
    def t_cb(done: float, total: float) -> None:
        if progress:
            pct = current + w_transcribe * (done / total)
            progress(int(pct), total_pct)

    if force:
        segments = transcribe(norm, progress=t_cb)
    else:
        segments = load_json(t_cache)
        if segments is None:
            segments = transcribe(norm, progress=t_cb)
            save_json(t_cache, segments)
        else:
            logger.info("cache.hit.transcription", file=str(norm))
            if progress:
                progress(int(current + w_transcribe), total_pct)
    current += w_transcribe
    if progress:
        progress(int(current), total_pct)

    tr_cache = translation_cache_path(norm)
    def tr_cb(done: int, total: int) -> None:
        if progress:
            pct = current + w_translate * (done / total)
            progress(int(pct), total_pct)

    if force:
        translated = translate_segments(segments, progress=tr_cb)
    else:
        translated = load_json(tr_cache)
        if translated is None:
            translated = translate_segments(segments, progress=tr_cb)
            save_json(tr_cache, translated)
        else:
            logger.info("cache.hit.translation", file=str(norm))
            if progress:
                progress(int(current + w_translate), total_pct)
    current += w_translate
    if progress:
        progress(int(current), total_pct)
    # build srt
    from uuid import uuid4

    out = Path(settings.subs_dir) / f"{uuid4().hex}.srt"
    build_srt(translated, out)
    current += w_srt
    if progress:
        progress(int(current), total_pct)
    return out
