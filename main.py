import os
import sys
import feedparser
import requests
from googletrans import Translator

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: 未設定 DISCORD_WEBHOOK_URL")
    sys.exit(1)

FEED_URL = "https://www.dexerto.com/feed/"
HISTORY_FILE = "last_posted.txt"  # 用來記錄上次發送過的文章網址

def get_last_posted_link():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_last_posted_link(link):
    with open(HISTORY_FILE, "w") as f:
        f.write(link)

def fetch_and_post():
    feed = feedparser.parse(FEED_URL)
    
    if not feed.entries:
        print("❌ 未能抓取到任何新聞文章。")
        sys.exit(1)

    latest_entry = feed.entries[0]
    link = latest_entry.get("link", "")
    
    # 🔍 檢查是否已經發送過這篇文章
    last_link = get_last_posted_link()
    if link == last_link:
        print("ℹ️ 最新文章已經發送過，本次不重複推送。")
        return

    title = latest_entry.get("title", "")
    summary = latest_entry.get("summary", "")
    
    # 提取圖片
    image_url = None
    if 'media_content' in latest_entry and len(latest_entry.media_content) > 0:
        image_url = latest_entry.media_content[0].get('url')
    elif 'media_thumbnail' in latest_entry and len(latest_entry.media_thumbnail) > 0:
        image_url = latest_entry.media_thumbnail[0].get('url')
    elif 'enclosures' in latest_entry and len(latest_entry.enclosures) > 0:
        image_url = latest_entry.enclosures[0].get('url')

    clean_summary = summary.split('<')[0][:300] if summary else ""

    # 翻譯
    translator = Translator()
    try:
        translated_title = translator.translate(title, dest='zh-tw').text
        translated_summary = translator.translate(clean_summary, dest='zh-tw').text if clean_summary else ""
    except Exception as e:
        print(f"⚠️ 翻譯失敗，使用原文: {e}")
        translated_title = title
        translated_summary = clean_summary

    embed = {
        "title": f"{translated_title}",
        "description": translated_summary,
        "url": link,
        "color": 1940434,  # Twitter 藍
        "footer": {
        }
    }
    
    if image_url:
        embed["image"] = {"url": image_url}

    payload = {
        "username": "新們男孩",
        "avatar_url": "https://i.imgur.com/8N69fS7.png",
        "embeds": [embed]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print("🚀 新聞男成功推送最新新聞到 Discord！")
        save_last_posted_link(link)  # 記錄本次發送的連結
    else:
        print(f"❌ 發送到 Discord 失敗: {response.status_code}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_and_post()
