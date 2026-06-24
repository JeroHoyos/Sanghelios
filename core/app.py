from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

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
