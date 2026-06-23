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
from handlers.start_menu import start_menu   # ✅ FIXED IMPORT

import asyncio


# ================= USER SAVE =================

async def save_user(update):
    if update.effective_user:
        users.update_one(
            {"user_id": update.effective_user.id},
            {"$set": {"user_id": update.effective_user.id}},
            upsert=True
        )
=============== FORCE JOIN =================

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

async def send_file(update, context, movie_id, owner_id=None):

    movie = files.find_one({"movie_id": movie_id})

    if not movie:
        await update.message.reply_text("File not found")
        return

    user_id = update.effective_user.id

    # 🔒 SECURITY FIX (User A cannot open User B file)
    if owner_id and owner_id != user_id:
        await update.message.reply_text(
            f"❌ ʜᴇʏ {update.effective_user.mention_html()}, ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ʀᴇQᴜᴇꜱᴛ!",
            parse_mode="HTML"
        )
        return

    msg = await context.bot.send_document(
        chat_id=user_id,
        document=movie["file_id"],
        caption=f"<b>{movie['caption']}</b>",
        parse_mode="HTML"
    )

    # ⏳ AUTO DELETE AFTER 15 MIN
    asyncio.create_task(auto_delete(context, msg.chat_id, msg.message_id))


# ================= AUTO DELETE =================

async def auto_delete(context, chat_id, message_id, seconds=900):
    await asyncio.sleep(seconds)
    try:
        await context.bot.delete_message(chat_id, message_id)
    except:
        pass


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_user(update)

    user = update.effective_user

    # FILE OPEN MODE
    if context.args:

        movie_id = context.args[0]

        if not await is_joined(update, context):

            buttons = [
                [InlineKeyboardButton("Join Channel", url=FORCE_CHANNEL_LINK)],
                [InlineKeyboardButton("Try Again", callback_data=f"check_{movie_id}")]
            ]

            await update.message.reply_text(
                "⚠️ You must join our channel first!",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        await send_file(update, context, movie_id, user.id)
        return

    #from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
from handlers.start_menu import start_menu   # ✅ FIXED IMPORT

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

async def send_file(update, context, movie_id, owner_id=None):

    movie = files.find_one({"movie_id": movie_id})

    if not movie:
        await update.message.reply_text("File not found")
        return

    user_id = update.effective_user.id

    # 🔒 SECURITY FIX (User A cannot open User B file)
    if owner_id and owner_id != user_id:
        await update.message.reply_text(
            f"❌ ʜᴇʏ {update.effective_user.mention_html()}, ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ʀᴇQᴜᴇꜱᴛ!",
            parse_mode="HTML"
        )
        return

    msg = await context.bot.send_document(
        chat_id=user_id,
        document=movie["file_id"],
        caption=f"<b>{movie['caption']}</b>",
        parse_mode="HTML"
    )

    # ⏳ AUTO DELETE AFTER 15 MIN
    asyncio.create_task(auto_delete(context, msg.chat_id, msg.message_id))


# ================= AUTO DELETE =================

async def auto_delete(context, chat_id, message_id, seconds=900):
    await asyncio.sleep(seconds)
    try:
        await context.bot.delete_message(chat_id, message_id)
    except:
        pass


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_user(update)

    user = update.effective_user

    # FILE OPEN MODE
    if context.args:

        movie_id = context.args[0]

        if not await is_joined(update, context):

            buttons = [
                [InlineKeyboardButton("Join Channel", url=FORCE_CHANNEL_LINK)],
                [InlineKeyboardButton("Try Again", callback_data=f"check_{movie_id}")]
            ]

            await update.message.reply_text(
                "⚠️ You must join our channel first!",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        await send_file(update, context, movie_id, user.id)
        return

    # NORMAL START → START MENU
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
            InlineKeyboardButton(
                f"{movie['file_name'][:45]}",
                url=link
            )
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

    if data.startswith("check_"):

        movie_id = data.split("_")[1]

        if not await is_joined(update, context):
            await q.message.reply_text("❌ Still not joined channel.")
            return

        await send_file(update, context, movie_id, q.from_user.id)


# ================= ADMIN =================

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
                await context.bot.send_message(u["user_id"], text)
                sent += 1
            except:
                pass

        broadcast_mode[user_id] = False

        await update.message.reply_text(f"Sent to {sent} users")


# ================= ADMIN CALLBACK =================

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
    async def start(update, context):
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
            InlineKeyboardButton(
                f"{movie['file_name'][:45]}",
                url=link
            )
        ])
