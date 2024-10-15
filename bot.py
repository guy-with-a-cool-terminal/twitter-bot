import requests
import os
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from requests_oauthlib import OAuth1

# Load the environment variables
load_dotenv()

# Fetch API keys
API_KEY = os.getenv('twitter_key')
API_SECRET_KEY = os.getenv('twitter_secret_key')
ACCESS_TOKEN = os.getenv('twitter_access_key')
ACCESS_TOKEN_SECRET = os.getenv('twitter_access_secret_key')
NEWS_API_KEY = os.getenv('news_api_key') 
GNEWS_API_KEY = os.getenv('gnews_api_key') 
CURRENTS_API_KEY = os.getenv('currents_api_key') 

# Ensure all keys are available
def check_env_keys():
    keys = [API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, NEWS_API_KEY, GNEWS_API_KEY, CURRENTS_API_KEY]
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

# Function to get cybersecurity news from NewsAPI
def get_cyber_news_newsapi():
    topics = ['cybersecurity', 'databreach', 'malware', 'cyber attack']
    selected_topic = random.choice(topics)
    url = f'https://newsapi.org/v2/everything?q={selected_topic}&language=en&apiKey={NEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()
            if news['articles']:
                title = news['articles'][0]['title']
                article_url = news['articles'][0]['url']
                return title, article_url
            else:
                return "No news found!", ""
        else:
            return f"Error fetching from NewsAPI: {response.json().get('message')}", ""
    except Exception as e:
        return f"NewsAPI request error: {e}", ""

# Function to get news from GNews API
def get_from_secondapi():
    topics = ['cybersecurity', 'privacy breach', 'phishing', 'internet security']
    selected_topic = random.choice(topics)
    url = f'https://gnews.io/api/v4/search?q={selected_topic}&language=en&token={GNEWS_API_KEY}'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()
            if news['articles']:
                title = news['articles'][0]['title']
                article_url = news['articles'][0]['url']
                return title, article_url
            else:
                return "No news found!", ""
        else:
            return f"Error fetching from GNews: {response.json().get('message')}", ""
    except Exception as e:
        return f"GNews request error: {e}", ""

# Function to get news from Currents API
def get_cyber_news_currents():
    topics = ['cybersecurity', 'cyber law', 'emerging threats', 'cloud security']
    selected_topic = random.choice(topics)
    url = f'https://api.currentsapi.services/v1/search?keywords={selected_topic}&language=en&apiKey={CURRENTS_API_KEY}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()
            if news['articles']:
                title = news['articles'][0]['title']
                article_url = news['articles'][0]['url']
                return title, article_url
            else:
                return "No news found!", ""
        else:
            return f"Error fetching from CurrentsAPI: {response.json().get('message')}", ""
    except Exception as e:
        return f"CurrentsAPI request error: {e}", ""

# Function to select an API randomly and fetch news
def get_cyber_news():
    api_choice = random.choice(['newsapi', 'secondapi', 'currents'])
    if api_choice == 'newsapi':
        return get_cyber_news_newsapi()
    elif api_choice == 'secondapi':
        return get_from_secondapi()
    elif api_choice == 'currents':
        return get_cyber_news_currents()
    else:
        return "Error selecting!", ""

# Function to tweet the news
def tweet_news(session, auth):
    news_title, news_url = get_cyber_news()
    print(f"Fetched news: {news_title}, URL: {news_url}")
    if news_url:
        tweet = f"{news_title} - Read more here: {news_url}"
        # Ensure tweet is within 280 characters limit
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        
        # Set the URL for posting a tweet
        url = "https://api.twitter.com/2/tweets"
        
        # Post the tweet using OAuth1
        response = session.post(url, auth=auth, json={"text": tweet})
        
        if response.status_code == 201:
            print("Cybersecurity news tweeted:", tweet)
        else:
            print(f"Failed to tweet: {response.json().get('message')}")
    else:
        print("No news to tweet at this time.")

# Scheduler to run the tweet function at regular intervals
def schedule_tweets(session, auth):
    tweet_news(session, auth)
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: tweet_news(session, auth), 'interval', hours=1)
    print("Scheduler started, will tweet every hour...")
    scheduler.start()

# Run the tweet scheduling
if __name__ == "__main__":
    check_env_keys()
    session, auth = authenticate_twitter()
    if session:
        schedule_tweets(session, auth)
