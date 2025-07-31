from faster_whisper import WhisperModel
import ctranslate2
from pathlib import Path
from ..config import settings
from ..logger import logger

_model_singleton = None


def get_model():
    global _model_singleton
    if _model_singleton is None:
        logger.info(
            'whisper.load',
            size=settings.whisper_model_size,
            device=settings.whisper_device,
        )
        _model_singleton = WhisperModel(
            settings.whisper_model_size,
            device=(
                settings.whisper_device
                if settings.whisper_device != 'auto'
                else 'cuda'
                if ctranslate2.get_cuda_device_count() > 0
                else 'cpu'
            ),
            compute_type=(
                settings.whisper_compute_type
                if settings.whisper_compute_type != 'auto'
                else 'int8'
            ),
        )
    return _model_singleton


def transcribe(audio_path: Path):
    model = get_model()
    logger.info('transcribe.start', file=str(audio_path))
    segments, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        vad_filter=True,
    )
    collected = []
    for seg in segments:
        seg_text = seg.text.strip()
        # Merge small gaps when the combined text is not too long
        if (
            collected
            and seg.start - collected[-1]['end'] < settings.merge_gap_seconds
            and len(collected[-1]['text']) + 1 + len(seg_text)
            <= settings.max_segment_chars
        ):
            collected[-1]['text'] += ' ' + seg_text
            collected[-1]['end'] = seg.end
        else:
            collected.append({
                'start': float(seg.start),
                'end': float(seg.end),
                'text': seg_text
            })
    logger.info('transcribe.done', segments=len(collected))
    return collected
