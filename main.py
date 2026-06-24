from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
from handlers.start_menu import start_menu

import asyncio


# ================= USER SAVE =================

async def save_user(update):
    if update.effective_user:
        users.update_one(
            {"user_id": update.effective_user.id},
            {"$set": {"user_id": update.effective_user.id}},
            upsert=True
        )


# ================= FORCE JOIN =================

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

    msg = await context.bot.send_document(
        chat_id=update.effective_user.id,
        document=movie["file_id"],
        caption=f"<b>{movie['caption']}</b>",
        parse_mode="HTML"
    )

    asyncio.create_task(auto_delete(context, msg.chat_id, msg.message_id))


# ================= AUTO DELETE =================

async def auto_delete(context, chat_id, message_id, seconds=900):
    await asyncio.sleep(seconds)
    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except Exception as e:
        print("AUTO DELETE ERROR:", e)

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_user(update)

    user = update.effective_user

    if context.args:
        movie_id = context.args[0]

        if not await is_joined(update, context):
            buttons = [
                [InlineKeyboardButton("Jᴏɪɴ", url=FORCE_CHANNEL_LINK)],
                [InlineKeyboardButton("Tʀʏ ᴀɢᴀɪɴ", callback_data=f"check_{movie_id}")]
            ]

            await update.message.reply_text(
                "⚠️ Yᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴄᴏᴜɴᴛɪɴᴜᴇ!",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        await send_file(update, context, movie_id)
        return

    await start_menu(update, context)


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

    if not buttons:
        await update.message.reply_text("No results found")
        return

    msg = await update.message.reply_text(
        "🎬 Results:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    asyncio.create_task(auto_delete(context, msg.chat_id, msg.message_id))


# ================= CALLBACK =================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()
    data = q.data

    # JOIN CHECK
    if data.startswith("check_"):
        movie_id = data.split("_")[1]

        if not await is_joined(update, context):
            await q.message.reply_text("❌ Sᴛɪʟʟ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴄʜᴀɴɴᴇʟ!")
            return

        await send_file(update, context, movie_id, q.from_user.id)

    # ADMIN BUTTONS
    elif data == "status":
        total = users.count_documents({})
        await q.message.reply_text(f"👥 Total Users: {total}")

    elif data == "broadcast":
        broadcast_mode[q.from_user.id] = True
        await q.message.reply_text("Send broadcast message now...")

    elif data == "help":
        await q.message.reply_text("Help menu coming soon")

    elif data == "about":
        await q.message.reply_text("About bot coming soon")

    elif data == "close":
        await q.message.delete()
# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
app.add_handler(CallbackQueryHandler(callback))

if __name__ == "__main__":
    print("BOT STARTED 🚀")
    app.run_polling()
