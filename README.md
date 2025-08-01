# Émanet Subtitles – Version 100% Offline

Cette version supprime toute dépendance aux APIs distantes :
- **Transcription** locale via *mistralai/Voxtral-Small-24B-2507*.
- **Traduction** locale via *mistralai/mistral-medium-2505* (Turc → Français).
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
poetry install --without dev
```
Note: Ce projet cible **Python 3.11**. Utiliser Python 3.12 peut nécessiter des
paquets système comme `cmake` pour compiler `sentencepiece`.

## Configuration (optionnelle)
```bash
cp .env.example .env
# ajustez VOXTRAL_MODEL et MISTRAL_MODEL si besoin
```

## Utilisation CLI
```bash
emanet-subtitles offline --url https://www.youtube.com/watch?v=VIDEO_ID
# Pour activer un serveur debugpy:
emanet-subtitles offline --url https://youtu.be/ID --debug
```
VLC s’ouvrira automatiquement (si installé) avec les sous-titres générés dans `subs/`.

## GUI
```bash
python -m src.gui
```
Entrer l’URL, lancer. Pour activer le débogage distant, cochez "Debug" avant d'exécuter.

## Caching
- Transcription : `cache/transcription/<hash>.json`
- Traduction : `cache/translation/<hash>.json`
Supprimer ces fichiers pour forcer une régénération.

## Choix de modèles
- STT : variable `VOXTRAL_MODEL` (par défaut Voxtral Small).
- LLM  : variable `MISTRAL_MODEL` (par défaut Mistral Medium 2505).

## Optimisation
- GPU : si CUDA dispo, mettre `VOXTRAL_DEVICE=cuda` pour accélérer la transcription.

## Tests
```bash
poetry run pytest -q
```
(Certains tests sont marqués `skip` car ils nécessitent un vrai média.)

## Déploiement Runpod
Une image Docker est fournie pour exécuter le pipeline sur Runpod.io :

```bash
docker build -t emanet-runpod .
# puis lancer avec les volumes nécessaires
```

## Licence
MIT.
