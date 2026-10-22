import os
import asyncio
import threading
from flask import Flask, render_template_string
from telegram import Bot
from telethon import TelegramClient, events

API_ID = 37351508
API_HASH = "8f8c10087a3a64bc4eed894655cea8c5"
BOT_TOKEN = "8992637196:AAG0dHgABa5NP85RhmOXr7NjdvP_BXGXblE"
TARGET_CHANNEL = "@Rased_k"

SOURCE_CHANNELS = [
    "@joob_99", "@almusaedsa", "@almusaedEng", "@EasternJobs",
    "@jobsteams", "@jobs333", "@Reem_management_jobs", "@atalla3", "@oodyyf"
]

# قائمة كلمات مفتاحية شاملة (بالعربي والإنجليزي ومع صيغ الجمع)
KEYWORDS = [
    "وظيفة", "وظائف", "شاغر", "مطلوب", "مهندس", "مهندسين", "مراقب", "سجل", "للتقديم", "فني", "إداري", "فرصة", "اعلان توظيف",
    "engineer", "engineers", "safety", "quality", "project", "manager", "job", "jobs", "hse", "technician"
]

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الراصد الوظيفي</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 30px; border-radius: 16px; text-align: center; max-width: 400px; }
        .success { color: #4ade80; font-size: 18px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🤖 الراصد الوظيفي</h2>
        <div class="success">
            ✅ النظام يعمل وفي حالة استماع مباشر!
            <p style="color: #94a3b8; font-size: 14px; font-weight: normal;">يتم سحب الوظائف ونشرها تلقائياً على @Rased_k</p>
        </div>
    </div>
</body>
</html>
"""

def start_telegram_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    client = TelegramClient("user_session", API_ID, API_HASH, loop=loop)

    @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
    async def handler(event):
        msg = event.raw_text
        if
