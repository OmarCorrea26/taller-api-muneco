#!/usr/bin/env bash
# Version macOS/Linux de levantar_todo.ps1 (procesos en segundo plano en la misma terminal).
# Ejecutar desde la raiz del repo:  bash scripts/levantar_todo.sh
source .venv/bin/activate
for spec in "1 validar" "2 limpiar" "3 calibrar" "4 indicadores" "5 precision" "6 publicar"; do
  set -- $spec
  uvicorn "etapas.etapa_$1_$2.app:app" --port "800$1" &
done
uvicorn ensamblador.app:app --port 8000 &
wait
