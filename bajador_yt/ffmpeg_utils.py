"""Detección y validación del binario de FFmpeg."""

from __future__ import annotations

import os
import shutil
from typing import Optional

_COMMON_PATHS: tuple[str, ...] = (
    'C:/Program Files/ffmpeg-7.0.2-full_build/bin/ffmpeg.exe',
    'C:/Program Files/ffmpeg/bin/ffmpeg.exe',
    'C:/ffmpeg/bin/ffmpeg.exe',
    '/usr/local/bin/ffmpeg',
    '/usr/bin/ffmpeg',
    '/opt/homebrew/bin/ffmpeg',
)


def detect_ffmpeg_path() -> Optional[str]:
    """Busca FFmpeg vía env var FFMPEG_PATH, PATH y rutas comunes."""
    env_path = os.environ.get('FFMPEG_PATH')
    if env_path and os.path.exists(env_path):
        return env_path

    which_path = shutil.which('ffmpeg')
    if which_path:
        return which_path

    for path in _COMMON_PATHS:
        if os.path.exists(path):
            return path
    return None


def validate_ffmpeg_path(path: Optional[str]) -> Optional[str]:
    """Devuelve el path si es un archivo existente; None si no lo es."""
    if not path:
        return None
    return path if os.path.isfile(path) else None
