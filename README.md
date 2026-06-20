# Interfaz Hombre-Máquina (HMI) Bimodal de Doble Autenticación

Este repositorio contiene el desarrollo del proyecto final para la materia de Administración y Gestión Hospitalaria / Ingeniería Biomédica. El sistema consiste en una interfaz bimodal que integra el procesamiento de señales electromiográficas (EMG) y el reconocimiento de comandos de voz en tiempo real para el control seguro de actuadores.

## 👥 Integrantes del Equipo
* **Daniek Armas** - *Ingeniería Biomédica*
* **Luis Martel** - *Ingeniería Biomédica*


---

## Estructura del Repositorio

El proyecto se encuentra organizado bajo la estructura requerida:

* **`/Hardware`**: Contiene los diagramas de conexión, esquemáticos del circuito de acondicionamiento analógico (amplificador de instrumentación AD620, filtros y etapas de ganancia con LM358) y la etapa de adquisición con el ESP32.
* **`/Software`**: Aloja los scripts desarrollados en Python:
  * `silencio.py`: Grabación de ruido de fondo ambiental.
  * `calcular_silencio.py`: Calibración estadística de umbrales mediante el criterio de las 3 sigmas.
  * `ultima_interfaz.py`: Sistema en tiempo real con interfaz gráfica (Tkinter), procesamiento FFT, ventanas de Hamming y emparejamiento por Correlación de Pearson bajo una ventana de seguridad bimodal de 2.0 segundos.
* **`/Reporte`**: Incluye el artículo científico final redactado bajo la estricta plantilla de conferencias de la IEEE tanto en formato **PDF** (máximo 4 páginas) como su archivo editable **.docx**.

---

## Requisitos e Instalación

Para ejecutar el software de este proyecto en un entorno local (compatible con Windows / WSL2 Ubuntu), asegúrese de instalar las siguientes dependencias de Python:

```bash
pip install numpy sounddevice soundfile scipy