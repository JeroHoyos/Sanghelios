from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Tell FastAPI where the templates are stored
templates = Jinja2Templates(directory="core/templates")
app.mount("/static", StaticFiles(directory="core/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"message": "Hello World from FastAPI Templates!"},
    )


