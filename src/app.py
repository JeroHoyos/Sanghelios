from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import os
import sqlite3
import uuid
from pathlib import Path

from pydantic import BaseModel

from src.campaign_ai import plan_campaign
from src.tools.write_images import FLYER_TEMPLATES, BloodDonationPoster, create_flyer


def _load_dotenv(path: Path = Path(".env")) -> None:
    """Carga variables de un .env al entorno (uvicorn no lo hace solo)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

_STATIC_ROOT = Path("src/static")
_GENERATED_DIR = _STATIC_ROOT / "generated"
_IMG_DIR = _STATIC_ROOT / "img"
_TEMPLATE_EVENT = str(_IMG_DIR / "event.png")
_TEMPLATE_PERSONAL = str(_IMG_DIR / "personal.png")
_GENERATED_DIR.mkdir(parents=True, exist_ok=True)

_DB_PATH = Path("data/sanghelios.db")


def _query_db(sql: str, params: tuple = ()) -> list[dict]:
    """Consulta de solo lectura contra la BD operativa (SQLite)."""
    con = sqlite3.connect(_DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in con.execute(sql, params).fetchall()]
    finally:
        con.close()

app = FastAPI(
    title="Sanghelios",
    description="Inteligencia Predictiva para Bancos de Sangre",
)

templates = Jinja2Templates(directory="src/templates")


class _NoCacheStatic(StaticFiles):
    """Sirve estáticos forzando revalidación (evita CSS/JS cacheados viejos)."""

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
        return response


app.mount("/static", _NoCacheStatic(directory="src/static"), name="static")


@app.get("/", response_class=HTMLResponse, name="index")
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/sanghelios-informe-eda", response_class=HTMLResponse, name="eda_report")
async def eda_report(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="eda_report.html",
    )


@app.get("/donation", response_class=HTMLResponse, name="donation")
async def donation(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="donation.html",
    )


@app.get("/image_generation", response_class=HTMLResponse, name="image_generation")
async def image_generation(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="image_generation.html",
    )


@app.post("/generate-image")
async def generate_image(
    poster_type: str = Form(...),
    place: str = Form(...),
    time: str = Form(""),
    name: str = Form(""),
    id_number: str = Form(""),
    message: str = Form(""),
):
    filename = f"{uuid.uuid4().hex}.png"
    output_path = str(_GENERATED_DIR / filename)

    if poster_type == "event":
        BloodDonationPoster.create_event(
            place=place,
            time=time,
            output_path=output_path,
            template_path=_TEMPLATE_EVENT,
        )
    else:
        BloodDonationPoster.create_personal(
            name=name,
            id_number=id_number,
            place=place,
            message=message,
            output_path=output_path,
            template_path=_TEMPLATE_PERSONAL,
        )

    return JSONResponse({"url": f"/static/generated/{filename}", "type": poster_type})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "active_view": "dashboard",
        },
    )


@app.get("/mapa", response_class=HTMLResponse)
async def mapa(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="map.html",
        context={
            "request": request,
            "active_view": "mapa",
        },
    )


@app.get("/campana", response_class=HTMLResponse)
async def campana(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="campain.html",
        context={
            "request": request,
            "active_view": "publicidad",
        },
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "request": request,
            "active_view": "about",
        },
    )


# ── API de datos operativos (leída por el dashboard) ─────────────────────────
def _require_db() -> JSONResponse | None:
    if not _DB_PATH.exists():
        return JSONResponse(
            {"error": "Base de datos no generada. Ejecuta scripts/build_db_and_model.py"},
            status_code=503,
        )
    return None


@app.get("/api/serie-diaria")
async def api_serie_diaria(desde: str | None = None, hasta: str | None = None):
    if (err := _require_db()) is not None:
        return err
    sql = "SELECT * FROM serie_diaria"
    clauses: list[str] = []
    params: list[str] = []
    if desde:
        clauses.append("fecha >= ?")
        params.append(desde)
    if hasta:
        clauses.append("fecha <= ?")
        params.append(hasta)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY fecha"
    return JSONResponse(_query_db(sql, tuple(params)))


@app.get("/api/stock")
async def api_stock():
    if (err := _require_db()) is not None:
        return err
    return JSONResponse(_query_db("SELECT * FROM stock ORDER BY unidades DESC"))


@app.get("/api/campanas")
async def api_campanas():
    if (err := _require_db()) is not None:
        return err
    return JSONResponse(_query_db("SELECT * FROM campanas ORDER BY fecha"))


class CampanaNueva(BaseModel):
    comuna: str
    titulo: str
    fecha: str
    tipo: str = "Todos"
    estado: str = "desplegada"
    flyer: str = ""


@app.post("/api/campanas")
async def crear_campana(c: CampanaNueva):
    """Registra una campaña (creada desde el asistente) para que aparezca en el mapa."""
    if (err := _require_db()) is not None:
        return err
    con = sqlite3.connect(_DB_PATH)
    try:
        for columna in ("tipo", "flyer"):
            try:
                con.execute(f"ALTER TABLE campanas ADD COLUMN {columna} TEXT")
            except sqlite3.OperationalError:
                pass  # la columna ya existe
        con.execute(
            "INSERT INTO campanas (fecha, comuna, titulo, estado, tipo, flyer) VALUES (?, ?, ?, ?, ?, ?)",
            (c.fecha, c.comuna, c.titulo, c.estado, c.tipo, c.flyer),
        )
        con.commit()
    finally:
        con.close()
    return JSONResponse({"ok": True, **c.model_dump()})


@app.get("/api/meta")
async def api_meta():
    if (err := _require_db()) is not None:
        return err
    return JSONResponse({r["clave"]: r["valor"] for r in _query_db("SELECT clave, valor FROM meta")})


class CampanaContexto(BaseModel):
    comuna: str = "Medellín"
    tipo: str = "O-"
    fecha: str = ""
    objetivo: str = ""
    tono: str = "cercano y urgente"


@app.post("/api/asistente-campana")
async def asistente_campana(ctx: CampanaContexto):
    """Propuesta de publicidad para una campaña de donación (IA + fallback)."""
    return JSONResponse(plan_campaign(ctx.model_dump()))


@app.get("/api/flyer-templates")
async def flyer_templates():
    """Plantillas de flyer disponibles (nombre, campos editables y preview)."""
    return JSONResponse([
        {
            "key": key,
            "nombre": spec["nombre"],
            "campos": list(spec["campos"].keys()),
            "url": f"/static/img/flyers/{key}.png",
        }
        for key, spec in FLYER_TEMPLATES.items()
    ])


class FlyerTextos(BaseModel):
    template: str = "gotita-feliz"
    titular: str = ""
    mensaje: str = ""
    fecha: str = ""
    lugar: str = ""
    publico: str = ""
    nota: str = ""


@app.post("/generate-flyer")
async def generate_flyer(f: FlyerTextos):
    """Rellena la plantilla elegida con los textos (solo letras)."""
    if f.template not in FLYER_TEMPLATES:
        return JSONResponse({"error": "Plantilla desconocida"}, status_code=400)
    filename = f"{uuid.uuid4().hex}.png"
    output_path = str(_GENERATED_DIR / filename)
    create_flyer(f.template, f.model_dump(), output_path)
    return JSONResponse({"url": f"/static/generated/{filename}", "template": f.template})
