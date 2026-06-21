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
        await update.message.reply_text(
            f"Found: {movie['file_name']}"
        )
    else:
        await update.message.reply_text("No files found")

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.document:
        doc = update.channel_post.document

        files.insert_one({
            "file_name": doc.file_name,
            "file_id": doc.file_id,
            "message_id": update.channel_post.message_id
        })

        print(f"SAVED: {doc.file_name}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("test", test))
app.add_handler(MessageHandler(filters.ALL, save_file))

app.run_polling()
