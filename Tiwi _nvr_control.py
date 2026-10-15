import os
import time

MAX_INTENTOS = int(os.getenv("TIWI_NVR_CONTROL_INTENTOS", "3"))

FACTOR_TOLERANCIA = float(os.getenv("TIWI_NVR_CONTROL_FACTOR", "1.5"))
MARGEN_EXTRA_S = float(os.getenv("TIWI_NVR_CONTROL_MARGEN_S", "15"))