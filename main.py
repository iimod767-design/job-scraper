import asyncio
import os
import threading
from flask import Flask, render_template_string, request, redirect, url_for
from telegram import Bot
from telethon import TelegramClient, events

API_ID = 37351508
API_HASH = "8f8c10087a3a64bc4eed894655cea8c5"
BOT_TOKEN = "8992637196:AAG0dHgABa5NP85RhmOXr7NjdvP_BXGXblE"
TARGET_CHANNEL = "@Rased_k"

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

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# إعداد حلقة العمل
loop = asyncio.new_event_loop()
client = TelegramClient("user_session", API_ID, API_HASH, loop=loop)

login_data = {"phone": "", "hash": "", "step": "phone", "error": ""}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الراصد الوظيفي - ربط الحساب</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 350px; text-align: center; }
        input { width: 85%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 16px; }
        button { background: #3b82f6; color: white; border: none; padding: 12px 20px; width: 90%; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:hover { background: #2563eb; }
        .success { color: #22c55e; font-size: 18px; font-weight: bold; }
        .error { color: #ef4444; font-size: 14px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🤖 الراصد الوظيفي</h2>
        {% if is_authorized %}
            <p class="success">✅ البوت متصل ويراقب القنوات بنجاح!</p>
            <p style="color: #94a3b8; font-size: 14px;">يعمل الآن على مدار الساعة ويرسل الوظائف إلى @Rased_k</p>
        {% elif step == 'phone' %}
            <p>أدخل رقم جوالك مع رمز الدولة:</p>
            <form method="POST" action="/send-code">
                <input type="text" name="phone" placeholder="+9665XXXXXXXX" required>
                <button type="submit">إرسال كود التحقق</button>
            </form>
        {% elif step == 'code' %}
            <p>أدخل كود التحقق (OTP) الذي وصلك على تيليجرام:</p>
            <form method="POST" action="/verify-code">
                <input type="text" name="code" placeholder="12345" required>
                <button type="submit">تأكيد وتسجيل الدخول</button>
            </form>
        {% endif %}
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/")
def index():
  async def check():
    if not client.is_connected():
      await client.connect()
    return await client.is_user_authorized()

  is_authorized = loop.run_until_complete(check())
  step = login_data["step"]
  if is_authorized:
    step = "authorized"
  return render_template_string(
      HTML_PAGE,
      is_authorized=is_authorized,
      step=step,
      error=login_data["error"],
  )


@app.route("/send-code", methods=["POST"])
def send_code():
  phone = request.form.get("phone")
  login_data["phone"] = phone
  try:

    async def req():
      if not client.is_connected():
        await client.connect()
      res = await client.send_code_request(phone)
      login_data["hash"] = res.phone_code_hash

    loop.run_until_complete(req())
    login_data["step"] = "code"
    login_data["error"] = ""
  except Exception as e:
    login_data["error"] = str(e)
  return redirect(url_for("index"))


@app.route("/verify-code", methods=["POST"])
def verify_code():
  code = request.form.get("code")
  phone = login_data["phone"]
  phone_code_hash = login_data["hash"]
  try:

    async def verify():
      await client.sign_in(
          phone=phone, code=code, phone_code_hash=phone_code_hash
      )

    loop.run_until_complete(verify())
    login_data["step"] = "authorized"
    login_data["error"] = ""
    threading.Thread(target=start_listener, daemon=True).start()
  except Exception as e:
    login_data["error"] = str(e)
  return redirect(url_for("index"))


def start_listener():
  @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
  async def handler(event):
    msg = event.raw_text
    if not msg:
      return
    if any(k in msg for k in KEYWORDS):
      print(f"📌 تم رصد وظيفة من: {event.chat.title}")
      txt = (
          f"🚨 **فرصة وظيفية جديدة**\n\n{msg}\n\n🤖 *تم النشر أوتوماتيكياً عبر"
          " الراصد الوظيفي*"
      )
      try:
        await bot.send_message(chat_id=TARGET_CHANNEL, text=txt)
        print("✅ تم الإرسال بنجاح إلى القناة!")
      except Exception as ex:
        print(f"❌ خطأ بالنشر: {ex}")

  asyncio.set_event_loop(loop)
  loop.run_until_complete(client.run_until_disconnected())


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
  async def init():
    if not client.is_connected():
      await client.connect()
    if await client.is_user_authorized():
      threading.Thread(target=start_listener, daemon=True).start()
      print("🤖 تم العثور على الجلسة، والبدء في الاستماع...")

  loop.run_until_complete(init())
  run_flask()
