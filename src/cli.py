import json
import subprocess
import time
from pathlib import Path

import typer
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from .offline.pipeline_offline import run_offline
from .offline.transcriber_offline import get_model
from .offline.translator_offline import get_translator
from .offline.cache import (
    transcription_cache_path,
    translation_cache_path,
    load_json,
)
from .logger import logger


app = typer.Typer(help="Émanet subtitles offline pipeline (CLI étendue)")


@app.command("offline")
def offline(
    url: str = typer.Argument(..., help="URL YouTube de l'épisode"),
    open_vlc: bool = typer.Option(True, help="Ouvrir VLC après génération"),
    no_cache: bool = typer.Option(
        False, help="Ignorer le cache (lecture/écriture)"
    ),
) -> None:
    start = time.time()
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Pipeline", total=None)
        srt = run_offline(url, force=no_cache)
        progress.update(task, description="Terminé")
    typer.echo(f"Sous-titres générés: {srt} (en {time.time() - start:.1f}s)")
    if open_vlc:
        try:
            subprocess.Popen(["vlc", "--sub-file", str(srt)])
        except FileNotFoundError:
            typer.secho("VLC introuvable dans le PATH", fg="red")
    logger.info(
        "pipeline.complete",
        srt=str(srt),
        seconds=f"{time.time() - start:.2f}",
    )


@app.command("prewarm")
def prewarm() -> None:
    get_model()
    get_translator()
    typer.echo("Modèles chargés en mémoire.")


@app.command("inspect-cache")
def inspect_cache(audio_file: Path) -> None:
    t = transcription_cache_path(audio_file)
    tr = translation_cache_path(audio_file)
    data = {
        'transcription_cache_exists': t.exists(),
        'translation_cache_exists': tr.exists(),
        'transcription_segments': len(load_json(t) or []),
        'translation_segments': len(load_json(tr) or [])
    }
    typer.echo(json.dumps(data, indent=2, ensure_ascii=False))


@app.command("batch")
def batch(
    urls_file: Path = typer.Argument(
        ..., help="Fichier texte: 1 URL par ligne"
    ),
    parallel: int = typer.Option(1, help="Nb de processus"),
    open_vlc: bool = typer.Option(
        False, help="Ouvrir VLC après chaque génération"
    ),
) -> None:
    import concurrent.futures

    urls = [u.strip() for u in urls_file.read_text().splitlines() if u.strip()]
    typer.echo(f"Traitement de {len(urls)} URL(s) (parallel={parallel})")

    def worker(u):
        try:
            return u, str(run_offline(u))
        except Exception as e:
            return u, f"ERREUR: {e}"

    results = []
    if parallel > 1:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=parallel
        ) as ex:
            for r in ex.map(worker, urls):
                results.append(r)
                typer.echo(f"→ {r[0]} => {r[1]}")
    else:
        for u in urls:
            r = worker(u)
            results.append(r)
            typer.echo(f"→ {r[0]} => {r[1]}")

    if open_vlc:
        for _, srt in results:
            if srt.endswith(".srt"):
                subprocess.Popen(["vlc", "--sub-file", srt])

    summary = {
        "success": [r for r in results if r[1].endswith(".srt")],
        "failed": [r for r in results if not r[1].endswith(".srt")],
    }

    typer.echo(json.dumps(summary, indent=2, ensure_ascii=False))


@app.command("bench")
def bench(
    url: str = typer.Argument(...),
    loops: int = typer.Option(1, help="Nb répétitions"),
) -> None:
    times = []
    for i in range(loops):
        start = time.time()
        run_offline(url, force=True)
        dt = time.time() - start
        typer.echo(f"Run {i + 1}/{loops}: {dt:.2f}s")
        times.append(dt)
    avg = sum(times) / len(times)
    typer.echo(
        f"Moyenne: {avg:.2f}s | "
        f"Min: {min(times):.2f}s | Max: {max(times):.2f}s"
    )


if __name__ == "__main__":
    app()
