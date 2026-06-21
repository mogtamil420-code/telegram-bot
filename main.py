from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)
from bson import ObjectId
import os
from pymongo import MongoClient

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["autofilter"]
files = db["files"]

GROUP_LINK = "https://t.me/+0sWBTplLi4s3ODM9"  # 🔴 CHANGE THIS

# START (PM STYLE LIKE MOVIE BOTS)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎬 Movies Search Group", url=GROUP_LINK)]
    ]

    await update.message.reply_text(
        "⚠️ ꜱᴏʀʀʏ ɪ ᴄᴀɴ'ᴛ ᴡᴏʀᴋ ɪɴ ᴘᴍ\n\n👉 ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇꜱ ɪɴ ᴏᴜʀ ɢʀᴏᴜᴘ.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# SAVE FILE FROM CHANNEL
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.document:
        doc = update.channel_post.document

        files.insert_one({
            "file_name": doc.file_name,
            "file_id": doc.file_id
        })

        print(f"SAVED: {doc.file_name}")

# GROUP SEARCH (MAIN SYSTEM)
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
        keyboard.append([
            InlineKeyboardButton(
                movie["file_name"][:60],
                callback_data=str(movie["_id"])
            )
        ])

    if count == 0:
        await update.message.reply_text("No results found 😑")
        return

    await update.message.reply_text(
        f"🎬 Search Results ({count})",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# BUTTON CLICK → SEND FILE IN PM OR GROUP
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    doc_id = query.data

    movie = files.find_one({"_id": ObjectId(doc_id)})

    if movie:
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=movie["file_id"],
            caption=f"🎬 {movie['file_name']}"
        )
    else:
        await query.message.reply_text("File not found 😑")

# APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

# group search ONLY
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_search))

# channel save
app.add_handler(MessageHandler(filters.ChatType.CHANNEL & filters.Document.ALL, save_file))

# buttons
app.add_handler(CallbackQueryHandler(button_click))

app.run_polling()
