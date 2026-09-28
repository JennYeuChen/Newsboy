import os
import sys
import requests
from googletrans import Translator

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: 未設定 DISCORD_WEBHOOK_URL")
    sys.exit(1)

TWITTER_HANDLE = "Dexerto"

def fetch_latest_tweet():
    # 利用 Twitter 官方 Syndication (Widget) API，穩定且不需 Token
    url = f"https://syndication.twitter.com/srv/timeline-profile/priv-raw?screen_name={TWITTER_HANDLE}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ API 回傳狀態碼: {response.status_code}")
            return None

        data = response.json()
        timeline = data.get("timeline", {})
        instructions = timeline.get("instructions", [])

        tweets = []
        for instruction in instructions:
            if instruction.get("type") == "TimelineAddEntries":
                entries = instruction.get("entries", [])
                for entry in entries:
                    content = entry.get("content", {})
                    item_content = content.get("itemContent", {})
                    tweet_results = item_content.get("tweet_results", {})
                    result = tweet_results.get("result", {})
                    if result:
                        tweets.append(result)

        if not tweets:
            print("⚠️ 未找到任何推文資料")
            return None

        return tweets[0]  # 最新的一則推文

    except Exception as e:
        print(f"❌ 抓取推文失敗: {e}")
        return None

def fetch_and_post():
    tweet = fetch_latest_tweet()

    if not tweet:
        print("❌ 無法取得 @Dexerto 的推文。")
        sys.exit(1)

    # 解析推文內容
    legacy = tweet.get("legacy", {})
    tweet_id = legacy.get("id_str")
    full_text = legacy.get("full_text", "")
    
    # 建立原推文連結
    tweet_url = f"https://x.com/{TWITTER_HANDLE}/status/{tweet_id}"

    # 提取圖片網址 (媒體附加內容)
    image_url = None
    extended_entities = legacy.get("extended_entities", {})
    media_list = extended_entities.get("media", [])
    if media_list:
        image_url = media_list[0].get("media_url_https")

    print(f"📌 最新推文 ID: {tweet_id}")
    print(f"📌 推文連結: {tweet_url}")
    print(f"📌 原文內容: {full_text[:50]}...")

    # 翻譯內文
    translator = Translator()
    try:
        translated_text = translator.translate(full_text, dest='zh-tw').text
    except Exception as e:
        print(f"⚠️ 翻譯失敗，使用原文: {e}")
        translated_text = full_text

    # 組裝 Discord Embed
    embed = {
        "title": "📰 Newsboy 快訊 (X / Twitter)",
        "description": translated_text,
        "url": tweet_url,
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
        print("🚀 Newsboy 成功推送推文到 Discord！")
    else:
        print(f"❌ 發送到 Discord 失敗，狀態碼: {response.status_code}, 回應: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_and_post()
