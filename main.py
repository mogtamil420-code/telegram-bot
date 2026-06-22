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
from collections import OrderedDict


# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

ADMIN_ID = 5565826679
BOT_USERNAME = "Gezxbot"

FORCE_CHANNEL = "https://t.me/+SZWfXlte9ddkMTJl"


# ================= DB =================

client = MongoClient(MONGO_URL)
db = client["autofilter"]

files = db["files"]
users = db["users"]


# ================= FAST CACHE (FIX RAILWAY CRASH) =================

cache = OrderedDict()
CACHE_LIMIT = 50


def set_cache(key, value):
    if key in cache:
        cache.move_to_end(key)
    cache[key] = value
    if len(cache) > CACHE_LIMIT:
        cache.popitem(last=False)


def get_cache(key):
    return cache.get(key)


# ================= UTIL =================

async def save_user(update):
    if update.effective_user:
        users.update_one(
            {"user_id": update.effective_user.id},
            {"$set": {"user_id": update.effective_user.id}},
            upsert=True
        )


# ================= FORCE JOIN =================

async def check_join(update, context):
    user = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(
            chat_id="@SZWfXlte9ddkMTJl",
            user_id=user
        )

        if member.status in ["left", "kicked"]:
            return False

    except:
        return False

    return True


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    # FORCE JOIN CHECK
    if not await check_join(update, context):

        btn = [
            [InlineKeyboardButton("Join Channel", url=FORCE_CHANNEL)],
            [InlineKeyboardButton("Try Again", callback_data="retry")]
        ]

        await update.message.reply_text(
            "⚠️ You must join our channel to use this bot",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return

    args = context.args

    if args:
        movie_id = args[0]

        movie = files.find_one({"movie_id": movie_id})

        if not movie:
            await update.message.reply_text("File not found")
            return

        # cache check
        cached = get_cache(movie_id)
        if cached:
            file_id = cached
        else:
            file_id = movie["file_id"]
            set_cache(movie_id, file_id)

        await context.bot.send_document(
            chat_id=update.effective_user.id,
            document=file_id,
            caption=f"<b>{movie['caption']}</b>",
            parse_mode="HTML"
        )

        return

    await update.message.reply_text(
        "🎬 Welcome to Movie Bot\nSearch in group to get movies"
    )


# ================= SEARCH =================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    query = update.message.text.strip().lower()

    cached = get_cache(query)

    if cached:
        results = cached
    else:
        results = list(files.find({
            "file_name": {"$regex": query, "$options": "i"}
        }).limit(10))
        set_cache(query, results)

    if not results:
        await update.message.reply_text("No results found")
        return

    buttons = []

    for movie in results:

        link = f"https://t.me/{BOT_USERNAME}?start={movie['movie_id']}"

        buttons.append([
            InlineKeyboardButton(movie["file_name"][:45], url=link)
        ])

    await update.message.reply_text(
        f"Results for: {query}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= ADMIN DASHBOARD =================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    total_users = users.count_documents({})
    total_files = files.count_documents({})

    btn = [
        [InlineKeyboardButton("Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("Refresh Stats", callback_data="stats")]
    ]

    await update.message.reply_text(
        f" ADMIN DASHBOARD\n\n"
        f" Users: {total_users}\n"
        f" Files: {total_files}\n"
        f" Cache size: {len(cache)}",
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ================= CALLBACK =================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    if q.data == "retry":
        await q.message.reply_text("Try /start again")

    elif q.data == "stats":
        total_users = users.count_documents({})
        total_files = files.count_documents({})

        await q.message.reply_text(
            f"📊 LIVE STATS\nUsers: {total_users}\nFiles: {total_files}"
        )


# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
app.add_handler(CallbackQueryHandler(callback))

print("BOT RUNNING SAFE VERSION 🚀")
app.run_polling()
