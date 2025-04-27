import os
from google.generativeai import GenerativeModel, configure
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API setup
GEMINI_API_KEY = "AIzaSyDBB1-2c5so_UHHMiPowYFnasZIqsUvp9g"
configure(api_key=GEMINI_API_KEY)
model = GenerativeModel('gemini-2.0-flash')

# Twitter API setup
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

def generate_tweet():
    """Generate a tweet using Gemini AI"""
    prompt = "generate a funny tweet"
    response = model.generate_content(prompt)
    return response.text

def post_to_twitter(tweet_text):
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        
        # Post the tweet
        response = client.create_tweet(text=tweet_text)
        print(f"Successfully posted tweet! Tweet ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"Error posting to Twitter: {e}")
        return False

def main():
    # Generate tweet
    tweet_text = generate_tweet()
    print(f"Generated tweet: {tweet_text}")
    
    # Post to Twitter
    if post_to_twitter(tweet_text):
        print("Tweet posted successfully!")
    else:
        print("Failed to post tweet.")

if __name__ == "__main__":
    main() 