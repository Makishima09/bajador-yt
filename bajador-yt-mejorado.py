#!/usr/bin/env python3
"""
Bajador YouTube - Versión Mejorada
Descargador de audio de YouTube con mejoras en manejo de errores,
configuración flexible y mejor feedback al usuario.
"""

import csv
import os
import sys
import json
import shutil
import logging
import argparse
from pathlib import Path
from typing import List, Optional
import yt_dlp
from tqdm import tqdm

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class YouTubeDownloader:
    """Clase para manejar la descarga de audio de YouTube."""
    
    def __init__(self, output_folder: str = './downloads', 
                 audio_quality: str = '192',
                 audio_format: str = 'mp3',
                 ffmpeg_path: Optional[str] = None,
                 skip_existing: bool = True):
        self.output_folder = Path(output_folder)
        self.audio_quality = audio_quality
        self.audio_format = audio_format
        self.ffmpeg_path = ffmpeg_path or self._find_ffmpeg()
        self.skip_existing = skip_existing
        self.stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        # Crear carpeta de descargas si no existe
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Busca FFmpeg en el sistema."""
        # Buscar en PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return str(Path(ffmpeg_path).parent)
        
        # Buscar en ubicaciones comunes (Windows)
        if sys.platform == 'win32':
            common_paths = [
                'C:/Program Files/ffmpeg/bin',
                'C:/ffmpeg/bin',
                'C:/Program Files/ffmpeg-7.0.2-full_build/bin'
            ]
            for path in common_paths:
                if Path(path).exists():
                    return path
        
        logger.warning("FFmpeg no encontrado. Asegúrate de tenerlo instalado.")
        return None
    
    def _is_valid_url(self, url: str) -> bool:
        """Valida si la URL es de YouTube."""
        youtube_patterns = [
            'youtube.com/watch',
            'youtu.be/',
            'youtube.com/playlist',
            'youtube.com/watch?v='
        ]
        return any(pattern in url for pattern in youtube_patterns)
    
    def _file_exists(self, title: str) -> bool:
        """Verifica si el archivo ya existe."""
        if not self.skip_existing:
            return False
        file_path = self.output_folder / f"{self._sanitize_filename(title)}.{self.audio_format}"
        return file_path.exists()
    
    def _sanitize_filename(self, filename: str) -> str:
        """Limpia el nombre de archivo de caracteres inválidos."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:200]  # Limitar longitud
    
    def download_audio(self, url: str) -> bool:
        """Descarga el audio de una URL de YouTube."""
        if not self._is_valid_url(url):
            logger.error(f"URL inválida: {url}")
            self.stats['failed'] += 1
            return False
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.output_folder / '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.audio_format,
                    'preferredquality': self.audio_quality,
                }],
            }
            
            # Agregar ruta de FFmpeg si está disponible
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Obtener información del video
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                # Verificar si ya existe
                if self._file_exists(title):
                    logger.info(f"⏭️  Saltando (ya existe): {title}")
                    self.stats['skipped'] += 1
                    return True
                
                logger.info(f"⬇️  Descargando: {title}")
                ydl.download([url])
                logger.info(f"✅ Completado: {title}")
                self.stats['success'] += 1
                return True
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"❌ Error al descargar {url}: {str(e)}")
            self.stats['failed'] += 1
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado con {url}: {str(e)}")
            self.stats['failed'] += 1
            return False
    
    def download_from_csv(self, csv_file: str) -> None:
        """Descarga audio desde un archivo CSV."""
        if not Path(csv_file).exists():
            logger.error(f"Archivo CSV no encontrado: {csv_file}")
            return
        
        try:
            links = []
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'link' in row and row['link'].strip():
                        links.append(row['link'].strip())
            
            if not links:
                logger.warning("No se encontraron URLs en el archivo CSV")
                return
            
            logger.info(f"📋 Encontradas {len(links)} URLs para descargar")
            
            # Descargar con barra de progreso
            for link in tqdm(links, desc="Descargando", unit="video"):
                self.download_audio(link)
            
            # Mostrar resumen
            self._print_summary()
            
        except Exception as e:
            logger.error(f"Error al leer CSV: {str(e)}")
    
    def _print_summary(self) -> None:
        """Imprime un resumen de las descargas."""
        total = sum(self.stats.values())
        logger.info("\n" + "="*50)
        logger.info("📊 RESUMEN DE DESCARGA")
        logger.info("="*50)
        logger.info(f"✅ Exitosas: {self.stats['success']}")
        logger.info(f"⏭️  Saltadas: {self.stats['skipped']}")
        logger.info(f"❌ Fallidas: {self.stats['failed']}")
        logger.info(f"📦 Total: {total}")
        logger.info("="*50)


def load_config(config_file: str) -> dict:
    """Carga configuración desde archivo JSON."""
    if Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Descargador de audio de YouTube desde CSV'
    )
    parser.add_argument(
        '--csv', 
        default='./url-list.csv',
        help='Archivo CSV con URLs (default: ./url-list.csv)'
    )
    parser.add_argument(
        '--output', 
        default='./downloads',
        help='Carpeta de salida (default: ./downloads)'
    )
    parser.add_argument(
        '--quality', 
        choices=['128', '192', '256', '320'],
        default='192',
        help='Calidad de audio (default: 192)'
    )
    parser.add_argument(
        '--format',
        choices=['mp3', 'ogg', 'flac'],
        default='mp3',
        help='Formato de audio (default: mp3)'
    )
    parser.add_argument(
        '--ffmpeg',
        help='Ruta a FFmpeg (opcional, se detecta automáticamente)'
    )
    parser.add_argument(
        '--config',
        help='Archivo de configuración JSON'
    )
    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='No saltar archivos existentes'
    )
    
    args = parser.parse_args()
    
    # Cargar configuración si se proporciona
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Crear descargador
    downloader = YouTubeDownloader(
        output_folder=config.get('output_folder', args.output),
        audio_quality=config.get('audio_quality', args.quality),
        audio_format=config.get('audio_format', args.format),
        ffmpeg_path=config.get('ffmpeg_path', args.ffmpeg),
        skip_existing=not args.no_skip and config.get('skip_existing', True)
    )
    
    # Iniciar descarga
    csv_file = config.get('csv_file', args.csv)
    downloader.download_from_csv(csv_file)


if __name__ == '__main__':
    main()
