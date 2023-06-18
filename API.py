import asyncio
from fastapi import FastAPI, APIRouter, Request, Form, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.websockets import WebSocket

from pathlib import Path
from utils import *
import json
import requests
import httpx

app = FastAPI()

api_router = APIRouter()
BASE_PATH = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="static"), name="static")
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))
USER_ID = 1

async def make_http_request(url: str, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
    return response

@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("static/favicon.ico")

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


    # redirect to call page
    return RedirectResponse(f"/questions/{call_id}", status_code=303)



@app.get("/questions/{call_id}", response_class=HTMLResponse)
async def questions(request: Request, call_id: str):
    '''
    Page to view call history
    '''
    # generate questions
    return TEMPLATES.TemplateResponse(
        "questions.html",
        {
            "request": request,
            "call_id": call_id,
            "page": "questions",
            "questions": []
        }
    )


@app.post("/questions", response_class=HTMLResponse)
async def questions(request: Request, call_id: str = Form()):
    '''
    Page to view call history
    '''
    # verify responses are valid

    # save to db

    # redirect to call [TODO]

    return RedirectResponse(f"/call/{call_id}", status_code=303)


@app.get("/call/{call_id}", response_class=HTMLResponse)
async def call(request: Request, call_id: str, background_tasks: BackgroundTasks):
    '''
    Page to view ongoinng call
    ''' 
    # initiate call [TODO]
    url = 'http://127.0.0.1:8000/start_call'

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT phone_number FROM call_log WHERE id = ?", (call_id,))
        call = cur.fetchone()

    data = {
        'call_id': call_id,
        'phone_number': call[0]
    }
    
    # Add the request function to the background tasks
    background_tasks.add_task(make_http_request, url, data)

    return TEMPLATES.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "page": "call",
            'call_id': call_id
        }
    )

@app.post("/post_to_client")
def post_to_client(data):
    '''
    Send data to client
    '''
    send_data_to_clients(data)


# SOCKETS
sockets = []
async def send_data_to_clients(data):
    # Iterate over each connected websocket
    for websocket in sockets:
        try:
            data = json.dumps(data)
            await websocket.send_text(data)
        except Exception:
            # Handle any errors that occur while sending data
            pass


@app.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Append the connected websocket to the 'sockets' list
    sockets.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # Send the received data to all connected clients
            await send_data_to_clients(data)
    except WebSocketDisconnect:
        print("client disconnected")
        sockets.remove(websocket)


@app.get("/account", response_class=HTMLResponse)
async def history(request: Request):
    '''
    Page to view call history
    '''
    return TEMPLATES.TemplateResponse(
        "account.html",
        {
            "request": request,
        }
    )


# end call
@app.post("/end_call")
async def end_call(request: Request):
    '''
    End call
    '''
    # try:
    body = await request.json()
    call_id = body['call_id']

    print('ending call' + call_id)
    
    # add message
    return {'status': 'success'}
    # except Exception as e:
    #     print(e)
    #     return {'status': 'failed'}


# add message
@app.post("/send_message")
async def add_message(request: Request):
    '''
    End call
    '''
    # try:
    body = await request.json()
    call_id = body['call_id']
    message = body['message']
    
    print('sending message' + message)
    # add message

    return {'status': 'success'}
    # except Exception as e:
    #     print(e)
    #     return {'status': 'failed'}