"""Configuración de logging para CLI y GUI."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

_LOGGER_NAME = 'bajador_yt'
_FMT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
_DATEFMT = '%Y-%m-%d %H:%M:%S'


def setup_logger(
    *,
    verbose: bool = False,
    log_file: Optional[str] = None,
    console: bool = True,
) -> logging.Logger:
    """Configura el logger raíz del paquete.

    Idempotente: si ya hay handlers, los reemplaza para evitar duplicados
    cuando el CLI o la GUI se reinician en la misma sesión de Python.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(_FMT, datefmt=_DATEFMT)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Obtiene un logger hijo del logger del paquete."""
    if name is None:
        return logging.getLogger(_LOGGER_NAME)
    return logging.getLogger(f'{_LOGGER_NAME}.{name}')
