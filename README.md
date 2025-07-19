# Émanet Subtitles – Version 100% Offline

Cette version supprime toute dépendance aux APIs distantes :
- **Transcription** locale via *faster-whisper* (modèle Whisper).
- **Traduction** locale via *NLLB 200 distilled* (Turc → Français).
- **Téléchargement** YouTube avec *yt-dlp*.
- **Génération** directe des SRT à partir des timestamps Whisper (fusion adaptative des segments).
- **Cache** SHA256 pour éviter de retraiter un même épisode.

## Installation
```bash
git clone <repo>
cd emanet-subtitles
python3.11 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install poetry
poetry install --no-dev
```

## Configuration (optionnelle)
```bash
cp .env.example .env
# ajustez WHISPER_MODEL_SIZE, NLLB_MODEL, etc.
```

## Utilisation CLI
```bash
emanet-subtitles offline --url https://www.youtube.com/watch?v=VIDEO_ID
```
VLC s’ouvrira automatiquement (si installé) avec les sous-titres générés dans `subs/`.

## GUI
```bash
python src/gui.py
```
Entrer l’URL, lancer.

## Caching
- Transcription : `cache/transcription/<hash>.json`
- Traduction : `cache/translation/<hash>.json`
Supprimer ces fichiers pour forcer une régénération.

## Choix de modèles
- Whisper : changer `WHISPER_MODEL_SIZE` (`tiny`, `base`, `small`, `medium`, `large-v3`).
- Traduction : variable `NLLB_MODEL` (p. ex. `facebook/nllb-200-distilled-600M`).

## Optimisation
- GPU : si CUDA dispo, mettre `WHISPER_DEVICE=cuda` et `WHISPER_COMPUTE_TYPE=float16`.
- CPU : garder `auto` + quantization par défaut (`int8_float16`).

## Tests
```bash
poetry run pytest -q
```
(Certains tests sont marqués `skip` car ils nécessitent un vrai média.)

## Licence
MIT.
