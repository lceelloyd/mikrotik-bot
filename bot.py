# bot.py
import os
import telebot
from routeros_api import RouterOsApiPool

# ---- Environment variables (set on Pella) ----
TELEGRAM_TOKEN = os.environ.get("8124056082:AAFIQf0SHEsG1qB0iEhtQY8KaQuM_GxFFKU")
ROUTER_IP = os.environ.get("ROUTER_IP")
ROUTER_USER = os.environ.get("ROUTER_USER")
ROUTER_PASS = os.environ.get("ROUTER_PASS")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ---- Helper function to connect to Mikrotik router ----
def connect_router():
    pool = RouterOsApiPool(
        host=ROUTER_IP,
        username=ROUTER_USER,
        password=ROUTER_PASS,
        port=8728,
        plaintext_login=True
    )
    api = pool.get_api()
    return api, pool

# ---- /status command ----
@bot.message_handler(commands=['status'])
def status(message):
    try:
        api, pool = connect_router()
        system_resource = api.get_resource('/system/resource')
        status_msg = f"CPU: {system_resource['cpu-load']}%\n" \
                     f"Free Memory: {system_resource['free-memory']}\n" \
                     f"Uptime: {system_resource['uptime']}"
        pool.disconnect()
        bot.reply_to(message, status_msg)
    except Exception as e:
        bot.reply_to(message, f"Error connecting to router: {e}")

# ---- /reboot command ----
@bot.message_handler(commands=['reboot'])
def reboot(message):
    try:
        api, pool = connect_router()
        api.get_resource('/system/reboot')
        pool.disconnect()
        bot.reply_to(message, "Router is rebooting...")
    except Exception as e:
        bot.reply_to(message, f"Error rebooting router: {e}")

# ---- /getvouchers command ----
@bot.message_handler(commands=['getvouchers'])
def get_vouchers(message):
    try:
        api, pool = connect_router()
        hotspot_users = api.get_resource('/ip/hotspot/user').get()
        pool.disconnect()
        if hotspot_users:
            reply = "Hotspot users:\n" + "\n".join([u['name'] for u in hotspot_users])
        else:
            reply = "No hotspot users found."
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Error fetching vouchers: {e}")

# ---- /adduser command ----
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
        bot.reply_to(message, f"User '{username}' added successfully.")
    except Exception as e:
        bot.reply_to(message, f"Error adding user: {e}")

# ---- /blockuser command ----
@bot.message_handler(commands=['blockuser'])
def block_user(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /blockuser <username>")
            return
        username = parts[1]
        api, pool = connect_router()
        user_resource = api.get_resource('/ip/hotspot/user')
        user_list = user_resource.get(name=username)
        if user_list:
            user_resource.update(id=user_list[0]['.id'], disabled=True)
            reply = f"User '{username}' blocked."
        else:
            reply = f"User '{username}' not found."
        pool.disconnect()
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Error blocking user: {e}")

# ---- Start bot with long polling ----
bot.polling(none_stop=True)

