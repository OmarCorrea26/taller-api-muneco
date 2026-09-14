# ensamblador/app.py
# El ensamblador: consulta las seis etapas, valida sus respuestas y dibuja el muneco.
#
#   uvicorn ensamblador.app:app --port 8000
#   abrir http://localhost:8000
#
# Rutas:
#   GET /          pagina con el muneco (se actualiza sola cada 10 segundos)
#   GET /estado    el mismo diagnostico en JSON, por si lo quieres consumir desde otro lado

from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from contrato.etapas import ETAPAS
from ensamblador.verificar import verificar_etapa

app = FastAPI(title="Ensamblador del muneco", version="1.0.0")

COLOR = {"ok": "#3CB371", "chueco": "#E6B422", "ausente": "none"}
BORDE = {"ok": "#1F6E43", "chueco": "#9C7A00", "ausente": "#C8C8C8"}

# Geometria de cada parte: (x, y, ancho, alto, angulo de giro cuando esta chueca)
PARTES = {
    "cabeza":           dict(cx=200, cy=70, r=45),
    "torso":            dict(x=150, y=125, w=100, h=140, ang=8),
    "brazo_izquierdo":  dict(x=90,  y=130, w=50, h=140, ang=30),
    "brazo_derecho":    dict(x=260, y=130, w=50, h=140, ang=-30),
    "pierna_izquierda": dict(x=152, y=275, w=42, h=150, ang=22),
    "pierna_derecha":   dict(x=206, y=275, w=42, h=150, ang=-22),
}


def diagnosticar() -> list[dict]:
    with ThreadPoolExecutor(max_workers=6) as pool:
        return list(pool.map(lambda e: verificar_etapa(e["numero"]), ETAPAS))


def _cara(cx: int, cy: int, estado: str) -> str:
    """Ojos y boca: sonrie si esta ok, boca recta si esta chueco."""
    boca_y = cy + 30 if estado == "ok" else cy + 12
    return (f'<circle cx="{cx-15}" cy="{cy-8}" r="5" fill="#222"/>'
            f'<circle cx="{cx+15}" cy="{cy-8}" r="5" fill="#222"/>'
            f'<path d="M {cx-18} {cy+12} Q {cx} {boca_y} {cx+18} {cy+12}" stroke="#222" stroke-width="3" fill="none"/>')


def _svg_parte(parte: str, estado: str) -> str:
    g = PARTES[parte]
    fill, stroke = COLOR[estado], BORDE[estado]
    dash = ' stroke-dasharray="6 6"' if estado == "ausente" else ""
    if parte == "cabeza":
        ang = 25 if estado == "chueco" else 0
        return (f'<g transform="rotate({ang} {g["cx"]} {g["cy"]})">'
                f'<circle cx="{g["cx"]}" cy="{g["cy"]}" r="{g["r"]}" fill="{fill}" stroke="{stroke}" stroke-width="4"{dash}/>'
                + (_cara(g["cx"], g["cy"], estado) if estado != "ausente" else "")
                + "</g>")
    ang = g["ang"] if estado == "chueco" else 0
    # Giramos alrededor del punto de union con el cuerpo (arriba del rectangulo)
    px, py = g["x"] + g["w"] / 2, g["y"]
    return (f'<g transform="rotate({ang} {px} {py})">'
            f'<rect x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="4"{dash}/>'
            "</g>")


def render_html(resultados: list[dict]) -> str:
    partes = "".join(_svg_parte(r["parte"], r["estado"]) for r in resultados)
    n_ok = sum(r["estado"] == "ok" for r in resultados)
    filas = "".join(
        f'<tr class="{r["estado"]}"><td>{r["numero"]}</td><td>{r["nombre"]}</td><td>{r["parte"].replace("_", " ")}</td>'
        f'<td><b>{r["estado"].upper()}</b></td><td>{"<br>".join(r["detalle"])}</td></tr>'
        for r in resultados
    )
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="10"><title>Ensamblador — {n_ok}/6</title>
<style>
 body{{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#222;background:#fafafa}}
 .fila{{display:flex;gap:32px;align-items:flex-start;flex-wrap:wrap}}
 table{{border-collapse:collapse;font-size:14px;max-width:760px}} td,th{{border:1px solid #ddd;padding:6px 10px;vertical-align:top}}
 tr.ok td{{background:#e9f7ef}} tr.chueco td{{background:#fff8e1}} tr.ausente td{{background:#f3f3f3;color:#777}}
 h1{{margin:0 0 4px}} .sub{{color:#666;margin-bottom:16px}}
</style></head><body>
<h1>El muñeco: {n_ok} de 6 partes en orden</h1>
<div class="sub">Verde = cumple el contrato · Amarillo y torcido = responde pero falla la validación · Punteado = no responde. Se actualiza cada 10 s.</div>
<div class="fila">
<svg width="400" height="440" viewBox="0 0 400 440" xmlns="http://www.w3.org/2000/svg">{partes}</svg>
<table><tr><th>#</th><th>Etapa</th><th>Parte</th><th>Estado</th><th>Detalle</th></tr>{filas}</table>
</div></body></html>"""


@app.get("/estado")
def estado():
    return diagnosticar()


@app.get("/", response_class=HTMLResponse)
def inicio():
    return render_html(diagnosticar())
