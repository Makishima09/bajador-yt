import csv
"""from pytube import YouTube"""
import yt_dlp

# Función para leer el archivo CSV y extraer enlaces
def extract_links_from_csv(csv_file):
    links = []
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            links.append(row['link'])
    return links

# Función para descargar el audio de YouTube
"""def download_audio_from_youtube(link, output_folder):
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()
    output_file = stream.download(output_folder)
    return output_file"""

def download_audio_from_youtube(link, output_folder):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'ffmpeg_location': 'C:/Program Files/ffmpeg-7.0.2-full_build/bin',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

# Función principal de automatización
def automate_youtube_download(csv_file, output_folder):
    links = extract_links_from_csv(csv_file)
    for link in links:
        print(f"Downloading audio from: {link}")
        download_audio_from_youtube(link, output_folder)
        print("Download complete!")

# Ejecutar la automatización
csv_file = './url-list.csv'
output_folder = './downloads'
automate_youtube_download(csv_file, output_folder)
