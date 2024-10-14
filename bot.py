# by @ifconfigbrian on github

import tweepy
import requests
import os
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

# load the environment variables
load_dotenv()

# fetch API keys
API_KEY = os.getenv('twitter_key')
API_SECRET_KEY = os.getenv('twitter_secret_key')
ACCESS_TOKEN = os.getenv('twitter_access_key')
ACCESS_TOKEN_SECRET = os.getenv('twitter_access_token_key')
NEWS_API_KEY = os.getenv('news_api_key') 
GNEWS_API_KEY = os.getenv('gnews_api_key') 
CURRENTS_API_KEY = os.getenv('currents_api_key') 

# ensure all keys are available
def check_env_keys():
    keys =[API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, NEWS_API_KEY, GNEWS_API_KEY, CURRENTS_API_KEY]
    if None in keys or '' in keys:
        raise EnvironmentError("keys missing,check .env for clarity!!")

# authenticate with twitter
def authenticate_twitter():
    try:
        auth = tweepy.OAuthHandler(API_KEY,API_SECRET_KEY)
        auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
        return tweepy.API(auth)
    except Exception as e:
        print(f'error authenticating with twitter: {e}')
        return None

# function to get cybersecurity news from NewsAPI
def get_cyber_news_newsapi():
    # topics to be fetched from this API
    topics = ['cybersecurity', 'databreach', 'malware', 'cyber attack']
    selected_topic = random.choice(topics)

    url = f'https://newsapi.org/v2/everything?q={selected_topic}&apiKey={NEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()
            if news['articles']:
                title = news['articles'][0]['title']
                article_url = news['articles'][0]['url']
                return title, article_url
            else:
                return "no news found!!"
        else:
            return f"error fetching from NewsApi: {response.json().get('message')}",""
    except Exception as e:
        return f"NewsApi request error!: {e}",""

# function to get news from second API
def get_from_secondapi():
    # topics to be fetched from this API
    topics = ['cybersecurity', 'privacy breach', 'phishing', 'internet security']
    selected_topic = random.choice(topics)

    url = f'https://gnews.io/api/v4/search?q={selected_topic}&token={GNEWS_API_KEY}'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()
            if news['articles']:
                title = news['articles'][0]['title']
                article_url = news['articles'][0]['url']
                return title, article_url
            else:
                return "no news found!!"
        else:
            return f"error fetching from GNews: {response.json().get('message')}",""
    except Exception as e:
        return f"GNews request error!: {e}",""

# Function to get news from Currents API
def get_cyber_news_currents():
    # topics from this API
    topics = ['cybersecurity', 'cyber law', 'emerging threats', 'cloud security']
    selected_topic = random.choice(topics)

    url = f'https://api.currentsapi.services/v1/search?keywords={selected_topic}&apiKey={CURRENTS_API_KEY}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()
            if news['articles']:
                title = news['articles'][0]['title']
                article_url = news['articles'][0]['url']
                return title, article_url
            else:
                return "no news found!!"
        else:
            return f"error fetching from CurrentsApi: {response.json().get('message')}",""
    except Exception as e:
        return f"CurrentsApi request error!: {e}",""


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
        return "Error selecting!!", ""

# function to tweet the news
def tweet_news(api):
    """
    Fetches latest news and tweets it
    """
    news_title, news_url = get_cyber_news()
    if news_url:
        tweet = f"{news_title} - Read more here: {news_url}"
        # ensure tweet is within 280 characters limit
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        api.update_status(tweet)
        print("Cybersecurity news tweeted:", tweet)
    else:
        print("No news to tweet at this time.")

# scheduler to run the tweet function at regular intervals
def schedule_tweets(api):
    """
    Schedules the tweet_news function to run every hour using APScheduler.
    """
    tweet_news(api)
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: tweet_news(api), 'interval', hours=1)
    print("Scheduler started, will tweet every hour...")
    scheduler.start()

# run the tweet scheduling
if __name__ == "__main__":
    check_env_keys()
    twitter_api = authenticate_twitter()
    if twitter_api:
        schedule_tweets(twitter_api)
