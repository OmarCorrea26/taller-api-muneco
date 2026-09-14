# etapas/etapa_1_validar/app.py
# Etapa 1 — validar
#
# Responsable: [tu nombre]
# Ejecutar desde la raiz del repo:
#   uvicorn etapas.etapa_1_validar.app:app --port 8001 --reload
#
# Reglas del contrato para esta etapa: contrato/esquemas.py (Entrada1 / Salida1)
# y contrato/validaciones.py (validar_etapa_1).

from contrato.servicio import crear_app

NUMERO = 1


def procesar(entrada: dict) -> dict:
    """Recibe el JSON de entrada (un dict) y devuelve el JSON de salida (otro dict).

    Mientras esta funcion lance NotImplementedError, el muneco no tendra esta parte.
    Cuando devuelva algo con la forma equivocada, la parte saldra chueca.
    """
    raise NotImplementedError(f"La etapa {NUMERO} todavia no esta implementada")


app = crear_app(NUMERO, procesar)
