import base64
from flask import Flask, request, redirect, url_for
from flask_socketio import SocketIO, emit
from twilio.twiml.voice_response import VoiceResponse, Gather, Start, Connect, Stream
from twilio.rest import Client
import openai
import os
import requests
import uuid
from twilio.rest import Client
from configs import *

from utils import voice_to_text

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/convo', methods=['POST'])
def convo():
    recording_url = request.values.get('RecordingUrl', None)
    response = VoiceResponse()
    if recording_url:
        text = voice_to_text(recording_url)
        print(text)
        if len(text) > 0:
            # chat.add(text)
            post_to_client(text, 'callee')
            response.pause()
            # value = chat.generate() [TODO]
            if "bye" in value.lower():
                response.say(value)
                response.hangup()
            else:
                if "/user" in value.lower():
                    user_info = None
                    while user_info is None:
                        response.pause()
                        user_info = input(value.split('/user')[1])
                    value = user_info
                # chat.add(value, role='assistant')
                post_to_client(value, 'caller')
                response.say(value)
    
    response.record(max_length=20, timeout=3, action='/convo', play_beep=False, trim='trim-silence')
    return str(response)


def post_to_client(message, sender):
    url = "http://127.0.0.1:8201/post_to_client"
    data = {"message": message, "sender": sender}
    requests.post(url, data=data)

if __name__ == '__main__':
    app.run(port=5001, debug=True)

