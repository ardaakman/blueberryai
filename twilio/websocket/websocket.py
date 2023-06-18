from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

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
    try:
        while True:
            data = await websocket.receive_text()
            manager.data_received.append(data)
            await manager.send_data(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Connection closed.")

@app.get("/get_data")
async def get_data():
    return {"data": manager.data_received}
