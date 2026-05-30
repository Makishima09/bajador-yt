"""Configuración centralizada. Soporta JSON + overrides."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path
from typing import Any, Optional

from .constants import AUDIO_FORMATS, MODES, QUALITY_LEVELS, VIDEO_FORMATS

SUPPORTED_BROWSERS: frozenset[str] = frozenset(
    {'chrome', 'firefox', 'edge', 'brave', 'opera', 'vivaldi', 'chromium', 'safari'}
)


class ConfigError(ValueError):
    """Valor inválido en la configuración."""


@dataclass(frozen=True)
class DownloadConfig:
    """Contenedor inmutable con todas las opciones de descarga."""

    output_folder: str = './downloads'
    csv_file: str = './url-list.csv'
    mode: str = 'audio'
    audio_format: str = 'mp3'
    audio_quality: str = '192'
    video_format: str = 'mp4'
    ffmpeg_path: Optional[str] = None
    skip_existing: bool = True
    allow_playlist: bool = False
    max_retries: int = 3
    retry_backoff: float = 2.0
    parallel_downloads: int = 1
    log_file: Optional[str] = None
    verbose: bool = False
    write_metadata: bool = False
    embed_thumbnail: bool = False
    cookies_from_browser: Optional[str] = None
    cookies_file: Optional[str] = None

    def merged(self, overrides: dict[str, Any]) -> 'DownloadConfig':
        """Devuelve una nueva instancia con los overrides aplicados."""
        valid = {f.name for f in fields(self)}
        clean = {k: v for k, v in overrides.items() if k in valid and v is not None}
        return replace(self, **clean)

    def validate(self) -> None:
        """Verifica que los valores estén en los conjuntos permitidos."""
        if self.mode not in MODES:
            raise ConfigError(f"mode debe ser uno de {sorted(MODES)}; recibido: {self.mode!r}")
        if self.audio_format not in AUDIO_FORMATS:
            raise ConfigError(
                f"audio_format debe ser uno de {sorted(AUDIO_FORMATS)}; recibido: {self.audio_format!r}"
            )
        if self.audio_quality not in QUALITY_LEVELS:
            raise ConfigError(
                f"audio_quality debe ser uno de {sorted(QUALITY_LEVELS)}; recibido: {self.audio_quality!r}"
            )
        if self.video_format not in VIDEO_FORMATS:
            raise ConfigError(
                f"video_format debe ser uno de {sorted(VIDEO_FORMATS)}; recibido: {self.video_format!r}"
            )
        if self.max_retries < 1:
            raise ConfigError('max_retries debe ser >= 1.')
        if self.retry_backoff <= 0:
            raise ConfigError('retry_backoff debe ser > 0.')
        if self.parallel_downloads < 1:
            raise ConfigError('parallel_downloads debe ser >= 1.')
        if self.cookies_from_browser is not None and self.cookies_from_browser not in SUPPORTED_BROWSERS:
            raise ConfigError(
                f"cookies_from_browser debe ser uno de {sorted(SUPPORTED_BROWSERS)} "
                f"o null; recibido: {self.cookies_from_browser!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: str | Path) -> DownloadConfig:
    """Carga un JSON y lo convierte en DownloadConfig, ignorando claves desconocidas."""
    p = Path(path)
    if not p.exists():
        raise ConfigError(f'No existe el archivo de configuración: {p}')
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"JSON inválido en {p}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"Se esperaba un objeto JSON en {p}, no {type(data).__name__}.")

    valid = {f.name for f in fields(DownloadConfig)}
    clean = {k: v for k, v in data.items() if k in valid}
    config = DownloadConfig(**clean)
    config.validate()
    return config
