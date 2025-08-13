
---

# Audio Analyzer Dashboard

---

## Descripción

Audio Analyzer es una aplicación web interactiva construida con Dash para cargar archivos de audio y visualizar análisis espectral en tiempo real, incluyendo:

- Forma de onda (waveform)
- Espectrograma
- Espectro de potencia (FFT)
- Densidad espectral de potencia (PSD) mediante método de Welch

Además permite hacer zoom y seguimiento sincronizado del tiempo actual de reproducción.

---

## Estructura del proyecto

```
audio_analyzer/
├── app/
│   └── main.py               # Punto de entrada principal
├── components/
│   └── layout.py             # Definición del layout Dash
├── callbacks/
│   └── callbacks.py          # Callbacks Dash para interacción
├── utils/
│   └── audio_utils.py        # Utilidades para procesamiento de audio
├── visualization/
│   └── plot.py               # Funciones para graficar análisis espectral
├── assets/
│   └── styles.css            # Estilos CSS personalizados
├── requirements.txt          # Lista de dependencias de Python
├── run_app.bat               # Script Windows para ejecutar app con venv
├── README.md                 # Este archivo
└── ...
```

## Instalación

1. Clona el repositorio :

```bash
git clone https://github.com/javdazdaz/audio-analyzer.git
cd audio-analyzer
```

2. Crea y activa un entorno virtual:

### En Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### En Windows Powershell/Command Prompt:

```powershell
python -m venv venv
venv\Scripts\activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

---

## Ejecución

### En Windows

Ejecuta doble clic sobre `run_app.bat`, que:

- Activa el entorno virtual
- Levanta la app Dash
- Abre automáticamente el navegador en `http://127.0.0.1:8050/`

### En Linux/macOS

Desde la raíz del proyecto y con entorno activado, ejecuta:

```bash
python -m app.main
```

Luego abre manualmente en el navegador:

```
http://127.0.0.1:8050/
```

---

## Uso

- Sube un archivo de audio compatible (wav, mp3, etc.).
- Visualiza la forma de onda, espectrograma y análisis espectral.
- Usa el zoom en los gráficos para analizar segmentos específicos.
- Reproduce el audio con el reproductor integrado.
- La línea roja sincroniza la posición actual de reproducción en los gráficos.

---

## Dependencias principales

- [Dash](https://dash.plotly.com/)
- [Librosa](https://librosa.org/)
- [Plotly](https://plotly.com/python/)
- [NumPy](https://numpy.org/)
- [SciPy](https://scipy.org/)

---
