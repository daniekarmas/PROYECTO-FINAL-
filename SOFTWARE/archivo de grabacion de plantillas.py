import sounddevice as sd
import soundfile as sf

# ==========================================
# CONFIGURACIÓN
# ==========================================

FS = 16000
DURACION = 10

NOMBRE_ARCHIVO = "alto.wav"
# Cambiar por:
# "abre.wav"
# "alto.wav"

# ==========================================
# GRABACIÓN
# ==========================================

print("===================================")
print("GRABACIÓN")
print("===================================")

print(f"Grabando {NOMBRE_ARCHIVO}...")

audio = sd.rec(
    int(DURACION * FS),
    samplerate=FS,
    channels=1,
    dtype="float32"
)

sd.wait()

sf.write(
    NOMBRE_ARCHIVO,
    audio,
    FS
)

print("Archivo guardado correctamente.")