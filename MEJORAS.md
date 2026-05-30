# Bajador YT — registro de mejoras

## Estado: v2.0.0 — refactor completo aplicado

Todas las mejoras propuestas en la versión inicial se han implementado. Este documento se conserva como historial de lo que se hizo y guía para ampliaciones futuras.

---

## Aplicado en v2.0.0

### Arquitectura
- Proyecto reorganizado como paquete `bajador_yt/` con módulos separados por responsabilidad: `config`, `constants`, `csv_utils`, `downloader`, `errors`, `ffmpeg_utils`, `logger`, `models`, `validators`.
- CLI (`bajador-yt.py`) y GUI (`app.py`) como entradas delgadas que consumen el paquete.
- Eliminado el antiguo `yt_downloader.py` monolítico.

### Robustez de descarga
- Reintentos automáticos con backoff exponencial configurable (`max_retries`, `retry_backoff`), **solo** para errores recuperables (red, timeout, 403, genéricos).
- Errores permanentes (privado, eliminado, geo-bloqueo, copyright, edad) se devuelven inmediatamente con mensaje claro.
- Clasificación de errores en `errors.py` + mensajes amigables con `user_friendly_message`.
- `socket_timeout=30` pasado a yt-dlp.
- Eliminada la doble llamada a `extract_info` (ahora una sola vía `process_ie_result`).
- `skip_existing` ahora maneja playlists sin romperse.
- `ensure_output_folder` ya no se llama dos veces en la misma ruta.

### Configuración
- `DownloadConfig` dataclass inmutable con `merged()` y `validate()`.
- Carga desde JSON vía `load_config()` con errores explícitos (JSON malformado, no-objeto, campos inválidos).
- Los campos desconocidos del JSON se ignoran silenciosamente (forward-compat).

### CLI
- `argparse` completo: `--config`, `--csv`, `--urls`, `--output`, `--mode`, `--audio-format`, `--audio-quality`, `--video-format`, `--ffmpeg`, `--parallel`, `--retries`, `--retry-backoff`, `--skip-existing`/`--no-skip-existing`, `--allow-playlist`/`--no-playlist`, `--write-metadata`, `--embed-thumbnail`, `--log-file`, `--verbose`, `--validate-only`, `--no-progress`.
- Barra de progreso con `tqdm` (ahora **sí** se importa y usa).
- Códigos de salida consistentes: 0 éxito, 1 con errores, 2 uso incorrecto.
- Validación previa (`--validate-only`) lista URLs sin descargar.
- Deduplica URLs manteniendo el orden.

### GUI
- Descarga en un `threading.Thread` aparte — la ventana **ya no se congela**.
- Comunicación entre hilo worker y UI vía `queue.Queue` + `root.after(100, ...)`.
- Botón **Cancelar** usa `threading.Event` cooperativo (respetado en reintentos y entre descargas).
- `ttk.Progressbar` determinista con total = nº URLs.
- Controles para paralelismo, reintentos, metadatos, thumbnail.
- Auto-detección de FFmpeg al abrir la ventana.
- Selector de FFmpeg adaptado a Windows vs Unix.

### Logging
- Logger configurado vía `setup_logger` (consola + archivo opcional).
- Formato estructurado con timestamp, nivel y módulo.
- Nivel DEBUG con `--verbose`.

### Validación
- `is_valid_youtube_url` endurecido: rechaza `evil.com.youtube.com.attack` (antes lo aceptaba por `endswith('youtube.com')` sin separador).
- CSV sin columna `link` → `CsvFormatError` en vez de lista vacía silenciosa.
- `validate_ffmpeg_path` verifica existencia antes de usar el path provisto.
- Validación previa de `DownloadConfig` antes de iniciar descargas.

### Paralelismo
- `parallel_downloads > 1` activa `ThreadPoolExecutor` en `download_many`.

### Metadatos
- `write_metadata` añade postprocessor `FFmpegMetadata`.
- `embed_thumbnail` añade `writethumbnail` + `EmbedThumbnail`.

### Tests
- Suite en `tests/` (pytest):
  - `test_validators.py`
  - `test_errors.py`
  - `test_csv_utils.py`
  - `test_ffmpeg_utils.py`
  - `test_config.py`
  - `test_models.py`
  - `test_downloader_summary.py`
- Tests sin red: todos usan `tmp_path` y `monkeypatch` de stdlib.

### Documentación
- README reescrito, sincronizado con el código real (sin referencias a líneas obsoletas).
- Tabla de argumentos CLI y códigos de salida.
- Ejemplos de API programática.
- `config.example.json` ampliado con todos los campos.

### Calidad
- `.gitignore` completo: caches de pytest, mypy, ruff, coverage, IDE.
- `bajador-yt-gui.bat` verifica que Python esté en el PATH y muestra errores al usuario.
- Type hints consistentes (`from __future__ import annotations`).
- Docstrings breves en módulos y funciones públicas.

---

## Ideas futuras (no críticas)

### Extras de descarga
- Descargar subtítulos (`writesubtitles`, `subtitleslangs`).
- Filtros por duración / tamaño / resolución.
- Chapters como archivos separados.

### Distribución
- `pyproject.toml` con `console_scripts` para `bajador-yt`.
- Workflow de GitHub Actions para ejecutar tests en push.
- Linter/formatter (`ruff`, `black`) preconfigurados.

### Observabilidad
- Exportar resumen a JSON con `--summary-json out.json`.
- Estadísticas de duración total, bytes descargados por URL.

### UX
- Modo oscuro en la GUI (`ttk.Style`).
- Arrastrar y soltar archivos CSV sobre la ventana.
- i18n básica (es/en).

### Infra
- Cache de metadatos (evitar `extract_info` repetido entre runs).
- Verificación opcional de integridad (hash) tras la descarga.
