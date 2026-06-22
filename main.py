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

# ✅ YOUR CHANNEL ID (FIXED)
FORCE_CHANNEL_ID = -1003791438228
FORCE_CHANNEL_LINK = "https://t.me/+SZWfXlte9ddkMTJl"


# ================= DB =================

client = MongoClient(MONGO_URL)
db = client["autofilter"]

files = db["files"]
users = db["users"]


# ================= USER SAVE =================

async def save_user(update):
    if update.effective_user:
        users.update_one(
            {"user_id": update.effective_user.id},
            {"$set": {"user_id": update.effective_user.id}},
            upsert=True
        )


# ================= FORCE JOIN CHECK (FIXED 100%) =================

async def is_joined(update, context):

    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(
            chat_id=FORCE_CHANNEL_ID,
            user_id=user_id
        )

        # important fix
        if member.status in ["left", "kicked"]:
            return False

        return True

    except Exception as e:
        print("JOIN ERROR:", e)
        return False


# ================= SEND FILE =================

async def send_file(update, context, movie_id):

    movie = files.find_one({"movie_id": movie_id})

    if not movie:
        await update.message.reply_text("File not found")
        return

    await context.bot.send_document(
        chat_id=update.effective_user.id,
        document=movie["file_id"],
        caption=f"<b>{movie['caption']}</b>",
        parse_mode="HTML"
    )


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    args = context.args
    user_id = update.effective_user.id

    # ================= FILE REQUEST =================
    if args:

        movie_id = args[0]

        # FORCE JOIN CHECK
        if not await is_joined(update, context):

            btn = [
                [InlineKeyboardButton("Jᴏɪɴ", url=FORCE_CHANNEL_LINK)],
                [InlineKeyboardButton("Tʀʏ ᴀɢᴀɪɴ", callback_data=f"check_{movie_id}")]
            ]

            await update.message.reply_text(
                "⚠️ Yᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴄᴏᴜɴᴛɪɴᴜᴇ",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return

        # if joined → send file
        await send_file(update, context, movie_id)
        return

    await update.message.reply_text("🎬 Welcome! Search movies in group")


# ================= SEARCH =================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    query = update.message.text

    results = files.find({
        "file_name": {"$regex": query, "$options": "i"}
    }).limit(10)

    buttons = []

    for movie in results:

        link = f"https://t.me/{BOT_USERNAME}?start={movie['movie_id']}"

        buttons.append([
            InlineKeyboardButton(movie["file_name"][:45], url=link)
        ])

    await update.message.reply_text(
        "🎬 Results:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= CALLBACK (FIXED JOIN AFTER CLICK) =================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    data = q.data
    user_id = q.from_user.id

    if data.startswith("check_"):

        movie_id = data.split("_")[1]

        # small delay fix (Telegram update delay)
        await asyncio.sleep(2)

        if await is_joined(update, context):

            await send_file(update, context, movie_id)

        else:

            await q.message.reply_text(
                "❌ Sᴛɪʟʟ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴄʜᴀɴɴᴇʟ.\nPlease join and try again."
            )


# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
app.add_handler(CallbackQueryHandler(callback))

print("BOT STARTED SUCCESSFULLY 🚀")
app.run_polling()
