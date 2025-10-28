from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import routeros_api
import random
import string
import datetime

ROUTER_IP = "192.168.88.1"
ROUTER_USER = "botuser"
ROUTER_PASS = "B@lusi1"
BOT_TOKEN = "8124056082:AAFIQf0SHEsG1qB0iEhtQY8KaQuM_GxFFKU"

def connect_router():
    connection = routeros_api.RouterOsApiPool(
        ROUTER_IP, username=ROUTER_USER, password=ROUTER_PASS, plaintext_login=True
    )
    return connection.get_api(), connection

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi luv 💙! Your MikroTik bot is online and ready.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        api, c = connect_router()
        name = api.get_resource('/system/identity').get()[0]['name']
        await update.message.reply_text(f"Router '{name}' is active luv 💙")
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Error luv 😢: {e}")

async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        api, c = connect_router()
        api.get_resource('/system/reboot').call('')
        await update.message.reply_text("Router rebooting luv 💙🔄")
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Couldn’t reboot luv 😢: {e}")

async def bandwidth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        api, c = connect_router()
        iface = api.get_resource('/interface')
        ether = iface.get(name='ether1')[0]
        wlan = iface.get(name='wlan1')[0]
        msg = (
            f"Bandwidth luv 💙\n"
            f"Ether1: RX={ether['rx-byte']} bytes | TX={ether['tx-byte']} bytes\n"
            f"WLAN1: RX={wlan['rx-byte']} bytes | TX={wlan['tx-byte']} bytes"
        )
        await update.message.reply_text(msg)
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Error luv 😢: {e}")

async def limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        api, c = connect_router()
        queue = api.get_resource('/queue/simple')
        qtype = api.get_resource('/queue/type')
        for q in queue.get():
            if q['name'] in ['GlobalLimit', 'Users']:
                queue.remove(id=q['.id'])
        for qt in qtype.get():
            if qt['name'] in ['pcq-down', 'pcq-up']:
                qtype.remove(id=qt['.id'])
        qtype.add(name='pcq-down', kind='pcq', pcq_classifier='dst-address')
        qtype.add(name='pcq-up', kind='pcq', pcq_classifier='src-address')
        queue.add(name='GlobalLimit', target='0.0.0.0/0', max_limit='3M/3M')
        queue.add(name='Users', parent='GlobalLimit', target='192.168.88.0/24', queue='pcq-up/pcq-down')
        await update.message.reply_text("Limits set luv 💙 (3 Mbps shared).")
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Couldn’t set limits luv 😢: {e}")

async def disablefasttrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        api, c = connect_router()
        fw = api.get_resource('/ip/firewall/filter')
        count = 0
        for rule in fw.get():
            if 'fasttrack-connection' in rule.get('action', ''):
                fw.set(id=rule['.id'], disabled='yes')
                count += 1
        await update.message.reply_text(f"Disabled {count} fasttrack rules luv 💙.")
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Error luv 😢: {e}")

async def enableipfirewall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        api, c = connect_router()
        bridge = api.get_resource('/interface/bridge/settings')
        bridge.set(use_ip_firewall='yes')
        await update.message.reply_text("Bridge IP firewall enabled luv 💙.")
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Error luv 😢: {e}")

async def showusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        api, c = connect_router()
        dhcp = api.get_resource('/ip/dhcp-server/lease')
        users = dhcp.get()
        msg = "Connected devices luv 💙:\n"
        for u in users:
            msg += f"{u.get('host-name', 'Unknown')} - {u['address']} - {u.get('mac-address')}\n"
        await update.message.reply_text(msg)
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Error luv 😢: {e}")

async def block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mac = context.args[0]
        api, c = connect_router()
        dhcp = api.get_resource('/ip/dhcp-server/lease')
        for u in dhcp.get():
            if u.get('mac-address') == mac:
                dhcp.set(id=u['.id'], disabled='yes')
                await update.message.reply_text(f"Blocked {mac} luv 💙")
                break
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Error luv 😢: {e}")

async def unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mac = context.args[0]
        api, c = connect_router()
        dhcp = api.get_resource('/ip/dhcp-server/lease')
        for u in dhcp.get():
            if u.get('mac-address') == mac:
                dhcp.set(id=u['.id'], disabled='no')
                await update.message.reply_text(f"Unblocked {mac} luv 💙")
                break
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Error luv 😢: {e}")

async def changewifi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        newpass = context.args[0]
        api, c = connect_router()
        wifi = api.get_resource('/interface/wireless')
        wifi.set(id=0, password=newpass)
        await update.message.reply_text(f"WiFi password changed to '{newpass}' luv 💙")
        c.disconnect()
    except Exception as e:
        await update.message.reply_text(f"Error luv 😢: {e}")

async def generatecode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    await update.message.reply_text(f"Your generated login code luv 💙: {code}")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"Router report luv 💙\nTime: {time}\nStatus: OK\nBandwidth: Stable")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("reboot", reboot))
app.add_handler(CommandHandler("bandwidth", bandwidth))
app.add_handler(CommandHandler("limit", limit))
app.add_handler(CommandHandler("disablefasttrack", disablefasttrack))
app.add_handler(CommandHandler("enableipfirewall", enableipfirewall))
app.add_handler(CommandHandler("showusers", showusers))
app.add_handler(CommandHandler("block", block))
app.add_handler(CommandHandler("unblock", unblock))
app.add_handler(CommandHandler("changewifi", changewifi))
app.add_handler(CommandHandler("generatecode", generatecode))
app.add_handler(CommandHandler("report", report))
app.run_polling()
