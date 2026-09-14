# etapas/etapa_4_indicadores/app.py
# Etapa 4 — indicadores
#
# Responsable: [tu nombre]
# Ejecutar desde la raiz del repo:
#   uvicorn etapas.etapa_4_indicadores.app:app --port 8004 --reload
#
# Reglas del contrato para esta etapa: contrato/esquemas.py (Entrada4 / Salida4)
# y contrato/validaciones.py (validar_etapa_4).

from contrato.servicio import crear_app

NUMERO = 4


def procesar(entrada: dict) -> dict:
    """Recibe el JSON de entrada (un dict) y devuelve el JSON de salida (otro dict).

    Mientras esta funcion lance NotImplementedError, el muneco no tendra esta parte.
    Cuando devuelva algo con la forma equivocada, la parte saldra chueca.
    """
    raise NotImplementedError(f"La etapa {NUMERO} todavia no esta implementada")


app = crear_app(NUMERO, procesar)
