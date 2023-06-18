import speech_recognition as sr
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydub import AudioSegment
import json
import base64

app = FastAPI()
r = sr.Recognizer()

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.data_received = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_data(self, data: str):
        for connection in self.active_connections:
            await connection.send_text(data)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Connection established.")
    
    recognizer = sr.Recognizer()
    try:
        while True:
            audio_data = await websocket.receive_bytes()
            
            # Convert the bytes to audio data
            audio = sr.AudioData(audio_data, 44100, 2)  # Check your audio's sample rate & channels
            
            # Use the recognizer to transcribe the audio data to text
            text = recognizer.recognize_google(audio)
            
            manager.data_received.append(text)
            await manager.send_data(f"Transcribed text was: {text}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Connection closed.")

@app.websocket("/audio_detection")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Connection established.")
    
    try:
        while True:
            voice_detected = False
            # You are receiving text message, not bytes
            data = await websocket.receive_text()

            # Parse the received JSON string
            message = json.loads(data)
            
            # Extract the payload (base64 encoded audio)
            audio_base64 = message.get('media', {}).get('payload')
            
            # Convert base64 string to bytes
            audio_bytes = base64.b64decode(audio_base64)
            
            # Convert the bytes to audio data
            audio = AudioSegment(audio_bytes, frame_rate=44100, channels=2)
            
            # Calculate the loudness of the audio
            loudness = audio.dBFS
            if loudness < 20:
                # If no voice is detected, write 'yes' into a file
                with open('../voice_detection.txt', 'w') as file:
                    file.write('yes')

            manager.data_received.append(loudness)
            await manager.send_data(f"Loudness was: {loudness} dBFS")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Connection closed.")
    except websockets.exceptions.ConnectionClosedError:
        print("Connection closed abruptly.")