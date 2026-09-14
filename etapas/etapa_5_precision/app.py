# etapas/etapa_5_precision/app.py
# Etapa 5 — precision
#
# Responsable: [tu nombre]
# Ejecutar desde la raiz del repo:
#   uvicorn etapas.etapa_5_precision.app:app --port 8005 --reload
#
# Reglas del contrato para esta etapa: contrato/esquemas.py (Entrada5 / Salida5)
# y contrato/validaciones.py (validar_etapa_5).

from contrato.servicio import crear_app

NUMERO = 5


def procesar(entrada: dict) -> dict:
    """Recibe el JSON de entrada (un dict) y devuelve el JSON de salida (otro dict).

    Mientras esta funcion lance NotImplementedError, el muneco no tendra esta parte.
    Cuando devuelva algo con la forma equivocada, la parte saldra chueca.
    """
    raise NotImplementedError(f"La etapa {NUMERO} todavia no esta implementada")


app = crear_app(NUMERO, procesar)
