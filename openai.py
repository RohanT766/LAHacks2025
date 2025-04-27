import time
import os
import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect
from dotenv import load_dotenv
from sesame_ai import SesameAI, SesameWebSocket, TokenManager

load_dotenv()

def load_prompt(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    prompt_path = os.path.join(dir_path, 'prompts', f'{file_name}.txt')

    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Could not find file: {prompt_path}")
        raise

# Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
NGROK_URL = os.getenv('NGROK_URL')
PORT = int(os.getenv('PORT', 5050))

SYSTEM_MESSAGE = load_prompt('system_prompt')
CHARACTER = "Maya"  # or "Miles"

app = FastAPI()

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
    raise ValueError('Missing Twilio configuration. Please set it in the .env file.')

# Initialize Sesame AI client
api_client = SesameAI()
token_manager = TokenManager(api_client, token_file="token.json")

@app.get("/", response_class=HTMLResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

@app.post("/make-call")
async def make_call(request: Request):
    """Make an outgoing call to the specified phone number."""
    data = await request.json()
    to_phone_number = data.get("to")
    if not to_phone_number:
        return {"error": "Phone number is required"}

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        url=f"{NGROK_URL}/outgoing-call",
        to=to_phone_number,
        from_=TWILIO_PHONE_NUMBER
    )
    return {"call_sid": call.sid}

@app.api_route("/outgoing-call", methods=["GET", "POST"])
async def handle_outgoing_call(request: Request):
    """Handle outgoing call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    response.say("Please wait while we connect your call to the AI voice assistant...")
    response.pause(length=1)
    response.say("O.K. you can start talking!")
    connect = Connect()
    connect.stream(url=f'wss://{request.url.hostname}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and Sesame AI."""
    print("Client connected")
    await websocket.accept()

    # Get Sesame AI token
    id_token = token_manager.get_valid_token()
    
    # Connect to Sesame AI
    sesame_ws = SesameWebSocket(id_token=id_token, character=CHARACTER)
    
    def on_connect():
        print("Connected to SesameAI!")

    def on_disconnect():
        print("Disconnected from SesameAI")

    sesame_ws.set_connect_callback(on_connect)
    sesame_ws.set_disconnect_callback(on_disconnect)
    sesame_ws.connect()

    stream_sid = None

    async def receive_from_twilio():
        """Receive audio data from Twilio and send it to Sesame AI."""
        nonlocal stream_sid
        try:
            async for message in websocket.iter_text():
                data = json.loads(message)
                if data['event'] == 'media' and sesame_ws.is_connected():
                    # Convert base64 to raw audio bytes
                    audio_data = base64.b64decode(data['media']['payload'])
                    sesame_ws.send_audio_data(audio_data)
                elif data['event'] == 'start':
                    stream_sid = data['start']['streamSid']
                    print(f"Incoming stream has started {stream_sid}")
        except WebSocketDisconnect:
            print("Client disconnected.")
            sesame_ws.disconnect()

    async def send_to_twilio():
        """Receive audio from Sesame AI and send it to Twilio."""
        nonlocal stream_sid
        try:
            while True:
                audio_chunk = sesame_ws.get_next_audio_chunk(timeout=0.01)
                if audio_chunk and stream_sid:
                    # Convert raw audio to base64
                    audio_payload = base64.b64encode(audio_chunk).decode('utf-8')
                    audio_delta = {
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {
                            "payload": audio_payload
                        }
                    }
                    await websocket.send_json(audio_delta)
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"Error in send_to_twilio: {e}")

    await asyncio.gather(receive_from_twilio(), send_to_twilio())

if __name__ == "__main__":
    import uvicorn
    to_phone_number = input("Please enter the phone number to call: ")
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        call = client.calls.create(
            url=f"{NGROK_URL}/outgoing-call",
            to=to_phone_number,
            from_=TWILIO_PHONE_NUMBER
        )
        print(f"Call initiated with SID: {call.sid}")
    except Exception as e:
        print(f"Error initiating call: {e}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)