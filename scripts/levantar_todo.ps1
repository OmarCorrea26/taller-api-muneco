# scripts/levantar_todo.ps1
# Levanta las seis etapas y el ensamblador, cada uno en su propia ventana de PowerShell.
# Ejecutar desde la raiz del repo con el entorno virtual creado:
#   .\scripts\levantar_todo.ps1

$raiz = (Get-Location).Path
$activar = "$raiz\.venv\Scripts\Activate.ps1"

$etapas = @(
  @{n=1; nombre="validar"},
  @{n=2; nombre="limpiar"},
  @{n=3; nombre="calibrar"},
  @{n=4; nombre="indicadores"},
  @{n=5; nombre="precision"},
  @{n=6; nombre="publicar"}
)

foreach ($e in $etapas) {
  $modulo = "etapas.etapa_$($e.n)_$($e.nombre).app:app"
  $puerto = 8000 + $e.n
  Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$raiz'; & '$activar'; uvicorn $modulo --port $puerto"
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$raiz'; & '$activar'; uvicorn ensamblador.app:app --port 8000"
Start-Sleep -Seconds 3
Start-Process "http://localhost:8000"
