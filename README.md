# Taller: APIs con FastAPI y trabajo colaborativo en GitHub

> **Ejercicio de formación.** Los datos son sintéticos y el proyecto es ficticio. No corresponde a ningún producto ni operación estadística oficial.

Un proceso estadístico dividido en seis etapas, un servicio HTTP por persona y un muñeco que solo queda
completo cuando las seis cumplen el contrato. Es material para aprender a trabajar en equipo con Git y
APIs: ramas, Pull Requests, revisión de código, integración continua y rebase, sobre un problema que se
parece al trabajo real de un equipo de estadística.

> [!NOTE]
> **Los errores que veas en el historial son parte del ejercicio.** Los Pull Requests con errores, los
> checks en rojo y los conflictos de rebase están puestos a propósito: son justo lo que el taller enseña
> a resolver. Incluso hay un cambio de contrato planeado a mitad del taller para que aparezcan.

---

## Si llegas de afuera

### Qué aprendes

| Tema | Qué haces en el taller |
|------|------------------------|
| APIs con FastAPI | Expones una etapa del proceso como servicio HTTP, con validación de tipos (Pydantic) y documentación automática |
| Pruebas de contrato | Tu servicio se verifica contra un contrato explícito de entrada y salida, igual en tu máquina que en CI |
| Integración continua | GitHub Actions corre `pytest` en cada Pull Request |
| Git en equipo | Rama propia, commits con convención, Pull Request, revisión de un compañero y rebase cuando `main` cambia |

### Qué necesitas saber antes

- Python con funciones y `pandas` básico: `groupby`, `merge`, filtros, `fillna`, `drop_duplicates`.
- Entornos virtuales e instalación con `pip install -r requirements.txt`.
- Git básico: `add`, `commit`, `push` y qué es `origin`.
- Python 3.11 o superior y una cuenta de GitHub.

No necesitas experiencia previa con APIs ni con Git colaborativo: eso es lo que enseña el taller.

### Cuánto toma

| Módulo | Tiempo aproximado |
|--------|-------------------|
| 0. Preparar el entorno y ver el muñeco vacío | 30 min |
| 1. Qué es una API y cómo se construye con FastAPI | 2 h |
| 2. Implementar una etapa hasta que cumpla el contrato | 3 a 5 h |
| 3. Git colaborativo: Pull Request, revisión y rebase | 3 h, repartidas en varios días |
| 4. Ensamble final | 1 h |

En total, unas 10 a 12 horas de trabajo por persona. El módulo 3 depende del ritmo del equipo, así que
en calendario suele tomar varias semanas.

### Cómo usarlo

- **En equipo (recomendado):** haz un fork, invita a tus compañeros como colaboradores y asigna una etapa
  a cada persona. En tu fork, activa GitHub Actions desde la pestaña *Actions*: GitHub lo desactiva por
  defecto en los forks.
- **Solo:** clona el repositorio e implementa tú las seis etapas. Te pierdes la revisión y los conflictos,
  pero el contrato, las pruebas y el muñeco funcionan igual.

### Primeros pasos

```powershell
git clone https://github.com/OmarCorrea26/taller-api-muneco.git
cd taller-api-muneco
python -m venv .venv
.venv\Scripts\activate            # macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest                            # deben salir 6 "skipped": nada implementado todavía, ningún error
uvicorn ensamblador.app:app --port 8000
```

Abre http://localhost:8000: vas a ver el muñeco con sus seis partes punteadas. Ese es el punto de partida.

### Cómo funciona

Cada etapa es un servicio FastAPI que recibe JSON, hace su parte del proceso y devuelve JSON. Un
**ensamblador** llama a las seis, valida que cumplan el contrato y dibuja el muñeco: cada etapa es una
parte del cuerpo.

| Estado de la parte | Significado |
|--------------------|-------------|
| Punteada | La etapa no responde o todavía no está implementada |
| Amarilla y torcida | Responde, pero lo que devuelve no cumple el contrato |
| Verde y derecha | Cumple el contrato |

| # | Etapa | Qué hace | Parte del muñeco | Puerto |
|---|-------|----------|------------------|--------|
| 1 | validar | Verifica columnas y tipos, cuenta nulos | cabeza | 8001 |
| 2 | limpiar | Elimina duplicados, trata atípicos, imputa ingresos faltantes | torso | 8002 |
| 3 | calibrar | Ajusta los factores de expansión a totales poblacionales conocidos | brazo izquierdo | 8003 |
| 4 | indicadores | Estima tasa de ocupación e ingreso promedio, ponderados | brazo derecho | 8004 |
| 5 | precision | Error estándar, coeficiente de variación e intervalos de confianza | pierna izquierda | 8005 |
| 6 | publicar | Clasifica la calidad de cada estimación y exporta a Excel | pierna derecha | 8006 |

```
contrato/        Esquemas (Pydantic), reglas de validación y registro de etapas. NO se toca sin PR de contrato.
datos/           Generador de la encuesta sintética.
fixtures/        Entrada y salida de referencia de cada etapa. Con esto se prueba cada etapa por separado.
etapas/          Una carpeta por etapa. Cada quien edita SOLO la suya.
ensamblador/     La app que dibuja el muñeco y el probador de terminal.
tests/           Pruebas de contrato que corre GitHub Actions en cada PR.
scripts/         Utilidades para levantar todo.
apendice_r/      La misma etapa implementada en R con plumber.
```

---

## Para el equipo del taller

La guía paso a paso (módulos 0 a 4, con checkpoints y troubleshooting) es el documento
`Taller_2_APIs_y_Git_Colaborativo.docx` que recibiste. Esta sección es el resumen operativo.

### Asignaciones

| # | Etapa | Parte del muñeco | Responsable |
|---|-------|------------------|-------------|
| 1 | validar | cabeza | Jessika |
| 2 | limpiar | torso | Alejandra |
| 3 | calibrar | brazo izquierdo | |
| 4 | indicadores | brazo derecho | |
| 5 | precision | pierna izquierda | |
| 6 | publicar | pierna derecha | |

### Puesta en marcha

Los mismos comandos de [Primeros pasos](#primeros-pasos), clonando este repositorio (no un fork).

### Ciclo de trabajo de cada etapa

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

Luego abres un Pull Request en GitHub, pides revisión a un compañero y esperas el check verde de
GitHub Actions. Solo el facilitador mezcla a `main`.

### Reglas

- **`main` está protegida:** no acepta push directo. Todo entra por Pull Request con 1 aprobación y el
  check `pytest` en verde.
- **Ramas:** `feature/etapa-N-nombre-tunombre`. Una rama por etapa, nunca trabajar directo en `main`.
- **Commits:** `tipo(alcance): descripción en imperativo`. Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
- **Alcance:** solo tocas `etapas/etapa_N_.../`. Cambios a `contrato/` van en un PR aparte etiquetado
  `contrato` y los revisa todo el equipo.
- **Antes de abrir PR:** rebase sobre `origin/main`, `probar` en OK, `pytest` en verde.
- **Revisión:** quien revisa clona la rama, corre `probar`, lee el código y comenta. Aprobar no es un trámite.

### Ver el muñeco completo

```powershell
.\scripts\levantar_todo.ps1      # Windows (abre 7 ventanas y el navegador)
bash scripts/levantar_todo.sh    # macOS / Linux
```

Abre http://localhost:8000.

---

## Licencia

El código se publica bajo licencia [MIT](LICENSE): puedes usarlo, adaptarlo y compartirlo, conservando el
aviso de copyright.
