import os
import telebot
from routeros_api import RouterOsApiPool
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
ROUTER_IP = os.getenv("ROUTER_IP")
ROUTER_USER = os.getenv("ROUTER_USER")
ROUTER_PASS = os.getenv("ROUTER_PASS")
ROUTER_PORT = int(os.getenv("ROUTER_PORT", 8728))

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive 💙"

def connect_router():
    pool = RouterOsApiPool(
        host=ROUTER_IP,
        username=ROUTER_USER,
        password=ROUTER_PASS,
        port=ROUTER_PORT,
        plaintext_login=True
    )
    api = pool.get_api()
    return api, pool

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hey luv 💙, I’m online and ready to manage your router!")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "/status - Show router status\n"
        "/reboot - Reboot your router\n"
        "/getvouchers - List hotspot users\n"
        "/adduser <username> <password> - Add new hotspot user\n"
        "/blockuser <username> - Block hotspot user\n"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['status'])
def status(message):
    try:
        api, pool = connect_router()
        r = api.get_resource('/system/resource').get()[0]
        msg = f"💻 CPU Load: {r['cpu-load']}%\n🧠 Free Memory: {r['free-memory']}\n⏱️ Uptime: {r['uptime']}"
        pool.disconnect()
        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, f"Error connecting to router: {e}")

@bot.message_handler(commands=['reboot'])
def reboot(message):
    try:
        api, pool = connect_router()
        api.get_resource('/system/reboot').call('reboot')
        pool.disconnect()
        bot.reply_to(message, "Router is rebooting now, luv 💙")
    except Exception as e:
        bot.reply_to(message, f"Error rebooting router: {e}")

@bot.message_handler(commands=['getvouchers'])
def get_vouchers(message):
    try:
        api, pool = connect_router()
        users = api.get_resource('/ip/hotspot/user').get()
        pool.disconnect()
        if users:
            reply = "💳 Hotspot Users:\n" + "\n".join([u['name'] for u in users])
        else:
            reply = "No hotspot users found, luv 💙"
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Error fetching vouchers: {e}")

@bot.message_handler(commands=['adduser'])
def add_user(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "Usage: /adduser <username> <password>")
            return
        username, password = parts[1], parts[2]
        api, pool = connect_router()
        api.get_resource('/ip/hotspot/user').add(name=username, password=password, server="hotspot1")
        pool.disconnect()
        bot.reply_to(message, f"User '{username}' added successfully, luv 💙")
    except Exception as e:
        bot.reply_to(message, f"Error adding user: {e}")

@bot.message_handler(commands=['blockuser'])
def block_user(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /blockuser <username>")
            return
        username = parts[1]
        api, pool = connect_router()
        res = api.get_resource('/ip/hotspot/user')
        user_list = res.get(name=username)
        if user_list:
            res.set(id=user_list[0]['.id'], disabled="true")
            reply = f"User '{username}' blocked, luv 💙"
        else:
            reply = f"User '{username}' not found, luv 💙"
        pool.disconnect()
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Error blocking user: {e}")

def run_bot():
    print("Bot is running... 💙")
    bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()


