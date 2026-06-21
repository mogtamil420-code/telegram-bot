from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from pymongo import MongoClient
import os
import uuid
import asyncio


# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

ADMIN_ID = 5565826679
BOT_USERNAME = "Gezxbot"

SEARCH_GROUP = "https://t.me/+0sWBTplLi4s3ODM9"


# ================= DB =================

client = MongoClient(MONGO_URL)

db = client["autofilter"]

files = db["files"]
users = db["users"]
settings = db["settings"]


if not settings.find_one({"_id": "main"}):
    settings.insert_one({
        "_id": "main",
        "powered": "@Tamil_Movies_Gez",
        "note": "✓Note : Search Movies Name With Year!",
        "button_text": "Search Movies Group",
        "start_text": "⚠️ ꜱᴏʀʀʏ ɪ ᴄᴀɴ'ᴛ ᴡᴏʀᴋ ɪɴ ᴘᴍ\n\nSearch movies in our movie search group."
    })


# ================= UTIL =================

async def save_user(update):
    if not update.effective_user:
        return

    users.update_one(
        {"user_id": update.effective_user.id},
        {"$set": {"user_id": update.effective_user.id}},
        upsert=True
    )


async def auto_delete(messages, delay):
    await asyncio.sleep(delay)
    for m in messages:
        try:
            await m.delete()
        except:
            pass


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    args = context.args

    if args:
        movie_id = args[0]

        movie = files.find_one({"movie_id": movie_id})

        if not movie:
            await update.message.reply_text("File not found")
            return

        # file delivery
        sent_msgs = []

        warn = await update.message.reply_text(
            "⚠️ ᴀꜰᴛᴇʀ 15 minutes ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇᴅ 🗑️\n"
            "⚠️ ɪᴍᴘᴏʀᴛᴀɴᴛ : ғᴏʀᴡᴀʀᴅ ᴛʜᴇsᴇ ᴍᴇssᴀɢᴇs ᴛᴏ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs",
        )

        sent_msgs.append(warn)

        file_msg = await context.bot.send_document(
            chat_id=update.effective_user.id,
            document=movie["file_id"],
            caption=f"<b>{movie['caption']}</b>",
            parse_mode="HTML"
        )

        sent_msgs.append(file_msg)

        asyncio.create_task(auto_delete(sent_msgs, 900))  # 15 min

        return

    data = settings.find_one({"_id": "main"})

    btn = [
        [InlineKeyboardButton(data["button_text"], url=SEARCH_GROUP)]
    ]

    await update.message.reply_text(
        data["start_text"],
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ================= SAVE FILE =================

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.channel_post:
        return

    msg = update.channel_post

    doc = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)

    if not doc:
        return

    file_id = doc.file_id

    movie_id = str(uuid.uuid4())[:8]

    caption = msg.caption if msg.caption else "No Caption"

    files.insert_one({
        "movie_id": movie_id,
        "file_id": file_id,
        "file_name": caption,
        "caption": caption
    })

    print("Saved:", movie_id)


# ================= SEARCH =================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    query = update.message.text

    data = settings.find_one({"_id": "main"})

    results = files.find({
        "file_name": {"$regex": query, "$options": "i"}
    }).limit(10)

    buttons = []
    count = 0

    for movie in results:
        count += 1

        link = f"https://t.me/{BOT_USERNAME}?start={movie['movie_id']}"

        label = f"{movie['file_name'][:45]}"

        buttons.append([
            InlineKeyboardButton(
                label,
                url=link
            )
        ])

    if count == 0:
        await update.message.reply_text("No results found")
        return

    mention = update.effective_user.mention_html()

    text = (
        f"Tʜᴇ Rᴇꜱᴜʟᴛꜱ Fᴏʀ ☞ {query}\n\n"
        f"Rᴇǫᴜᴇsᴛᴇᴅ Bʏ ☞ : {mention}\n\n"
        f"ᴘᴏᴡᴇʀᴇᴅ ʙʏ ☞ : {data['powered']}\n\n"
        f"{data['note']}"
    )

    msg = await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    asyncio.create_task(auto_delete([msg], 300))  # 5 min delete


# ================= ADMIN =================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    btn = [
        [InlineKeyboardButton("Status", callback_data="status")],
        [InlineKeyboardButton("Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("Settings", callback_data="settings")]
    ]

    await update.message.reply_text(
        "Admin Panel",
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ================= CALLBACK =================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    data = q.data

    if data == "status":
        total = users.count_documents({})
        await q.message.reply_text(f"Total Users: {total}")

    elif data == "broadcast":
        context.user_data["broadcast"] = True
        await q.message.reply_text("Send broadcast message")

    elif data == "settings":
        s = settings.find_one({"_id": "main"})
        await q.message.reply_text(
            f"Powered: {s['powered']}\n"
            f"Note: {s['note']}\n"
            f"Button: {s['button_text']}"
        )


# ================= BROADCAST =================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if not context.user_data.get("broadcast"):
        return

    msg = update.message.text

    sent = 0

    for u in users.find():
        try:
            await context.bot.send_message(u["user_id"], msg)
            sent += 1
        except:
            pass

    context.user_data["broadcast"] = False

    await update.message.reply_text(f"Sent to {sent} users")


# ================= UNKNOWN =================

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start command")


# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))

app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, save_file))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

app.add_handler(CallbackQueryHandler(callback))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast))

app.add_handler(MessageHandler(filters.ALL, unknown))

print("BOT STARTED 🚀")
app.run_polling()
