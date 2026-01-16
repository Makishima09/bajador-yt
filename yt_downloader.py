import csv
import os
from typing import Iterable, List

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


def download_audio_from_youtube(link: str, output_folder: str) -> None:
    if not link:
        return
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'ffmpeg_location': 'C:/Program Files/ffmpeg-7.0.2-full_build/bin',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


def download_from_links(links: Iterable[str], output_folder: str) -> None:
    ensure_output_folder(output_folder)
    for link in links:
        if not link:
            continue
        print(f'Downloading audio from: {link}')
        download_audio_from_youtube(link, output_folder)
        print('Download complete!')


def download_from_csv(csv_file: str, output_folder: str) -> None:
    links = extract_links_from_csv(csv_file)
    download_from_links(links, output_folder)
