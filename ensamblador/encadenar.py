# ensamblador/encadenar.py
# Corre el proceso COMPLETO de punta a punta: lee el CSV, se lo manda a la etapa 1,
# la salida de la 1 a la 2, y asi hasta la 6. Es el "modo produccion" del taller:
# aqui ya no se usan fixtures, cada etapa recibe lo que hizo la anterior.
#
#   python -m ensamblador.encadenar
#
# Requiere las seis etapas corriendo (scripts/levantar_todo.ps1).

import json
import sys
from pathlib import Path

import httpx
import pandas as pd

from contrato.etapas import ETAPAS
from contrato.validaciones import validar

RAIZ = Path(__file__).resolve().parent.parent


def main() -> int:
    df = pd.read_csv(RAIZ / "datos" / "encuesta_hogares.csv")
    entrada = {"registros": df.astype(object).where(df.notna(), None).to_dict(orient="records")}
    print(f"Entrada: {len(entrada['registros'])} registros del CSV")

    for e in ETAPAS:
        url = f"http://localhost:{e['puerto']}/procesar"
        try:
            r = httpx.post(url, json=entrada, timeout=60)
        except httpx.HTTPError as ex:
            print(f"  Etapa {e['numero']} ({e['nombre']}): no responde ({type(ex).__name__}). Se detiene la cadena.")
            return 1
        if r.status_code != 200:
            print(f"  Etapa {e['numero']} ({e['nombre']}): HTTP {r.status_code} {r.text[:200]}. Se detiene la cadena.")
            return 1
        salida = r.json()
        # En modo encadenado no comparamos contra la referencia: solo coherencia interna
        errores = validar(e["numero"], entrada, salida, usar_referencia=False)
        estado = "OK" if not errores else f"CHUECO ({errores[0]})"
        print(f"  Etapa {e['numero']} ({e['nombre']}): {estado}")
        entrada = salida

    destino = RAIZ / "salida" / "resultado_final.json"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultado final guardado en {destino.relative_to(RAIZ)}")
    print(f"Excel del tabulado: {salida.get('archivo_excel')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
