"""Dataclasses compartidas entre CLI, GUI y núcleo de descarga."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DownloadResult:
    """Resultado inmutable de intentar descargar una URL.

    status es uno de: 'success', 'skipped', 'invalid', 'error', 'cancelled'.
    """

    url: str
    status: str
    message: str
    output_path: Optional[str] = None
    category: Optional[str] = None
