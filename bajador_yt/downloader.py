"""Lógica central de descarga con reintentos, threading y skip inteligente."""

from __future__ import annotations

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional

import yt_dlp

from .config import DownloadConfig
from .errors import classify_error, is_retryable, user_friendly_message
from .ffmpeg_utils import detect_ffmpeg_path, validate_ffmpeg_path
from .logger import get_logger
from .models import DownloadResult
from .validators import is_valid_youtube_url

ProgressCallback = Callable[[DownloadResult, int, int], None]


class Downloader:
    """Envuelve yt-dlp con reintentos, skip, threading y callback de progreso."""

    def __init__(
        self,
        config: DownloadConfig,
        *,
        progress_callback: Optional[ProgressCallback] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> None:
        config.validate()
        self.config = config
        self.progress_callback = progress_callback
        self.cancel_event = cancel_event
        self._log = get_logger('downloader')
        self._ffmpeg_path = (
            validate_ffmpeg_path(config.ffmpeg_path) or detect_ffmpeg_path()
        )
        if config.ffmpeg_path and not self._ffmpeg_path:
            self._log.warning(
                "FFmpeg configurado en %s no existe; usando detección automática.",
                config.ffmpeg_path,
            )

    # ------------------------------------------------------------------ helpers

    def _cancelled(self) -> bool:
        return bool(self.cancel_event and self.cancel_event.is_set())

    def _build_ydl_opts(self) -> dict[str, Any]:
        cfg = self.config
        out_template = str(Path(cfg.output_folder) / '%(title)s.%(ext)s')
        opts: dict[str, Any] = {
            'format': 'bestaudio/best' if cfg.mode == 'audio' else 'bestvideo+bestaudio/best',
            'outtmpl': out_template,
            'noplaylist': not cfg.allow_playlist,
            'restrictfilenames': True,
            'nooverwrites': True,
            'retries': cfg.max_retries,
            'fragment_retries': cfg.max_retries,
            'quiet': not cfg.verbose,
            'no_warnings': not cfg.verbose,
            'ignoreerrors': False,
            'socket_timeout': 30,
        }

        postprocessors: list[dict[str, Any]] = []
        if cfg.mode == 'audio':
            postprocessors.append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': cfg.audio_format,
                'preferredquality': cfg.audio_quality,
            })
        else:
            opts['merge_output_format'] = cfg.video_format

        if cfg.write_metadata:
            postprocessors.append({'key': 'FFmpegMetadata'})
        if cfg.embed_thumbnail:
            opts['writethumbnail'] = True
            postprocessors.append({'key': 'EmbedThumbnail'})

        if postprocessors:
            opts['postprocessors'] = postprocessors

        if self._ffmpeg_path:
            opts['ffmpeg_location'] = self._ffmpeg_path

        if cfg.cookies_from_browser:
            # yt-dlp espera una tupla (browser, profile, keyring, container).
            opts['cookiesfrombrowser'] = (cfg.cookies_from_browser,)
        if cfg.cookies_file:
            opts['cookiefile'] = cfg.cookies_file

        return opts

    def _expected_output(self, ydl: yt_dlp.YoutubeDL, info: dict[str, Any]) -> Optional[str]:
        try:
            path = ydl.prepare_filename(info)
        except Exception:  # pragma: no cover — defensive
            return None
        base, _ = os.path.splitext(path)
        ext = self.config.audio_format if self.config.mode == 'audio' else self.config.video_format
        return f'{base}.{ext}'

    def _validate_url_params(self, url: str) -> Optional[DownloadResult]:
        url = url.strip()
        if not url:
            return DownloadResult(url=url, status='invalid', message='URL vacía.')
        if not is_valid_youtube_url(url):
            return DownloadResult(url=url, status='invalid', message='URL no válida.')
        return None

    # ------------------------------------------------------------------ public

    def download_one(self, url: str) -> DownloadResult:
        """Descarga una única URL aplicando reintentos con backoff exponencial."""
        url = url.strip()
        invalid = self._validate_url_params(url)
        if invalid is not None:
            return invalid

        if self._cancelled():
            return DownloadResult(url=url, status='cancelled', message='Cancelado por el usuario.')

        Path(self.config.output_folder).mkdir(parents=True, exist_ok=True)
        opts = self._build_ydl_opts()

        last_exc: Optional[BaseException] = None
        last_category = 'generic'
        for attempt in range(1, self.config.max_retries + 1):
            if self._cancelled():
                return DownloadResult(url=url, status='cancelled', message='Cancelado por el usuario.')

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info is None:
                        return DownloadResult(
                            url=url,
                            status='error',
                            message='No se pudo obtener información del video.',
                            category='extractor',
                        )

                    if info.get('_type') == 'playlist':
                        if not self.config.allow_playlist:
                            return DownloadResult(
                                url=url,
                                status='invalid',
                                message='La URL es una playlist y "Permitir playlists" está desactivado.',
                            )
                        ydl.process_ie_result(info, download=True)
                        entries = info.get('entries') or []
                        return DownloadResult(
                            url=url,
                            status='success',
                            message=f'Playlist descargada ({sum(1 for _ in entries)} elementos).',
                        )

                    expected = self._expected_output(ydl, info)
                    if (
                        self.config.skip_existing
                        and expected
                        and Path(expected).exists()
                    ):
                        return DownloadResult(
                            url=url,
                            status='skipped',
                            message='El archivo ya existe.',
                            output_path=expected,
                        )

                    ydl.process_ie_result(info, download=True)
                    final_path = expected if expected and Path(expected).exists() else None
                    return DownloadResult(
                        url=url,
                        status='success',
                        message='Descarga completada.',
                        output_path=final_path,
                    )
            except yt_dlp.utils.DownloadError as exc:
                last_exc = exc
                last_category = classify_error(exc)
                if not is_retryable(last_category) or attempt >= self.config.max_retries:
                    break
                wait = self.config.retry_backoff ** attempt
                self._log.warning(
                    'Fallo %s (categoría=%s) en %s; reintento %d/%d en %.1fs.',
                    exc, last_category, url, attempt, self.config.max_retries, wait,
                )
                self._sleep_interruptible(wait)
            except Exception as exc:  # pragma: no cover — red de seguridad
                last_exc = exc
                last_category = classify_error(exc)
                break

        return DownloadResult(
            url=url,
            status='error',
            message=user_friendly_message(last_exc, last_category),
            category=last_category,
        )

    def download_many(self, urls: Iterable[str]) -> List[DownloadResult]:
        """Descarga varias URLs, usando threading si parallel_downloads > 1."""
        url_list = [u for u in (x.strip() for x in urls) if u]
        total = len(url_list)
        if total == 0:
            return []

        results: List[DownloadResult] = []
        if self.config.parallel_downloads <= 1:
            for index, url in enumerate(url_list, start=1):
                if self._cancelled():
                    results.append(DownloadResult(url=url, status='cancelled', message='Cancelado.'))
                    self._emit(results[-1], index, total)
                    continue
                result = self.download_one(url)
                results.append(result)
                self._emit(result, index, total)
            return results

        self._log.info('Descargando en paralelo con %d workers.', self.config.parallel_downloads)
        completed = 0
        with ThreadPoolExecutor(max_workers=self.config.parallel_downloads) as pool:
            future_map = {pool.submit(self.download_one, url): url for url in url_list}
            for future in as_completed(future_map):
                completed += 1
                try:
                    result = future.result()
                except Exception as exc:  # pragma: no cover
                    result = DownloadResult(
                        url=future_map[future],
                        status='error',
                        message=str(exc),
                        category=classify_error(exc),
                    )
                results.append(result)
                self._emit(result, completed, total)
        return results

    # ------------------------------------------------------------------ util

    def _emit(self, result: DownloadResult, index: int, total: int) -> None:
        self._log.info('[%d/%d] %s — %s', index, total, result.status, result.url)
        if self.progress_callback:
            try:
                self.progress_callback(result, index, total)
            except Exception:
                self._log.exception('Error en progress_callback; se ignora.')

    def _sleep_interruptible(self, seconds: float) -> None:
        """Duerme en intervalos pequeños para respetar la cancelación."""
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            if self._cancelled():
                return
            time.sleep(min(0.25, end - time.monotonic()))


def summarize(results: Iterable[DownloadResult]) -> dict[str, int]:
    """Cuenta resultados por estado para mostrar resumen."""
    summary = {'success': 0, 'skipped': 0, 'invalid': 0, 'error': 0, 'cancelled': 0}
    for r in results:
        if r.status in summary:
            summary[r.status] += 1
    return summary
