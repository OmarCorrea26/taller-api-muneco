# contrato/etapas.py
# Registro central de las seis etapas del proceso.
# Aqui se define QUIEN es cada etapa, en QUE puerto corre y QUE parte del muneco representa.
# Este archivo es parte del contrato: si cambia, cambia para todos.

ETAPAS = [
    {
        "numero": 1,
        "nombre": "validar",
        "parte": "cabeza",
        "puerto": 8001,
        "descripcion": "Carga y validacion de esquema de la encuesta",
    },
    {
        "numero": 2,
        "nombre": "limpiar",
        "parte": "torso",
        "puerto": 8002,
        "descripcion": "Eliminacion de duplicados, tratamiento de atipicos e imputacion de ingreso",
    },
    {
        "numero": 3,
        "nombre": "calibrar",
        "parte": "brazo_izquierdo",
        "puerto": 8003,
        "descripcion": "Calibracion de factores de expansion a totales poblacionales conocidos",
    },
    {
        "numero": 4,
        "nombre": "indicadores",
        "parte": "brazo_derecho",
        "puerto": 8004,
        "descripcion": "Estimacion ponderada de indicadores: tasa de ocupacion e ingreso promedio",
    },
    {
        "numero": 5,
        "nombre": "precision",
        "parte": "pierna_izquierda",
        "puerto": 8005,
        "descripcion": "Error estandar, coeficiente de variacion e intervalos de confianza",
    },
    {
        "numero": 6,
        "nombre": "publicar",
        "parte": "pierna_derecha",
        "puerto": 8006,
        "descripcion": "Clasificacion de calidad, metadatos y exportacion del tabulado final",
    },
]

PUERTO_ENSAMBLADOR = 8000


def etapa(numero: int) -> dict:
    """Devuelve la definicion de una etapa por su numero (1 a 6)."""
    for e in ETAPAS:
        if e["numero"] == numero:
            return e
    raise ValueError(f"No existe la etapa {numero}")
