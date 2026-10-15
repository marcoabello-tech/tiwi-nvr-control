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

    for intento in range(1, MAX_INTENTOS + 1):
        a, b = _ventana_para_intento(t0, t1, intento)
        res = pull_fn(channel, a, b, out_path)
        if not res:
            log(f"CONTROL ch{channel}: el NVR no devolvió clip "
                f"(intento {intento}/{MAX_INTENTOS})")
            return None

            dur = medir_fn(out_path)
            largo = es_clip_largo(dur, b - a)

            if largo is None:
            res["control"] = {
                "estado": "sin_medir", "intentos": intento,
                "duracion_real_s": None, "pedido_s": round(pedido_s, 1),
                "motivo": "no se pudo medir la duración del archivo"}
            log(f"CONTROL ch{channel}: no se pudo medir el clip, se sube igual")
            return res

            if not largo:
            res["control"] = {
                "estado": "ok", "intentos": intento,
                "duracion_real_s": round(dur, 1),
                "pedido_s": round(pedido_s, 1),
                "motivo": "la duración coincide con el cruce"}
            log(f"CONTROL ch{channel}: OK ({dur:.0f}s) en intento {intento}")
            return res

        log(f"CONTROL ch{channel}: clip largo ({dur:.0f}s para un cruce de "
            f"{b - a:.0f}s), intento {intento}/{MAX_INTENTOS}")
        if intento < MAX_INTENTOS:
            time.sleep(espera_s)
            
    motivo = (f"El clip dura {dur:.0f}s y el cruce fue de {pedido_s:.0f}s. "
              f"Se intentó acotar {MAX_INTENTOS} veces sin éxito. "
              f"Buscar el camión cerca del instante del cruce.")
    _escribir_marca_revision(out_path, motivo)
    res["control"] = {
        "estado": "revision_manual", "intentos": MAX_INTENTOS,
        "duracion_real_s": round(dur, 1), "pedido_s": round(pedido_s, 1),
        "motivo": motivo}
    log(f"CONTROL ch{channel}: REVISION MANUAL - {motivo}")
    return res

    