from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from pydantic import BaseModel
from typing import Any
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return "hello world"

class Message(BaseModel):
    type: str
    data: Any

class SocketManager:
    
    def __init__(self):
        self.active_websockets = set()
    
    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_websockets.add(websocket)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def broadcast_all(self, message: Message, websocket: WebSocket):
        for ws in self.active_websockets:
            if ws != websocket:
                await ws.send_text(message)

    async def disconnect(self, websocket: WebSocket):
        self.active_websockets.discard(websocket)

socket_manager = SocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await socket_manager.connect(websocket)
        while True:
            message = await websocket.receive_text()
            print('message:',message)
            await socket_manager.broadcast_all(message, websocket)
    except WebSocketDisconnect:
        await socket_manager.disconnect(websocket)
    except Exception as e:
        # Handle unexpected exceptions
        print(f"Unexpected error: {e}")



