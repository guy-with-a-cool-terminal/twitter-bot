import requests
import os
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from requests_oauthlib import OAuth1
from urllib.parse import quote

# Load the environment variables
load_dotenv()

# Fetch API keys
API_KEY = os.getenv('twitter_key')
API_SECRET_KEY = os.getenv('twitter_secret_key')
ACCESS_TOKEN = os.getenv('twitter_access_key')
ACCESS_TOKEN_SECRET = os.getenv('twitter_access_secret_key')
NEWS_API_KEY = os.getenv('news_api_key') 
GNEWS_API_KEY = os.getenv('gnews_api_key') 

# Ensure all keys are available
def check_env_keys():
    keys = [API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, NEWS_API_KEY, GNEWS_API_KEY]
    if None in keys or '' in keys:
        raise EnvironmentError("Keys missing, check .env for clarity!")

# Authenticate with Twitter using OAuth1
def authenticate_twitter():
    try:
        auth = OAuth1(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        return requests.Session(), auth
    except Exception as e:
        print(f'Error authenticating with Twitter: {e}')
        return None
    
# Set to keep track of previously tweeted news
tweeted_news = set()

# Function to get news from NewsAPI
def get_cyber_news_newsapi():
    search_terms = ['cybersecurity', 'hacking', 'data breach', 'malware', 'cyber attack', 'information security', 'phishing']
    selected_search_term = random.choice(search_terms)
    print(f"Selected topic: {selected_search_term}")
    
    url = f'https://newsapi.org/v2/everything?q={quote(selected_search_term)}&language=en&apiKey={NEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()
            if news['articles']:
                for article in news['articles']:
                    title = article['title']
                    article_url = article['url']
                    # Ensure the article is not already tweeted
                    if (title, article_url) not in tweeted_news:
                        print(f"Adding to tweet: {title} - {article_url}")
                        return title, article_url
            return "No new news found!", ""
        else:
            return f"Error fetching from NewsAPI: {response.json().get('message')}", ""
    except Exception as e:
        return f"NewsAPI request error: {e}", ""

# Function to get news from GNews API
def get_from_secondapi():
    search_terms = ['cybersecurity', 'hacking', 'data breach', 'malware', 'cyber attack', 'information security', 'phishing']
    selected_search_term = random.choice(search_terms)
    print(f"Selected topic: {selected_search_term}")
    
    url = f'https://gnews.io/api/v4/search?q={quote(selected_search_term)}&language=en&token={GNEWS_API_KEY}'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()
            if news['articles']:
                for article in news['articles']:
                    title = article['title']
                    article_url = article['url']
                    # Ensure the article is not already tweeted
                    if (title, article_url) not in tweeted_news:
                        print(f"Adding to tweet: {title} - {article_url}")
                        return title, article_url
            return "No new news found!", ""
        else:
            return f"Error fetching from GNewsAPI: {response.json().get('message')}", ""
    except Exception as e:
        return f"GNewsAPI request error: {e}", ""

def get_cyber_news():
    api_choice = random.choice(['newsapi', 'secondapi'])
    print(f"Selected API: {api_choice}")  # Debug which API is selected
    if api_choice == 'newsapi':
        return get_cyber_news_newsapi()
    elif api_choice == 'secondapi':
        return get_from_secondapi()
    else:
        return "Error selecting!", ""

# Function to create a thread of tweets
def create_tweet_thread(session, auth, tweets):
    # Set the URL for posting a tweet
    url = "https://api.twitter.com/2/tweets"
    
    # Post the first tweet
    response = session.post(url, auth=auth, json={"text": tweets[0]})
    
    if response.status_code == 201:
        print("First tweet posted:", tweets[0])
        tweet_id = response.json()['data']['id']  # Get the ID of the first tweet
        
        # Post subsequent tweets in the thread
        for tweet in tweets[1:]:
            response = session.post(url, auth=auth, json={"text": tweet, "reply": {"in_reply_to_tweet_id": tweet_id}})
            if response.status_code == 201:
                print("Thread tweet posted:", tweet)
                tweet_id = response.json()['data']['id']  # Update tweet_id for the next reply
            else:
                print(f"Failed to post thread tweet: {response.json().get('message')}")
    else:
        print(f"Failed to tweet: {response.json().get('message')}")

# Function to tweet the news
def tweet_news(session, auth):
    news_title, news_url = get_cyber_news()
    print(f"Fetched news: {news_title}, URL: {news_url}")
    if news_url:
        tweet_base = f"{news_title} - Read more here: {news_url}"
        
        # Split the tweet into a thread if it exceeds 280 characters
        if len(tweet_base) > 280:
            # Split the tweet into chunks
            chunks = []
            while len(tweet_base) > 280:
                # Find the last space within the limit
                last_space = tweet_base.rfind(' ', 0, 277)  # Ensure we leave room for ellipsis
                if last_space == -1:  # If no space found, just cut it
                    last_space = 277
                chunks.append(tweet_base[:last_space] + "...")
                tweet_base = tweet_base[last_space:].lstrip()  # Remove leading spaces
            
            # Add the remaining part of the tweet
            if tweet_base:
                chunks.append(tweet_base)

            # Create a thread of tweets
            create_tweet_thread(session, auth, chunks)
        else:
            tweet = tweet_base
            # Post the single tweet
            create_tweet_thread(session, auth, [tweet])
    else:
        print("No news to tweet at this time.")

# Scheduler to run the tweet function at regular intervals
def schedule_tweets(session, auth):
    tweet_news(session, auth)
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: tweet_news(session, auth), 'interval', minutes=16)
    print("Scheduler started, will tweet every 16 minutes...")
    scheduler.start()

# Run the tweet scheduling
if __name__ == "__main__":
    check_env_keys()
    session, auth = authenticate_twitter()
    if session:
        schedule_tweets(session, auth)