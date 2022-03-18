from typing import List
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Notes</title>
    </head>
    <body>
        <h1>Message Processor</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <div id='messages'>
        </div>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('p')
                var response = JSON.parse(event.data);
                var text = response.number + '. ' + response.text
                var content = document.createTextNode(text)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                var msg = {
                    message: input.value
                  };
                ws.send(JSON.stringify(msg))
                input.value = ''
                event.preventDefault()
            };
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.number = 0

    async def connect(self, websocket: WebSocket):
        # self.number = 0
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def get():

    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    n = 0
    try:
        while True:
            data = await websocket.receive_json()
            n += 1
            await manager.send_message({"number": n, "text": data["message"]}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
