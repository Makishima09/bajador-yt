"""Interfaz gráfica Tkinter para Bajador YT.

La descarga corre en un hilo aparte y comunica el progreso por una Queue.
El hilo de Tk solo consume la cola vía `after`, así la ventana no se congela
y el botón "Cancelar" puede detener el proceso en limpio.
"""

from __future__ import annotations

import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from bajador_yt import DownloadConfig, Downloader, __version__
from bajador_yt.config import SUPPORTED_BROWSERS
from bajador_yt.constants import AUDIO_FORMATS, MODES, QUALITY_LEVELS, VIDEO_FORMATS
from bajador_yt.csv_utils import extract_links_from_text
from bajador_yt.downloader import summarize
from bajador_yt.ffmpeg_utils import detect_ffmpeg_path
from bajador_yt.logger import get_logger, setup_logger
from bajador_yt.models import DownloadResult

POLL_INTERVAL_MS = 100


class BajadorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f'Bajador YT v{__version__} — Descargas')
        self.root.geometry('820x760')
        self.root.minsize(700, 680)
        self.root.resizable(True, True)

        self.progress_queue: 'queue.Queue[tuple[str, object]]' = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker: Optional[threading.Thread] = None
        self.results: list[DownloadResult] = []

        self.log = get_logger('gui')

        self._build_widgets()
        self._handle_mode_change()

    # ------------------------------------------------------------- UI layout

    def _build_widgets(self) -> None:
        root = self.root

        tk.Label(
            root,
            text='Pega una o varias URLs de YouTube (una por línea):',
            font=('Arial', 11, 'bold'),
        ).pack(pady=(16, 6), padx=16, anchor='w')

        self.urls_textbox = tk.Text(root, height=8, width=88)
        self.urls_textbox.pack(padx=16, pady=(0, 12))

        output_frame = tk.Frame(root)
        output_frame.pack(padx=16, pady=(0, 12), fill='x')
        tk.Label(output_frame, text='Carpeta de salida:').pack(side='left')
        self.output_folder_var = tk.StringVar(value='./downloads')
        tk.Entry(output_frame, textvariable=self.output_folder_var, width=52).pack(
            side='left', padx=(8, 6)
        )
        tk.Button(output_frame, text='Examinar', command=self._select_folder, width=12).pack(
            side='left'
        )

        options_row = tk.Frame(root)
        options_row.pack(padx=16, pady=(0, 6), fill='x')
        self.allow_playlist_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_row,
            text='Permitir playlists',
            variable=self.allow_playlist_var,
        ).pack(side='left', padx=(0, 16))
        self.skip_existing_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text='Saltar archivos existentes',
            variable=self.skip_existing_var,
        ).pack(side='left', padx=(0, 16))
        self.write_metadata_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_row,
            text='Metadatos',
            variable=self.write_metadata_var,
        ).pack(side='left', padx=(0, 16))
        self.embed_thumbnail_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_row,
            text='Thumbnail',
            variable=self.embed_thumbnail_var,
        ).pack(side='left')

        format_row = tk.Frame(root)
        format_row.pack(padx=16, pady=(0, 12), fill='x')
        tk.Label(format_row, text='Tipo:').pack(side='left', padx=(0, 6))
        self.mode_var = tk.StringVar(value='audio')
        self.mode_select = ttk.Combobox(
            format_row,
            textvariable=self.mode_var,
            values=tuple(sorted(MODES)),
            state='readonly',
            width=8,
        )
        self.mode_select.pack(side='left', padx=(0, 16))
        self.mode_select.bind('<<ComboboxSelected>>', self._handle_mode_change)

        tk.Label(format_row, text='Audio:').pack(side='left', padx=(0, 6))
        self.audio_format_var = tk.StringVar(value='mp3')
        self.audio_format_select = ttk.Combobox(
            format_row,
            textvariable=self.audio_format_var,
            values=tuple(sorted(AUDIO_FORMATS)),
            state='readonly',
            width=8,
        )
        self.audio_format_select.pack(side='left', padx=(0, 16))

        tk.Label(format_row, text='Calidad:').pack(side='left', padx=(0, 6))
        self.audio_quality_var = tk.StringVar(value='192')
        self.audio_quality_select = ttk.Combobox(
            format_row,
            textvariable=self.audio_quality_var,
            values=tuple(sorted(QUALITY_LEVELS)),
            state='readonly',
            width=8,
        )
        self.audio_quality_select.pack(side='left', padx=(0, 16))

        tk.Label(format_row, text='Video:').pack(side='left', padx=(0, 6))
        self.video_format_var = tk.StringVar(value='mp4')
        self.video_format_select = ttk.Combobox(
            format_row,
            textvariable=self.video_format_var,
            values=tuple(sorted(VIDEO_FORMATS)),
            state='readonly',
            width=8,
        )
        self.video_format_select.pack(side='left')

        advanced_row = tk.Frame(root)
        advanced_row.pack(padx=16, pady=(0, 12), fill='x')
        tk.Label(advanced_row, text='Paralelo:').pack(side='left', padx=(0, 6))
        self.parallel_var = tk.IntVar(value=1)
        tk.Spinbox(advanced_row, from_=1, to=8, textvariable=self.parallel_var, width=4).pack(
            side='left', padx=(0, 16)
        )
        tk.Label(advanced_row, text='Reintentos:').pack(side='left', padx=(0, 6))
        self.retries_var = tk.IntVar(value=3)
        tk.Spinbox(advanced_row, from_=1, to=10, textvariable=self.retries_var, width=4).pack(
            side='left', padx=(0, 16)
        )

        tk.Label(advanced_row, text='Cookies navegador:').pack(side='left', padx=(0, 6))
        self.cookies_browser_var = tk.StringVar(value='')
        ttk.Combobox(
            advanced_row,
            textvariable=self.cookies_browser_var,
            values=('',) + tuple(sorted(SUPPORTED_BROWSERS)),
            state='readonly',
            width=10,
        ).pack(side='left')

        cookies_file_frame = tk.Frame(root)
        cookies_file_frame.pack(padx=16, pady=(0, 8), fill='x')
        tk.Label(cookies_file_frame, text='Cookies (archivo .txt):').pack(side='left')
        self.cookies_file_var = tk.StringVar(value='')
        tk.Entry(cookies_file_frame, textvariable=self.cookies_file_var, width=44).pack(
            side='left', padx=(8, 6)
        )
        tk.Button(cookies_file_frame, text='Buscar', command=self._select_cookies_file, width=12).pack(
            side='left'
        )

        ffmpeg_frame = tk.Frame(root)
        ffmpeg_frame.pack(padx=16, pady=(0, 12), fill='x')
        tk.Label(ffmpeg_frame, text='FFmpeg (opcional):').pack(side='left')
        detected = detect_ffmpeg_path() or ''
        self.ffmpeg_path_var = tk.StringVar(value=detected)
        tk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path_var, width=52).pack(
            side='left', padx=(8, 6)
        )
        tk.Button(ffmpeg_frame, text='Buscar', command=self._select_ffmpeg, width=12).pack(
            side='left'
        )

        buttons_frame = tk.Frame(root)
        buttons_frame.pack(pady=(4, 8))
        self.download_button = tk.Button(
            buttons_frame, text='Descargar', command=self._start_download, width=20
        )
        self.download_button.pack(side='left', padx=(0, 8))
        self.cancel_button = tk.Button(
            buttons_frame, text='Cancelar', command=self._cancel_download, width=12, state='disabled'
        )
        self.cancel_button.pack(side='left')

        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            root, orient='horizontal', mode='determinate', length=720, variable=self.progress_var
        )
        self.progress_bar.pack(padx=16, pady=(0, 4))

        results_frame = tk.Frame(root)
        results_frame.pack(padx=16, pady=(0, 4), fill='both', expand=True)
        tk.Label(results_frame, text='Estado por URL:').pack(anchor='w')

        tree_frame = tk.Frame(results_frame)
        tree_frame.pack(fill='both', expand=True)

        columns = ('#', 'url', 'status', 'message')
        self.results_list = ttk.Treeview(
            tree_frame, columns=columns, show='headings', height=7
        )
        for col, width, anchor in (
            ('#', 30, 'center'),
            ('url', 380, 'w'),
            ('status', 90, 'center'),
            ('message', 220, 'w'),
        ):
            self.results_list.heading(col, text=col.upper() if col == '#' else col.title())
            self.results_list.column(col, width=width, minwidth=30, anchor=anchor, stretch=(col == 'url'))

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.results_list.yview)
        self.results_list.configure(yscrollcommand=scrollbar.set)
        self.results_list.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.results_list.bind('<<TreeviewSelect>>', self._on_row_select)

        detail_frame = tk.Frame(root)
        detail_frame.pack(padx=16, pady=(0, 4), fill='x')
        tk.Label(detail_frame, text='Detalle:', anchor='w').pack(anchor='w')
        self.detail_text = tk.Text(detail_frame, height=3, wrap='word', state='disabled',
                                   bg='#f3f4f6', relief='flat', font=('Consolas', 9))
        detail_scroll = ttk.Scrollbar(detail_frame, orient='vertical', command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scroll.set)
        self.detail_text.pack(side='left', fill='x', expand=True)
        detail_scroll.pack(side='right', fill='y')

        self.status_var = tk.StringVar(value='Listo para descargar.')
        tk.Label(root, textvariable=self.status_var, fg='#1f2937').pack(pady=(2, 4))

    # ------------------------------------------------------------- handlers

    def _select_folder(self) -> None:
        current = self.output_folder_var.get().strip() or '.'
        folder = filedialog.askdirectory(title='Selecciona la carpeta de salida', initialdir=current)
        if folder:
            self.output_folder_var.set(folder)

    def _select_cookies_file(self) -> None:
        path = filedialog.askopenfilename(
            title='Selecciona el archivo de cookies',
            filetypes=[('Cookies', '*.txt'), ('Todos los archivos', '*.*')],
        )
        if path:
            self.cookies_file_var.set(path)

    def _select_ffmpeg(self) -> None:
        initial = self.ffmpeg_path_var.get().strip() or '.'
        file_types = [('Ejecutables', '*.exe'), ('Todos los archivos', '*.*')] if sys.platform.startswith('win') else [('Todos los archivos', '*.*')]
        path = filedialog.askopenfilename(
            title='Selecciona el ejecutable de FFmpeg',
            initialdir=initial,
            filetypes=file_types,
        )
        if path:
            self.ffmpeg_path_var.set(path)

    def _handle_mode_change(self, event: object = None) -> None:
        if self.mode_var.get() == 'video':
            self.audio_format_select.configure(state='disabled')
            self.audio_quality_select.configure(state='disabled')
            self.video_format_select.configure(state='readonly')
        else:
            self.audio_format_select.configure(state='readonly')
            self.audio_quality_select.configure(state='readonly')
            self.video_format_select.configure(state='disabled')

    def _build_config(self) -> Optional[DownloadConfig]:
        output_folder = self.output_folder_var.get().strip()
        if not output_folder:
            messagebox.showerror('Error', 'Debes definir una carpeta de salida.')
            return None
        try:
            cfg = DownloadConfig(
                output_folder=output_folder,
                mode=self.mode_var.get(),
                audio_format=self.audio_format_var.get(),
                audio_quality=self.audio_quality_var.get(),
                video_format=self.video_format_var.get(),
                ffmpeg_path=self.ffmpeg_path_var.get().strip() or None,
                skip_existing=bool(self.skip_existing_var.get()),
                allow_playlist=bool(self.allow_playlist_var.get()),
                max_retries=int(self.retries_var.get()),
                parallel_downloads=int(self.parallel_var.get()),
                write_metadata=bool(self.write_metadata_var.get()),
                embed_thumbnail=bool(self.embed_thumbnail_var.get()),
                cookies_from_browser=(self.cookies_browser_var.get().strip() or None),
                cookies_file=(self.cookies_file_var.get().strip() or None),
            )
            cfg.validate()
            return cfg
        except Exception as exc:
            messagebox.showerror('Configuración inválida', str(exc))
            return None

    def _start_download(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        urls = extract_links_from_text(self.urls_textbox.get('1.0', tk.END))
        if not urls:
            messagebox.showerror('Error', 'Debes ingresar al menos una URL.')
            return
        config = self._build_config()
        if config is None:
            return

        Path(config.output_folder).mkdir(parents=True, exist_ok=True)
        self.results_list.delete(*self.results_list.get_children())
        self.progress_bar.configure(maximum=len(urls))
        self.progress_var.set(0)
        self.status_var.set(f'Descargando 0/{len(urls)}…')
        self.cancel_event = threading.Event()
        self.download_button.configure(state='disabled')
        self.cancel_button.configure(state='normal')
        self.results = []

        downloader = Downloader(
            config,
            progress_callback=self._progress_callback,
            cancel_event=self.cancel_event,
        )

        def worker() -> None:
            try:
                results = downloader.download_many(urls)
                self.progress_queue.put(('done', results))
            except Exception as exc:
                self.progress_queue.put(('crash', exc))

        self.worker = threading.Thread(target=worker, daemon=True)
        self.worker.start()
        self.root.after(POLL_INTERVAL_MS, self._drain_queue)

    def _cancel_download(self) -> None:
        if not (self.worker and self.worker.is_alive()):
            return
        self.cancel_event.set()
        self.status_var.set('Cancelando…')
        self.cancel_button.configure(state='disabled')

    def _progress_callback(self, result: DownloadResult, index: int, total: int) -> None:
        self.progress_queue.put(('progress', (result, index, total)))

    def _drain_queue(self) -> None:
        try:
            while True:
                kind, payload = self.progress_queue.get_nowait()
                if kind == 'progress':
                    result, index, total = payload
                    self._append_result_row(index, result)
                    self.progress_var.set(index)
                    self.status_var.set(f'Procesado {index}/{total}: {result.status}')
                elif kind == 'done':
                    self.results = list(payload)
                    self._finish_download()
                    return
                elif kind == 'crash':
                    messagebox.showerror('Error inesperado', str(payload))
                    self._finish_download()
                    return
        except queue.Empty:
            pass

        if self.worker and self.worker.is_alive():
            self.root.after(POLL_INTERVAL_MS, self._drain_queue)
        else:
            self._finish_download()

    def _on_row_select(self, event: object = None) -> None:
        selected = self.results_list.selection()
        if not selected:
            return
        values = self.results_list.item(selected[0], 'values')
        if not values:
            return
        _, url, status, message = values
        text = f'URL: {url}\nEstado: {status}\nMensaje: {message}'
        self.detail_text.configure(state='normal')
        self.detail_text.delete('1.0', tk.END)
        self.detail_text.insert('1.0', text)
        self.detail_text.configure(state='disabled')

    def _append_result_row(self, index: int, result: DownloadResult) -> None:
        self.results_list.insert(
            '', tk.END, values=(str(index), result.url, result.status, result.message)
        )

    def _finish_download(self) -> None:
        self.download_button.configure(state='normal')
        self.cancel_button.configure(state='disabled')
        self.worker = None

        if not self.results:
            self.status_var.set('Sin resultados.')
            return

        summary = summarize(self.results)
        total = len(self.results)
        text = (
            f'Total: {total}\n'
            f'Exitosas: {summary["success"]}\n'
            f'Saltadas: {summary["skipped"]}\n'
            f'Inválidas: {summary["invalid"]}\n'
            f'Errores: {summary["error"]}\n'
            f'Canceladas: {summary["cancelled"]}'
        )
        if summary['error'] or summary['invalid']:
            self.status_var.set('Descarga finalizada con advertencias.')
            messagebox.showwarning('Resultado', text)
        elif summary['cancelled']:
            self.status_var.set('Descarga cancelada.')
            messagebox.showinfo('Cancelado', text)
        else:
            self.status_var.set('Descarga completada.')
            messagebox.showinfo('Listo', text)


def main() -> int:
    setup_logger(verbose=False)
    root = tk.Tk()
    BajadorApp(root)
    root.mainloop()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
