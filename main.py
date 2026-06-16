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


# Save files from channel
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.document:
        file = update.channel_post.document

        files.insert_one({
            "file_name": file.file_name,
            "file_id": file.file_id
        })

        print(f"Saved: {file.file_name}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(filters.Document.ALL, save_file)
)

app.run_polling()
