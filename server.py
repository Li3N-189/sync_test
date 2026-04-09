from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from typing import List

import requests
import time
import threading

app = FastAPI()

app.mount("/client", StaticFiles(directory="html", html=True), name="html")

# 接続中クライアント管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
def index():
    return {"Hello": "World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 14 minutes
INTERVAL = 840;
def refresh():
    try:
        requests.get("https://sync-test-8zvh.onrender.com/")
    finally:
        threading.Timer(INTERVAL, refresh).start()

threading.Timer(INTERVAL, refresh).start()
