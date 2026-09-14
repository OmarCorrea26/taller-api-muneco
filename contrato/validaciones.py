# contrato/validaciones.py
# Reglas de validacion de cada etapa. Es lo que decide si una parte del muneco sale
# DERECHA (lista vacia de errores) o CHUECA (uno o mas errores).
#
# Hay dos capas:
#   1. Estructura: la salida debe ajustarse al esquema Pydantic (contrato/esquemas.py).
#   2. Coherencia estadistica: reglas de negocio que un esquema no puede expresar
#      (una tasa entre 0 y 1, un factor que suma la poblacion, un CV consistente).
#
# Todas las funciones reciben la ENTRADA que se envio al servicio, la SALIDA que
# devolvio, y opcionalmente la salida de REFERENCIA (fixtures/) para comparar con
# tolerancia. Devuelven una lista de mensajes de error; lista vacia = todo bien.

import json
from collections import Counter
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from contrato import esquemas

RAIZ = Path(__file__).resolve().parent.parent
FIXTURES = RAIZ / "fixtures"

COLUMNAS_ESPERADAS = [
    "id_persona", "id_hogar", "departamento", "area", "sexo",
    "edad", "ocupado", "ingreso", "factor_expansion",
]
DEPARTAMENTOS = ["Antioquia", "Bogota", "Narino", "Santander", "Valle"]
TOLERANCIA_CALIBRACION = 0.005      # 0.5 % de diferencia permitida contra la poblacion objetivo
TOLERANCIA_TASA = 0.01              # +/- 1 punto porcentual contra la referencia
TOLERANCIA_INGRESO_REL = 0.02       # +/- 2 % relativo contra la referencia
TOLERANCIA_CV_REL = 0.20            # +/- 20 % relativo contra la referencia
UMBRAL_CV_BUENA = 7.5               # CV <= 7.5 %  -> "buena"
UMBRAL_CV_ACEPTABLE = 15.0          # CV <= 15 %   -> "aceptable"; mayor -> "poco confiable"


def cargar_fixture(nombre: str) -> dict:
    """Lee un archivo JSON de la carpeta fixtures/."""
    with open(FIXTURES / nombre, encoding="utf-8") as f:
        return json.load(f)


def _validar_estructura(numero: int, salida: dict) -> list[str]:
    modelo = esquemas.SALIDAS[numero]
    try:
        modelo.model_validate(salida)
    except ValidationError as e:
        # Mostramos solo los primeros errores para no inundar la pantalla
        errores = e.errors()[:5]
        return ["[estructura] " + " -> ".join(str(p) for p in err["loc"]) + f": {err['msg']}" for err in errores]
    return []


def _clave_dominio(ind: dict) -> tuple:
    return (ind["indicador"], tuple(sorted(ind["desagregacion"].items())))


# ---------------------------------------------------------------------------
# Etapa 1 — validar
# ---------------------------------------------------------------------------
def validar_etapa_1(entrada: dict, salida: dict, referencia: dict | None = None) -> list[str]:
    errores = _validar_estructura(1, salida)
    if errores:
        return errores
    reg = salida["registros"]
    res = salida["resumen"]
    if res["n_filas"] != len(reg):
        errores.append(f"resumen.n_filas ({res['n_filas']}) no coincide con el numero de registros ({len(reg)})")
    if len(reg) != len(entrada["registros"]):
        errores.append("La etapa 1 no debe eliminar filas: eso es tarea de la etapa 2")
    if res["columnas"] != COLUMNAS_ESPERADAS:
        errores.append(f"resumen.columnas debe ser exactamente {COLUMNAS_ESPERADAS}")
    for col in COLUMNAS_ESPERADAS:
        if col not in res["n_nulos_por_columna"]:
            errores.append(f"resumen.n_nulos_por_columna no reporta la columna '{col}'")
            break
    malos = [r["id_persona"] for r in reg if r["departamento"] not in DEPARTAMENTOS]
    if malos:
        errores.append(f"Departamentos fuera de catalogo en {len(malos)} registros (ej. id_persona={malos[0]})")
    if any(r["sexo"] not in ("H", "M") for r in reg):
        errores.append("sexo debe ser 'H' o 'M'")
    if any(r["area"] not in ("Urbana", "Rural") for r in reg):
        errores.append("area debe ser 'Urbana' o 'Rural'")
    sin_ocup = sum(1 for r in reg if r["edad"] >= 15 and r["ocupado"] is None)
    if sin_ocup:
        errores.append(f"{sin_ocup} personas de 15 anos o mas sin dato de 'ocupado'")
    return errores


# ---------------------------------------------------------------------------
# Etapa 2 — limpiar
# ---------------------------------------------------------------------------
def validar_etapa_2(entrada: dict, salida: dict, referencia: dict | None = None) -> list[str]:
    errores = _validar_estructura(2, salida)
    if errores:
        return errores
    reg = salida["registros"]
    res = salida["resumen"]
    n_in = len(entrada["registros"])
    ids_in = Counter(r["id_persona"] for r in entrada["registros"])
    dup_esperados = sum(c - 1 for c in ids_in.values())

    if res["n_entrada"] != n_in:
        errores.append(f"resumen.n_entrada ({res['n_entrada']}) no coincide con las filas recibidas ({n_in})")
    if res["n_duplicados_eliminados"] != dup_esperados:
        errores.append(f"Se esperaba eliminar {dup_esperados} duplicados, se reportaron {res['n_duplicados_eliminados']}")
    if res["n_salida"] != len(reg):
        errores.append("resumen.n_salida no coincide con el numero de registros devueltos")
    if len(reg) != n_in - dup_esperados:
        errores.append(f"Deberian quedar {n_in - dup_esperados} registros y quedaron {len(reg)}")
    ids_out = Counter(r["id_persona"] for r in reg)
    if any(c > 1 for c in ids_out.values()):
        errores.append("Todavia hay id_persona repetidos en la salida")
    sin_ingreso = sum(1 for r in reg if r["ocupado"] == 1 and r["ingreso"] is None)
    if sin_ingreso:
        errores.append(f"{sin_ingreso} ocupados siguen sin ingreso: falta imputar")
    n_imp = sum(1 for r in reg if r["ingreso_imputado"])
    if res["n_imputados"] != n_imp:
        errores.append(f"resumen.n_imputados ({res['n_imputados']}) no coincide con las marcas ingreso_imputado ({n_imp})")
    if not (1 <= res["n_atipicos_ajustados"] <= 30):
        errores.append(f"n_atipicos_ajustados={res['n_atipicos_ajustados']} es implausible (se esperan unos pocos)")
    max_ing = max((r["ingreso"] for r in reg if r["ingreso"] is not None), default=0)
    if max_ing > 20_000_000:
        errores.append(f"Persiste un ingreso atipico de {max_ing:,.0f}: el tratamiento de atipicos no funciono")
    if not res["metodo_imputacion"].strip():
        errores.append("metodo_imputacion no puede ir vacio: documenta lo que hiciste")
    return errores


# ---------------------------------------------------------------------------
# Etapa 3 — calibrar
# ---------------------------------------------------------------------------
def validar_etapa_3(entrada: dict, salida: dict, referencia: dict | None = None) -> list[str]:
    errores = _validar_estructura(3, salida)
    if errores:
        return errores
    reg = salida["registros"]
    res = salida["resumen"]
    objetivo = json.loads((RAIZ / "contrato" / "poblacion_objetivo.json").read_text(encoding="utf-8"))

    if len(reg) != len(entrada["registros"]):
        errores.append("La calibracion no debe cambiar el numero de registros")
    sumas: dict[str, float] = {}
    for r in reg:
        sumas[r["departamento"]] = sumas.get(r["departamento"], 0.0) + r["factor_calibrado"]
    for dpto, pob in objetivo.items():
        if dpto not in sumas:
            errores.append(f"No hay registros calibrados para {dpto}")
            continue
        if abs(sumas[dpto] - pob) / pob > TOLERANCIA_CALIBRACION:
            errores.append(f"{dpto}: la suma de factor_calibrado ({sumas[dpto]:,.0f}) no llega a la poblacion objetivo ({pob:,})")
        reportado = res["totales_por_departamento"].get(dpto)
        if reportado is None or abs(reportado - sumas[dpto]) > 1:
            errores.append(f"resumen.totales_por_departamento[{dpto}] no coincide con lo que suman los registros")
    if res["poblacion_objetivo"] != {k: float(v) for k, v in objetivo.items()}:
        errores.append("resumen.poblacion_objetivo debe copiar contrato/poblacion_objetivo.json")
    return errores


# ---------------------------------------------------------------------------
# Etapa 4 — indicadores
# ---------------------------------------------------------------------------
def validar_etapa_4(entrada: dict, salida: dict, referencia: dict | None = None) -> list[str]:
    errores = _validar_estructura(4, salida)
    if errores:
        return errores
    ind = salida["indicadores"]
    if len(salida["registros"]) != len(entrada["registros"]):
        errores.append("Los registros deben pasar intactos a la etapa 5 (ella necesita el microdato)")
    tasas = [i for i in ind if i["indicador"] == "tasa_ocupacion"]
    ingresos = [i for i in ind if i["indicador"] == "ingreso_promedio"]
    if len(tasas) != 10:
        errores.append(f"tasa_ocupacion debe tener 10 dominios (5 departamentos x 2 sexos), hay {len(tasas)}")
    if len(ingresos) != 2:
        errores.append(f"ingreso_promedio debe tener 2 dominios (Urbana, Rural), hay {len(ingresos)}")
    for t in tasas:
        if not (0 <= t["valor"] <= 1):
            errores.append(f"Tasa fuera de [0,1] en {t['desagregacion']}: {t['valor']}")
            break
    for i in ingresos:
        if i["valor"] <= 0:
            errores.append(f"Ingreso promedio no positivo en {i['desagregacion']}")
    if referencia:
        ref = {_clave_dominio(i): i for i in referencia["indicadores"]}
        for i in ind:
            r = ref.get(_clave_dominio(i))
            if r is None:
                errores.append(f"Dominio inesperado: {i['indicador']} {i['desagregacion']}")
                continue
            if i["indicador"] == "tasa_ocupacion" and abs(i["valor"] - r["valor"]) > TOLERANCIA_TASA:
                errores.append(f"tasa_ocupacion {i['desagregacion']}: {i['valor']:.3f} se aleja de la referencia {r['valor']:.3f}")
            if i["indicador"] == "ingreso_promedio" and abs(i["valor"] - r["valor"]) / r["valor"] > TOLERANCIA_INGRESO_REL:
                errores.append(f"ingreso_promedio {i['desagregacion']}: {i['valor']:,.0f} se aleja de la referencia {r['valor']:,.0f}")
    return errores


# ---------------------------------------------------------------------------
# Etapa 5 — precision
# ---------------------------------------------------------------------------
def validar_etapa_5(entrada: dict, salida: dict, referencia: dict | None = None) -> list[str]:
    errores = _validar_estructura(5, salida)
    if errores:
        return errores
    ind = salida["indicadores"]
    if len(ind) != len(entrada["indicadores"]):
        errores.append(f"Deben salir los mismos {len(entrada['indicadores'])} indicadores que entraron")
    for i in ind:
        if not (i["limite_inferior"] <= i["valor"] <= i["limite_superior"]):
            errores.append(f"El valor no esta dentro de su intervalo en {i['indicador']} {i['desagregacion']}")
            break
        if i["error_estandar"] <= 0:
            errores.append(f"error_estandar debe ser positivo en {i['desagregacion']}")
            break
        cv_calc = 100 * i["error_estandar"] / i["valor"] if i["valor"] else None
        if cv_calc is not None and abs(cv_calc - i["cv"]) > 0.05:
            errores.append(f"cv debe ser 100*error_estandar/valor (en porcentaje). En {i['desagregacion']} no cuadra")
            break
    if referencia:
        ref = {_clave_dominio(i): i for i in referencia["indicadores"]}
        for i in ind:
            r = ref.get(_clave_dominio(i))
            if r and r["cv"] > 0 and abs(i["cv"] - r["cv"]) / r["cv"] > TOLERANCIA_CV_REL:
                errores.append(f"cv de {i['indicador']} {i['desagregacion']} ({i['cv']:.2f}) se aleja de la referencia ({r['cv']:.2f})")
                break
    return errores


# ---------------------------------------------------------------------------
# Etapa 6 — publicar
# ---------------------------------------------------------------------------
def clasificar_calidad(cv: float) -> str:
    if cv <= UMBRAL_CV_BUENA:
        return "buena"
    if cv <= UMBRAL_CV_ACEPTABLE:
        return "aceptable"
    return "poco confiable"


def validar_etapa_6(entrada: dict, salida: dict, referencia: dict | None = None) -> list[str]:
    errores = _validar_estructura(6, salida)
    if errores:
        return errores
    tab = salida["tabulados"]
    meta = salida["metadatos"]
    if len(tab) != len(entrada["indicadores"]):
        errores.append("El tabulado debe contener todos los indicadores recibidos")
    if meta["n_indicadores"] != len(tab):
        errores.append("metadatos.n_indicadores no coincide con el numero de tabulados")
    for t in tab:
        esperada = clasificar_calidad(t["cv"])
        if t["calidad"] != esperada:
            errores.append(f"calidad='{t['calidad']}' pero con cv={t['cv']:.2f} deberia ser '{esperada}'")
            break
    try:
        date.fromisoformat(meta["fecha_proceso"])
    except ValueError:
        errores.append("metadatos.fecha_proceso debe estar en formato ISO (AAAA-MM-DD)")
    if not salida["archivo_excel"].lower().endswith(".xlsx"):
        errores.append("archivo_excel debe apuntar a un archivo .xlsx")
    if len(meta["nota_metodologica"]) < 40:
        errores.append("La nota metodologica es demasiado corta: explica como se clasifico la calidad")
    return errores


VALIDADORES = {
    1: validar_etapa_1, 2: validar_etapa_2, 3: validar_etapa_3,
    4: validar_etapa_4, 5: validar_etapa_5, 6: validar_etapa_6,
}


def validar(numero: int, entrada: dict, salida: dict, usar_referencia: bool = True) -> list[str]:
    """Punto de entrada unico: valida la salida de la etapa `numero`."""
    referencia = None
    if usar_referencia:
        ruta = FIXTURES / f"etapa_{numero}_salida.json"
        if ruta.exists():
            referencia = cargar_fixture(ruta.name)
    return VALIDADORES[numero](entrada, salida, referencia)
