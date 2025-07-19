import tkinter as tk, threading, subprocess, time
from tkinter import messagebox, filedialog
from pathlib import Path
from .offline.pipeline_offline import run_offline
from .offline.transcriber_offline import get_model
from .offline.translator_offline import get_translator

class App:
    def __init__(self, root):
        root.title('Émanet Offline GUI')
        tk.Label(root, text='Episode URL:').grid(row=0, column=0, sticky='e')
        self.url_entry = tk.Entry(root, width=70)
        self.url_entry.grid(row=0, column=1, columnspan=2)
        tk.Button(root, text='Run', command=self.run_pipeline).grid(row=1, column=1, sticky='w')
        tk.Button(root, text='Batch File', command=self.batch_select).grid(row=1, column=2, sticky='w')
        tk.Button(root, text='Prewarm Models', command=self.prewarm).grid(row=1, column=0, sticky='e')
        self.log = tk.Text(root, height=18, width=100)
        self.log.grid(row=2, column=0, columnspan=3)

    def prewarm(self):
        self.append('Chargement des modèles...
')
        threading.Thread(target=lambda: (get_model(), get_translator(), self.append('Modèles prêts.
')), daemon=True).start()

    def batch_select(self):
        path = filedialog.askopenfilename(title='Fichier URLs (1 par ligne)')
        if not path: return
        threading.Thread(target=self.run_batch, args=(Path(path),), daemon=True).start()

    def run_batch(self, file: Path):
        urls=[u.strip() for u in file.read_text().splitlines() if u.strip()]
        self.append(f'Batch: {len(urls)} URLs
')
        for u in urls:
            self.append(f'→ {u} ...
')
            t0=time.time()
            try:
                srt=run_offline(u)
                self.append(f'   OK {srt} ({time.time()-t0:.1f}s)
')
            except Exception as e:
                self.append(f'   ERREUR {e}
')

    def run_pipeline(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror('Erreur', 'URL requise'); return
        threading.Thread(target=self._do_run, args=(url,), daemon=True).start()

    def _do_run(self, url: str):
        t0=time.time()
        try:
            self.append('Téléchargement / Transcription / Traduction...
')
            srt = run_offline(url)
            self.append(f'OK: {srt} en {time.time()-t0:.1f}s
Ouverture VLC...
')
            try: subprocess.Popen(['vlc','--sub-file',str(srt)])
            except FileNotFoundError: self.append('VLC non trouvé.
')
        except Exception as e:
            self.append(f'ERREUR: {e}
')

    def append(self, text: str):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

if __name__=='__main__':
    root = tk.Tk(); App(root); root.mainloop()

import tkinter as tk, threading, subprocess
from tkinter import messagebox
from pathlib import Path
from .offline.pipeline_offline import run_offline

class App:
    def __init__(self, root):
        root.title('Émanet Offline GUI')
        tk.Label(root, text='Episode URL:').grid(row=0, column=0, sticky='e')
        self.url_entry = tk.Entry(root, width=60)
        self.url_entry.grid(row=0, column=1)
        tk.Button(root, text='Run Offline', command=self.run_pipeline).grid(row=1, column=1, sticky='w')
        self.log = tk.Text(root, height=15, width=80)
        self.log.grid(row=2, column=0, columnspan=2)

    def run_pipeline(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror('Erreur', 'URL requise')
            return
        def target():
            try:
                self.append('Téléchargement / Transcription / Traduction...
')
                srt = run_offline(url)
                self.append(f'OK: {srt}
Ouverture VLC...
')
                subprocess.Popen(['vlc','--sub-file',str(srt)])
            except Exception as e:
                self.append(f'ERREUR: {e}
')
        threading.Thread(target=target, daemon=True).start()

    def append(self, text: str):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

if __name__=='__main__':
    root = tk.Tk(); App(root); root.mainloop()

