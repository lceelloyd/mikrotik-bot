import telebot
from routeros_api import RouterOsApiPool

BOT_TOKEN = "8124056082:AAFIQf0SHEsG1qB0iEhtQY8KaQuM_GxFFKU"
ROUTER_IP = "102.0.15.136"
ROUTER_USER = "botuser"
ROUTER_PASS = "lloyd!?balusi!?"
ROUTER_PORT = 8728

bot = telebot.TeleBot(BOT_TOKEN)

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
        "Hey luv 💙, here’s what I can do:\n\n"
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
        system_resource = api.get_resource('/system/resource').get()[0]
        status_msg = (
            f"💻 CPU Load: {system_resource['cpu-load']}%\n"
            f"🧠 Free Memory: {system_resource['free-memory']}\n"
            f"⏱️ Uptime: {system_resource['uptime']}"
        )
        pool.disconnect()
        bot.reply_to(message, f"Here you go, luv 💙\n\n{status_msg}")
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
        hotspot_users = api.get_resource('/ip/hotspot/user').get()
        pool.disconnect()
        if hotspot_users:
            reply = "💳 Hotspot Users:\n" + "\n".join([u['name'] for u in hotspot_users])
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
        user_resource = api.get_resource('/ip/hotspot/user')
        user_list = user_resource.get(name=username)
        if user_list:
            user_resource.set(id=user_list[0]['.id'], disabled="true")
            reply = f"User '{username}' blocked, luv 💙"
        else:
            reply = f"User '{username}' not found, luv 💙"
        pool.disconnect()
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Error blocking user: {e}")

print("Bot is running... 💙")
bot.polling(none_stop=True)
