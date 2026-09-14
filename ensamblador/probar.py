# ensamblador/probar.py
# Prueba UNA etapa desde la terminal, sin abrir el navegador.
#
#   python -m ensamblador.probar --etapa 3
#   python -m ensamblador.probar --etapa 3 --url http://localhost:8003
#
# Requiere que el servicio de esa etapa este corriendo (uvicorn) en otra terminal.

import argparse

from ensamblador.verificar import verificar_etapa

ICONOS = {"ok": "[OK]     ", "chueco": "[CHUECO] ", "ausente": "[AUSENTE]"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Prueba una etapa contra el contrato")
    parser.add_argument("--etapa", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--url", default=None, help="URL base del servicio (por defecto localhost:800N)")
    args = parser.parse_args()

    res = verificar_etapa(args.etapa, args.url)
    print(f"{ICONOS[res['estado']]} Etapa {res['numero']} ({res['nombre']}, {res['parte']}) en {res['url']}")
    for linea in res["detalle"]:
        print(f"   - {linea}")
    return 0 if res["estado"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
