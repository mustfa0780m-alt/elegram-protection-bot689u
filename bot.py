# bot.py
from telethon import TelegramClient, events, types
import os

# جلب القيم من متغيرات البيئة (Heroku) أو من config.py
API_ID = int(os.environ.get('API_ID', '1234567'))
API_HASH = os.environ.get('API_HASH', 'YOUR_API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN')

BLOCK_LINKS = True       # منع الروابط
BLOCK_SPAM = True        # منع الرسائل المكررة
BLOCK_MEDIA = False      # منع الوسائط (اختياري)
WARN_BEFORE_BAN = 2      # عدد التحذيرات قبل الحظر
ADMINS = []              # معرفات الأدمن

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

warnings = {}

@client.on(events.NewMessage)
async def monitor(event):
    sender = await event.get_sender()
    sender_id = sender.id
    message = event.raw_text

    if sender_id in ADMINS:
        return

    # حظر الروابط
    if BLOCK_LINKS and ('http://' in message or 'https://' in message):
        await event.delete()
        warnings[sender_id] = warnings.get(sender_id, 0) + 1

    # حظر الرسائل المكررة
    if BLOCK_SPAM:
        last_msg = getattr(sender, 'last_msg', None)
        if last_msg == message:
            await event.delete()
            warnings[sender_id] = warnings.get(sender_id, 0) + 1
        sender.last_msg = message

    # تنفيذ الحظر عند الوصول للتحذيرات القصوى
    if warnings.get(sender_id, 0) >= WARN_BEFORE_BAN:
        try:
            await client.kick_participant(event.chat_id, sender_id)
            warnings[sender_id] = 0
        except:
            pass

client.run_until_disconnected()