import os
import time

MAX_INTENTOS = int(os.getenv("TIWI_NVR_CONTROL_INTENTOS", "3"))

FACTOR_TOLERANCIA = float(os.getenv("TIWI_NVR_CONTROL_FACTOR", "1.5"))
MARGEN_EXTRA_S = float(os.getenv("TIWI_NVR_CONTROL_MARGEN_S", "15"))

def es_clip_largo(duracion_real_s, pedido_s):
    if duracion_real_s is None:
        return None
    limite = max(pedido_s * FACTOR_TOLERANCIA, pedido_s + MARGEN_EXTRA_S)
    return duracion_real_s > limite