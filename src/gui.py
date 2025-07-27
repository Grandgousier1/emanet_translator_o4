import subprocess
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from .offline.pipeline_offline import run_offline
from .offline.transcriber_offline import get_model
from .offline.translator_offline import get_translator


class App:
    def __init__(self, root: tk.Tk) -> None:
        root.title("Émanet Offline GUI")
        tk.Label(root, text="Episode URL:").grid(row=0, column=0, sticky="e")
        self.url_entry = tk.Entry(root, width=70)
        self.url_entry.grid(row=0, column=1, columnspan=2)
        tk.Button(root, text="Run", command=self.run_pipeline).grid(row=1, column=1, sticky="w")
        tk.Button(root, text="Batch File", command=self.batch).grid(row=1, column=2, sticky="w")
        tk.Button(root, text="Prewarm Models", command=self.prewarm).grid(row=1, column=0, sticky="e")
        self.log = tk.Text(root, height=18, width=100)
        self.log.grid(row=2, column=0, columnspan=3)

    def append(self, text: str) -> None:
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

    def prewarm(self) -> None:
        self.append("Chargement des modèles...\n")

        def load():
            get_model()
            get_translator()
            self.append("Modèles prêts.\n")

        threading.Thread(target=load, daemon=True).start()

    def batch(self) -> None:
        path = filedialog.askopenfilename(title="Fichier URLs (1 par ligne)")
        if not path:
            return

        def worker(file_path: str) -> None:
            urls = [u.strip() for u in Path(file_path).read_text().splitlines() if u.strip()]
            self.append(f"Batch: {len(urls)} URLs\n")
            for u in urls:
                self.append(f"→ {u} ...\n")
                start = time.time()
                try:
                    srt = run_offline(u)
                    self.append(f"   OK {srt} ({time.time() - start:.1f}s)\n")
                except Exception as e:  # noqa: BLE001
                    self.append(f"   ERREUR {e}\n")

        threading.Thread(target=worker, args=(path,), daemon=True).start()

    def run_pipeline(self) -> None:
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erreur", "URL requise")
            return

        def target() -> None:
            start = time.time()
            try:
                self.append("Téléchargement / Transcription / Traduction...\n")
                srt = run_offline(url)
                self.append(f"OK: {srt} en {time.time() - start:.1f}s\nOuverture VLC...\n")
                try:
                    subprocess.Popen(["vlc", "--sub-file", str(srt)])
                except FileNotFoundError:
                    self.append("VLC non trouvé.\n")
            except Exception as e:  # noqa: BLE001
                self.append(f"ERREUR: {e}\n")

        threading.Thread(target=target, daemon=True).start()


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
