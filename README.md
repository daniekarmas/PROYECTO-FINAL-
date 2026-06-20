# Interfaz Hombre-Máquina (HMI) Bimodal de Doble Autenticación

Este repositorio contiene el desarrollo del proyecto final para la materia de Procesamiento de señales biomédicas / Ingeniería Biomédica. El sistema consiste en una interfaz bimodal que integra el procesamiento de señales electromiográficas (EMG) y el reconocimiento de comandos de voz en tiempo real para el control seguro de actuadores.

## 👥 Integrantes del Equipo
* **Daniek Armas** - *Ingeniería Biomédica*
* **Luis Martel** - *Ingeniería Biomédica*


---

## Estructura del Repositorio

El proyecto se encuentra organizado bajo la estructura requerida:

* **`/Hardware`**: Contiene los diagramas de conexión, esquemáticos del circuito de acondicionamiento analógico (amplificador de instrumentación AD620, filtros y etapas de ganancia con LM358) y la etapa de adquisición con el ESP32.
* **`/Software`**: Aloja los scripts desarrollados en Python:
  * `archivo de grabacion de plantillas.py`: Grabación de ruido de fondo ambiental.
  * `calcular e y zcr de plantillas.py`: Calibración estadística de umbrales mediante el criterio de las 3 sigmas.
  * `Interfaz humano-máquina por gestos con doble seguridad.py`: Sistema en tiempo real con interfaz gráfica (Tkinter), procesamiento FFT, ventanas de Hamming y emparejamiento por Correlación de Pearson bajo una ventana de seguridad bimodal de 2.0 segundos.
* **`/Reporte`**: Incluye el artículo científico final redactado bajo la estricta plantilla de conferencias de la IEEE tanto en formato **PDF** como su archivo editable **.docx**.

---

## Requisitos e Instalación

Para ejecutar el software de este proyecto en un entorno local (compatible con Windows / WSL2 Ubuntu), asegúrese de instalar las siguientes dependencias de Python:

```bash
pip install numpy sounddevice soundfile scipy

Ejecución:
1. Conecte el hardware (ESP32 y electrodos EMG) al puerto correspondiente.

2. Ejecute la interfaz en vivo desde la carpeta /Software:
        python ultima_interfaz.py

Especificaciones del Sistema:
Frecuencia de Muestreo de Voz: 16,000 Hz
Tamaño de Bloque (Block Size): 1024 muestras
Ventana de Seguridad Bimodal: 2.0 segundos (tiempo límite para hablar tras la activación por EMG).
Criterio de Calibración: Regla de las 3 sigmas para filtrado robusto del ruido de fondo de la habitación.
