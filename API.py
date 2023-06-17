from fastapi import FastAPI, APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from pathlib import Path

app = FastAPI()

api_router = APIRouter()
BASE_PATH = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="static"), name="static")
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

@app.get("/", response_class=HTMLResponse)
async def init(request: Request):
    '''
    Load page to set call settings
    '''
    return TEMPLATES.TemplateResponse(
        "init.html",
        {
            "request": request,
        }
    )


@app.get("/call/{call_id}", response_class=HTMLResponse)
async def call(request: Request, call_id: str):
    '''
    Page to view ongoinng call
    '''
    return TEMPLATES.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "page": "call",
        }
    )


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    '''
    Page to view call history
    '''
    return TEMPLATES.TemplateResponse(
        "history.html",
        {
            "request": request,
        }
    )