import os
import sys
import feedparser
import requests
from googletrans import Translator

# 取得環境變數中的 Discord Webhook URL
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: 未設定 DISCORD_WEBHOOK_URL 環境變數")
    sys.exit(1)

# Dexerto RSS 來源
FEED_URL = "https://www.dexerto.com/feed/"

def fetch_and_post():
    feed = feedparser.parse(FEED_URL)
    if not feed.entries:
        print("未抓取到任何文章")
        return

    # 取得最新的一篇文章
    latest_entry = feed.entries[0]
    title = latest_entry.title
    summary = latest_entry.get("summary", "")
    link = latest_entry.link
    
    # 嘗試抓取文章圖片
    image_url = None
    if 'media_content' in latest_entry and len(latest_entry.media_content) > 0:
        image_url = latest_entry.media_content[0].get('url')
    elif 'media_thumbnail' in latest_entry and len(latest_entry.media_thumbnail) > 0:
        image_url = latest_entry.media_thumbnail[0].get('url')

    # 翻譯內容為繁體中文
    translator = Translator()
    try:
        translated_title = translator.translate(title, dest='zh-tw').text
        # 清理 summary 中的 HTML 標籤（若有）並截斷過長文字
        clean_summary = summary.split('<')[0][:300] if summary else ""
        translated_summary = translator.translate(clean_summary, dest='zh-tw').text if clean_summary else ""
    except Exception as e:
        print(f"翻譯失敗，將使用原文: {e}")
        translated_title = title
        translated_summary = summary[:300]

    # 組裝 Discord Embed 訊息
    embed = {
        "title": f"📰 Newsboy 快訊：{translated_title}",
        "description": translated_summary,
        "url": link,
        "color": 15258703,  # 橘黃色
        "footer": {
            "text": "Newsboy • 轉譯自 Dexerto"
        }
    }
    
    if image_url:
        embed["image"] = {"url": image_url}

    # 發送到 Discord
    payload = {
        "username": "Newsboy",
        "avatar_url": "https://i.imgur.com/8N69fS7.png",  # 可替換成你喜歡的大頭貼網址
        "embeds": [embed]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print("Newsboy 成功推送最新新聞！")
    else:
        print(f"發送失敗，狀態碼: {response.status_code}, 回應: {response.text}")

if __name__ == "__main__":
    fetch_and_post()
