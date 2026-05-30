"""Valores permitidos para modos, formatos y calidades."""

AUDIO_FORMATS: frozenset[str] = frozenset({'mp3', 'm4a', 'opus', 'wav'})
VIDEO_FORMATS: frozenset[str] = frozenset({'mp4', 'mkv', 'webm'})
QUALITY_LEVELS: frozenset[str] = frozenset({'128', '192', '256', '320'})
MODES: frozenset[str] = frozenset({'audio', 'video'})

DOWNLOAD_STATUSES: frozenset[str] = frozenset(
    {'success', 'skipped', 'invalid', 'error', 'cancelled'}
)
