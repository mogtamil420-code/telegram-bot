from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os
from pymongo import MongoClient

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["autofilter"]
files = db["files"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running 🚀")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie = files.find_one()

    if movie:
        await update.message.reply_text(f"Found: {movie['file_name']}")
    else:
        await update.message.reply_text("No files found")

# SAVE FILES FROM CHANNEL ONLY
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.document:
        doc = update.channel_post.document

        files.insert_one({
            "file_name": doc.file_name,
            "file_id": doc.file_id,
            "message_id": update.channel_post.message_id
        })

        print(f"SAVED: {doc.file_name}")

# GROUP SEARCH HANDLER (IMPORTANT)
async def group_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    result = files.find_one({"file_name": {"$regex": query, "$options": "i"}})

    if result:
        await update.message.reply_text(
            f"🎬 Search Result:\n\n📁 {result['file_name']}"
        )
    else:
        await update.message.reply_text("No results found 😢")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("test", test))

# group messages → search
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_search))

# channel posts → save files
app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, save_file))

app.run_polling()
