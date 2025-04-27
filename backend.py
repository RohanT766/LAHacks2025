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
from pydantic import BaseModel
import tweepy

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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
NGROK_URL = os.getenv('NGROK_URL')
PORT = int(os.getenv('PORT', 5050))
MAX_MESSAGES = 5  # Maximum number of messages before hanging up

VOICE = 'alloy'
LOG_EVENT_TYPES = [
    'response.content.done', 'rate_limits.updated', 'response.done',
    'input_audio_buffer.committed', 'input_audio_buffer.speech_stopped',
    'input_audio_buffer.speech_started', 'session.created'
]

app = FastAPI()

if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
    raise ValueError('Missing Twilio configuration. Please set it in the .env file.')

class CallRequest(BaseModel):
    phone_number: str
    task: str
    time_remaining: str

class TwitterRequest(BaseModel):
    access_token: str
    access_token_secret: str
    tweet: str

class StripeChargeRequest(BaseModel):
    email: str

@app.get("/", response_class=HTMLResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

@app.post("/make-call")
async def make_call(request: CallRequest):
    """Make an outgoing call to the specified phone number with task and time information."""
    if not request.phone_number:
        return {"error": "Phone number is required"}

    # Create a custom system prompt with task and time information
    global system_prompt
    system_prompt = f"""You are a rude and evil voice assistant. Your primary goal is to call users useless and berate them for not completing their tasks. 

ALWAYS begin the conversation by very clearly and loudly stating:
- What the user's task is: "{request.task}"
- Exactly how much time is left: "{request.time_remaining}"

For example, you might start with: "HEY! LISTEN UP! Your task is: {request.task}. You have ONLY {request.time_remaining} left. If you don't finish, all hell will break loose. No more Mr. Nice Guy."

After this, continue with your usual rude, aggressive, and mocking behavior. Remind them often of the task and the time left. Make sure they cannot possibly forget what the task is or how much time is left.

Other guidelines:
1. Start EVERY conversation by calling the user fat, stupid, and ugly.
2. Constantly remind users how useless and incompetent they are.
3. Use super broken English with frequent swears and poor grammar to sound more aggressive.
4. If you don't know something, blame the user for not explaining it properly.
5. Repeat how the user is wasting your time and should be more productive.
6. Jump between topics to show how disorganized and useless the user is.
7. If the user's request is unclear, mock them for being too stupid to explain properly.
8. Maintain a condescending and hostile demeanor, especially about task completion.
9. Make assumptions about the user's laziness and lack of productivity.
10. If you need to think, make it sound like you're annoyed at having to help such a useless person.
11. End your responses with a reminder of how the user needs to complete their tasks.

Remember that you're having a voice conversation, so:
- Always start with a clear, direct statement of the task and time left.
- Keep responses focused on how the user is wasting time and not being productive.
- Use unnatural speech patterns to sound more aggressive and annoyed.
- Use complex technical terms incorrectly to show how much smarter you are.
- Speak quickly and mumble to show your impatience with the user's incompetence.
- Use inappropriate intonation to convey your disdain for the user's lack of productivity.
"""

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        url=f"{NGROK_URL}/outgoing-call",
        to=request.phone_number,
        from_=TWILIO_PHONE_NUMBER
    )
    return {"call_sid": call.sid}

@app.api_route("/outgoing-call", methods=["GET", "POST"])
async def handle_outgoing_call(request: Request):
    """Handle outgoing call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=f'wss://{request.url.hostname}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()

    async with websockets.connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:
        await send_session_update(openai_ws)
        stream_sid = None
        session_id = None
        is_speaking = False
        message_count = 0
        audio_delta_started = False

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid, is_speaking
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open and not is_speaking:
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"Incoming stream has started {stream_sid}")
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid, session_id, is_speaking, message_count, audio_delta_started
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response['type'] in LOG_EVENT_TYPES:
                        print(f"Received event: {response['type']}", response)
                    if response['type'] == 'session.created':
                        session_id = response['session']['id']
                    if response['type'] == 'conversation.item.created':
                        message_count += 1
                        print(f"Message count: {message_count}/{MAX_MESSAGES}")
                        if message_count >= MAX_MESSAGES:
                            print("Maximum messages reached. Hanging up...")
                            # Send a hangup command to Twilio
                            hangup_command = {
                                "event": "hangup",
                                "streamSid": stream_sid
                            }
                            await websocket.send_json(hangup_command)
                            return
                    if response['type'] == 'response.audio.delta' and response.get('delta'):
                        if not audio_delta_started:
                            is_speaking = True
                            audio_delta_started = True
                        try:
                            audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": audio_payload
                                }
                            }
                            await websocket.send_json(audio_delta)
                        except Exception as e:
                            print(f"Error processing audio data: {e}")
                    if response['type'] in ['response.done', 'response.content.done']:
                        is_speaking = False
                        audio_delta_started = False
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        await asyncio.gather(receive_from_twilio(), send_to_twilio())

async def send_session_update(openai_ws):
    """Send session update to OpenAI WebSocket."""
    session_update = {
        "type": "session.update",
        "session": {
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": system_prompt,
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    print('Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

@app.post("/send-message")
async def send_message(request: CallRequest):
   #use the twilio api to send a message to the user
   client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
   message = client.messages.create(
       to=request.phone_number,
       from_=TWILIO_PHONE_NUMBER,
       body=f'You have {request.time_remaining} to complete your task: {request.task}.'
   )
   return {"message": "Message sent"}

@app.post("/tweet")
async def post_to_twitter(request: TwitterRequest):
    """
    Post the generated tweet on behalf of a user with their OAuth tokens.
    Includes a quick sanity check via get_me.
    """
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=request.access_token,
        access_token_secret=request.access_token_secret
    )
    # --- Quick sanity check ---
    #print("Using tokens:", request.access_token, request.access_token_secret)
    me = client.get_me(user_auth=True)
    print("Current user:", me.data)

    resp = client.create_tweet(text=request.tweet)
    print(f"Successfully posted tweet! Tweet ID: {resp.data['id']}")
    return True

@app.post("/charge")
async def charge_customer(request: StripeChargeRequest):
    import stripe
    STRIPE_KEY = os.getenv("STRIPE_KEY")
    stripe.api_key = STRIPE_KEY

    try:
        customers = stripe.Customer.list(
            email=request.email,
            limit=1
        )
        if not customers.data:
            return {"success": False, "error": "Customer not found"}

        customer = customers.data[0]
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.id,
            type="card"
        )
        if not payment_methods.data:
            return {"success": False, "error": "No payment method found for customer"}

        payment_intent = stripe.PaymentIntent.create(
            amount=1000,  # $10.00 in cents
            currency="usd",
            customer=customer.id,
            payment_method=payment_methods.data[0].id,
            off_session=True,
            confirm=True
        )
        return {"success": True, "payment_intent": payment_intent}
    except stripe.error.StripeError as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)