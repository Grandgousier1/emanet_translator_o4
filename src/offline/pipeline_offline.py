from pathlib import Path
from ..util.downloader import download_audio
from ..util.audio import normalize
from .transcriber_offline import transcribe
from .translator_offline import translate_segments
from .srt_offline import build_srt
from .cache import (
    transcription_cache_path, translation_cache_path,
    load_json, save_json
)
from ..config import settings
from ..logger import logger


def run_offline(url: str, *, force: bool = False) -> Path:
    """Run the offline pipeline for a single YouTube URL."""
    audio = download_audio(url)
    norm = normalize(audio)

    t_cache = transcription_cache_path(norm)
    segments = None if force else load_json(t_cache)
    if segments is None:
        segments = transcribe(norm)
        save_json(t_cache, segments)
    else:
        logger.info('cache.hit.transcription', file=str(norm))

    tr_cache = translation_cache_path(norm)
    translated = None if force else load_json(tr_cache)
    if translated is None:
        translated = translate_segments(segments)
        save_json(tr_cache, translated)
    else:
        logger.info('cache.hit.translation', file=str(norm))
    # build srt
    from uuid import uuid4
    out = Path(settings.subs_dir)/f"{uuid4().hex}.srt"
    build_srt(translated, out)
    return out

