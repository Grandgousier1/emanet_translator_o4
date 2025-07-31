import yt_dlp
from pathlib import Path
from ..logger import logger
from ..config import settings

def download_audio(url: str) -> Path:
    Path(settings.download_dir).mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': f"{settings.download_dir}/%(id)s.%(ext)s",
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}
        ]
    }
    logger.info('download.start', url=url)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = Path(ydl.prepare_filename(info)).with_suffix('.wav')
    logger.info('download.done', path=str(audio_path))
    return audio_path

