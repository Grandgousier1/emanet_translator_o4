from faster_whisper import WhisperModel
from pathlib import Path
from ..config import settings
from ..logger import logger

_model_singleton = None

def get_model():
    global _model_singleton
    if _model_singleton is None:
        logger.info('whisper.load', size=settings.whisper_model_size, device=settings.whisper_device)
        _model_singleton = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device if settings.whisper_device!='auto' else 'cuda' if WhisperModel.is_cuda_available() else 'cpu',
            compute_type=settings.whisper_compute_type if settings.whisper_compute_type!='auto' else 'int8_float16'
        )
    return _model_singleton

def transcribe(audio_path: Path):
    model = get_model()
    logger.info('transcribe.start', file=str(audio_path))
    segments, info = model.transcribe(str(audio_path), beam_size=5, vad_filter=True)
    collected = []
    last_end = None
    for seg in segments:
        # Merge small gaps
        if collected and seg.start - collected[-1]['end'] < settings.merge_gap_seconds:
            collected[-1]['text'] += ' ' + seg.text.strip()
            collected[-1]['end'] = seg.end
        else:
            collected.append({
                'start': float(seg.start),
                'end': float(seg.end),
                'text': seg.text.strip()
            })
    logger.info('transcribe.done', segments=len(collected))
    return collected

