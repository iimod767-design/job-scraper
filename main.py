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
        if not msg:
            return
            
        msg_lower = msg.lower()
        if any(k.lower() in msg_lower for k in KEYWORDS):
            print("📌 تم رصد منشور وظيفي جديد!")
            txt = f"🚨 **فرصة وظيفية جديدة**\n\n{msg}\n\n🤖 *تم النشر أوتوماتيكياً عبر الراصد الوظيفي*"
            try:
                await bot.send_message(chat_id=TARGET_CHANNEL, text=txt)
                print("✅ تم الإرسال بنجاح إلى @Rased_k")
            except Exception as ex:
                print(f"❌ خطأ في الإرسال: {ex}")

    async def main():
        print("⚡ جاري الاتصال بتيليجرام...")
        await client.start()
        print("🚀 الاتصال موثق وجاري الاستماع للقنوات الآن...")
        await client.run_until_disconnected()

    try:
        loop.run_until_complete(main())
    except Exception as e:
        print(f"❌ خطأ في المحرك: {e}")

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

if __name__ == "__main__":
    t = threading.Thread(target=start_telegram_listener, daemon=True)
    t.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
