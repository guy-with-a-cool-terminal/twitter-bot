import requests
import os
import random
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from requests_oauthlib import OAuth1
from urllib.parse import quote
import time

# Load the environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.error(f'Error authenticating with Twitter: {e}')
        return None

# Set to keep track of previously tweeted news
tweeted_news = set()

# Function to get news from NewsAPI
def get_cyber_news_newsapi():
    search_terms = ['cybersecurity', 'hacking', 'data breach', 'malware', 'cyber attack', 'information security', 'phishing']
    selected_search_term = random.choice(search_terms)
    logging.info(f"Selected topic: {selected_search_term}")

    url = f'https://newsapi.org/v2/everything?q={quote(selected_search_term)}&language=en&apiKey={NEWS_API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        news = response.json()
        if news['articles']:
            articles_summary = []
            for article in news['articles']:
                title = article['title']
                description = article.get('description', 'No description available.')
                
                # Limit to 280 characters and summarize
                summary = f"**{title}**: {description[:200]}..."  # Truncate to fit within character limit
                if summary not in tweeted_news:
                    articles_summary.append(summary)
                    tweeted_news.add(summary)  # Track tweeted summaries

            return articles_summary
        return ["No new news found!"]
    except requests.exceptions.RequestException as e:
        logging.error(f"NewsAPI request error: {e}")
        return ["Error fetching news!"]

# Function to get news from GNews API
def get_from_secondapi():
    search_terms = ['cybersecurity', 'hacking', 'data breach', 'malware', 'cyber attack', 'information security', 'phishing']
    selected_search_term = random.choice(search_terms)
    logging.info(f"Selected topic: {selected_search_term}")

    url = f'https://gnews.io/api/v4/search?q={quote(selected_search_term)}&language=en&token={GNEWS_API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        news = response.json()
        if news['articles']:
            articles_summary = []
            for article in news['articles']:
                title = article['title']
                description = article.get('description', 'No description available.')
                
                # Limit to 280 characters and summarize
                summary = f"**{title}**: {description[:200]}..."  # Truncate to fit within character limit
                if summary not in tweeted_news:
                    articles_summary.append(summary)
                    tweeted_news.add(summary)  # Track tweeted summaries

            return articles_summary
        return ["No new news found!"]
    except requests.exceptions.RequestException as e:
        logging.error(f"GNewsAPI request error: {e}")
        return ["Error fetching news!"]

def get_cyber_news():
    api_choice = random.choice(['newsapi', 'secondapi'])
    logging.info(f"Selected API: {api_choice}")  # Debug which API is selected
    if api_choice == 'newsapi':
        return get_cyber_news_newsapi()
    elif api_choice == 'secondapi':
        return get_from_secondapi()
    else:
        return ["Error selecting!"]

# Function to create a thread of tweets
def create_tweet_thread(session, auth, tweets):
    url = "https://api.twitter.com/2/tweets"
    
    # Post the first tweet
    response = session.post(url, auth=auth, json={"text": tweets[0]})
    
    if response.status_code == 201:
        logging.info("First tweet posted: %s", tweets[0])
        tweet_id = response.json()['data']['id']  # Get the ID of the first tweet
        
        # Post subsequent tweets in the thread
        for tweet in tweets[1:]:
            if len(tweet) > 280:
                logging.error(f"Tweet exceeds character limit: {tweet}")
                continue  # Skip tweets that are too long
            
            time.sleep(10)  # Add a 10-second delay between tweets in the thread

            response = session.post(url, auth=auth, json={"text": tweet, "reply": {"in_reply_to_tweet_id": tweet_id}})
            if response.status_code == 201:
                logging.info("Thread tweet posted: %s", tweet)
                tweet_id = response.json()['data']['id']  # Update tweet_id for the next reply
            elif response.status_code == 429:
                logging.error(f"Rate limit hit! Waiting before retrying: {response.json()}")
                time.sleep(900)  # Sleep for 15 minutes before retrying if rate limit is hit
            else:
                logging.error(f"Failed to post thread tweet: {response.json()} - Status Code: {response.status_code}")
    elif response.status_code == 429:
        logging.error(f"Rate limit hit! Waiting before retrying: {response.json()}")
        time.sleep(900)  # Sleep for 15 minutes before retrying if rate limit is hit
    else:
        logging.error(f"Failed to tweet: {response.json()} - Status Code: {response.status_code}")


# Function to tweet the news
def tweet_news(session, auth):
    articles_summary = get_cyber_news()
    logging.info(f"Fetched news summaries: {articles_summary}")

    if articles_summary:
        # Create a thread of tweets with the content of all articles
        create_tweet_thread(session, auth, articles_summary)
    else:
        logging.warning("No news to tweet at this time.")

# Scheduler to run the tweet function at regular intervals
def schedule_tweets(session, auth):
    tweet_news(session, auth)
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: tweet_news(session, auth), 'interval', hours=2)
    logging.info("Scheduler started, will tweet every 16 minutes...")
    scheduler.start()

# Run the tweet scheduling
if __name__ == "__main__":
    check_env_keys()
    session, auth = authenticate_twitter()
    if session:
        schedule_tweets(session, auth)
