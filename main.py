from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)
from bson import ObjectId
import os
import uuid
from pymongo import MongoClient

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

ADMIN_ID = 5565826679  # ✅ YOUR ADMIN ID

BOT_USERNAME = "Gezxbot"  # 🔴 CHANGE THIS

# ---------------- DB ----------------
client = MongoClient(MONGO_URL)
db = client["autofilter"]
files = db["files"]

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    # Deep link handler
    if args:
        movie_id = args[0]

        movie = files.find_one({"movie_id": movie_id})

        if movie:
            await context.bot.send_document(
                chat_id=update.effective_user.id,
                document=movie["file_id"],
                caption=f" {movie['file_name']}"
            )
            return

    await update.message.reply_text(
        "⚠️ Please use group to search movies."
    )

# ---------------- ADMIN CHECK ----------------
def is_admin(update: Update):
    return update.effective_user and update.effective_user.id == ADMIN_ID

# ---------------- SAVE FILE (ADMIN ONLY) ----------------
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return

    if update.channel_post and update.channel_post.document:
        doc = update.channel_post.document

        movie_id = str(uuid.uuid4())[:8]

        files.insert_one({
            "file_name": doc.file_name,
            "file_id": doc.file_id,
            "movie_id": movie_id
        })

        print(f"SAVED: {doc.file_name} | {movie_id}")

# ---------------- GROUP SEARCH ----------------
async def group_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    query = update.message.text.strip()

    results = files.find(
        {"file_name": {"$regex": query, "$options": "i"}}
    ).limit(5)

    keyboard = []
    count = 0

    for movie in results:
        count += 1

        link = f"https://t.me/{BOT_USERNAME}?start={movie['movie_id']}"

        keyboard.append([
            InlineKeyboardButton(
                f" {movie['file_name'][:50]}",
                url=link
            )
        ])

    if count == 0:
        await update.message.reply_text("No results found 😑")
        return

    await update.message.reply_text(
        f"🎬 Search Results ({count})",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_search))

app.add_handler(MessageHandler(filters.ChatType.CHANNEL & filters.Document.ALL, save_file))

app.run_polling()
