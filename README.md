# Bajador YouTube - Descargador de Audio Automatizado

Script Python para descargar automáticamente audio de videos de YouTube desde una lista de URLs en formato CSV. Convierte automáticamente el audio a formato MP3 con calidad de 192 kbps.

## 📋 Descripción

Este proyecto permite descargar múltiples audios de YouTube de forma automatizada. Simplemente agrega las URLs de los videos que deseas descargar en un archivo CSV y el script se encargará de descargarlos y convertirlos a MP3.

## 🚀 Características

- ✅ Descarga automática de audio desde múltiples URLs de YouTube
- ✅ Lectura de URLs desde archivo CSV
- ✅ Conversión automática a formato MP3
- ✅ Calidad de audio configurable (192 kbps por defecto)
- ✅ Procesamiento por lotes de múltiples videos
- ✅ Uso de `yt-dlp` (alternativa mejorada a youtube-dl)
- ✅ **Versión mejorada disponible** con manejo de errores, CLI y mejor feedback

## 📁 Estructura del Proyecto

```
bajador-yt/
├── bajador-yt.py              # Script original (simple)
├── bajador-yt-mejorado.py     # Script mejorado (recomendado)
├── url-list.csv               # Archivo CSV con las URLs de YouTube
├── requirements.txt           # Dependencias del proyecto
├── config.example.json        # Plantilla de configuración
├── .gitignore                 # Archivos a ignorar en Git
├── MEJORAS.md                 # Documentación de mejoras
└── downloads/                 # Carpeta donde se guardan los archivos descargados
```

## 🛠️ Tecnologías Utilizadas

- **Python 3**: Lenguaje de programación
- **yt-dlp**: Biblioteca para descargar videos de YouTube y otras plataformas
- **FFmpeg**: Herramienta para conversión de audio a MP3
- **tqdm**: Barra de progreso visual (versión mejorada)
- **CSV**: Formato para almacenar la lista de URLs

## 📦 Requisitos Previos

### 1. Instalar Python 3

Asegúrate de tener Python 3 instalado en tu sistema.

### 2. Instalar FFmpeg

FFmpeg es necesario para la conversión de audio a MP3.

**Windows:**
- Descarga FFmpeg desde: https://ffmpeg.org/download.html
- Extrae el archivo y agrega la ruta `bin` al PATH del sistema
- O actualiza la ruta en el script: `'ffmpeg_location': 'C:/ruta/a/ffmpeg/bin'`

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 3. Instalar Dependencias de Python

```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install yt-dlp tqdm
```

## 🚀 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/Makishima09/bajador-yt.git
cd bajador-yt
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura FFmpeg (ver sección de Requisitos Previos)

4. La carpeta de descargas se crea automáticamente, pero puedes crearla manualmente:
```bash
mkdir downloads
```

## 📝 Uso

### Versión Mejorada (Recomendada) ⭐

La versión mejorada incluye manejo de errores robusto, CLI con argumentos, detección automática de FFmpeg, validación de URLs, barra de progreso y mucho más.

#### Uso Básico

```bash
python bajador-yt-mejorado.py
```

#### Con Argumentos Personalizados

```bash
# Especificar archivo CSV y carpeta de salida
python bajador-yt-mejorado.py --csv urls.csv --output ./music

# Cambiar calidad de audio
python bajador-yt-mejorado.py --quality 320

# Cambiar formato de audio
python bajador-yt-mejorado.py --format ogg

# Especificar ruta de FFmpeg manualmente
python bajador-yt-mejorado.py --ffmpeg "C:/Program Files/ffmpeg/bin"

# No saltar archivos existentes
python bajador-yt-mejorado.py --no-skip
```

#### Con Archivo de Configuración

1. Copia el archivo de ejemplo:
```bash
cp config.example.json config.json
```

2. Edita `config.json` con tus preferencias

3. Ejecuta con la configuración:
```bash
python bajador-yt-mejorado.py --config config.json
```

#### Características de la Versión Mejorada

- ✅ **Detección automática de FFmpeg**: Busca FFmpeg en PATH y ubicaciones comunes
- ✅ **Validación de URLs**: Verifica que las URLs sean válidas antes de descargar
- ✅ **Verificación de archivos existentes**: Evita descargar duplicados
- ✅ **Barra de progreso visual**: Muestra el progreso de las descargas
- ✅ **Logging estructurado**: Guarda logs en archivo `download.log`
- ✅ **Resumen de estadísticas**: Muestra resumen al final (éxitos/fallos/saltados)
- ✅ **Manejo de errores robusto**: Captura y maneja errores específicos
- ✅ **Sanitización de nombres**: Limpia caracteres inválidos en nombres de archivo
- ✅ **CLI flexible**: Argumentos de línea de comandos para personalización

### Versión Original (Simple)

Para uso básico sin características adicionales:

```bash
python bajador-yt.py
```

**Nota**: Necesitarás editar el script para cambiar la ruta de FFmpeg si no está en tu PATH.

## 📂 Preparar el Archivo CSV

Edita el archivo `url-list.csv` y agrega las URLs de YouTube que deseas descargar:

```csv
link
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

- Primera fila: encabezado con `link`
- Filas siguientes: una URL por línea

## ⚙️ Configuración

### Versión Mejorada

Puedes configurar el script de tres formas:

1. **Argumentos de línea de comandos** (más flexible)
2. **Archivo de configuración JSON** (para configuraciones persistentes)
3. **Valores por defecto** (si no especificas nada)

### Versión Original

Puedes personalizar el script modificando las opciones en `ydl_opts`:

```python
ydl_opts = {
    'format': 'bestaudio/best',           # Formato de audio
    'outtmpl': f'{output_folder}/%(title)s.%(ext)s',  # Plantilla de nombre
    'ffmpeg_location': 'ruta/a/ffmpeg',   # Ruta a FFmpeg
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',          # Formato de salida
        'preferredquality': '192',        # Calidad (192, 256, 320)
    }],
}
```

### Opciones de Calidad

- `'128'`: Calidad básica
- `'192'`: Calidad estándar (por defecto)
- `'256'`: Calidad mejorada
- `'320'`: Calidad máxima

### Formatos de Audio Soportados

- `mp3`: Formato más compatible (por defecto)
- `ogg`: Formato libre y eficiente
- `flac`: Formato sin pérdida (archivos más grandes)

## 🔧 Solución de Problemas

### Error: "FFmpeg not found"

**Versión Mejorada**: El script intenta detectar FFmpeg automáticamente. Si no lo encuentra:
- Asegúrate de que FFmpeg está instalado
- Usa el argumento `--ffmpeg` para especificar la ruta manualmente
- Verifica que FFmpeg está en tu PATH del sistema

**Versión Original**: 
- Edita `bajador-yt.py` y actualiza la ruta: `'ffmpeg_location': 'C:/ruta/a/ffmpeg/bin'`
- En Windows, usa barras `/` o dobles barras `\\`

### Error: "ModuleNotFoundError: No module named 'yt_dlp'"

```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install yt-dlp tqdm
```

### Error: "No video formats found"

- Verifica que las URLs sean válidas
- Algunos videos pueden tener restricciones geográficas o de privacidad
- Intenta actualizar yt-dlp: `pip install --upgrade yt-dlp`

### Los archivos no se descargan

- Verifica que la carpeta `downloads` existe o puede ser creada
- Verifica los permisos de escritura en el directorio
- Revisa que las URLs en el CSV sean correctas
- Revisa el archivo `download.log` para más detalles (versión mejorada)

## 📝 Notas Importantes

- ⚠️ **Respeto a los derechos de autor**: Solo descarga contenido que tengas permiso para descargar
- ⚠️ **Términos de servicio**: Asegúrate de cumplir con los términos de servicio de YouTube
- 🔄 **Actualización de yt-dlp**: YouTube cambia frecuentemente, actualiza yt-dlp regularmente:
  ```bash
  pip install --upgrade yt-dlp
  ```
- 📊 **Logs**: La versión mejorada guarda logs en `download.log` para facilitar el debugging

## 🔮 Mejoras Futuras

Consulta el archivo [MEJORAS.md](MEJORAS.md) para ver todas las mejoras sugeridas y futuras implementaciones.

Algunas mejoras ya implementadas en la versión mejorada:
- ✅ Manejo de errores robusto
- ✅ CLI con argumentos
- ✅ Detección automática de FFmpeg
- ✅ Validación de URLs
- ✅ Barra de progreso
- ✅ Logging estructurado
- ✅ Verificación de archivos existentes

Mejoras pendientes:
- [ ] Interfaz gráfica (GUI)
- [ ] Soporte para otras plataformas (Vimeo, etc.)
- [ ] Descarga de video completo además de audio
- [ ] Descarga paralela (multithreading)
- [ ] Soporte para playlists de YouTube

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar este proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y personal.

## 👤 Autor

**Makishima09**

- GitHub: [@Makishima09](https://github.com/Makishima09)

## 🙏 Agradecimientos

- A los desarrolladores de [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- A la comunidad de Python
- A los desarrolladores de [tqdm](https://github.com/tqdm/tqdm) por la barra de progreso

---

⭐ Si este proyecto te resulta útil, ¡no olvides darle una estrella!
