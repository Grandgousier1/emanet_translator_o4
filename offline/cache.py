import json, hashlib
from pathlib import Path
from ..config import settings
from ..logger import logger

def _hash_file(path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

def transcription_cache_path(audio_path) -> Path:
    h = _hash_file(audio_path)
    p = Path(settings.cache_dir)/'transcription'
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{h}.json"

def translation_cache_path(audio_path) -> Path:
    h = _hash_file(audio_path)
    p = Path(settings.cache_dir)/'translation'
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{h}.json"

def load_json(path: Path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            logger.warning('cache.read_failed', path=str(path))
    return None

def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

