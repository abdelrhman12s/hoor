import telebot
from telebot import types
import requests
import json

# =================== CONFIG ===================
BOT_TOKEN = "8186750168:AAF6GONeh2xZ7Tfex0d2YEVQVfU2FL-tUd0"
GEMINI_API_KEY = "AIzaSyDadpkfov7Wnd2NQj7UaW2bEAwQ87uqGhE"
ADMIN_PASS = "6666"  # الرمز السري للدخول إلى لوحة الأدمن

bot = telebot.TeleBot(BOT_TOKEN)

# =================== التخزين ===================
users = set()
story_history = {}

# =================== توليد القصص ===================
def generate_horror_story(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()
    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return "حدث خطأ أثناء توليد القصة. حاول مرة أخرى."

# =================== أوامر المستخدم ===================
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    users.add(uid)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📖 أرعبني الآن", "🗂️ قصصي السابقة")
    markup.add("🧠 تواصل مع المطور")
    bot.send_message(uid, "👻 مرحبًا بك في بوت الرعب! اضغط \"أرعبني الآن\" لتبدأ رحلتك المظلمة...", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📖 أرعبني الآن")
def horror_now(msg):
    uid = msg.from_user.id
    prompt = "اكتب لي قصة رعب مرعبة ومظلمة ومرعبة جدًا لم يتم سردها من قبل"
    bot.send_message(uid, "🕯️ يتم الآن استدعاء الأرواح... انتظر قليلًا!")
    story = generate_horror_story(prompt)
    bot.send_message(uid, story)
    story_history.setdefault(uid, []).append(story)

@bot.message_handler(func=lambda msg: msg.text == "🗂️ قصصي السابقة")
def show_history(msg):
    uid = msg.from_user.id
    history = story_history.get(uid, [])
    if history:
        for i, s in enumerate(history[-5:], 1):
            bot.send_message(uid, f"📚 قصة #{i}:\n{s}")
    else:
        bot.send_message(uid, "📭 لا يوجد لديك قصص محفوظة حتى الآن.")

@bot.message_handler(func=lambda msg: msg.text == "🧠 تواصل مع المطور")
def contact_dev(msg):
    uid = msg.from_user.id
    bot.send_message(uid, "📩 تواصل مع المطور: @Abd0_technical")

# =================== لوحة الأدمن ===================
@bot.message_handler(commands=['admin'])
def admin_panel(msg):
    uid = msg.from_user.id
    args = msg.text.split()

    if len(args) == 2 and args[1] == ADMIN_PASS:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📊 إحصائيات البوت", "📢 إرسال إعلان")
        markup.add("⬅️ رجوع")
        bot.send_message(uid, "🎩 تم الدخول إلى لوحة الأدمن بنجاح", reply_markup=markup)
    else:
        bot.send_message(uid, "🚫 رمز الأدمن غير صحيح.")

@bot.message_handler(func=lambda msg: msg.text == "📊 إحصائيات البوت")
def stats(msg):
    bot.send_message(msg.chat.id, f"👥 عدد المستخدمين: {len(users)}")

@bot.message_handler(func=lambda msg: msg.text == "📢 إرسال إعلان")
def broadcast(msg):
    sent_msg = bot.send_message(msg.chat.id, "📝 أرسل نص الإعلان الآن:")
    bot.register_next_step_handler(sent_msg, send_broadcast)

def send_broadcast(msg):
    for uid in users:
        try:
            bot.send_message(uid, f"📢 إعلان من المطور:\n\n{msg.text}")
        except:
            pass
    bot.send_message(msg.chat.id, "✅ تم إرسال الإعلان.")

@bot.message_handler(func=lambda msg: msg.text == "⬅️ رجوع")
def back_to_main(msg):
    start(msg)

# =================== تشغيل البوت ===================
bot.infinity_polling()
