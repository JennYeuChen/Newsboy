import os
import sys
import requests
from ntscraper import Nitter
from googletrans import Translator

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: 未設定 DISCORD_WEBHOOK_URL")
    sys.exit(1)

# 可用的 Nitter 鏡站網址清單
INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.hu",
    "https://nitter.cz"
]

def fetch_tweets():
    # 正確初始化 ntscraper (不傳入無效參數)
    scraper = Nitter(log_level=1)
    
    for instance in INSTANCES:
        print(f"🔍 嘗試使用 Nitter 鏡站: {instance}")
        try:
            # 在 get_tweets 時傳入 instance 參數
            tweets = scraper.get_tweets("Dexerto", mode='user', number=5, instance=instance)
            
            if tweets and tweets.get('tweets') and len(tweets['tweets']) > 0:
                print(f"✅ 成功從 {instance} 抓取到 {len(tweets['tweets'])} 則推文！")
                return tweets['tweets']
            else:
                print(f"⚠️ {instance} 回傳空資料，切換下一個鏡站...")
        except Exception as e:
            print(f"❌ 鏡站 {instance} 抓取失敗: {e}")
            
    return None

def fetch_and_post():
    tweets = fetch_tweets()

    if not tweets:
        print("❌ 所有 Nitter 鏡站皆無法抓取到 @Dexerto 的推文。")
        sys.exit(1)

    # 取最新的第一則推文
    latest_tweet = tweets[0]
    tweet_text = latest_tweet.get('text', '')
    tweet_link = latest_tweet.get('link', '')
    pictures = latest_tweet.get('pictures', [])
    
    print(f"📌 抓取到的最新推文連結: {tweet_link}")
    print(f"📌 原文內容: {tweet_text[:50]}...")

    image_url = pictures[0] if pictures else None

    # 翻譯推文內容
    translator = Translator()
    try:
        translated_text = translator.translate(tweet_text, dest='zh-tw').text
    except Exception as e:
        print(f"⚠️ 翻譯失敗，使用原文: {e}")
        translated_text = tweet_text

    # 組裝 Discord Embed
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

    # 發送到 Discord
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print("🚀 Newsboy 成功推送推文到 Discord！")
    else:
        print(f"❌ 發送到 Discord 失敗，狀態碼: {response.status_code}, 回應: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_and_post()
