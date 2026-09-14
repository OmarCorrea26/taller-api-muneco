# generar_datos.py
# Genera la encuesta sintetica de hogares para el Taller 2 (APIs + Git colaborativo).
# Es un conjunto de datos FICTICIO con problemas deliberados: duplicados, ingresos
# faltantes, valores atipicos y factores de expansion sin calibrar.
# Ejecutar desde la raiz del repo:  python datos/generar_datos.py

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(2026)

N = 1200
DEPARTAMENTOS = ["Antioquia", "Bogota", "Narino", "Santander", "Valle"]
PESOS_DPTO = [0.25, 0.30, 0.10, 0.15, 0.20]

ids = np.arange(1, N + 1)
hogar = np.random.randint(1, N // 3 + 1, size=N)
depto = np.random.choice(DEPARTAMENTOS, size=N, p=PESOS_DPTO)
area = np.random.choice(["Urbana", "Rural"], size=N, p=[0.75, 0.25])
sexo = np.random.choice(["H", "M"], size=N)
edad = np.random.randint(0, 90, size=N)

# Ocupacion: solo se pregunta a personas de 15 anos o mas (menores quedan en nulo)
prob = np.where(sexo == "M", 0.52, 0.62)
ocupado = np.where(edad >= 15, np.random.binomial(1, prob), np.nan)

# Ingreso mensual (COP): lognormal, nulo para no ocupados y menores,
# con 4% de faltantes entre los ocupados
base = np.random.lognormal(mean=14.2, sigma=0.5, size=N)
ingreso = np.where(ocupado == 1, base.round(-3), np.nan)
faltantes = (ocupado == 1) & (np.random.rand(N) < 0.04)
ingreso = np.where(faltantes, np.nan, ingreso)

# Factor de expansion crudo (sin calibrar)
factor = np.random.uniform(120, 480, size=N).round(2)

df = pd.DataFrame({
    "id_persona": ids,
    "id_hogar": hogar,
    "departamento": depto,
    "area": area,
    "sexo": sexo,
    "edad": edad,
    "ocupado": ocupado,
    "ingreso": ingreso,
    "factor_expansion": factor,
})

# --- Suciedad deliberada -----------------------------------------------------
# 1) 15 filas duplicadas exactas
dup = df.sample(15, random_state=1)
df = pd.concat([df, dup], ignore_index=True)

# 2) 6 valores atipicos de ingreso (error de digitacion: un cero de mas)
idx = df[df["ingreso"].notna()].sample(6, random_state=2).index
df.loc[idx, "ingreso"] = df.loc[idx, "ingreso"] * 10

# 3) Desordenar filas
df = df.sample(frac=1, random_state=3).reset_index(drop=True)

df["ocupado"] = df["ocupado"].astype("Int64")

salida = Path(__file__).parent / "encuesta_hogares.csv"
df.to_csv(salida, index=False)
print(f"Archivo creado: {salida.name} con {len(df)} filas y {df.shape[1]} columnas")
print(f"  duplicados: {df.duplicated().sum()}  ingresos faltantes en ocupados: {int(((df['ocupado']==1) & df['ingreso'].isna()).sum())}")
