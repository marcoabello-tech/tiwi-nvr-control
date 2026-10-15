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

def _ventana_para_intento(t0, t1, intento):
    if intento <= 1:
        return t0, t1
    centro = (t0 + t1) / 2.0
    mitad = max(5.0, ((t1 - t0) / 2.0) / intento)
    return centro - mitad, centro + mitad

def _escribir_marca_revision(path, motivo):
    marca = path + ".REVISAR.txt"
    try:
        with open(marca, "w", encoding="utf-8") as f:
            f.write("PENDIENTE DE REVISION MANUAL\n")
            f.write(motivo + "\n")
    except Exception:
        pass
    return marca

def descargar_con_control(pull_fn, medir_fn, channel, t0, t1, out_path,
                          log=print, espera_s=2.0):
    pedido_s = float(t1) - float(t0)
    res = None
    dur = None