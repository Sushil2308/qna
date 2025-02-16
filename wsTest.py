import websocket
import json
 
import sys
 
 
# Define the WebSocket URL (use wss:// for secure connection)
ws_url = "ws://127.0.0.1:8000/qna/docChat/?sessionUUID=82357f00-9f20-470f-baee-8790d453bda4"
 
def on_message(ws, message):
    messageData = json.loads(message)
    if messageData["type"] in ["status","answer"]:
        sys.stdout.write(messageData["response"])
        sys.stdout.flush()
       
 
def on_error(ws, error):
    print("Error:", error)
 
def on_close(ws, close_status_code, close_msg):
    print("Connection closed", close_msg)
 
def on_open(ws):
    print("Connection established")
   
    # Send a message (JSON format, if required)
    message = {
        "question": "All Character names"
    }
    ws.send(json.dumps(message))
 
# Initialize WebSocket
ws = websocket.WebSocketApp(ws_url,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close,
                            on_open=on_open,
                            header={
                                "Authorization":"Token 0ef77d5ab474a40c05f0e2e671105c645cd55c41"
                            })
 
# Connect to the WebSocket server
ws.run_forever()