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
    steps = 5
    current = 0
    if progress:
        progress(current, steps)

    audio = download_audio(url)
    current += 1
    if progress:
        progress(current, steps)

    norm = normalize(audio)
    current += 1
    if progress:
        progress(current, steps)

    t_cache = transcription_cache_path(norm)
    if force:
        segments = transcribe(norm)
    else:
        segments = load_json(t_cache)
        if segments is None:
            segments = transcribe(norm)
            save_json(t_cache, segments)
        else:
            logger.info("cache.hit.transcription", file=str(norm))
    current += 1
    if progress:
        progress(current, steps)

    tr_cache = translation_cache_path(norm)
    if force:
        translated = translate_segments(segments)
    else:
        translated = load_json(tr_cache)
        if translated is None:
            translated = translate_segments(segments)
            save_json(tr_cache, translated)
        else:
            logger.info("cache.hit.translation", file=str(norm))
    current += 1
    if progress:
        progress(current, steps)
    # build srt
    from uuid import uuid4

    out = Path(settings.subs_dir) / f"{uuid4().hex}.srt"
    build_srt(translated, out)
    current += 1
    if progress:
        progress(current, steps)
    return out
