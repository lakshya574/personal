import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import threading
from flask import Flask

# --- CONFIGURATION ---
API_TOKEN = "8640344823:AAHmk3NbLlvxe-fFtskDlcVdR-kbCjDvDDs" 
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME', '@luffycdgf') 

bot = telebot.TeleBot(API_TOKEN)

# --- DUMMY WEB SERVER (FOR RENDER FREE TIER) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_web_server():
    # Render assigns a dynamic port, we must bind to it
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    # Run the web server in a separate background thread
    t = threading.Thread(target=run_web_server)
    t.start()

# --- BOT LOGIC ---
def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if check_membership(user_id):
        bot.reply_to(message, "✅ Welcome! You are a member of the channel. You can now use the bot.")
    else:
        markup = InlineKeyboardMarkup()
        channel_url = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
        join_btn = InlineKeyboardButton("📢 Join Channel", url=channel_url)
        check_btn = InlineKeyboardButton("✅ I have joined", callback_data="check_join")
        
        markup.add(join_btn)
        markup.add(check_btn)
        
        bot.reply_to(
            message, 
            "⚠️ **Access Denied!**\n\nYou must join our official channel to use this bot.", 
            reply_markup=markup,
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check(call):
    user_id = call.from_user.id
    if check_membership(user_id):
        bot.answer_callback_query(call.id, "Thank you for joining!")
        bot.edit_message_text(
            "✅ Access granted! Send /start again to begin.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "❌ You haven't joined yet! Please join first.", show_alert=True)

# --- START EVERYTHING ---
if __name__ == '__main__':
    # 1. Start the dummy web server to trick Render
    keep_alive()
    
    # 2. Start the Telegram bot
    print("Bot is starting...")
    bot.infinity_polling()
