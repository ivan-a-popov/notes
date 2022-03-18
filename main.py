from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse


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


@app.get("/")
async def get():
    global n
    n = 0
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        global n
        n += 1
        await websocket.send_json({"number": n, "text": data["message"]})
