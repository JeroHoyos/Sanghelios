from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Sanghelios", description="Inteligencia Predictiva para Bancos de Sangre"
)

templates = Jinja2Templates(directory="core/templates")
app.mount("/static", StaticFiles(directory="core/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/sanghelios-informe-eda", response_class=HTMLResponse)
async def sanghelios_informe_eda(request: Request):
    return templates.TemplateResponse(
        request=request, name="sanghelios_informe_eda.html", context={}
    )


@app.get("/donation", response_class=HTMLResponse)
async def valid_donation(request: Request):
    return templates.TemplateResponse(
        request=request, name="valid_donation.html", context={}
    )


@app.get("/image_generation", response_class=HTMLResponse)
async def image_generation(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="image_generation.html",
        context={
            "request": request,
            "active_view": "image_generation",
        },
    )


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
