import speech_recognition as sr
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

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