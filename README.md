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

## 📁 Estructura del Proyecto

```
bajador-yt/
├── bajador-yt.py    # Script principal de descarga
├── url-list.csv     # Archivo CSV con las URLs de YouTube
└── downloads/       # Carpeta donde se guardan los archivos descargados
```

## 🛠️ Tecnologías Utilizadas

- **Python 3**: Lenguaje de programación
- **yt-dlp**: Biblioteca para descargar videos de YouTube y otras plataformas
- **FFmpeg**: Herramienta para conversión de audio a MP3
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
pip install yt-dlp
```

O usando `requirements.txt` (si lo creas):
```bash
pip install -r requirements.txt
```

## 🚀 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/Makishima09/bajador-yt.git
cd bajador-yt
```

2. Instala las dependencias:
```bash
pip install yt-dlp
```

3. Configura FFmpeg (ver sección de Requisitos Previos)

4. Crea la carpeta de descargas (se crea automáticamente, pero puedes crearla manualmente):
```bash
mkdir downloads
```

## 📝 Uso

### 1. Preparar el archivo CSV

Edita el archivo `url-list.csv` y agrega las URLs de YouTube que deseas descargar:

```csv
link
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

### 2. Configurar la ruta de FFmpeg (si es necesario)

Si FFmpeg no está en tu PATH, edita `bajador-yt.py` y actualiza la ruta:

```python
'ffmpeg_location': 'C:/ruta/a/tu/ffmpeg/bin',
```

### 3. Ejecutar el script

```bash
python bajador-yt.py
```

Los archivos MP3 se descargarán en la carpeta `downloads/`.

## ⚙️ Configuración

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

- `'192'`: Calidad estándar (por defecto)
- `'256'`: Calidad mejorada
- `'320'`: Calidad máxima

## 📂 Estructura del CSV

El archivo `url-list.csv` debe tener el siguiente formato:

```csv
link
https://www.youtube.com/watch?v=VIDEO_ID
```

- Primera fila: encabezado con `link`
- Filas siguientes: una URL por línea

## 🔧 Solución de Problemas

### Error: "FFmpeg not found"

- Asegúrate de que FFmpeg está instalado
- Verifica que la ruta en el script es correcta
- En Windows, asegúrate de que la ruta use barras `/` o dobles barras `\\`

### Error: "ModuleNotFoundError: No module named 'yt_dlp'"

```bash
pip install yt-dlp
```

### Error: "No video formats found"

- Verifica que las URLs sean válidas
- Algunos videos pueden tener restricciones geográficas o de privacidad
- Intenta actualizar yt-dlp: `pip install --upgrade yt-dlp`

### Los archivos no se descargan

- Verifica que la carpeta `downloads` existe o puede ser creada
- Verifica los permisos de escritura en el directorio
- Revisa que las URLs en el CSV sean correctas

## 📝 Notas Importantes

- ⚠️ **Respeto a los derechos de autor**: Solo descarga contenido que tengas permiso para descargar
- ⚠️ **Términos de servicio**: Asegúrate de cumplir con los términos de servicio de YouTube
- 🔄 **Actualización de yt-dlp**: YouTube cambia frecuentemente, actualiza yt-dlp regularmente:
  ```bash
  pip install --upgrade yt-dlp
  ```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar este proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🔮 Mejoras Futuras

- [ ] Interfaz gráfica (GUI)
- [ ] Soporte para otras plataformas (Vimeo, etc.)
- [ ] Descarga de video completo además de audio
- [ ] Configuración mediante archivo de configuración
- [ ] Progreso de descarga más detallado
- [ ] Manejo de errores mejorado

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y personal.

## 👤 Autor

**Makishima09**

- GitHub: [@Makishima09](https://github.com/Makishima09)

## 🙏 Agradecimientos

- A los desarrolladores de [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- A la comunidad de Python

---

⭐ Si este proyecto te resulta útil, ¡no olvides darle una estrella!
