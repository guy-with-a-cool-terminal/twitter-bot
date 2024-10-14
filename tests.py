import tweepy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('twitter_key')
API_SECRET_KEY = os.getenv('twitter_secret_key')
ACCESS_TOKEN = os.getenv('twitter_access_key')
ACCESS_TOKEN_SECRET = os.getenv('twitter_access_token_key')

# Authenticate with Twitter
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Try tweeting a simple message
try:
    api.update_status("Hello, world! This is a test tweet.")
    print("Tweet posted successfully!")
except tweepy.errors.Forbidden as e:
    print(f"Error posting tweet: {e}")
