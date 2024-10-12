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

# authenticate with twitter
auth = tweepy.OAuthHandler(API_KEY,API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# function to get cybersecurity news from API
def get_cyber_news_newsapi():
    url = f'https://newsapi.org/v2/everything?q=cybersecurity&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        news = response.json()
        if news['articles']:
            title = news['articles'][0]['title']
            article_url = news['articles'][0]['url']
            return title,article_url
        else:
            return "No cybersecurity news found!!",""
    else:
        return "Error fetching from API!!",""

# function to get news from second API
def get_from_secondapi():
    url = f'https://gnews.io/api/v4/search?q=cybersecurity&token={GNEWS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        news = response.json()
        if news['articles']:
            title = news['articles'][0]['title']
            article_url = news['articles'][0]['url']
            return title,article_url
        else:
            return "no news found!!",""
    else:
        return "error fetching from second API",""

def get_cyber_news_currents():
    url = f'https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}&category=technology'
    response = requests.get(url)
    if response.status_code == 200:
        news = response.json()
        if news['news']:
            title = news['news'][0]['title']
            article_url = news['news'][0]['url']
            return title, article_url
        else:
            return "No cybersecurity news found!", ""
    else:
        return "Error fetching from Currents API!", ""

# function to select an API randomly
api_choice = random.choice(['newsapi','secondapi'])

if api_choice == 'newsapi':
    return get_cyber_news_newsapi()
elif api_choice == 'secondapi':
    return get_from_secondapi()
elif api_choice == 'currents':
    return get_cyber_news_currents()
else:
    return "error selecting!!"

# function to tweet the news
def tweet_news():
    """

    fetches latest news and tweets it
    
    """
    news_title, news_url = get_cyber_news()
    if news_url:
        tweet = f"{news_title} - Read more here: {news_url}"
        api.update_status(tweet)
        print("cybersecurity news tweeted:", tweet)
    else:
        print("No news to tweet at this time.")

# scheduler to run the tweet function at regular intervals
def schedule_tweets():
    """
    Schedules the tweet_news function to run every hour using APScheduler.

    """
    scheduler = BlockingScheduler()
    scheduler.add_job(tweet_news, 'interval', hours=1)
    print("Scheduler started,will tweet every hour..")
    scheduler.start()

# run the tweet scheduling..
if __name__ == "__main__":
    schedule_tweets()

