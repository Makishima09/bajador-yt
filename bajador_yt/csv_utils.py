"""Lectura de URLs desde CSV o texto libre."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List


class CsvFormatError(ValueError):
    """El CSV no contiene la columna esperada."""


def extract_links_from_csv(csv_file: str | Path) -> List[str]:
    """Lee un CSV con columna 'link' y devuelve las URLs no vacías.

    Lanza CsvFormatError si falta la columna 'link' para que el usuario
    reciba feedback claro en vez de una lista vacía silenciosa.
    """
    path = Path(csv_file)
    with path.open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or 'link' not in reader.fieldnames:
            raise CsvFormatError(
                f"El CSV '{path}' debe tener una columna 'link' en la cabecera."
            )
        return [row['link'].strip() for row in reader if row.get('link') and row['link'].strip()]


def extract_links_from_text(urls_text: str) -> List[str]:
    """Convierte un bloque de texto multilínea en una lista de URLs."""
    if not urls_text:
        return []
    return [line.strip() for line in urls_text.splitlines() if line.strip()]
