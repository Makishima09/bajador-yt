"""Clasificación de errores de yt-dlp y conversión a mensajes legibles."""

from __future__ import annotations

import re
from typing import Optional

_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mK]')

_FRIENDLY_MESSAGES: dict[str, str] = {
    'private': 'Video privado — no se puede descargar.',
    'unavailable': 'Video eliminado o no disponible.',
    'geo_blocked': 'Video bloqueado en tu región.',
    'forbidden': 'YouTube rechazó la solicitud (HTTP 403). Actualiza yt-dlp.',
    'copyright': 'Video retirado por motivos de copyright.',
    'age_restricted': 'Video con restricción de edad — requiere cookies del navegador.',
    'login_required': 'YouTube pide iniciar sesión para este video. Usa "Cookies navegador" (GUI) o --cookies-from-browser (CLI).',
    'cookie_locked': 'No se pudo leer las cookies de Chrome porque está abierto. Cierra Chrome completamente y vuelve a intentarlo, o selecciona otro navegador.',
    'network': 'Error de red. Revisa tu conexión.',
    'timeout': 'Tiempo de espera agotado.',
    'js_runtime': 'Falta un runtime de JavaScript soportado (Node/Deno).',
    'extractor': 'Error del extractor. Actualiza yt-dlp.',
    'postprocessing': 'Error durante el postprocesado (ffmpeg/ffprobe). Verifica la instalación de FFmpeg.',
    'generic': 'Error inesperado durante la descarga.',
}

_RETRYABLE = frozenset({'network', 'timeout', 'forbidden', 'generic'})
_NON_RETRYABLE = frozenset(
    {'private', 'unavailable', 'geo_blocked', 'copyright', 'age_restricted',
     'login_required', 'cookie_locked', 'postprocessing', 'js_runtime'}
)


def classify_error(exc: Optional[BaseException]) -> str:
    """Devuelve una categoría corta basada en el texto del error."""
    if exc is None:
        return 'generic'
    msg = str(exc).lower()

    if 'private video' in msg or 'this video is private' in msg:
        return 'private'
    if 'has been removed' in msg or 'video unavailable' in msg or 'no longer available' in msg:
        return 'unavailable'
    if 'not available in your country' in msg or 'geo' in msg:
        return 'geo_blocked'
    if 'copyright' in msg:
        return 'copyright'
    if 'sign in to confirm your age' in msg or 'age-restricted' in msg or 'age restricted' in msg:
        return 'age_restricted'
    if 'could not copy' in msg and 'cookie' in msg:
        return 'cookie_locked'
    if 'please sign in' in msg or 'login required' in msg or 'requires authentication' in msg or 'use --cookies' in msg:
        return 'login_required'
    if 'http error 403' in msg or 'forbidden' in msg:
        return 'forbidden'
    if 'timed out' in msg or 'timeout' in msg:
        return 'timeout'
    if 'javascript runtime' in msg or 'no supported javascript' in msg:
        return 'js_runtime'
    if any(kw in msg for kw in (
        'connection', 'connect', 'network', 'name or service not known',
        'temporary failure in name resolution', 'unreachable',
    )):
        return 'network'
    if ('postprocessing' in msg
            or 'ffprobe' in msg
            or ('ffmpeg' in msg and 'not found' in msg)):
        return 'postprocessing'
    if 'extractorerror' in msg or 'unable to extract' in msg:
        return 'extractor'
    return 'generic'


def is_retryable(category: str) -> bool:
    return category in _RETRYABLE


def user_friendly_message(exc: Optional[BaseException], category: Optional[str] = None) -> str:
    """Formatea el error con una explicación breve y el detalle técnico."""
    category = category or classify_error(exc)
    base = _FRIENDLY_MESSAGES.get(category, _FRIENDLY_MESSAGES['generic'])
    if exc is None:
        return base
    detail = _ANSI_ESCAPE.sub('', str(exc))
    return f'{base} Detalle: {detail}'
