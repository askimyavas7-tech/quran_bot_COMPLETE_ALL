import telebot
import json
import random
import os
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

with open("data/quran_tr.json", encoding="utf-8") as f:
    quran = json.load(f)

RECITERS = {
    "alafasy": "ar.alafasy",
    "basit": "ar.abdulbasitmurattal",
    "sudais": "ar.abdurrahmansudais"
}

user_reciter = {}

def random_ayah():
    return random.choice(quran)

def format_ayah(a):
    return (
        f"📖 *{a['surah']} {a['ayah']}*\n\n"
        f"🕋 {a['text']}\n\n"
        f"📘 *Meal:*\n{a['meal']}"
    )

@bot.message_handler(commands=["start"])
def start(message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📖 Rastgele Ayet", callback_data="random"),
        InlineKeyboardButton("🔊 Sesli Ayet", callback_data="voice")
    )
    kb.add(
        InlineKeyboardButton("🎧 Sesli Sure (Yasin)", callback_data="surah"),
        InlineKeyboardButton("🎙 Hafız Seç", callback_data="reciter")
    )
    bot.send_message(
        message.chat.id,
        "🌙 *Kur'an-ı Kerim Botu*\nTüm özellikler aktif.",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    reciter = user_reciter.get(user_id, "alafasy")

    if call.data == "random":
        a = random_ayah()
        bot.send_message(chat_id, format_ayah(a))

    elif call.data == "voice":
        a = random_ayah()
        url = f"https://cdn.islamic.network/quran/audio/128/{RECITERS[reciter]}/{a['ayah']}.mp3"
        bot.send_audio(chat_id, url, caption=f"{a['surah']} {a['ayah']}")

    elif call.data == "surah":
        url = f"https://cdn.islamic.network/quran/audio-surah/128/{RECITERS[reciter]}/36.mp3"
        bot.send_audio(chat_id, url, caption="Yasin Suresi")

    elif call.data == "reciter":
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("🎙 Alafasy", callback_data="r_alafasy"),
            InlineKeyboardButton("🎙 Abdul Basit", callback_data="r_basit"),
            InlineKeyboardButton("🎙 Sudais", callback_data="r_sudais")
        )
        bot.send_message(chat_id, "🎙 Hafız seç:", reply_markup=kb)

    elif call.data.startswith("r_"):
        user_reciter[user_id] = call.data.replace("r_", "")
        bot.answer_callback_query(call.id, "Hafız ayarlandı")

def auto_send():
    while True:
        if CHAT_ID:
            a = random_ayah()
            bot.send_message(CHAT_ID, format_ayah(a))
        time.sleep(21600)

threading.Thread(target=auto_send, daemon=True).start()

bot.infinity_polling()
def load_json(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@bot.message_handler(commands=["favori"])
def show_favorites(msg):
    favs = load_json("data/favorites.json")
    user_id = str(msg.from_user.id)

    if user_id not in favs or not favs[user_id]:
        bot.send_message(msg.chat.id, "⭐ Henüz favori ayetin yok.")
        return

    for a in favs[user_id][-5:]:
        bot.send_message(msg.chat.id, format_ayah(a))
