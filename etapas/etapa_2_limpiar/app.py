# etapas/etapa_2_limpiar/app.py
# Etapa 2 — limpiar
#
# Responsable: [tu nombre]
# Ejecutar desde la raiz del repo:
#   uvicorn etapas.etapa_2_limpiar.app:app --port 8002 --reload
#
# Reglas del contrato para esta etapa: contrato/esquemas.py (Entrada2 / Salida2)
# y contrato/validaciones.py (validar_etapa_2).

from contrato.servicio import crear_app

NUMERO = 2


def procesar(entrada: dict) -> dict:
    """Recibe el JSON de entrada (un dict) y devuelve el JSON de salida (otro dict).

    Mientras esta funcion lance NotImplementedError, el muneco no tendra esta parte.
    Cuando devuelva algo con la forma equivocada, la parte saldra chueca.
    """
    raise NotImplementedError(f"La etapa {NUMERO} todavia no esta implementada")


app = crear_app(NUMERO, procesar)
