# ensamblador/verificar.py
# Logica compartida por el ensamblador (web) y por probar.py (terminal):
# envia el fixture de entrada a un servicio y valida lo que devuelve.

import httpx

from contrato.etapas import etapa as definicion_etapa
from contrato.validaciones import cargar_fixture, validar

TIMEOUT = 30  # segundos; los JSON pesan ~300 KB y pandas necesita un momento


def verificar_etapa(numero: int, url_base: str | None = None) -> dict:
    """Devuelve {"numero", "nombre", "parte", "estado", "detalle"} donde estado es
    'ausente' (no responde), 'chueco' (responde pero falla la validacion) u 'ok'."""
    defi = definicion_etapa(numero)
    url = url_base or f"http://localhost:{defi['puerto']}"
    resultado = {"numero": numero, "nombre": defi["nombre"], "parte": defi["parte"], "url": url}

    entrada = cargar_fixture(f"etapa_{numero}_entrada.json")
    try:
        r = httpx.post(f"{url}/procesar", json=entrada, timeout=TIMEOUT)
    except httpx.HTTPError as e:
        return {**resultado, "estado": "ausente", "detalle": [f"No responde en {url}: {type(e).__name__}"]}

    if r.status_code == 501:
        return {**resultado, "estado": "ausente", "detalle": ["El servicio corre pero procesar() aun lanza NotImplementedError"]}
    if r.status_code != 200:
        return {**resultado, "estado": "chueco", "detalle": [f"HTTP {r.status_code}: {r.text[:300]}"]}

    try:
        salida = r.json()
    except ValueError:
        return {**resultado, "estado": "chueco", "detalle": ["La respuesta no es JSON valido"]}

    errores = validar(numero, entrada, salida)
    if errores:
        return {**resultado, "estado": "chueco", "detalle": errores}
    return {**resultado, "estado": "ok", "detalle": ["Cumple el contrato"]}
