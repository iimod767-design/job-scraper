import asyncio
import os
import threading
from flask import Flask
from telegram import Bot
from telethon import TelegramClient, events

# 1. بيانات الاعتماد (Telegram App API)
API_ID = 37351508
API_HASH = "8f8c10087a3a64bc4eed894655cea8c5"

# 2. بيانات البوت وقناتك المستهدفة بالنشر
BOT_TOKEN = "8992637196:AAG0dHgABa5NP85RhmOXr7NjdvP_BXGXblE"
TARGET_CHANNEL = "@Rased_k"

# 3. القنوات المصدرية المراد سحب الوظائف منها
SOURCE_CHANNELS = [
    "@joob_99",
    "@almusaedsa",
    "@almusaedEng",
    "@EasternJobs",
    "@jobsteams",
    "@jobs333",
    "@Reem_management_jobs",
    "@atalla3",
    "@oodyyf",
]

# 4. الكلمات المفتاحية لتصفية إعلانات الوظائف
KEYWORDS = [
    "وظيفة",
    "وظائف",
    "شاغر",
    "مطلوب",
    "مهندس",
    "مراقب",
    "سجل",
    "للتقديم",
    "فني",
    "إداري",
    "فرصة",
]

# --- سيرفر الويب لإبقاء Render شغالاً ---
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running 24/7!"


def run_flask():
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)


# --- بوت التيليجرام والراصد ---
client = TelegramClient("job_monitor_session", API_ID, API_HASH)
bot = Bot(token=BOT_TOKEN)


@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def job_listener_handler(event):
  message_text = event.raw_text
  if not message_text:
    return

  if any(keyword in message_text for keyword in KEYWORDS):
    print(f"📌 تم رصد وظيفة جديدة من القناة: {event.chat.title}")
    formatted_msg = (
        f"🚨 **فرصة وظيفية جديدة**\n\n{message_text}\n\n🤖 *تم النشر"
        " أوتوماتيكياً عبر الراصد الوظيفي*"
    )
    try:
      await bot.send_message(chat_id=TARGET_CHANNEL, text=formatted_msg)
      print("✅ تم إرسال الوظيفة بنجاح إلى @Rased_k!")
    except Exception as e:
      print(f"❌ خطأ أثناء النشر: {e}")


async def run_bot():
  print("🤖 جاري تشغيل الراصد الوظيفي والاستماع للقنوات...")
  await client.start()
  await client.run_until_disconnected()


if __name__ == "__main__":
  # تشغيل سيرفر الويب في خلفية منفصلة
  threading.Thread(target=run_flask, daemon=True).start()

  # تشغيل بوت تيليجرام
  asyncio.run(run_bot())
