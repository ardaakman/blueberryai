from fastapi import FastAPI, APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from pathlib import Path

from utils import *

app = FastAPI()

api_router = APIRouter()
BASE_PATH = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="static"), name="static")
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))
USER_ID = 1

@app.get("/", response_class=HTMLResponse)
async def init(request: Request):
    '''
    Load page to set call settings
    '''
    # get phonebook from db
    with get_db_connection() as conn:
        # select distict phone numbers and recipient from call_log where user_id is user id
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT phone_number, recipient FROM call_log WHERE user_id = ?", (USER_ID,))
        phonebook = cur.fetchall()

    return TEMPLATES.TemplateResponse(
        "init.html",
        {
            "request": request,
            "page": "init",
            "phonebook": phonebook,
        }
    )


@app.post("/init_call", response_class=HTMLResponse)
async def init(request: Request, number: str = Form(), recipient: str = Form(), context: str = Form()):
    '''
    Load page to set call settings
    '''

    # save call to db [TODO]
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO call_log (user_id, phone_number, recipient, context) VALUES (?, ?, ?, ?)", (USER_ID, number, recipient, context))
        call_id = cur.lastrowid
        conn.commit()

    # initiate call [TODO]


    # redirect to call page
    return RedirectResponse(f"/call/{call_id}", status_code=303)


@app.get("/call/{call_id}", response_class=HTMLResponse)
async def call(request: Request, call_id: str):
    '''
    Page to view ongoinng call
    '''

    return TEMPLATES.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "page": "call"
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