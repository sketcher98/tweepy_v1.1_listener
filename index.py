import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

class MyStreamListener(tweepy.Stream):
    def on_status(self, status):
        print(f"✅ New tweet from @{status.user.screen_name}: {status.text}")
        try:
            import requests
            requests.post(WEBHOOK_URL, json={
                "username": status.user.screen_name,
                "tweet": status.text,
                "tweet_id": status.id_str
            })
        except Exception as e:
            print("⚠️ Failed to send webhook:", e)

    def on_error(self, status_code):
        print("❌ Stream error:", status_code)
        return False

with open("usernames.txt", "r") as f:
    usernames = [line.strip() for line in f if line.strip()]

user_ids = []
for username in usernames:
    try:
        user = api.get_user(screen_name=username)
        user_ids.append(str(user.id))
        print(f"{username} => {user.id}")
    except Exception as e:
        print(f"Failed to resolve {username}:", e)

print("📡 Listening for tweets from:", usernames)
stream = MyStreamListener(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
stream.filter(follow=user_ids, is_async=False)