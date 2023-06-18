import base64
from flask import Flask, request, redirect, url_for
from flask_socketio import SocketIO, emit
from twilio.twiml.voice_response import VoiceResponse, Gather, Start, Connect, Stream
from twilio.rest import Client
import openai
import os
import requests
import uuid
import configs

from utils import *

app = Flask(__name__)
socketio = SocketIO(app)
openai.api_key = configs.openai

class Chat:
    def __init__(self, context):
        self.agent_description = self.generate_agent_description(context)
        self.history = [{'role': 'system', 'content': self.agent_description}]

    def generate_agent_description(self, context):
        prompt = f"""
            You're imitating a human that is trying to {context}. 
            You're on a call with customer service.  
            Sound like a human and use your context to return the appropriate response. Keep responses short, simple, and informal.
            You could use filler words like 'um' and 'uh' to sound more human. To end the call, just return 'bye'. For information you are unsure about, return "/user <question>".
            Here is some information about you:
        """
        with open('info.txt', 'r') as f:
            info = f.read()
        prompt += info
        print(prompt)
        return prompt

    def add(self, message, role='user'):
        self.history.append({'role': role, 'content': message})

    def generate(self):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.history,
            )
            value = completion.choices[0].message['content']
            print(value)
            return value
        except:
            return "Sorry, I don't understand. Can you repeat that?"

    def stream(self, socket):
        return True
    
class Call:
    def __init__(self, to, context):
        self.recipient = to
        self.context = context
        if os.stat("info.txt").st_size == 0:
            self.questions = self.generate_questions()
        self.chat = Chat(context)

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
        
    
call = Call('9495016532', 'I want to cancel my subscription for the gym')
chat = call.chat

@app.route('/convo', methods=['POST'])
def convo():
    recording_url = request.values.get('RecordingUrl', None)
    response = VoiceResponse()
    if recording_url:
        text = voice_to_text(recording_url)
        print(text)
        if len(text) > 0:
            chat.add(text)
            response.pause()
            value = chat.generate()
            if "bye" in value.lower():
                response.hangup()
            else:
                if "/user" in value.lower():
                    user_info = None
                    while user_info is None:
                        response.pause()
                        user_info = input(value.split('/user')[1])
                    value = user_info
                chat.add(value, role='assistant')
                response.say(value)
    
    response.record(max_length=20, timeout=3, action='/convo', play_beep=False, trim='trim-silence')
    return str(response)


if __name__ == '__main__':
    socketio.run(app, port=5001, debug=True)

