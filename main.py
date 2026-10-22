import os
import asyncio
from flask import Flask, render_template_string, request, redirect, url_for
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

KEYWORDS = ["وظيفة", "وظائف", "شاغر", "مطلوب", "مهندس", "مراقب", "سجل", "للتقديم", "فني", "إداري", "فرصة"]

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

login_state = {"phone": "", "hash": "", "step": "phone", "error": ""}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الراصد الوظيفي - ربط الحساب</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        .card { background: #1e293b; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 100%; max-width: 400px; text-align: center; }
        h2 { margin-top: 0; color: #38bdf8; }
        input { width: 100%; padding: 14px; margin: 12px 0; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 16px; box-sizing: border-box; text-align: center; }
        button { background: #2563eb; color: white; border: none; padding: 14px; width: 100%; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:hover { background: #1d4ed8; }
        .success { color: #4ade80; font-size: 18px; font-weight: bold; line-height: 1.5; }
        .error { color: #f87171; font-size: 14px; margin-top: 12px; background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🤖 الراصد الوظيفي</h2>
        {% if step == 'authorized' %}
            <div class="success">
                ✅ الحساب متصل بنجاح!
                <p style="color: #94a3b8; font-size: 14px; font-weight: normal; margin-top: 8px;">الراصد يعمل الآن تلقائياً ويراقب القنوات ويرسل الوظائف إلى @Rased_k</p>
            </div>
        {% elif step == 'phone' %}
            <p style="color: #cbd5e1;">أدخل رقم جوالك المربوط بتيليجرام مع رمز الدولة:</p>
            <form method="POST" action="/send-code">
                <input type="text" name="phone" placeholder="+9665XXXXXXXX" required>
                <button type="submit">إرسال كود التحقق</button>
            </form>
        {% elif step == 'code' %}
            <p style="color: #cbd5e1;">أدخل كود التحقق (OTP) الذي وصلك على تطبيق تيليجرام:</p>
            <form method="POST" action="/verify-code">
                <input type="text" name="code" placeholder="12345" required>
                <button type="submit">تأكيد وتسجيل الدخول</button>
            </form>
        {% endif %}
        {% if error %}
            <div class="error">{{ error }}</div>
        {%/ if %}
    </div>
</body>
</html>
"""

def run_async_safe(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route("/")
def index():
    async def check():
        async with TelegramClient("user_session", API_ID, API_HASH) as client:
            return await client.is_user_authorized()
    
    try:
        is_auth = run_async_safe(check())
        if is_auth:
            login_state["step"] = "authorized"
    except Exception:
        pass

    return render_template_string(HTML_PAGE, step=login_state["step"], error=login_state["error"])

@app.route("/send-code", methods=["POST"])
def send_code():
    phone = request.form.get("phone", "").strip()
    login_state["phone"] = phone
    async def req():
        client = TelegramClient("user_session", API_ID, API_HASH)
        await client.connect()
        res = await client.send_code_request(phone)
        login_state["hash"] = res.phone_code_hash
        await client.disconnect()

    try:
        run_async_safe(req())
        login_state["step"] = "code"
        login_state["error"] = ""
    except Exception as e:
        login_state["error"] = f"خطأ: {str(e)}"
    return redirect(url_for("index"))

@app.route("/verify-code", methods=["POST"])
def verify_code():
    code = request.form.get("code", "").strip()
    async def verify():
        client = TelegramClient("user_session", API_ID, API_HASH)
        await client.connect()
        await client.sign_in(phone=login_state["phone"], code=code, phone_code_hash=login_state["hash"])
        await client.disconnect()

    try:
        run_async_safe(verify())
        login_state["step"] = "authorized"
        login_state["error"] = ""
    except Exception as e:
        login_state["error"] = f"كود خاطئ: {str(e)}"
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
