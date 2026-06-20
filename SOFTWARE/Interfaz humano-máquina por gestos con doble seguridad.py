import serial
import numpy as np
import tkinter as tk
import threading
import time
from collections import deque
import sounddevice as sd

# Integración de Matplotlib con Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
# CONFIGURACIÓN
# ==========================================
PUERTO = "COM5"
BAUDIOS = 230400

FS = 1200 #Fs del emg 
VENTANA = int(0.2 * FS) # 240 muestras por ventana

UMBRAL_EMG = 250 # Umbral para reconocer una contracción 

# Valores de calibración basados en las muestras filtradas

#UMBRAL_ENERGIA = 5.777873
#UMBRAL_ZCR = 0.031066

UMBRAL_ENERGIA = 0.005  
UMBRAL_ZCR = 0.001     

VENTANA_SEGURIDAD = 2.0 # tiempo para detectar

SAMPLE_RATE = 16000 #
BLOCK_SIZE = 1024  

UMBRAL_ABRE = 0.40
UMBRAL_ALTO = 0.58

# ==========================================
# VARIABLES GLOBALES
# ==========================================
ultimo_emg = 0
emg_activo = False
voz_activa = False

energia_actual = 0
zcr_actual = 0

palabra_audio = []
grabando_voz = False
bloques_silencio_consecutivos = 0

# Historial para la gráfica temporal de EMG (últimas 600 muestras para fluidez)
historial_grafica_emg = deque([0]*600, maxlen=600)

# ==========================================
# CONEXIÓN SERIAL ESP32
# ==========================================
try:
    ser = serial.Serial(PUERTO, BAUDIOS)
    print(f" Conectado al ESP32 en el puerto {PUERTO}")
except Exception as e:
    print(f"Error al abrir puerto serial {PUERTO}: {e}")
    ser = None

buffer = deque(maxlen=VENTANA)

# ==========================================
# CARGAR PLANTILLAS
# ==========================================
try:
    plantilla_abre = np.load("abre_plantilla.npy")
    plantilla_alto = np.load("alto_plantilla.npy")
    print("Plantillas espectrales cargadas correctamente.")
except Exception as e:
    print(f"Error al cargar plantillas: {e}")

# ==========================================
# FUNCIONES AUXILIARES MATEMÁTICAS
# ==========================================
def calcular_zcr(fragmento):
    cambios_signo = np.diff(np.sign(fragmento)) != 0
    return np.mean(cambios_signo)

def calcular_energia(fragmento):
    return np.mean(fragmento ** 2)

# ==========================================
# PROCESAMIENTO Y VALIDACIÓN (HILO DE FONDO)
# ==========================================
def procesar_y_validar_comando(audio_completo):
    global ultimo_emg, emg_activo
    
    
    
    if len(audio_completo) > SAMPLE_RATE:
        audio_completo = audio_completo[:SAMPLE_RATE]
    elif len(audio_completo) < SAMPLE_RATE:
        audio_completo = np.pad(audio_completo, (0, SAMPLE_RATE - len(audio_completo)), 'constant')

    audio_completo = audio_completo - np.mean(audio_completo)           # Restamos el offset a todas las muestras    
    audio_completo = audio_completo * np.hamming(len(audio_completo))     # np.hamming(16000) 
    fft_actual = np.abs(np.fft.rfft(audio_completo))                       
    fft_actual = fft_actual / np.max(fft_actual)                           

    

    # --------------------- 

    # Encontrar el vector de frecuencias correspondiente al eje X
    frecuencias = np.fft.rfftfreq(len(audio_completo), d=1/SAMPLE_RATE)
    
    # Actualizar la gráfica en el dominio de la frecuencia
    linea_voz.set_data(frecuencias, fft_actual)
    ax_voz.set_xlim(0, 4000) # Enfocar la vista en el rango de interés (0-4 kHz)
    fig_voz.canvas.draw_idle()


    # ---- Coeficientes de correlación cruzada de Pearson 
    corr_abre = np.corrcoef(plantilla_abre, fft_actual)[0, 1]
    corr_alto = np.corrcoef(plantilla_alto, fft_actual)[0, 1]

    # Calculos de tiempo con respecto al factor EMG de seguridad 
    ahora = time.time()
    delta = ahora - ultimo_emg
    emg_en_ventana = delta <= VENTANA_SEGURIDAD

    # Evaluación y actualización del Indicador Virtual y Textos
    if corr_abre >= UMBRAL_ABRE and corr_abre > corr_alto:
        if emg_en_ventana:
            lbl_coincidencia.config(text=f"COINCIDENCIA: ABRE ({corr_abre:.2f})")
            lbl_estado.config(text=f"ACCESO CONCEDIDO\nComando 'ABRE' validado", bg="#8cc63f")  #(Δt = {delta:.2f}s)
        else:
            lbl_coincidencia.config(text=f"COINCIDENCIA: ABRE ({corr_abre:.2f}) - SIN EMG")
            lbl_estado.config(text=f"ACCESO BLOQUEADO\nTiempo de seguridad muscular expirado", bg="#d9534f")

    elif corr_alto >= UMBRAL_ALTO and corr_alto > corr_abre:
        if emg_en_ventana:
            lbl_coincidencia.config(text=f"COINCIDENCIA: ALTO ({corr_alto:.2f})")
            lbl_estado.config(text=f"PERÍMETRO ASEGURADO\nComando 'ALTO' validado", bg="#8cc63f")
        else:
            lbl_coincidencia.config(text=f"COINCIDENCIA: ALTO ({corr_alto:.2f}) - SIN EMG")
            lbl_estado.config(text=f"ACCESO BLOQUEADO\nTiempo de seguridad muscular expirado", bg="#d9534f")

    else:
        lbl_coincidencia.config(text="COINCIDENCIA: --- (No Reconocido)")
        lbl_estado.config(text="COMANDO NO RECONOCIDO\nHuella acústica inválida", bg="#d9534f")

# ==========================================
# INTERFAZ GRÁFICA (TKINTER + MATPLOTLIB)
# ==========================================
ventana = tk.Tk()
ventana.title("Interfaz Hombre-Máquina - Doble Factor")
ventana.geometry("800x750")
ventana.configure(bg="white")

# --- 1. INDICADOR VIRTUAL (Fila 0, ocupa ambas columnas) ---
lbl_estado = tk.Label(
    ventana, 
    text="SISTEMA EN ESPERA...\nActiva el EMG y di un comando", 
    font=("Arial", 18, "bold"), 
    bg="#a1cb46",  # Color verde/oliva de tu diseño para el estado neutral/activo
    fg="white", 
    height=4,
    relief="flat"
)
lbl_estado.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=15)

# --- 2. CONTROLES / VALORES MEDIDOS (Fila 1) ---
lbl_rms = tk.Label(
    ventana, 
    text="VALOR RMS EMG: ---", 
    font=("Arial", 12, "bold"), 
    bg="#7ebbc7",  # Tono azul/azul claro de tus botones inferiores
    fg="white",
    padx=15, pady=8,
    width=30,
    height=2
)
lbl_rms.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

lbl_coincidencia = tk.Label(
    ventana, 
    text="COINCIDENCIA PALABRA: ---", 
    font=("Arial", 12, "bold"), 
    bg="#7ebbc7", 
    fg="white",
    padx=15, pady=8,
    width=30,
    height=2
)
lbl_coincidencia.grid(row=1, column=1, padx=20, pady=5, sticky="ew")

# --- 3. SECCIÓN DE GRÁFICAS (Fila 2) ---
# Gráfica de EMG
fig_emg = Figure(figsize=(3.8, 3.2), dpi=100)
ax_emg = fig_emg.add_subplot(111)
ax_emg.set_title("GRÁFICA DE EMG", fontsize=10, weight='bold', color="#555555")
ax_emg.set_ylim(-200, 200) # Ajusta según la amplitud de tu ADC
ax_emg.set_xlim(0, 600)
ax_emg.grid(True, linestyle='--', alpha=0.5)
linea_emg, = ax_emg.plot([], [], color="#7ebbc7", lw=1.5)

canvas_emg = FigureCanvasTkAgg(fig_emg, master=ventana)
canvas_emg.get_tk_widget().grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

# Gráfica de Voz
fig_voz = Figure(figsize=(3.8, 3.2), dpi=100)
ax_voz = fig_voz.add_subplot(111)
ax_voz.set_title("ESPECTRO DE VOZ (FRECUENCIA)", fontsize=10, weight='bold', color="#555555")
ax_voz.set_xlim(0, 4000) # Mostramos hasta 4kHz que es donde está el habla útil
ax_voz.set_ylim(0, 1.1) # La FFT normalizada va de 0 a 1
ax_voz.grid(True, linestyle='--', alpha=0.5)
linea_voz, = ax_voz.plot([], [], color="#e7a56c", lw=1.5) # Color cálido diferenciador

canvas_voz = FigureCanvasTkAgg(fig_voz, master=ventana)
canvas_voz.get_tk_widget().grid(row=2, column=1, padx=20, pady=10, sticky="nsew")

# Configurar pesos de la cuadrícula para adaptabilidad dimensional
ventana.grid_rowconfigure(2, weight=1)
ventana.grid_columnconfigure(0, weight=1)
ventana.grid_columnconfigure(1, weight=1)

# ==========================================
# FUNCIONES DE ACTUALIZACIÓN DE GRÁFICAS
# ==========================================
def actualizar_grafica_voz(audio_datos):
    # Dibuja la forma de onda temporal de la palabra recién pronunciada
    linea_voz.set_data(np.arange(len(audio_datos)), audio_datos)
    ax_voz.set_xlim(0, len(audio_datos))
    fig_voz.canvas.draw_idle()

# ==========================================
# RUTINA ELECTROMIOGRAFÍA (EMG)
# ==========================================
def actualizar_emg():
    global ultimo_emg, emg_activo

    if ser is not None:
        while ser.in_waiting:
            try:
                muestra = int(ser.readline().decode(errors="ignore").strip())
                buffer.append(muestra)
                historial_grafica_emg.append(muestra - 2048) # Resta el offset dinámico aproximado (ej: VCC/2)
            except:
                pass

    if len(buffer) == VENTANA:
        datos = np.array(buffer)
        datos = datos - np.mean(datos)  
        rms = np.sqrt(np.mean(datos ** 2))

        lbl_rms.config(text=f"VALOR RMS EMG: {rms:.2f}")

        if rms > UMBRAL_EMG:
            emg_activo = True
            ultimo_emg = time.time()
            lbl_rms.config(bg="#5cb85c") # Se vuelve verde al contraer
        else:
            emg_activo = False
            lbl_rms.config(bg="#7ebbc7") # Color base azul de tu diseño

    # Refrescar la línea de la gráfica temporal de EMG de forma fluida
    y_data = list(historial_grafica_emg)
    linea_emg.set_data(np.arange(len(y_data)), y_data)
    
    # Auto-escalar eje Y si la señal es muy alta para que no se corte
    if len(y_data) > 0:
        max_val = max(abs(min(y_data)), abs(max(y_data)))
        if max_val > 150:
            ax_emg.set_ylim(-max_val*1.2, max_val*1.2)
            
    fig_emg.canvas.draw_idle()

    # Mantener el bucle en tiempo real cada 30ms para sincronía visual suave (~33 FPS)
    ventana.after(30, actualizar_emg)

# ==========================================
# DETECTOR DE ACTIVIDAD DE VOZ (VAD)
# ==========================================
def detectar_voz():
    global voz_activa, energia_actual, zcr_actual, palabra_audio, grabando_voz, bloques_silencio_consecutivos

    def callback(indata, frames, tiempo_info, status):
        global voz_activa, energia_actual, zcr_actual, palabra_audio, grabando_voz, bloques_silencio_consecutivos

        audio_bloque = indata[:, 0]
        energia_actual = calcular_energia(audio_bloque)
        zcr_actual = calcular_zcr(audio_bloque)

        if energia_actual > UMBRAL_ENERGIA and zcr_actual > UMBRAL_ZCR:
            voz_activa = True
            
            if not grabando_voz:
                grabando_voz = True
                palabra_audio = []  
                lbl_estado.config(text="🎙️ ESCUCHANDO COMANDO ACÚSTICO...", bg="#f0ad4e")
            
                # Borrar gráfica anterior de voz mientras se graba la nueva
                linea_voz.set_data([], [])
                fig_voz.canvas.draw_idle()
        

            palabra_audio.extend(audio_bloque)
            bloques_silencio_consecutivos = 0
        else:
            voz_activa = False
            
            if grabando_voz:
                palabra_audio.extend(audio_bloque)
                bloques_silencio_consecutivos += 1
                
                if bloques_silencio_consecutivos > 5:
                    grabando_voz = False
                    audio_final = np.array(palabra_audio, dtype='float32')
                    # Procesar la correlación en segundo plano para no congelar la app
                    threading.Thread(target=procesar_y_validar_comando, args=(audio_final,), daemon=True).start()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=BLOCK_SIZE, callback=callback):
        while True:
            sd.sleep(100)

# ==========================================
# INICIALIZACIÓN
# ==========================================
hilo_vad = threading.Thread(target=detectar_voz, daemon=True)
hilo_vad.start()

actualizar_emg()

ventana.mainloop()