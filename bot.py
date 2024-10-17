import requests
import os
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from requests_oauthlib import OAuth1
from urllib.parse import quote
from datetime import datetime

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

# Function to fetch news from a given API
def fetch_news(api_url, query_params):
    try:
        response = requests.get(api_url, params=query_params)
        if response.status_code == 200:
            news = response.json()
            if news['articles']:
                for article in news['articles']:
                    title = article['title']
                    article_url = article['url']
                    # Ensure the article is not already tweeted
                    if (title, article_url) not in tweeted_news:
                        print(f"Adding to tweet: {title} - {article_url}")
                        return title, article_url, article
            return "No new news found!", "", None
        else:
            return f"Error fetching news: {response.json().get('message')}", "", None
    except Exception as e:
        return f"Request error: {e}", "", None

# Function to get cybersecurity news from NewsAPI
def get_cyber_news_newsapi():
    search_terms = ['cybersecurity', 'hacking', 'data breach', 'malware', 'cyber attack', 'information security', 'phishing']
    selected_search_term = random.choice(search_terms)
    print(f"Selected topic: {selected_search_term}")
    query_params = {'q': selected_search_term, 'language': 'en', 'apiKey': NEWS_API_KEY}
    return fetch_news('https://newsapi.org/v2/everything', query_params)

# Function to get news from GNews API
def get_from_secondapi():
    search_terms = ['cybersecurity', 'hacking', 'data breach', 'malware', 'cyber attack', 'information security', 'phishing']
    selected_search_term = random.choice(search_terms)
    print(f"Selected topic: {selected_search_term}")
    query_params = {'q': selected_search_term, 'language': 'en', 'token': GNEWS_API_KEY}
    return fetch_news('https://gnews.io/api/v4/search', query_params)

def get_cyber_news():
    api_choice = random.choice(['newsapi', 'secondapi'])
    print(f"Selected API: {api_choice}")
    if api_choice == 'newsapi':
        return get_cyber_news_newsapi()
    else:
        return get_from_secondapi()

# Helper function to split content into tweet-sized chunks
def split_content_into_tweets(content, max_words=500, max_tweet_length=280):
    tweets = []
    words = content.split()
    current_tweet = ""

    for word in words:
        # Check if adding the next word exceeds the tweet length
        if len(current_tweet) + len(word) + 1 <= max_tweet_length:
            current_tweet += f" {word}" if current_tweet else word
        else:
            # When the tweet reaches the max length, save it and start a new tweet
            tweets.append(current_tweet)
            current_tweet = word  # Start a new tweet with the current word

        # If the current tweet reaches the max word limit, save it and start a new tweet
        if len(current_tweet.split()) >= max_words:
            tweets.append(current_tweet)
            current_tweet = ""

    # Append any remaining words as a final tweet
    if current_tweet:
        tweets.append(current_tweet)

    return tweets

# Function to get detailed content from the news article
def get_news_content(article):
    description = article.get('description', '')
    content = article.get('content', '')
    combined_content = f"{description} {content}".strip()
    return combined_content if combined_content else article.get('title', 'No content available.')

# Function to tweet news in a thread with more details in replies
def tweet_news(session, auth):
    news_title, news_url, article = get_cyber_news()
    print(f"Fetched news: {news_title}, URL: {news_url}")
    
    if news_url:
        # Fetch the news content from the API
        article_content = get_news_content(article)
        
        # Split the article content into tweet-sized chunks
        tweets = split_content_into_tweets(article_content, max_words=500, max_tweet_length=280)
        
        # First tweet contains the news title and a summary of the article
        tweet_text = f"{news_title} - {article_content[:250]}... \nRead more: {news_url}"  # Including a link in the main tweet
        
        url = "https://api.twitter.com/2/tweets"
        
        # Post the first tweet with the title and link
        response = session.post(url, auth=auth, json={"text": tweet_text})
        
        if response.status_code == 201:
            print(f"First tweet posted: {tweet_text}")
            first_tweet_id = response.json().get('data', {}).get('id')
            previous_tweet_id = first_tweet_id
            
            # Now, post the detailed replies
            for tweet_part in tweets:
                thread_response = session.post(
                    url,
                    auth=auth,
                    json={"text": tweet_part, "reply": {"in_reply_to_tweet_id": previous_tweet_id}}
                )
                
                if thread_response.status_code == 201:
                    print(f"Thread continued with: {tweet_part}")
                    previous_tweet_id = thread_response.json().get('data', {}).get('id')
                else:
                    print(f"Failed to post part of thread: {thread_response.json().get('message')}")
                    return

            # Optionally, you can add a final tweet summarizing or inviting discussion
            final_tweet = "What do you think about this news? Let's discuss!"
            final_response = session.post(
                url,
                auth=auth,
                json={"text": final_tweet, "reply": {"in_reply_to_tweet_id": previous_tweet_id}}
            )
            
            if final_response.status_code == 201:
                print(f"Final tweet posted for discussion: {final_tweet}")
                tweeted_news.add((news_title, news_url))
            else:
                print(f"Failed to post final tweet: {final_response.json().get('message')}")
        else:
            print(f"Failed to tweet: {response.json().get('message')}")
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
