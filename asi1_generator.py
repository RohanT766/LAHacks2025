#!/usr/bin/env python3
import os
import json
import requests
import tweepy
from dotenv import load_dotenv

# ───────────────────────────────────────────────────────────
# Load environment variables from a .env file. You should
# have ASI1_API_KEY, TWITTER_API_KEY, TWITTER_API_SECRET,
# TWITTER_ACCESS_TOKEN, and TWITTER_ACCESS_TOKEN_SECRET in it.
load_dotenv()

# ───────────────────────────────────────────────────────────
# ASI1 API setup
ASI1_API_KEY = os.getenv("ASI1_API_KEY")
ASI1_API_URL = "https://api.asi1.ai/v1/chat/completions"

# ───────────────────────────────────────────────────────────
# Twitter API setup
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

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
        "messages": [
            {
                "role": "user",
                "content": (
                    "I failed to complete a task on time. Generate pure text with no quotation marks that could be tweeted that is a few sentences long that is extremely self deprecating because of this. Should not be funny, just very rude to myself. Generate only the tweet and no other text. Make sure it is purely text and is not surrounded by quotation marks."
                )
            }
        ],
        "temperature": 0.7,
        "stream": True,
        "max_tokens": 280  # cap for safety
    }

    # json.dumps turns the Python dict into a JSON‐formatted string
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

        # Each streamed line is prefixed with "data: "
        if chunk.startswith(b"data: "):
            payload_chunk = chunk[len(b"data: "):]

            # End‐of‐stream marker
            if payload_chunk == b"[DONE]":
                break

            data = json.loads(payload_chunk)

            # Each event has a "choices" list with a "delta" containing new text
            delta = data["choices"][0].get("delta", {})
            content = delta.get("content")
            if content:
                tweet_text += content

    return tweet_text.strip()

def post_to_twitter(tweet_text):
    """
    Post the generated tweet via Tweepy.
    """
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        resp = client.create_tweet(text=tweet_text)
        print(f"Successfully posted tweet! Tweet ID: {resp.data['id']}")
        return True
    except Exception as e:
        print(f"Error posting to Twitter: {e}")
        return False

def main():
    tweet = generate_tweet()
    print(f"Generated tweet:\n{tweet}\n")
    post_to_twitter(tweet)

if __name__ == "__main__":
    main()
