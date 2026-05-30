#!/usr/bin/env python3
"""CLI de Bajador YT.

Carga configuración desde JSON, acepta overrides por argumentos, usa logging
estructurado y muestra una barra de progreso con tqdm.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from bajador_yt import DownloadConfig, Downloader, load_config
from bajador_yt.config import SUPPORTED_BROWSERS
from bajador_yt.constants import AUDIO_FORMATS, MODES, QUALITY_LEVELS, VIDEO_FORMATS
from bajador_yt.csv_utils import CsvFormatError, extract_links_from_csv
from bajador_yt.downloader import summarize
from bajador_yt.logger import get_logger, setup_logger
from bajador_yt.validators import is_valid_youtube_url

EXIT_OK = 0
EXIT_WITH_ERRORS = 1
EXIT_BAD_USAGE = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='bajador-yt',
        description='Descarga audio o video desde YouTube usando yt-dlp.',
    )
    parser.add_argument('--config', help='Ruta a un archivo JSON de configuración.')
    parser.add_argument('--csv', help='CSV con columna "link" que lista URLs.')
    parser.add_argument('--urls', nargs='+', help='URLs de YouTube a descargar.')
    parser.add_argument('--output', dest='output_folder', help='Carpeta de salida.')
    parser.add_argument('--mode', choices=sorted(MODES))
    parser.add_argument('--audio-format', dest='audio_format', choices=sorted(AUDIO_FORMATS))
    parser.add_argument('--audio-quality', dest='audio_quality', choices=sorted(QUALITY_LEVELS))
    parser.add_argument('--video-format', dest='video_format', choices=sorted(VIDEO_FORMATS))
    parser.add_argument('--ffmpeg', dest='ffmpeg_path', help='Ruta al ejecutable de FFmpeg.')
    parser.add_argument('--parallel', dest='parallel_downloads', type=int,
                        help='Número de descargas en paralelo (>=1).')
    parser.add_argument('--retries', dest='max_retries', type=int,
                        help='Reintentos por URL ante errores recuperables.')
    parser.add_argument('--retry-backoff', dest='retry_backoff', type=float,
                        help='Factor de backoff exponencial entre reintentos.')

    skip_group = parser.add_mutually_exclusive_group()
    skip_group.add_argument('--skip-existing', dest='skip_existing', action='store_true')
    skip_group.add_argument('--no-skip-existing', dest='skip_existing', action='store_false')
    parser.set_defaults(skip_existing=None)

    playlist_group = parser.add_mutually_exclusive_group()
    playlist_group.add_argument('--allow-playlist', dest='allow_playlist', action='store_true')
    playlist_group.add_argument('--no-playlist', dest='allow_playlist', action='store_false')
    parser.set_defaults(allow_playlist=None)

    parser.add_argument('--write-metadata', dest='write_metadata', action='store_true', default=None)
    parser.add_argument('--embed-thumbnail', dest='embed_thumbnail', action='store_true', default=None)
    parser.add_argument(
        '--cookies-from-browser', dest='cookies_from_browser',
        choices=sorted(SUPPORTED_BROWSERS),
        help='Usa cookies del navegador para sortear "Please sign in".',
    )
    parser.add_argument('--cookies-file', dest='cookies_file',
                        help='Ruta a un cookies.txt exportado (formato Netscape).')
    parser.add_argument('--log-file', dest='log_file', help='Ruta del archivo de log.')
    parser.add_argument('--verbose', '-v', action='store_true', default=None,
                        help='Activa logging detallado (DEBUG).')
    parser.add_argument('--validate-only', action='store_true',
                        help='Solo valida las URLs sin descargar.')
    parser.add_argument('--no-progress', action='store_true',
                        help='Desactiva la barra tqdm (útil en CI o logs).')
    return parser


def gather_urls(args: argparse.Namespace, config: DownloadConfig, log) -> Optional[list[str]]:
    """Reúne URLs según prioridad: --urls > --csv > csv_file de config.

    Si el usuario pasa --urls, ignora el CSV por defecto; así se evita mezclar
    URLs ad-hoc con la lista persistente.
    """
    urls: list[str] = []

    if args.urls:
        urls.extend(args.urls)
    elif args.csv:
        csv_path = Path(args.csv)
        if not csv_path.exists():
            log.error('El CSV indicado no existe: %s', csv_path)
            return None
        try:
            urls.extend(extract_links_from_csv(csv_path))
        except CsvFormatError as exc:
            log.error('%s', exc)
            return None
    elif config.csv_file:
        csv_path = Path(config.csv_file)
        if csv_path.exists():
            try:
                urls.extend(extract_links_from_csv(csv_path))
            except CsvFormatError as exc:
                log.error('%s', exc)
                return None

    # Eliminar duplicados conservando el orden.
    seen: set[str] = set()
    unique: list[str] = []
    for u in urls:
        if u and u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        config = load_config(args.config) if args.config else DownloadConfig()
    except Exception as exc:
        print(f'Error de configuración: {exc}', file=sys.stderr)
        return EXIT_BAD_USAGE

    overrides = {
        'output_folder': args.output_folder,
        'mode': args.mode,
        'audio_format': args.audio_format,
        'audio_quality': args.audio_quality,
        'video_format': args.video_format,
        'ffmpeg_path': args.ffmpeg_path,
        'parallel_downloads': args.parallel_downloads,
        'max_retries': args.max_retries,
        'retry_backoff': args.retry_backoff,
        'skip_existing': args.skip_existing,
        'allow_playlist': args.allow_playlist,
        'write_metadata': args.write_metadata,
        'embed_thumbnail': args.embed_thumbnail,
        'cookies_from_browser': args.cookies_from_browser,
        'cookies_file': args.cookies_file,
        'log_file': args.log_file,
        'verbose': args.verbose,
    }
    try:
        config = config.merged(overrides)
        config.validate()
    except Exception as exc:
        print(f'Configuración inválida: {exc}', file=sys.stderr)
        return EXIT_BAD_USAGE

    setup_logger(verbose=config.verbose, log_file=config.log_file)
    log = get_logger()

    urls = gather_urls(args, config, log)
    if urls is None:
        return EXIT_BAD_USAGE
    if not urls:
        log.error('No se proporcionaron URLs. Usa --urls o --csv.')
        return EXIT_BAD_USAGE

    if args.validate_only:
        bad = 0
        for url in urls:
            ok = is_valid_youtube_url(url)
            print(f'{"OK " if ok else "NO "} {url}')
            if not ok:
                bad += 1
        log.info('Validación completa. %d válidas, %d inválidas.', len(urls) - bad, bad)
        return EXIT_OK if bad == 0 else EXIT_WITH_ERRORS

    pbar: Optional[tqdm] = None
    if not args.no_progress:
        pbar = tqdm(total=len(urls), desc='Descargando', unit='video', leave=True)

    def progress(result, index, total):
        if pbar is not None:
            pbar.update(1)
            pbar.set_postfix_str(f'{result.status} · {result.url[:40]}')

    downloader = Downloader(config, progress_callback=progress)
    try:
        results = downloader.download_many(urls)
    finally:
        if pbar is not None:
            pbar.close()

    summary = summarize(results)
    log.info(
        'Resumen — total=%d éxitos=%d saltadas=%d inválidas=%d errores=%d canceladas=%d',
        len(results),
        summary['success'],
        summary['skipped'],
        summary['invalid'],
        summary['error'],
        summary['cancelled'],
    )
    for r in results:
        if r.status in ('error', 'invalid'):
            log.warning('[%s] %s — %s', r.status, r.url, r.message)

    return EXIT_OK if summary['error'] == 0 else EXIT_WITH_ERRORS


if __name__ == '__main__':
    raise SystemExit(main())
