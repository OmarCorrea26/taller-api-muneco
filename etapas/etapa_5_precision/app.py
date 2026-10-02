# etapas/etapa_5_precision/app.py
# Etapa 5 — precision
#
# Responsable: [tu nombre]
# Ejecutar desde la raiz del repo:
#   uvicorn etapas.etapa_5_precision.app:app --port 8005 --reload
#
# Reglas del contrato para esta etapa: contrato/esquemas.py (Entrada5 / Salida5)
# y contrato/validaciones.py (validar_etapa_5).

import math

import pandas as pd

from contrato.servicio import crear_app

NUMERO = 5
Z_95 = 1.96   # valor critico para un intervalo de confianza del 95 %


def _subconjunto(df: pd.DataFrame, ind: dict) -> tuple[pd.DataFrame, str]:
    """Registros del dominio del indicador y la variable sobre la que se calcula."""
    if ind["indicador"] == "tasa_ocupacion":
        sub = df[df["edad"] >= 15]
        variable = "ocupado"
    else:
        sub = df[df["ocupado"] == 1]
        variable = "ingreso"
    for k, v in ind["desagregacion"].items():
        sub = sub[sub[k].astype(str) == v]
    return sub, variable


def _error_estandar(x: pd.Series, w: pd.Series) -> float:
    """Error estandar aproximado con tamano de muestra efectivo de Kish."""
    media = (x * w).sum() / w.sum()
    varianza = (w * (x - media) ** 2).sum() / w.sum()
    n_ef = w.sum() ** 2 / (w ** 2).sum()
    return math.sqrt(varianza / n_ef)


def procesar(entrada: dict) -> dict:
    df = pd.DataFrame(entrada["registros"])

    indicadores = []
    for ind in entrada["indicadores"]:
        sub, variable = _subconjunto(df, ind)
        # Decision estadistica: ponderado por factor calibrado, sin efecto de diseno
        ee = _error_estandar(sub[variable], sub["factor_calibrado"])
        valor = ind["valor"]
        indicadores.append({
            **ind,
            "error_estandar": float(ee),
            "cv": float(100 * ee / valor),
            "limite_inferior": float(valor - Z_95 * ee),
            "limite_superior": float(valor + Z_95 * ee),
        })

    return {"indicadores": indicadores}


app = crear_app(NUMERO, procesar)
