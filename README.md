# Bajador YT

Descarga audio o video desde YouTube con yt-dlp. Dos interfaces: **CLI** (con `argparse`, logging y barra de progreso) e **interfaz gráfica Tkinter** (con hilo de descarga y botón cancelar).

## Características

- Audio (`mp3`, `m4a`, `opus`, `wav`) o video (`mp4`, `mkv`, `webm`)
- Entrada desde CSV (`url-list.csv`) o por argumentos
- Archivo de configuración JSON opcional + overrides por CLI
- Reintentos automáticos con backoff exponencial (solo para errores recuperables)
- Clasificación de errores (403, geo-bloqueo, privado, eliminado, red, runtime JS…)
- Salta archivos ya descargados (`skip_existing`)
- Descarga en paralelo opcional (`parallel_downloads`)
- GUI sin congelarse, con barra de progreso y botón Cancelar
- Logging a consola y/o archivo
- Embed opcional de metadatos y thumbnails
- Detección automática de FFmpeg (PATH, env var `FFMPEG_PATH`, rutas comunes)
- Tests unitarios en `tests/` (pytest)

## Requisitos

- Python 3.10 o superior
- FFmpeg (para conversión de audio y merge de video)
- yt-dlp y tqdm (instalados vía `pip`)

## Instalación

```bash
pip install -r requirements.txt
```

Para tests:

```bash
pip install pytest
```

## Estructura

```
bajador-yt/
├── bajador_yt/              # Paquete principal
│   ├── __init__.py
│   ├── config.py            # DownloadConfig + load_config
│   ├── constants.py         # formatos, calidades, modos
│   ├── csv_utils.py         # lectura de CSV y texto
│   ├── downloader.py        # núcleo: Downloader, reintentos, threading
│   ├── errors.py            # clasificación de errores de yt-dlp
│   ├── ffmpeg_utils.py      # detección y validación de FFmpeg
│   ├── logger.py            # setup de logging
│   ├── models.py            # DownloadResult
│   └── validators.py        # URLs y parámetros
├── bajador-yt.py            # CLI
├── app.py                   # GUI
├── bajador-yt-gui.bat       # Lanzador Windows para la GUI
├── config.example.json      # Plantilla de configuración
├── requirements.txt
├── url-list.csv
├── downloads/
└── tests/                   # pytest
```

## Uso (CLI)

```bash
# URLs directas
python bajador-yt.py --urls https://youtu.be/abc https://youtu.be/def

# Desde CSV (columna "link")
python bajador-yt.py --csv url-list.csv --output ./downloads

# Video en mkv con metadatos y thumbnail embebidos
python bajador-yt.py --urls https://youtu.be/abc \
    --mode video --video-format mkv \
    --write-metadata --embed-thumbnail

# Audio 320 con 3 descargas en paralelo y 5 reintentos
python bajador-yt.py --csv url-list.csv \
    --mode audio --audio-format mp3 --audio-quality 320 \
    --parallel 3 --retries 5

# Cargar configuración desde JSON
python bajador-yt.py --config config.json

# Solo validar URLs sin descargar
python bajador-yt.py --urls https://foo.com/x https://youtu.be/abc --validate-only

# Modo verbose con log a archivo
python bajador-yt.py --csv url-list.csv --verbose --log-file run.log
```

### Argumentos principales

| Flag | Descripción |
|------|-------------|
| `--config FILE` | Carga `DownloadConfig` desde JSON |
| `--csv FILE` | CSV con columna `link` |
| `--urls URL [URL ...]` | URLs directas (aceptadas también con `--csv`) |
| `--output DIR` | Carpeta de salida |
| `--mode {audio,video}` | Tipo de descarga |
| `--audio-format {mp3,m4a,opus,wav}` | |
| `--audio-quality {128,192,256,320}` | |
| `--video-format {mp4,mkv,webm}` | |
| `--ffmpeg PATH` | Ruta explícita a FFmpeg |
| `--parallel N` | Descargas concurrentes |
| `--retries N` | Reintentos por URL |
| `--retry-backoff X` | Factor exponencial (por defecto 2.0) |
| `--skip-existing` / `--no-skip-existing` | Saltar archivos ya presentes |
| `--allow-playlist` / `--no-playlist` | Permitir URLs de playlist |
| `--write-metadata` | Embeber metadatos en el archivo |
| `--embed-thumbnail` | Embeber thumbnail |
| `--cookies-from-browser NAV` | Usa cookies del navegador (chrome, firefox, edge…) |
| `--cookies-file PATH` | Archivo cookies.txt (formato Netscape) |
| `--log-file FILE` | Escribir log en archivo |
| `--verbose` | Nivel DEBUG |
| `--validate-only` | Sólo validar URLs |
| `--no-progress` | Deshabilitar tqdm (útil en CI) |

### Códigos de salida

| Código | Significado |
|--------|-------------|
| 0 | Todas las URLs procesadas sin errores |
| 1 | Terminó con al menos un error |
| 2 | Uso incorrecto / configuración inválida |

## Uso (GUI)

```bash
python app.py
```

En Windows hay un lanzador: `bajador-yt-gui.bat`.

La GUI permite:
- Pegar varias URLs (una por línea)
- Elegir carpeta de salida
- Alternar audio/video, formato, calidad
- Activar playlists, skip, metadatos, thumbnail
- Ajustar paralelismo y reintentos
- Ver progreso en tiempo real sin que la ventana se congele
- **Cancelar** la descarga en curso

![Captura de la interfaz](Capture.jpg)

## Configuración (JSON)

Copia `config.example.json` a `config.json` y edita:

```json
{
  "output_folder": "./downloads",
  "csv_file": "./url-list.csv",
  "mode": "audio",
  "audio_format": "mp3",
  "audio_quality": "192",
  "video_format": "mp4",
  "ffmpeg_path": null,
  "skip_existing": true,
  "allow_playlist": false,
  "max_retries": 3,
  "retry_backoff": 2.0,
  "parallel_downloads": 1,
  "log_file": null,
  "verbose": false,
  "write_metadata": false,
  "embed_thumbnail": false
}
```

Los argumentos CLI tienen prioridad sobre los del JSON.

## CSV de URLs

```csv
link
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
```

- La cabecera **debe** ser `link` (si falta, el CLI aborta con mensaje claro).
- Una URL por línea.

## API programática

```python
from bajador_yt import DownloadConfig, Downloader

config = DownloadConfig(output_folder='./out', mode='audio', audio_quality='320')
downloader = Downloader(config)
results = downloader.download_many([
    'https://youtu.be/abc',
    'https://youtu.be/def',
])
for r in results:
    print(r.status, r.url, r.message)
```

## Tests

```bash
pytest
```

Los tests cubren validators, errors, csv_utils, ffmpeg_utils, config, models y el resumen del downloader. No hacen peticiones de red.

## Solución de problemas

### `ERROR: [youtube] XXX: Please sign in` / `Login required` / restricción de edad

YouTube pide login (anti-bot). Solución: pasar cookies del navegador ya autenticado.

**GUI:** en el combo **"Cookies navegador"** elige `chrome`, `firefox`, `edge`, `brave`, etc.

**CLI:**
```bash
py bajador-yt.py --urls https://youtu.be/XXX --cookies-from-browser chrome
# o con un cookies.txt exportado:
py bajador-yt.py --urls https://youtu.be/XXX --cookies-file ./cookies.txt
```

Cierra el navegador antes de ejecutar (Chrome/Firefox bloquean su base de cookies mientras están abiertos).

### `HTTP Error 403: Forbidden` / `No supported JavaScript runtime`

```bash
pip install -U yt-dlp
```

Instala Node.js (o Deno) y añádelo al PATH. Más info: https://github.com/yt-dlp/yt-dlp/wiki/EJS

### `FFmpeg not found`

Define la variable:

```bash
# Linux/Mac
export FFMPEG_PATH=/usr/local/bin/ffmpeg

# Windows (PowerShell)
$env:FFMPEG_PATH = "C:\ruta\a\ffmpeg\bin\ffmpeg.exe"
```

O pásalo por CLI: `--ffmpeg "C:\ruta\a\ffmpeg.exe"`.

### `No module named 'yt_dlp'`

```bash
pip install -r requirements.txt
```

### `El CSV debe tener una columna 'link'`

Revisa la cabecera de `url-list.csv`. Debe ser literalmente `link` en la primera fila.

### Videos privados / eliminados / bloqueados por región

El mensaje de error ahora indica la causa. Estos errores **no se reintentan** automáticamente.

## Licencia

Uso personal. Respeta los Términos de Servicio de YouTube y los derechos de autor.
