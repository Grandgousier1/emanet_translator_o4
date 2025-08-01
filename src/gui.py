import threading
import subprocess
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from .offline.pipeline_offline import run_offline
from .offline.transcriber_offline import get_model
from .offline.translator_offline import get_translator


class App:
    def __init__(self, root: tk.Tk):
        root.title("Émanet Offline GUI")
        tk.Label(root, text="Episode URL:").grid(row=0, column=0, sticky="e")
        self.url_entry = tk.Entry(root, width=70)
        self.url_entry.grid(row=0, column=1, columnspan=2)
        self.debug_var = tk.BooleanVar(value=False)
        tk.Checkbutton(root, text="Debug", variable=self.debug_var).grid(
            row=0, column=3, sticky="w"
        )
        tk.Button(
            root,
            text="Run",
            command=self.run_pipeline,
        ).grid(row=1, column=1, sticky="w")
        tk.Button(root, text="Batch File", command=self.batch_select).grid(
            row=1, column=2, sticky="w"
        )
        tk.Button(root, text="Prewarm Models", command=self.prewarm).grid(
            row=1, column=0, sticky="e"
        )
        self.progress = ttk.Progressbar(
            root, length=300, mode="determinate", maximum=100
        )
        self.progress.grid(row=2, column=0, columnspan=3, sticky="we")
        self.log = tk.Text(root, height=18, width=100)
        self.log.grid(row=3, column=0, columnspan=3)

    def append(self, text: str) -> None:
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)

    def set_progress(self, current: int, total: int) -> None:
        def update():
            self.progress["maximum"] = total
            self.progress["value"] = current

        self.progress.after(0, update)

    def prewarm(self) -> None:
        self.append("Chargement des modèles...")

        def worker():
            get_model()
            get_translator()
            self.append("Modèles prêts.")

        threading.Thread(target=worker, daemon=True).start()

    def batch_select(self) -> None:
        path = filedialog.askopenfilename(title="Fichier URLs (1 par ligne)")
        if not path:
            return
        threading.Thread(
            target=self.run_batch,
            args=(Path(path),),
            daemon=True,
        ).start()

    def run_batch(self, file: Path) -> None:
        urls = [u.strip() for u in file.read_text().splitlines() if u.strip()]
        self.append(f"Batch: {len(urls)} URLs")
        for url in urls:
            self.append(f"→ {url} ...")
            t0 = time.time()
            try:
                srt = run_offline(url)
                self.append(f"   OK {srt} ({time.time() - t0:.1f}s)")
            except Exception as e:  # pragma: no cover - runtime errors
                self.append(f"   ERREUR {e}")

    def run_pipeline(self) -> None:
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erreur", "URL requise")
            return
        self.progress["value"] = 0
        threading.Thread(target=self._do_run, args=(url,), daemon=True).start()

    def _do_run(self, url: str) -> None:
        t0 = time.time()
        try:
            if self.debug_var.get():
                from . import debug as debug_module

                try:
                    debug_module.start()
                except Exception as e:  # pragma: no cover
                    self.append(f"Erreur démarrage debug: {e}")
            self.append("Téléchargement / Transcription / Traduction...")
            try:
                srt = run_offline(url, progress=self.set_progress)
            except TypeError:
                srt = run_offline(url)
            self.append(f"OK: {srt} en {time.time() - t0:.1f}s. Ouverture VLC...")
            try:
                subprocess.Popen(["vlc", "--sub-file", str(srt)])
            except FileNotFoundError:
                self.append("VLC non trouvé.")
        except Exception as e:  # pragma: no cover - runtime errors
            self.append(f"ERREUR: {e}")
            messagebox.showerror("Erreur", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
