# Taller 2 — APIs con FastAPI y trabajo colaborativo en GitHub

Proyecto ficticio de procesamiento estadístico de una encuesta de hogares, dividido en seis
etapas. Cada participante implementa una etapa como un servicio HTTP (FastAPI). Un
**ensamblador** llama a las seis etapas, valida que cumplan el contrato y dibuja un muñeco:
cada etapa es una parte del cuerpo. Si una etapa no responde, falta esa parte; si responde
pero rompe el contrato, sale chueca.

La guía completa (paso a paso, con checkpoints y troubleshooting) está en el documento
`Taller_2_APIs_y_Git_Colaborativo.docx`. Este README es el resumen operativo.

## Etapas y responsables

| # | Etapa | Parte del muñeco | Puerto | Responsable |
|---|-------|------------------|--------|-------------|
| 1 | validar | cabeza | 8001 | |
| 2 | limpiar | torso | 8002 | |
| 3 | calibrar | brazo izquierdo | 8003 | |
| 4 | indicadores | brazo derecho | 8004 | |
| 5 | precision | pierna izquierda | 8005 | |
| 6 | publicar | pierna derecha | 8006 | |

## Estructura

```
contrato/        Esquemas (Pydantic), reglas de validación y registro de etapas. NO se toca sin PR de contrato.
datos/           Generador de la encuesta sintética.
fixtures/        Entrada y salida de referencia de cada etapa. Con esto se prueba cada etapa por separado.
etapas/          Una carpeta por etapa. Cada quien edita SOLO la suya.
ensamblador/     La app que dibuja el muñeco y el probador de terminal.
tests/           Pruebas de contrato que corre GitHub Actions en cada PR.
scripts/         Utilidades para levantar todo.
```

## Puesta en marcha (una sola vez)

```powershell
git clone https://github.com/OmarCorrea26/taller-api-muneco.git
cd taller-api-muneco
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest          # deben salir 6 "skipped": nada implementado todavía, ningún error
```

## Ciclo de trabajo de cada etapa

```powershell
git switch main
git pull
git switch -c feature/etapa-3-calibrar-tu-nombre    # tu rama
# ... editas etapas/etapa_3_calibrar/app.py ...
uvicorn etapas.etapa_3_calibrar.app:app --port 8003 --reload   # terminal 1
python -m ensamblador.probar --etapa 3                         # terminal 2
pytest -k etapa_3
git add etapas/etapa_3_calibrar/app.py
git commit -m "feat(etapa-3): calibración por departamento"
git fetch origin
git rebase origin/main
git push -u origin feature/etapa-3-calibrar-tu-nombre
```

Luego abres un Pull Request en GitHub, pides revisión a un compañero y esperas el check verde
de GitHub Actions. Solo el facilitador mezcla a `main`.

## Convenciones

- **Ramas:** `feature/etapa-N-nombre-tunombre`. Una rama por etapa, nunca trabajar directo en `main`.
- **Commits:** `tipo(alcance): descripción en imperativo`. Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
- **Alcance:** solo tocas `etapas/etapa_N_.../`. Cambios a `contrato/` van en un PR aparte etiquetado `contrato` y los revisa todo el equipo.
- **Antes de abrir PR:** rebase sobre `origin/main`, `probar` en OK, `pytest` en verde.
- **Revisión:** quien revisa clona la rama, corre `probar`, lee el código y comenta. Aprobar no es un trámite.

## Ver el muñeco completo

```powershell
.\scripts\levantar_todo.ps1      # Windows (abre 7 ventanas y el navegador)
bash scripts/levantar_todo.sh    # macOS / Linux
```

Abre http://localhost:8000.
