#!/usr/bin/env python3
import os
import json
import requests
import tweepy
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

# ───────────────────────────────────────────────────────────
# Load environment variables
load_dotenv()
ASI1_API_KEY = os.getenv("ASI1_API_KEY")
ASI1_API_URL = "https://api.asi1.ai/v1/chat/completions"
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")

# MongoDB credentials from .env
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
DB_NAME = os.getenv("DB_NAME")

# Construct the connection URI (Atlas +srv)
MONGO_URI = (
    f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}/{DB_NAME}"
    "?retryWrites=true&w=majority"
)

# ───────────────────────────────────────────────────────────
# MongoDB setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db.users


def get_user_oauth_tokens(user_id):
    """
    Fetch the OAuth tokens for a given user from MongoDB.
    user_id should be a string representation of the user's ObjectId.
    """
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user or 'twitter' not in user:
        raise ValueError(f"No twitter object for user {user_id}")
    twitter = user['twitter']
    access_token = twitter.get('access_token')
    access_token_secret = twitter.get('access_token_secret')
    if not access_token or not access_token_secret:
        raise ValueError(f"No OAuth tokens found for user {user_id}")
    return access_token, access_token_secret


def generate_tweet():
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
            "I failed to complete a task on time. Generate pure text with no quotation marks that could be tweeted that is a few sentences long that is extremely self deprecating because of this. Should not be funny, just very rude to myself. Generate only the tweet and no other text. Make sure it is purely text and is not surrounded by quotation marks."
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
    return tweet_text.strip()


def post_to_twitter(tweet_text, oauth_token, oauth_token_secret):
    """
    Post the generated tweet on behalf of a user with their OAuth tokens.
    Includes a quick sanity check via get_me.
    """
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=oauth_token,
        access_token_secret=oauth_token_secret
    )
    # --- Quick sanity check ---
    print("Using tokens:", oauth_token, oauth_token_secret)
    me = client.get_me(user_auth=True)
    print("Current user:", me.data)

    resp = client.create_tweet(text=tweet_text)
    print(f"Successfully posted tweet! Tweet ID: {resp.data['id']}")
    return True


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 oauth_generator.py <user_id>")
        sys.exit(1)
    user_id = sys.argv[1]
    oauth_token, oauth_token_secret = get_user_oauth_tokens(user_id)
    tweet = generate_tweet()
    print(f"Generated tweet:\n{tweet}\n")
    post_to_twitter(tweet, oauth_token, oauth_token_secret)


if __name__ == "__main__":
    main()
