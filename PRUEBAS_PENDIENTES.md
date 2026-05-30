# Pruebas pendientes — ejecutar en Windows (Git Bash + `py`)

Guarda el resultado (pegando logs) junto a cada checkbox. Los tests unitarios ya pasan; esto son pruebas de integración reales contra YouTube + FFmpeg en Windows.

## Preparación

```bash
cd ~/Documents/Code/bajador-yt
py -m pip install -r requirements.txt
py -m pip install pytest
```

- [ ] `py -m pytest` → esperado: **58 passed**
- [ ] `py bajador-yt.py --help` muestra todos los flags
- [ ] `py bajador-yt.py --urls https://youtu.be/abc --validate-only` → `OK`, exit 0
- [ ] `py bajador-yt.py --urls not-a-url --validate-only` → `NO`, exit 1

---

## CLI — descargas básicas

### Audio mp3 (URL pública corta)
- [ ] `py bajador-yt.py --urls https://www.youtube.com/watch?v=9Ojb8t3T2Ng --output ./tmp-test --mode audio --audio-format mp3 --audio-quality 192`
  - Esperado: archivo `.mp3` creado, `Resumen — éxitos=1`, exit 0

### Audio 320 kbps múltiple
- [ ] `py bajador-yt.py --urls https://youtu.be/URL1 https://youtu.be/URL2 --output ./tmp-test --mode audio --audio-quality 320`
  - Esperado: 2 archivos mp3, barra tqdm avanza correctamente

### Video mp4
- [ ] `py bajador-yt.py --urls https://www.youtube.com/watch?v=9Ojb8t3T2Ng --output ./tmp-test --mode video --video-format mp4`
  - Esperado: archivo `.mp4` merged con audio+video

### Descarga desde CSV
- [ ] `py bajador-yt.py --csv url-list.csv --output ./tmp-test --mode audio`
  - Esperado: 3 descargas según `url-list.csv`

### --urls NO debe leer CSV por defecto (bug arreglado en esta sesión)
- [ ] `py bajador-yt.py --urls https://youtu.be/XXX --output ./tmp-test --mode audio --no-progress`
  - Esperado: **total=1**, NO procesa las 3 del `url-list.csv`

### Skip de existentes
- [ ] Ejecuta 2 veces seguidas la misma descarga.
  - Esperado en la 2ª: `Resumen — saltadas=1`, `El archivo ya existe.`

### Paralelismo
- [ ] `py bajador-yt.py --csv url-list.csv --output ./tmp-test --parallel 3`
  - Esperado: descargas concurrentes (revisa timestamps en el log), `Descargando en paralelo con 3 workers.`

### Log a archivo y verbose
- [ ] `py bajador-yt.py --urls https://youtu.be/XXX --log-file run.log --verbose`
  - Esperado: `run.log` creado con líneas DEBUG y el comando resumen final

### Carga de config JSON
- [ ] `cp config.example.json config.json`
- [ ] `py bajador-yt.py --config config.json --urls https://youtu.be/XXX`
  - Esperado: usa valores de config.json; `--urls` override aplica

---

## CLI — errores manejados

### URL privada / login required (el caso que te bloqueó)
- [ ] `py bajador-yt.py --urls https://www.youtube.com/watch?v=hQ5x8pHoIPA --retries 3`
  - Esperado: **1 solo intento** (no 3), mensaje `YouTube pide iniciar sesión…`

### Con cookies del navegador (misma URL)
- [ ] Cerrar Chrome completamente
- [ ] `py bajador-yt.py --urls https://www.youtube.com/watch?v=hQ5x8pHoIPA --cookies-from-browser chrome --output ./tmp-test --mode audio`
  - Esperado: descarga exitosa

### URL inválida
- [ ] `py bajador-yt.py --urls https://vimeo.com/123 --no-progress`
  - Esperado: `status=invalid`, mensaje `URL no válida.`, exit 1

### CSV sin columna `link`
- [ ] Crear `bad.csv` con cabecera `url` y una URL
- [ ] `py bajador-yt.py --csv bad.csv --no-progress`
  - Esperado: error claro `El CSV 'bad.csv' debe tener una columna 'link'`, exit 2

### FFmpeg inexistente
- [ ] `py bajador-yt.py --urls https://youtu.be/XXX --ffmpeg "C:/no-existe/ffmpeg.exe" --no-progress`
  - Esperado: warning en log `FFmpeg configurado en … no existe; usando detección automática.`

### Exit codes
- [ ] Comando con todo OK → `echo $?` debe ser `0`
- [ ] Con al menos un error → `1`
- [ ] Config inválida (`--mode bad`) → `2`

---

## GUI

### Arranque
- [ ] `py app.py` abre sin errores y detecta FFmpeg automáticamente (campo FFmpeg pre-rellenado)

### Descarga simple
- [ ] Pegar 1 URL, seleccionar modo audio → mp3, pulsar Descargar
  - Esperado: progressbar avanza, resultado aparece en la lista, popup final verde

### Múltiples + paralelismo
- [ ] Pegar 3 URLs, poner Paralelo=3
  - Esperado: se completa en ~1/3 del tiempo de serie

### Botón Cancelar
- [ ] Iniciar descarga de 5+ URLs, pulsar **Cancelar** a mitad
  - Esperado: se detiene tras la descarga actual, status=`Cancelando…`, resumen muestra `canceladas > 0`

### Cancelar no debe congelar la ventana
- [ ] Durante la descarga intenta mover la ventana o redimensionar
  - Esperado: UI responde sin bloqueos (el arreglo del threading)

### Metadatos y thumbnail
- [ ] Activar "Metadatos" y "Thumbnail", descargar mp3
  - Esperado: el mp3 tiene tags ID3 y carátula (abrir en reproductor)

### Cookies navegador en GUI
- [ ] Combo "Cookies navegador" = `chrome` (Chrome cerrado), descargar URL con login
  - Esperado: descarga exitosa

### Skip desde GUI
- [ ] Descargar misma URL dos veces con "Saltar archivos existentes" marcado
  - Esperado: 2ª vez `skipped`, sin re-descarga

### Modo video
- [ ] Cambiar combo Tipo a `video`, seleccionar mp4, descargar
  - Esperado: audio/quality se deshabilitan, video/format se habilita, archivo mp4 generado

### URLs mezcladas válidas + inválidas
- [ ] Pegar 1 URL válida + 1 basura + 1 válida
  - Esperado: popup `warning` con `Inválidas: 1`, `Exitosas: 2`

---

## Windows-specific

### Lanzador .bat
- [ ] Doble-click en `bajador-yt-gui.bat` desde el Explorador
  - Esperado: abre la GUI sin mostrar consola de error

### Ruta con espacios
- [ ] Carpeta de salida = `C:\Users\Miguel\Documents\Mi Música`
  - Esperado: descarga OK, sin errores de path

### Ejecución fuera del repo
- [ ] `cd` a otra carpeta y lanzar `py C:/Users/Miguel/Documents/Code/bajador-yt/bajador-yt.py --urls ...`
  - Esperado: funciona (paths relativos se resuelven bien)

---

## Troubleshooting que quiero verificar

- [ ] Chrome abierto al usar `--cookies-from-browser chrome` → mensaje de "database is locked" claro
- [ ] `yt-dlp` desactualizado → `pip install -U yt-dlp` lo arregla
- [ ] Sin conexión a internet → categoría `network`, reintentos aplican

---

## Notas

- Tests limpios: borrar `./tmp-test/` entre runs para tests de `skip-existing`.
- Si un test de descarga falla con `Please sign in`, prueba con `--cookies-from-browser chrome` antes de asumir que es bug.
- El error de postprocesado con `ffprobe` que vimos en WSL **no** debería aparecer en Windows nativo (ffmpeg + ffprobe están juntos).
