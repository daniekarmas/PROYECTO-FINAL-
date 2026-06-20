import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter

# ==========================================
# ARCHIVO
# ==========================================
FS = 16000

audio, FS = sf.read(
    "silencio.wav",
    dtype="float32"
)

# Cambiar por:
# "silencio.wav"
# "abre.wav"
# "alto.wav"

audio = audio.flatten()

# ==========================================
# PARÁMETROS
# ==========================================

VENTANA = 1024
 
#VENTANA_MS = 20
#VENTANA = int(FS * VENTANA_MS / 1000)

FREC_BAJA = 100
FREC_ALTA = 1500

TOLERANCIA = 0.005

# ==========================================
# FILTRO
# ==========================================

nyq = FS / 2

low = FREC_BAJA / nyq
high = FREC_ALTA / nyq

b, a = butter(
    4,
    [low, high],
    btype="band"
)

# ==========================================
# LISTAS
# ==========================================

energias = []
zcrs = []

# ==========================================
# ANÁLISIS
# ==========================================

for i in range(0, len(audio)-VENTANA, VENTANA):

    segmento = audio[i:i+VENTANA]

    # Eliminar offset DC
    segmento = segmento - np.mean(segmento)

    # Filtrar

    segmento = lfilter(
        b,
        a,
        segmento
    )

    # Eliminar amplitudes pequeñas

    segmento = np.where(
        np.abs(segmento) < TOLERANCIA,
        0,
        segmento
    )

    # --------------------------
    # Energía
    # --------------------------

    energia = np.sum(
        segmento**2
    )

    # --------------------------
    # ZCR
    # --------------------------

    signos = np.sign(
        segmento
    )

    cambios = np.abs(
        np.diff(signos)
    )

    cruces = np.sum(
        cambios == 2
    )

    zcr = cruces / len(segmento)

    energias.append(
        energia
    )

    zcrs.append(
        zcr
    )

# ==========================================
# RESULTADOS
# ==========================================

# media de las energías (mu)
mu_E = np.mean(
    energias
)

# desviación estandar de las energías 
sigma_E = np.std(
    energias
)

# aplica la formula del umbral = mu + 3 sigma
umbral_E = mu_E + 3*sigma_E


# media de los zcr 
mu_Z = np.mean(
    zcrs
)

# desviación estandar de los zcr
sigma_Z = np.std(
    zcrs
)

# aplica la formula del umbral a los zcr = mu + 3 sigma
umbral_Z = mu_Z + 3*sigma_Z

print("\n==========================")
print("RESULTADOS")
print("==========================")

print("\nENERGÍA")
print("--------------------------")
print(f"Media:      {mu_E:.6f}")
print(f"Desviación: {sigma_E:.6f}")
print(f"Umbral:     {umbral_E:.6f}")

print("\nZCR")
print("--------------------------")
print(f"Media:      {mu_Z:.6f}")
print(f"Desviación: {sigma_Z:.6f}")
print(f"Umbral:     {umbral_Z:.6f}")