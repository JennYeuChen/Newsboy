import os
import sys
import requests
from ntscraper import Nitter
from googletrans import Translator

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: 未設定 DISCORD_WEBHOOK_URL")
    sys.exit(1)

def fetch_and_post():
    # 初始化 scraper (會自動搜尋目前尚在運作的公用鏡站)
    scraper = Nitter()
    
    try:
        # 抓取 @Dexerto 最新 5 則推文
        tweets = scraper.get_tweets("Dexerto", mode='user', number=5)
    except Exception as e:
        print(f"抓取 X 貼文失敗: {e}")
        return

    if not tweets.get('tweets'):
        print("未抓取到任何推文")
        return

    # 取最新的推文
    latest_tweet = tweets['tweets'][0]
    tweet_text = latest_tweet.get('text', '')
    tweet_link = latest_tweet.get('link', '')
    pictures = latest_tweet.get('pictures', [])
    
    image_url = pictures[0] if pictures else None

    # 翻譯推文內容
    translator = Translator()
    try:
        translated_text = translator.translate(tweet_text, dest='zh-tw').text
    except Exception as e:
        print(f"翻譯失敗: {e}")
        translated_text = tweet_text

    embed = {
        "title": "📰 Newsboy 快訊 (X / Twitter)",
        "description": translated_text,
        "url": tweet_link,
        "color": 1940434,  # Twitter 藍
        "footer": {
            "text": "Newsboy • 轉譯自 @Dexerto"
        }
    }
    
    if image_url:
        embed["image"] = {"url": image_url}

    payload = {
        "username": "Newsboy",
        "avatar_url": "https://abs.twimg.com/icons/apple-touch-icon-192x192.png",
        "embeds": [embed]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print("Newsboy 成功推送 X 貼文！")
    else:
        print(f"發送失敗: {response.status_code}")

if __name__ == "__main__":
    fetch_and_post()
