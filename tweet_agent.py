import os
import json
from uagents import Agent, Model, Context, Protocol
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import requests

load_dotenv()

# Initialize agent
agent = Agent()

# For this example, you will need to set up an account and database on MongoDB Atlas:
# https://www.mongodb.com/atlas/database. Once you have done so, enter your details
# into the agent's .env file. And set the password as an agent secret.

# MongoDB Configuration
MONGO_USER = os.environ.get("MONGO_USER")
MONGO_HOST_URL = os.environ.get("MONGO_HOST_URL")
MONGO_PASSWORD_2 = os.environ.get("MONGO_PASSWORD_2")
ASI1_API_KEY = os.getenv("ASI1_API_KEY")
ASI1_API_URL = "https://api.asi1.ai/v1/chat/completions"

api_url = os.getenv('API_URL', f'{os.getenv("NGROK_URL")}/tweet')
uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD_2}@{MONGO_HOST_URL}retryWrites=true&w=majority"
print(uri)
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.lahacks25
users = db["users"]

class TweetRequest(Model):
    access_token: str
    access_token_secret: str
    text: str

@agent.on_message(model=TweetRequest)
async def generate_tweet(ctx: Context, sender: str, req: TweetRequest):
    """
    Generate a tweet by streaming from the ASI1 Mini model. 
    """
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {ASI1_API_KEY}'
    }
    payload = {
        "model": "asi1-mini",
        "messages": [{"role": "user", "content": (
            f"I failed to complete a task on time. Generate pure text with no quotation marks that could be tweeted that is a few sentences long that is extremely self deprecating because of this. Should not be funny, just very rude to myself. Generate only the tweet and no other text. Make sure it is purely text and is not surrounded by quotation marks. Make sure to mention the task that I failed to complete: {req.text}"
        )}],
        "temperature": 0.7,
        "stream": True,
        "max_tokens": 280
    }
    response = requests.post(
        ASI1_API_URL,
        headers=headers,
        data=json.dumps(payload),
        stream=True
    )
    tweet_text = ""
    for chunk in response.iter_lines():
        if not chunk:
            continue
        if chunk.startswith(b"data: "):
            payload_chunk = chunk[len(b"data: "):]
            if payload_chunk == b"[DONE]":
                break
            data = json.loads(payload_chunk)
            delta = data["choices"][0].get("delta", {})
            content = delta.get("content")
            if content:
                tweet_text += content
    #req.text = tweet_text.strip()

    # Send the generated tweet to the /tweet API endpoint
    tweet_payload = {
        "access_token": req.access_token,
        "access_token_secret": req.access_token_secret,
        "tweet": tweet_text.strip()
    }
    api_response = requests.post(api_url, json=tweet_payload)
    if api_response.status_code == 200:
        ctx.logger.info("Tweet sent to API successfully!")
    else:
        ctx.logger.error(f"Failed to send tweet to API: {api_response.text}")

if __name__ == "__main__":
    agent.run()
    