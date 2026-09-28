import os
import sys
import feedparser
import requests
from googletrans import Translator

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: 未設定 DISCORD_WEBHOOK_URL")
    sys.exit(1)

# Dexerto 官方網站 RSS
FEED_URL = "https://www.dexerto.com/feed/"

def fetch_and_post():
    print(f"🔍 正在抓取 Dexerto 官方新聞 RSS: {FEED_URL}")
    feed = feedparser.parse(FEED_URL)
    
    if not feed.entries:
        print("❌ 未能抓取到任何新聞文章。")
        sys.exit(1)

    # 取得最新的一篇文章
    latest_entry = feed.entries[0]
    title = latest_entry.get("title", "")
    summary = latest_entry.get("summary", "")
    link = latest_entry.get("link", "")
    
    # 嘗試提取文章的高清封面圖
    image_url = None
    if 'media_content' in latest_entry and len(latest_entry.media_content) > 0:
        image_url = latest_entry.media_content[0].get('url')
    elif 'media_thumbnail' in latest_entry and len(latest_entry.media_thumbnail) > 0:
        image_url = latest_entry.media_thumbnail[0].get('url')
    elif 'enclosures' in latest_entry and len(latest_entry.enclosures) > 0:
        image_url = latest_entry.enclosures[0].get('url')

    # 摘要文字清理（截斷過長 HTML 內文）
    clean_summary = summary.split('<')[0][:300] if summary else ""

    print(f"📌 抓取到的最新文章: {title}")
    print(f"📌 文章連結: {link}")

    # 翻譯標題與摘要為繁體中文
    translator = Translator()
    try:
        translated_title = translator.translate(title, dest='zh-tw').text
        translated_summary = translator.translate(clean_summary, dest='zh-tw').text if clean_summary else ""
    except Exception as e:
        print(f"⚠️ 翻譯失敗，使用英文原文: {e}")
        translated_title = title
        translated_summary = clean_summary

    # 組裝 Discord Embed
    embed = {
        "title": f"📰 Newsboy 快訊：{translated_title}",
        "description": translated_summary,
        "url": link,
        "color": 15258703,  # Dexerto 品牌橘色
        "footer": {
            "text": "Newsboy • 轉譯自 Dexerto.com"
        }
    }
    
    if image_url:
        embed["image"] = {"url": image_url}

    payload = {
        "username": "Newsboy",
        "avatar_url": "https://i.imgur.com/8N69fS7.png",
        "embeds": [embed]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print("🚀 Newsboy 成功推送最新新聞到 Discord！")
    else:
        print(f"❌ 發送到 Discord 失敗，狀態碼: {response.status_code}, 回應: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_and_post()
