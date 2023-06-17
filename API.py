from fastapi import FastAPI, APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from pathlib import Path

app = FastAPI()

api_router = APIRouter()
BASE_PATH = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="static"), name="static")
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates/employees"))

@app.get("/")
async def root(request: Request):
    '''
    Init call page
    '''
    return {"message": "Hello World"}
    # return TEMPLATES.TemplateResponse(
    #     "init.html",
    #     {
    #         "request": request,
    #     }
    # )