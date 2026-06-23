from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from config import *
from database import *

import asyncio
import uuid


# ================= USER SAVE =================

async def save_user(update):
    if update.effective_user:
        users.update_one(
            {"user_id": update.effective_user.id},
            {"$set": {"user_id": update.effective_user.id}},
            upsert=True
        )


# ================= FORCE JOIN CHECK =================

async def is_joined(update, context):
    try:
        member = await context.bot.get_chat_member(
            FORCE_CHANNEL_ID,
            update.effective_user.id
        )
        return member.status not in ["left", "kicked"]
    except:
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

    if context.args:

        movie_id = context.args[0]

        if not await is_joined(update, context):

            await update.message.reply_text(
                "⚠️ Join channel first!",
            )
            return

        await send_file(update, context, movie_id)
        return

    await update.message.reply_text(
        "Welcome to Movie Bot"
    )


# ================= SEARCH =================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    query = update.message.text

    results = files.find({
        "file_name": {"$regex": query, "$options": "i"}
    }).limit(10)

    for movie in results:

        link = f"https://t.me/{BOT_USERNAME}?start={movie['movie_id']}"

        await update.message.reply_text(
            f"{movie['file_name']}\n{movie.get('size','')}\n{link}"
        )


# ================= STORAGE CHANNEL SAVE =================

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.channel_post:
        return

    doc = update.channel_post.document
    if not doc:
        return

    movie_id = str(uuid.uuid4())[:8]

    files.insert_one({
        "movie_id": movie_id,
        "file_id": doc.file_id,
        "file_name": doc.file_name,
        "caption": update.channel_post.caption or doc.file_name,
        "size": doc.file_size
    })

    print("Saved:", doc.file_name)


# ================= CALLBACK (EMPTY FOR NOW) =================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, save_file))
app.add_handler(CallbackQueryHandler(callback))

print("BOT STARTED 🚀")
app.run_polling()
