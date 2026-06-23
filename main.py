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

import uuid
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

    await context.bot.send_document(
        chat_id=update.effective_user.id,
        document=movie["file_id"],
        caption=f"<b>{movie['caption']}</b>",
        parse_mode="HTML"
    )


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    user = update.effective_user

    # FILE OPEN MODE
    if context.args:

        movie_id = context.args[0]

        if not await is_joined(update, context):

            buttons = [
                [
                    InlineKeyboardButton(
                        "Join Channel",
                        url=FORCE_CHANNEL_LINK
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Try Again",
                        callback_data=f"check_{movie_id}"
                    )
                ]
            ]

            await update.message.reply_text(
                "⚠️ You must join our channel first!",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        await send_file(update, context, movie_id)
        return

    # NORMAL START
    await update.message.reply_text(
        f" Hello {user.mention_html()}\n\n"
        "I can provide movies. Just join our group and enjoy.",
        parse_mode="HTML"
    )


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
            InlineKeyboardButton(
                f"{movie['file_name'][:45]}",
                url=link
            )
        ])

    if not buttons:
        await update.message.reply_text("No results found")
        return

    await update.message.reply_text(
        "🎬 Results:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= CALLBACK =================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    data = q.data

    # CHECK JOIN AGAIN
    if data.startswith("check_"):

        movie_id = data.split("_")[1]

        joined = await is_joined(update, context)

        if not joined:
            await q.message.reply_text(
                "❌ Still not joined channel."
            )
            return

        movie = files.find_one({"movie_id": movie_id})

        if movie:
            await context.bot.send_document(
                chat_id=q.from_user.id,
                document=movie["file_id"],
                caption=f"<b>{movie['caption']}</b>",
                parse_mode="HTML"
            )


# ================= ADMIN PANEL =================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    buttons = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")]
    ]

    await update.message.reply_text(
        "⚙️ Admin Panel",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= BROADCAST =================

broadcast_mode = {}

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    if broadcast_mode.get(user_id):

        text = update.message.text

        sent = 0

        for u in users.find():

            try:
                await context.bot.send_message(
                    u["user_id"],
                    text
                )
                sent += 1
            except:
                pass

        broadcast_mode[user_id] = False

        await update.message.reply_text(f"Sent to {sent} users")


# ================= CALLBACK ADMIN =================

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    data = q.data

    if data == "status":

        total = users.count_documents({})

        await q.message.reply_text(f"👥 Total Users: {total}")

    elif data == "broadcast":

        broadcast_mode[q.from_user.id] = True

        await q.message.reply_text("Send broadcast message now...")


# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))

app.add_handler(CallbackQueryHandler(callback))
app.add_handler(CallbackQueryHandler(admin_callback))

print("BOT STARTED 🚀")

app.run_polling()
