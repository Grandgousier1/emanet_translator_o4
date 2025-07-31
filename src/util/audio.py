import subprocess
from pathlib import Path

from ..logger import logger
from ..config import settings


def normalize(audio_path: Path) -> Path:
    norm_dir = Path(settings.audio_dir)
    norm_dir.mkdir(parents=True, exist_ok=True)
    out = norm_dir / (audio_path.stem + '_norm.wav')
    logger.info('normalize.start', src=str(audio_path))
    cmd = [
        'ffmpeg', '-y', '-i', str(audio_path),
        '-ar', '16000', '-ac', '1', '-af', 'loudnorm',
        str(out)
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        logger.error('normalize.error', stderr=exc.stderr.decode())
        raise
    logger.info('normalize.done', out=str(out))
    return out
