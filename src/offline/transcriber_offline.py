from transformers import pipeline
from pathlib import Path
from ..config import settings
from ..logger import logger

_model_singleton = None


def get_model():
    global _model_singleton
    if _model_singleton is None:
        logger.info(
            'voxtral.load',
            model=settings.voxtral_model,
            device=settings.voxtral_device,
        )
        device = 0 if settings.voxtral_device == 'cuda' else -1
        _model_singleton = pipeline(
            'automatic-speech-recognition',
            model=settings.voxtral_model,
            device=device,
            return_timestamps=True,
        )
    return _model_singleton


def transcribe(audio_path: Path):
    model = get_model()
    logger.info('transcribe.start', file=str(audio_path))
    result = model(str(audio_path))
    segments = []
    for chunk in result.get('chunks', []):
        seg_text = chunk['text'].strip()
        start, end = chunk['timestamp']
        if (
            segments
            and start - segments[-1]['end'] < settings.merge_gap_seconds
            and len(segments[-1]['text']) + 1 + len(seg_text)
            <= settings.max_segment_chars
        ):
            segments[-1]['text'] += ' ' + seg_text
            segments[-1]['end'] = end
        else:
            segments.append({'start': float(start), 'end': float(end), 'text': seg_text})
    logger.info('transcribe.done', segments=len(segments))
    return segments
