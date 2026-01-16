import csv
import os
import shutil
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional
from urllib.parse import urlparse

import yt_dlp


def extract_links_from_csv(csv_file: str) -> List[str]:
    links: List[str] = []
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            link = row.get('link')
            if not link:
                continue
            links.append(link.strip())
    return links


def extract_links_from_text(urls_text: str) -> List[str]:
    if not urls_text:
        return []
    return [line.strip() for line in urls_text.splitlines() if line.strip()]


def ensure_output_folder(output_folder: str) -> None:
    if not output_folder:
        return
    os.makedirs(output_folder, exist_ok=True)

@dataclass(frozen=True)
class DownloadResult:
    url: str
    status: str
    message: str
    output_path: Optional[str] = None


def is_valid_youtube_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url.strip())
    if parsed.scheme not in ('http', 'https'):
        return False
    host = parsed.netloc.lower()
    if not host:
        return False
    return host == 'youtu.be' or host.endswith('youtube.com')


def detect_ffmpeg_path() -> Optional[str]:
    env_path = os.environ.get('FFMPEG_PATH')
    if env_path and os.path.exists(env_path):
        return env_path

    which_path = shutil.which('ffmpeg')
    if which_path:
        return which_path

    common_paths = [
        'C:/Program Files/ffmpeg-7.0.2-full_build/bin/ffmpeg.exe',
        'C:/Program Files/ffmpeg/bin/ffmpeg.exe',
        'C:/ffmpeg/bin/ffmpeg.exe',
        '/usr/local/bin/ffmpeg',
        '/usr/bin/ffmpeg',
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None


def build_ydl_options(
    output_folder: str,
    ffmpeg_path: Optional[str],
    allow_playlist: bool,
) -> dict:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': not allow_playlist,
        'restrictfilenames': True,
        'nooverwrites': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
    }
    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path
    return ydl_opts


def get_expected_mp3_path(ydl: yt_dlp.YoutubeDL, link: str) -> Optional[str]:
    info = ydl.extract_info(link, download=False)
    if not info:
        return None
    output_path = ydl.prepare_filename(info)
    base, _ = os.path.splitext(output_path)
    return f'{base}.mp3'


def download_audio_from_youtube(
    link: str,
    output_folder: str,
    ffmpeg_path: Optional[str] = None,
    skip_existing: bool = True,
    allow_playlist: bool = False,
) -> DownloadResult:
    if not link:
        return DownloadResult(url=link, status='invalid', message='URL vacía.')

    if not is_valid_youtube_url(link):
        return DownloadResult(url=link, status='invalid', message='URL no válida.')

    ensure_output_folder(output_folder)
    resolved_ffmpeg_path = ffmpeg_path or detect_ffmpeg_path()
    ydl_opts = build_ydl_options(output_folder, resolved_ffmpeg_path, allow_playlist)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            expected_mp3 = get_expected_mp3_path(ydl, link)
            if expected_mp3 and skip_existing and os.path.exists(expected_mp3):
                return DownloadResult(
                    url=link,
                    status='skipped',
                    message='El archivo ya existe.',
                    output_path=expected_mp3,
                )
            ydl.download([link])
            if expected_mp3 and os.path.exists(expected_mp3):
                return DownloadResult(
                    url=link,
                    status='success',
                    message='Descarga completada.',
                    output_path=expected_mp3,
                )
            return DownloadResult(url=link, status='success', message='Descarga completada.')
    except Exception as error:
        return DownloadResult(url=link, status='error', message=str(error))


def download_from_links(
    links: Iterable[str],
    output_folder: str,
    progress_callback: Optional[Callable[[DownloadResult, int, int], None]] = None,
    allow_playlist: bool = False,
) -> List[DownloadResult]:
    ensure_output_folder(output_folder)
    results: List[DownloadResult] = []
    links_list = [link for link in links if link]
    total = len(links_list)
    for index, link in enumerate(links_list, start=1):
        if not link:
            continue
        print(f'Downloading audio from: {link}')
        result = download_audio_from_youtube(
            link,
            output_folder,
            allow_playlist=allow_playlist,
        )
        results.append(result)
        print(result.message)
        if progress_callback:
            progress_callback(result, index, total)
    return results


def download_from_csv(csv_file: str, output_folder: str) -> None:
    links = extract_links_from_csv(csv_file)
    download_from_links(links, output_folder)
