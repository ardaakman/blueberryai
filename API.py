import asyncio
from fastapi import FastAPI, APIRouter, Request, Form, WebSocket, WebSocketDisconnect, BackgroundTasks, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.websockets import WebSocket

from pydantic import BaseModel

from pathlib import Path
from utils import *
import json
import requests
import httpx
import openai
import os
from config import *
# import twilio
from twilio.rest import Client


from chat import ContextManager
from agent_helpers import ContextManager, CallHandler
# from chat_agents import EfficientContextAgent

app = FastAPI()

class Item(BaseModel):
    data: dict


api_router = APIRouter()
BASE_PATH = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="static"), name="static")
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))
USER_ID = 1

openai.api_key = openai_api_key

class Chat:
    def __init__(self, call_id, context):
        self.call_id = call_id
        self.agent_description = self.generate_agent_description(context)
        self.history = [{'role': 'system', 'content': self.agent_description}] + self.get_history()

    def get_history(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT message, sender, id FROM chat WHERE call_id = ? ORDER BY id ASC", (self.call_id,))
            rows = cur.fetchall()
            rows = [{'role': row[1], 'content': row[0]} for row in rows]
            for row in rows:
                if row['role'] == 'caller':
                    row['role'] = 'assistant'
                elif row['role'] == 'callee':
                    row['role'] = 'user'
            return rows

    def generate_agent_description(self, context):
        prompt = f"""
            You're imitating a human that is trying to {context}. 
            You're on a call with customer service.  
            Sound like a human and use your context to return the appropriate response. Keep responses short, simple, and informal. Only give information when it is asked. 
            You could use filler words like 'um' and 'uh' to sound more human. When the call is finished, include the word 'bye'. For information you are unsure about, return "/user <question>".
            Here is some information about you:
        """
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT personal_info FROM call_log WHERE id = ?", (USER_ID,))
            info = cur.fetchone()[0]
        prompt += info
        print(prompt)
        return prompt

    def add(self, message, role='user'):
        # save to db
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO chat (call_id, message, sender) VALUES (?, ?, ?)", (self.call_id, message, role))
            conn.commit()
        if role == 'caller':
            role = 'assistant'
        elif role == 'callee':
            role = 'user'

        self.history.append({'role': role, 'content': message})

    def generate(self):
        # try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.history,
        )
        value = completion.choices[0].message['content']
        print(value)
        return value
        # except:
        #     return "Sorry, I don't understand. Can you repeat that?"

    
class Call:
    def __init__(self, call_id):
        self.call_id = call_id
        self.context, self.recipient = self.get_context()
        self.chat = Chat(call_id, self.context)
        self.call_id = call_id

    def get_context(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT context, recipient FROM call_log WHERE id = ?", (self.call_id,))
            context, recipient = cur.fetchone()
        return context, recipient

    def generate_questions(self):
        try:
            prompt = f"""Given the context of {self.context}, what are some possible personal questions, 
                        such as date of birth, account number, etc. that the customer service agent might ask the user?
                        Phrase questions as key words, such as "Date of Birth". Give multiple questions seperated by a new line."""
            prompt = [{'role': 'user', 'content': prompt}]
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=prompt,
            )
            value = completion.choices[0].message['content']
            questions = value.split('\n')
            
            for question in questions:
                # ask question in input terminal and save question: answer as a new line to info.txt
                answer = input(question + '\n')
                with open('info.txt', 'a') as f:
                    f.write(question + ': ' + answer + '\n')
        except:
            print('error')
            return False

    def call(self):
        client = Client(account_sid, auth_token)
        to = self.recipient
        to = "9495016532"
        ngrog = "https://fe8f-2607-f140-400-a011-20c1-f322-4b13-4bc9.ngrok-free.app"
        call = client.calls.create(
            url=f'''https://fe8f-2607-f140-400-a011-20c1-f322-4b13-4bc9.ngrok-free.app/convo/{self.call_id}''',
            # url=f'''{ngrog}/conversation/{self.call_id}''',
            to="+1" + to,
            from_="+18777192546"
        )
        print(call.sid)
        
# class CallHandler():
#     def __init__(self, to_phone_number, recipient_name, task_context):
#         self.recipient = to_phone_number
#         self.task_context = task_context
#         self.recipient_name = recipient_name
        
#         self.context_manager = ContextManager()
#         self.chat_agent = EfficientContextAgent(task_context, self.recipient_name, self.context_manager)
    
#     def generate_questions(self):
#         return self.context_manager.generate_questions_from_task(self.task_context)

#     def generate_response(self, response):
#         return self.chat_agent(response)
    
#     def call(self):
#         client = Client(account_sid, auth_token)
#         to = self.recipient
#         to = "9495016532"
#         call = client.calls.create(
#             # url='https://handler.twilio.com/twiml/EH9c51bf5611bc2091f8d417b4ff44d104',
#             url='https://fe8f-2607-f140-400-a011-20c1-f322-4b13-4bc9.ngrok-free.app/convo',
#             to="+1" + to,
#             from_="+18777192546"
#         )
#         print(call.sid)

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
    Root page => before anything happens
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
    Handles the press to call
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
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT context FROM call_log WHERE id = ?", (call_id,))
        context = cur.fetchone()[0]

    questions = ContextManager.generate_questions_from_task(context)
    # generate questions
    return TEMPLATES.TemplateResponse(
        "questions.html",
        {
            "request": request,
            "call_id": call_id,
            "page": "questions",
            "questions": questions
        }
    )


@app.post("/questions", response_class=HTMLResponse)
async def questions(request: Request, call_id: str = Form()):
    '''
    Page to view call history
    This is the function that runs when the user submits the answers to questions
    '''
    body = await request.form()
    print("printing body")
    question_answer_pairs = []
    for key in body.keys():
        if key != "call_id":
            question_answer_pairs.append(f'''{key}: {body[key]}''')

    # convert question_answer_pairs to str
    question_answer_pairs = "\n".join(question_answer_pairs)

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE call_log SET personal_info = ? WHERE id = ?", (question_answer_pairs, call_id))
        conn.commit()

    return RedirectResponse(f"/call/{call_id}", status_code=303)

#Use server to relieve twilio.
@app.post("/upload_to_wasabi")
async def upload_to_wasabi(request: Request, item: Item):
    '''
    Upload recording to wasabi
    '''
    path = item["path"]
    await upload_to_wasabi(path, "blueberryai-input")


@app.post("/update_personal_info")
async def update_personal_info(request: Request):
    body = await request.json()
    call_id = body["call_id"]
    info = body["info"]
    print(call_id, info)

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT personal_info FROM call_log WHERE id = ?", (call_id,))
        personal_info = cur.fetchone()[0]

    
    replace_str = [f'''{key["id"]}:{key["value"]}''' for key in info]
    replace_str = "\n".join(replace_str)
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE call_log SET personal_info = ? WHERE id = ?", (replace_str, call_id))
        conn.commit()
    
    return {"status":"success"}
    

@app.get("/call/{call_id}", response_class=HTMLResponse)
async def call(request: Request, call_id: str, background_tasks: BackgroundTasks):
    '''
    Page to view ongoinng call
    ''' 
    # initiate call [TODO]
    # url = 'http://127.0.0.1:5001/start_call'

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, recipient, personal_info FROM call_log WHERE id = ?", (call_id,))
        call = cur.fetchone()

    new_call = Call(call[0])
    question_answers = call[2]

    print(question_answers)
    
    question_answers = question_answers.split('\n')
    question_answers = [qa.split(':') for qa in question_answers]
    
    new_call.call()
    # data = {
    #     'call_id': call_id,
    #     'to': call[0],
    #     'context': call[1]
    # }

    # background_tasks.add_task(make_http_request, url, data)
    # print("added task")
    
    # # Add the request function to the background tasks
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(url, params=data)

    return TEMPLATES.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "page": "call",
            'call_id': call_id,
            'question_answers': question_answers,
            'recipient': call[1]
        }
    )

@app.post("/save_message")
async def save_message(request: Request):
    '''
    Send data to client
    '''
    data = await request.json()
    print(data)
    for key in data.keys():
        print(key, data[key])

    # define variables
    message = data["message"]
    call_id = data["call_id"]
    sender = data["sender"]

    # send to client
    await send_data_to_clients(json.dumps(data))
    print("sent to client")
    # save to db
    call = Call(call_id)
    
    # Interface with the agent
    agent = CallHandler(call_id)
    response_val = agent(message)
    url = save_generated_response_as_audio(response_val)
    
    # Update the database
    call.chat.add(message, sender)
    call.chat.add(response_val, "caller")

    # send caller response
    data = {"message": response_val, "call_id": call_id, "sender": 'caller'}
    await send_data_to_clients(json.dumps(data))
    return_str = {"url": url, "message": response_val}
    return json.dumps(return_str)


# SOCKETS
sockets = []
async def send_data_to_clients(data):
    # Iterate over each connected websocket
    print("sending data to clients")
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
    body = await request.json()
    call_id = body['call_id']

    print('ending call' + call_id)
    
    # add message
    return {'status': 'success'}


# add message
# @app.post("/send_message")
# async def add_message(request: Request):
#     '''
#     End call
#     '''
#     body = await request.json()
#     call_id = body['call_id']
#     message = body['message']
    
#     print('sending message' + message)
#     # add message

#     return {'status': 'success'}

def save_generated_response_as_audio(generated_response):
    conversational_style_id = "6434632c9f50eacb088edafd"
    marcus_speaker_id = "643463179f50eacb088edaec"

    url = "https://api.fliki.ai/v1/generate/text-to-speech"
    headers = {
        "Authorization": f"Bearer {os.getenv('FLIKI_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "content": generated_response,
        "voiceId": marcus_speaker_id,
        "voiceStyleId": conversational_style_id
    }
    
    response = requests.post(url, headers=headers, json=data)

    # Check the response status code
    if response.status_code == 200:
        # Process the response
        audio_data = response.content
        # Do something with the audio data
        response_dict = json.loads(audio_data)

        # Now you can access the dictionary elements
        success = response_dict["success"]
        audio_url = response_dict["data"]["audio"]
        duration = response_dict["data"]["duration"]
        
        return audio_url
    else:
        # Handle the error
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")