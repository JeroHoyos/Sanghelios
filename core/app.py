from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import uuid
from pathlib import Path

from core.tools.write_images import BloodDonationPoster

_STATIC_ROOT = Path("core/static")
_GENERATED_DIR = _STATIC_ROOT / "generated"
_IMG_DIR = _STATIC_ROOT / "img"
_TEMPLATE_EVENT = str(_IMG_DIR / "event.png")
_TEMPLATE_PERSONAL = str(_IMG_DIR / "personal.png")
_GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Sanghelios",
    description="Inteligencia Predictiva para Bancos de Sangre",
)

templates = Jinja2Templates(directory="core/templates")
app.mount("/static", StaticFiles(directory="core/static"), name="static")


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
