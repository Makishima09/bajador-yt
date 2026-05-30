"""Validación de URLs y parámetros."""

from __future__ import annotations

from urllib.parse import urlparse

from .constants import AUDIO_FORMATS, MODES, QUALITY_LEVELS, VIDEO_FORMATS

_VALID_HOSTS_SUFFIX = ('youtube.com',)
_VALID_HOSTS_EXACT = ('youtu.be',)


def is_valid_youtube_url(url: str) -> bool:
    """Comprueba que la URL apunte a un dominio de YouTube vía http/https."""
    if not url:
        return False
    parsed = urlparse(url.strip())
    if parsed.scheme not in ('http', 'https'):
        return False
    host = parsed.netloc.lower()
    if not host:
        return False
    if host in _VALID_HOSTS_EXACT:
        return True
    return any(host == suffix or host.endswith('.' + suffix) for suffix in _VALID_HOSTS_SUFFIX)


def is_supported_mode(mode: str) -> bool:
    return mode in MODES


def is_supported_audio_format(audio_format: str) -> bool:
    return audio_format in AUDIO_FORMATS


def is_supported_video_format(video_format: str) -> bool:
    return video_format in VIDEO_FORMATS


def is_supported_quality(quality: str) -> bool:
    return quality in QUALITY_LEVELS
