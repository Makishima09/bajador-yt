import csv
import os
import shutil
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional
from urllib.parse import urlparse

import yt_dlp

AUDIO_FORMATS = {'mp3', 'm4a', 'opus', 'wav'}
VIDEO_FORMATS = {'mp4', 'mkv', 'webm'}
QUALITY_LEVELS = {'128', '192', '256', '320'}
MODES = {'audio', 'video'}


@dataclass(frozen=True)
class DownloadResult:
    url: str
    status: str
    message: str
    output_path: Optional[str] = None


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


def is_supported_mode(mode: str) -> bool:
    return mode in MODES


def is_supported_audio_format(audio_format: str) -> bool:
    return audio_format in AUDIO_FORMATS


def is_supported_video_format(video_format: str) -> bool:
    return video_format in VIDEO_FORMATS


def is_supported_quality(quality: str) -> bool:
    return quality in QUALITY_LEVELS


def build_ydl_options(
    output_folder: str,
    ffmpeg_path: Optional[str],
    allow_playlist: bool,
    mode: str,
    audio_format: str,
    audio_quality: str,
    video_format: str,
) -> dict:
    ydl_opts = {
        'format': 'bestaudio/best' if mode == 'audio' else 'bestvideo+bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': not allow_playlist,
        'restrictfilenames': True,
        'nooverwrites': True,
    }
    if mode == 'audio':
        ydl_opts['postprocessors'] = [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': audio_quality,
            }
        ]
    else:
        ydl_opts['merge_output_format'] = video_format

    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    return ydl_opts


def get_expected_output_path(
    ydl: yt_dlp.YoutubeDL,
    link: str,
    mode: str,
    audio_format: str,
    video_format: str,
) -> Optional[str]:
    info = ydl.extract_info(link, download=False)
    if not info:
        return None
    output_path = ydl.prepare_filename(info)
    base, _ = os.path.splitext(output_path)
    extension = audio_format if mode == 'audio' else video_format
    return f'{base}.{extension}'


def download_media_from_youtube(
    link: str,
    output_folder: str,
    ffmpeg_path: Optional[str] = None,
    skip_existing: bool = True,
    allow_playlist: bool = False,
    mode: str = 'audio',
    audio_format: str = 'mp3',
    audio_quality: str = '192',
    video_format: str = 'mp4',
) -> DownloadResult:
    if not link:
        return DownloadResult(url=link, status='invalid', message='URL vacía.')

    if not is_valid_youtube_url(link):
        return DownloadResult(url=link, status='invalid', message='URL no válida.')

    if not is_supported_mode(mode):
        return DownloadResult(url=link, status='invalid', message='Modo no soportado.')

    if mode == 'audio' and not is_supported_audio_format(audio_format):
        return DownloadResult(url=link, status='invalid', message='Formato de audio no soportado.')

    if mode == 'audio' and not is_supported_quality(audio_quality):
        return DownloadResult(url=link, status='invalid', message='Calidad no soportada.')

    if mode == 'video' and not is_supported_video_format(video_format):
        return DownloadResult(url=link, status='invalid', message='Formato de video no soportado.')

    ensure_output_folder(output_folder)
    resolved_ffmpeg_path = ffmpeg_path or detect_ffmpeg_path()
    ydl_opts = build_ydl_options(
        output_folder,
        resolved_ffmpeg_path,
        allow_playlist,
        mode,
        audio_format,
        audio_quality,
        video_format,
    )

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            expected_output = get_expected_output_path(
                ydl,
                link,
                mode,
                audio_format,
                video_format,
            )
            if expected_output and skip_existing and os.path.exists(expected_output):
                return DownloadResult(
                    url=link,
                    status='skipped',
                    message='El archivo ya existe.',
                    output_path=expected_output,
                )
            ydl.download([link])
            if expected_output and os.path.exists(expected_output):
                return DownloadResult(
                    url=link,
                    status='success',
                    message='Descarga completada.',
                    output_path=expected_output,
                )
            return DownloadResult(url=link, status='success', message='Descarga completada.')
    except Exception as error:
        return DownloadResult(url=link, status='error', message=str(error))


def download_from_links(
    links: Iterable[str],
    output_folder: str,
    progress_callback: Optional[Callable[[DownloadResult, int, int], None]] = None,
    allow_playlist: bool = False,
    mode: str = 'audio',
    audio_format: str = 'mp3',
    audio_quality: str = '192',
    video_format: str = 'mp4',
    ffmpeg_path: Optional[str] = None,
) -> List[DownloadResult]:
    ensure_output_folder(output_folder)
    results: List[DownloadResult] = []
    links_list = [link for link in links if link]
    total = len(links_list)
    for index, link in enumerate(links_list, start=1):
        if not link:
            continue
        print(f'Downloading from: {link}')
        result = download_media_from_youtube(
            link,
            output_folder,
            ffmpeg_path=ffmpeg_path,
            allow_playlist=allow_playlist,
            mode=mode,
            audio_format=audio_format,
            audio_quality=audio_quality,
            video_format=video_format,
        )
        results.append(result)
        print(result.message)
        if progress_callback:
            progress_callback(result, index, total)
    return results


def download_from_csv(csv_file: str, output_folder: str) -> None:
    links = extract_links_from_csv(csv_file)
    download_from_links(links, output_folder)
