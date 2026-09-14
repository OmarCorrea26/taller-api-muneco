# contrato/esquemas.py
# Esquemas Pydantic de ENTRADA y SALIDA de cada etapa.
# Un esquema es la "forma" exacta del JSON que viaja entre servicios: que campos tiene,
# de que tipo son y cuales pueden ser nulos. Si tu servicio devuelve algo con otra forma,
# el ensamblador lo detecta y tu parte del muneco sale chueca.

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Base(BaseModel):
    # extra="forbid": si aparece un campo que no esta declarado, es error.
    # Esto obliga a que el contrato sea explicito.
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Registros (una fila de la encuesta) en sus distintas versiones
# ---------------------------------------------------------------------------

class RegistroCrudo(Base):
    """Fila tal como llega del CSV. Todo puede venir nulo o mal tipado."""
    model_config = ConfigDict(extra="allow")   # el CSV crudo puede traer columnas de mas
    id_persona: Optional[int] = None
    id_hogar: Optional[int] = None
    departamento: Optional[str] = None
    area: Optional[str] = None
    sexo: Optional[str] = None
    edad: Optional[int] = None
    ocupado: Optional[int] = None
    ingreso: Optional[float] = None
    factor_expansion: Optional[float] = None


class RegistroValidado(Base):
    """Salida de la etapa 1: tipos garantizados, nulos solo donde tienen sentido."""
    id_persona: int
    id_hogar: int
    departamento: str
    area: str
    sexo: str
    edad: int = Field(ge=0, le=120)
    ocupado: Optional[int] = Field(default=None, ge=0, le=1)
    ingreso: Optional[float] = Field(default=None, ge=0)
    factor_expansion: float = Field(gt=0)


class RegistroLimpio(RegistroValidado):
    """Salida de la etapa 2: sin duplicados, ingreso completo en ocupados, con marca de imputacion."""
    ingreso_imputado: bool


class RegistroCalibrado(RegistroLimpio):
    """Salida de la etapa 3: agrega el factor calibrado."""
    factor_calibrado: float = Field(gt=0)


# ---------------------------------------------------------------------------
# Resumenes y estructuras auxiliares
# ---------------------------------------------------------------------------

class ResumenValidacion(Base):
    n_filas: int
    columnas: list[str]
    n_nulos_por_columna: dict[str, int]


class ResumenLimpieza(Base):
    n_entrada: int
    n_duplicados_eliminados: int
    n_salida: int
    n_imputados: int
    n_atipicos_ajustados: int
    metodo_imputacion: str


class ResumenCalibracion(Base):
    totales_por_departamento: dict[str, float]
    poblacion_objetivo: dict[str, float]


class Indicador(Base):
    """Una estimacion puntual para un dominio (combinacion de desagregaciones)."""
    indicador: str                      # "tasa_ocupacion" | "ingreso_promedio"
    desagregacion: dict[str, str]       # p.ej. {"departamento": "Bogota", "sexo": "H"}
    valor: float
    n_muestra: int = Field(gt=0)
    poblacion_estimada: float = Field(gt=0)


class IndicadorConPrecision(Indicador):
    error_estandar: float = Field(ge=0)
    cv: float = Field(ge=0)             # coeficiente de variacion en PORCENTAJE
    limite_inferior: float
    limite_superior: float


class IndicadorPublicado(IndicadorConPrecision):
    calidad: str                        # "buena" | "aceptable" | "poco confiable"


class Metadatos(Base):
    titulo: str
    fuente: str
    fecha_proceso: str                  # ISO 8601, p.ej. "2026-09-10"
    n_indicadores: int
    nota_metodologica: str


# ---------------------------------------------------------------------------
# Entradas y salidas de cada etapa
# ---------------------------------------------------------------------------

class Entrada1(Base):
    registros: list[RegistroCrudo]

class Salida1(Base):
    registros: list[RegistroValidado]
    resumen: ResumenValidacion

Entrada2 = Salida1

class Salida2(Base):
    registros: list[RegistroLimpio]
    resumen: ResumenLimpieza

Entrada3 = Salida2

class Salida3(Base):
    registros: list[RegistroCalibrado]
    resumen: ResumenCalibracion

Entrada4 = Salida3

class Salida4(Base):
    registros: list[RegistroCalibrado]
    indicadores: list[Indicador]

Entrada5 = Salida4

class Salida5(Base):
    indicadores: list[IndicadorConPrecision]

Entrada6 = Salida5

class Salida6(Base):
    metadatos: Metadatos
    tabulados: list[IndicadorPublicado]
    archivo_excel: str


ENTRADAS = {1: Entrada1, 2: Entrada2, 3: Entrada3, 4: Entrada4, 5: Entrada5, 6: Entrada6}
SALIDAS = {1: Salida1, 2: Salida2, 3: Salida3, 4: Salida4, 5: Salida5, 6: Salida6}
