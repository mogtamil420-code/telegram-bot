from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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


# ================= STATIC SETTINGS (NO DB) =================

POWERED_BY = "@Tamil_Movies_Gez"
NOTE_TEXT = "✓Note : Search Movies Name With Year!"
BUTTON_TEXT = "Search Movies Group"
START_TEXT = "⚠️ Sorry, I can't work in PM\nSearch in our group."


# ================= DB =================

client = MongoClient(MONGO_URL)
db = client["autofilter"]

files = db["files"]
users = db["users"]


# ================= UTIL =================

async def save_user(update):
    if update.effective_user:
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

    # ================= FILE DELIVERY =================
    if args:
        movie_id = args[0]
        movie = files.find_one({"movie_id": movie_id})

        if not movie:
            await update.message.reply_text("File not found")
            return

        sent = []

        # FILE FIRST
        file_msg = await context.bot.send_document(
            chat_id=update.effective_user.id,
            document=movie["file_id"],
            caption=f"<b>{movie['caption']}</b>",
            parse_mode="HTML"
        )

        sent.append(file_msg)

        # WARNING SECOND
        warn_msg = await update.message.reply_text(
            "⚠️ ᴀꜰᴛᴇʀ 15 minutes ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ 🗑️\n"
            "⚠️ ɪᴍᴘᴏʀᴛᴀɴᴛ : ғᴏʀᴡᴀʀᴅ ᴛᴏ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs"
        )

        sent.append(warn_msg)

        asyncio.create_task(auto_delete(sent, 900))
        return

    btn = [[InlineKeyboardButton(BUTTON_TEXT, url=SEARCH_GROUP)]]

    await update.message.reply_text(
        START_TEXT,
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ================= SAVE FILE =================

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.channel_post:
        return

    msg = update.channel_post
    doc = msg.document or msg.video or (msg.photo[-1] if msg.photo else None)

    if not doc:
        return

    movie_id = str(uuid.uuid4())[:8]
    caption = msg.caption if msg.caption else "No Caption"

    files.insert_one({
        "movie_id": movie_id,
        "file_id": doc.file_id,
        "file_name": caption,
        "caption": caption
    })

    print("Saved:", movie_id)


# ================= SEARCH =================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    query = update.message.text

    results = files.find({
        "file_name": {"$regex": query, "$options": "i"}
    }).limit(10)

    buttons = []
    count = 0

    for movie in results:
        count += 1
        link = f"https://t.me/{BOT_USERNAME}?start={movie['movie_id']}"

        buttons.append([
            InlineKeyboardButton(movie["file_name"][:45], url=link)
        ])

    if count == 0:
        await update.message.reply_text("No results found")
        return

    mention = update.effective_user.mention_html()

    text = (
        f"Tʜᴇ Rᴇꜱᴜʟᴛꜱ Fᴏʀ ☞ {query}\n\n"
        f"Rᴇǫᴜᴇsᴛᴇᴅ Bʏ ☞ {mention}\n\n"
        f"ᴘᴏᴡᴇʀᴇᴅ ʙʏ ☞ {POWERED_BY}\n\n"
        f"{NOTE_TEXT}"
    )

    msg = await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    asyncio.create_task(auto_delete([msg], 300))


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

    if q.data == "status":
        total = users.count_documents({})
        await q.message.reply_text(f"Total Users: {total}")

    elif q.data == "broadcast":
        context.user_data["broadcast"] = True
        await q.message.reply_text("Send broadcast message")

    elif q.data == "settings":
        await q.message.reply_text(
            f"POWERED: {POWERED_BY}\n"
            f"NOTE: {NOTE_TEXT}\n"
            f"BUTTON: {BUTTON_TEXT}\n"
            f"START: {START_TEXT}"
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


# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

# IMPORTANT ORDER (FIX ADMIN ISSUE)
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, save_file))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

app.add_handler(CallbackQueryHandler(callback))

print("BOT STARTED 🚀")
app.run_polling()
