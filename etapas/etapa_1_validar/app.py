# etapas/etapa_1_validar/app.py
# Etapa 1 — validar
#
# Responsable: Jessika Buitrago
# Ejecutar desde la raiz del repo:
#   uvicorn etapas.etapa_1_validar.app:app --port 8001 --reload
#
# Reglas del contrato para esta etapa: contrato/esquemas.py (Entrada1 / Salida1)
# y contrato/validaciones.py (validar_etapa_1).

from contrato.servicio import crear_app
import pandas as pd
import json

NUMERO = 1


def procesar(entrada: dict) -> dict:
    """Recibe el JSON de entrada (un dict) y devuelve el JSON de salida (otro dict).

    Mientras esta funcion lance NotImplementedError, el muneco no tendra esta parte.
    Cuando devuelva algo con la forma equivocada, la parte saldra chueca.
    """
    with open("fixtures/etapa_1_entrada.json", encoding="utf-8") as f:
        entrada = json.load(f)
    #print(entrada.keys())
    #print(entrada["resumen"])
    #print(entrada["registros"][0])

    df = pd.DataFrame(entrada["registros"])      # JSON -> DataFrame
    # cambio el tipo de columna forsozamente
    df = df.astype({
    "id_persona": "int",
    "id_hogar": "int",
    "departamento": "str",
    "area": "str",
    "sexo": "str",
    "edad": "int",
    "ocupado": "Int64",
    "factor_expansion": "float",
    })
    df["ingreso"] = pd.to_numeric(df["ingreso"], errors="coerce")

    #establezco el orden de las columnas
    df = df[["id_persona", "id_hogar", "departamento", "area", "sexo", "edad",
        "ocupado", "ingreso", "factor_expansion"]]
    # converitir nulos a None para que el JSON se lea bien
    registros = df.astype(object).where(df.notna(), None).to_dict(orient="records")

    # Salida con el número de filas, columnas y nulos por columna
    resumen = {"n_filas": int(len(df)),
               "columnas": df.columns.tolist(),
               "n_nulos_por_columna": df.isna().sum().astype(int).to_dict() } 
                                
    return {"registros": registros, "resumen": resumen} 


app = crear_app(NUMERO, procesar)
