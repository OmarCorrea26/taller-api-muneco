# tests/test_contrato.py
# Pruebas de contrato: llaman a procesar() de cada etapa directamente (sin HTTP) con el
# fixture de entrada y validan la salida. Es lo mismo que hace el ensamblador, pero en pytest,
# para que GitHub Actions lo corra en cada Pull Request.
#
#   pytest                       -> todas las etapas
#   pytest -k etapa_3            -> solo la 3

import importlib

import pytest

from contrato.etapas import ETAPAS
from contrato.validaciones import cargar_fixture, validar


@pytest.mark.parametrize("defi", ETAPAS, ids=[f"etapa_{e['numero']}_{e['nombre']}" for e in ETAPAS])
def test_etapa_cumple_contrato(defi):
    n = defi["numero"]
    modulo = importlib.import_module(f"etapas.etapa_{n}_{defi['nombre']}.app")
    entrada = cargar_fixture(f"etapa_{n}_entrada.json")
    try:
        salida = modulo.procesar(entrada)
    except NotImplementedError:
        pytest.skip(f"Etapa {n} aun no implementada")
    errores = validar(n, entrada, salida)
    assert not errores, "\n".join(errores)
