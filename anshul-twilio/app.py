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
import json

app = Flask(__name__)
socketio = SocketIO(app)

def voice_to_text(url):
    # Download the file from `url` and save it locally under `file_name`:
    openai.api_key = openai_api_key
    random_uuid = str(uuid.uuid4())
    file_name = random_uuid + ".mp3"
    response = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(response.content)
    
    # Transcribe the audio file
    with open(file_name, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    # Delete the audio file
    os.remove(file_name)

    
    return transcript['text']


@app.route('/convo/<call_id>', methods=['POST'])
def convo(call_id: str):
    print('convo')
    recording_url = request.values.get('RecordingUrl', None)
    response = VoiceResponse()
    if recording_url:
        text = voice_to_text(recording_url)
        print(text)
        if len(text) > 0 and text != "you":
            response.pause()
            value = save_message(call_id, text, 'callee') # value = chat.generate() [TODO]
            value = json.loads(value)
            print(value)
            print(type(value))
            value = json.loads(value)
            value, url = value["message"], value["url"]
            if "bye" in value.lower():
                response.play(url)
                response.hangup()
            else:
                if "/user" in value.lower():
                    user_info = None
                    while user_info is None:
                        response.pause()
                        user_info = input(value.split('/user')[1])
                    value = user_info
                response.play(url)
    
    response.record(max_length=20, timeout=3, action=f'/convo/{call_id}', play_beep=False, trim='trim-silence')
    return str(response)

def save_message(call_id, message, sender='callee'):
    print('save_message')
    url = "http://127.0.0.1:8201/save_message"
    data = {"message": message, "sender": sender, "call_id": call_id}
    response_val = requests.post(url, data = json.dumps(data)) 
    print(response_val.text)
    return response_val.text

if __name__ == '__main__':
    app.run(port=5001, debug=True)

