import os
import sys
import feedparser
import requests
from googletrans import Translator

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: 未設定 DISCORD_WEBHOOK_URL")
    sys.exit(1)

# 使用 RSSHub 的 Twitter 路由 (提供多個備用公共節點)
RSSHUB_NODES = [
    "https://rsshub.app/twitter/user/Dexerto",
    "https://rsshub.rssforever.com/twitter/user/Dexerto",
    "https://rsshub.lit.edu.mo/twitter/user/Dexerto"
]

def fetch_feed():
    for url in RSSHUB_NODES:
        print(f"🔍 嘗試抓取 RSSHub 節點: {url}")
        try:
            # 加上 User-Agent 避免被阻擋
            feed = feedparser.parse(url, agent="Mozilla/5.0")
            if feed.entries and len(feed.entries) > 0:
                print(f"✅ 成功從 {url} 抓取到 {len(feed.entries)} 則內容！")
                return feed.entries
            else:
                print(f"⚠️ {url} 未返回有效文章，嘗試下一個節點...")
        except Exception as e:
            print(f"❌ 節點 {url} 抓取失敗: {e}")
    return None

def fetch_and_post():
    entries = fetch_feed()

    if not entries:
        print("❌ 所有 RSSHub 節點皆無法抓取到 @Dexerto 的推文。")
        sys.exit(1)

    latest = entries[0]
    title = latest.get('title', '')
    summary = latest.get('summary', '')
    link = latest.get('link', '')

    # 嘗試提取圖片
    image_url = None
    if 'media_content' in latest and len(latest.media_content) > 0:
        image_url = latest.media_content[0].get('url')
    elif 'enclosures' in latest and len(latest.enclosures) > 0:
        image_url = latest.enclosures[0].get('url')

    # 文字處理 (優先取 title，若太短則取 summary)
    raw_text = title if len(title) > len(summary) else summary
    # 清理簡單 HTML 標籤
    clean_text = raw_text.split('<')[0]

    print(f"📌 抓取到的最新連結: {link}")
    print(f"📌 原文內容: {clean_text[:50]}...")

    # 翻譯內容
    translator = Translator()
    try:
        translated_text = translator.translate(clean_text, dest='zh-tw').text
    except Exception as e:
        print(f"⚠️ 翻譯失敗，使用原文: {e}")
        translated_text = clean_text

    # 組裝 Discord Embed
    embed = {
        "title": "📰 Newsboy 快訊 (X / Twitter)",
        "description": translated_text,
        "url": link,
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
