from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)
import os
from pymongo import MongoClient

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["autofilter"]
files = db["files"]

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running 🚀")

# SAVE FILE FROM CHANNEL
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.document:
        doc = update.channel_post.document

        files.insert_one({
            "file_name": doc.file_name,
            "file_id": doc.file_id
        })

        print(f"SAVED: {doc.file_name}")

# SEARCH + BUTTONS
async def group_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    results = files.find(
        {"file_name": {"$regex": query, "$options": "i"}}
    ).limit(5)

    keyboard = []
    count = 0

    for movie in results:
        count += 1
        keyboard.append([
            InlineKeyboardButton(
                movie["file_name"][:50],
                callback_data=movie["file_id"]
            )
        ])

    if count == 0:
        await update.message.reply_text("No results found 😢")
        return

    await update.message.reply_text(
        f"🎬 Search Results ({count})",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# BUTTON CLICK → SEND FILE
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    file_id = query.data

    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=file_id
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

# group search
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_search))

# channel save
app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, save_file))

# button handler
app.add_handler(CallbackQueryHandler(button_click))

app.run_polling()
