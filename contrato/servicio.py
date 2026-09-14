# contrato/servicio.py
# Fabrica de servicios: convierte una funcion `procesar(entrada) -> salida` en una API FastAPI
# con dos rutas estandar. Todas las etapas usan esto, asi que todas se ven iguales desde afuera:
#
#   GET  /salud     -> {"etapa": 3, "nombre": "calibrar", "estado": "ok"}
#   POST /procesar  -> recibe el JSON de entrada y devuelve el JSON de salida
#
# Tu trabajo como responsable de una etapa es escribir `procesar`; el envoltorio HTTP ya esta.

from typing import Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from contrato.etapas import etapa as definicion_etapa


def crear_app(numero: int, procesar: Callable[[dict], dict]) -> FastAPI:
    defi = definicion_etapa(numero)
    app = FastAPI(
        title=f"Etapa {numero} — {defi['nombre']}",
        description=defi["descripcion"],
        version="1.0.0",
    )

    @app.get("/salud")
    def salud():
        return {"etapa": numero, "nombre": defi["nombre"], "estado": "ok"}

    @app.post("/procesar")
    async def procesar_ruta(request: Request):
        entrada = await request.json()
        try:
            salida = procesar(entrada)
        except NotImplementedError as e:
            # 501 = "Not Implemented": el servicio existe pero la logica aun no
            raise HTTPException(status_code=501, detail=str(e))
        except Exception as e:  # noqa: BLE001 - queremos ver cualquier error de la etapa
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
        return JSONResponse(content=salida)

    return app
