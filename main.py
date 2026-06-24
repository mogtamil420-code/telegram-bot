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


# ================= BROADCAST STATE =================
broadcast_mode = {}


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


# ================= AUTO DELETE =================
async def auto_delete(context, chat_id, message_id, seconds=900):
    await asyncio.sleep(seconds)
    try:
        await context.bot.delete_message(chat_id, message_id)
    except:
        pass


# ================= SEND FILE =================
async def send_file(update, context, movie_id):
    movie = files.find_one({"movie_id": movie_id})

    if not movie:
        await update.message.reply_text("❌ Rᴇǫᴜᴇsᴛ ɴᴏᴛ ғᴏᴜɴᴅ")
        return

    user_id = update.effective_user.id

    msg = await context.bot.send_document(
        chat_id=user_id,
        document=movie["file_id"],
        caption=f"<b>{movie['caption']}</b>",
        parse_mode="HTML"
    )

    asyncio.create_task(auto_delete(context, msg.chat_id, msg.message_id))


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_user(update)

    user = update.effective_user

    # FILE MODE
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

    # START MENU
    await start_menu(update, context)
    return


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type == "private":
        return

    query = update.message.text

    results = files.find({
        "file_name": {"$regex": query, "$options": "i"}
    }).limit(10)

    buttons = []

    for movie in results:

        link = f"https://t.me/{BOT_USERNAME}?start={movie['movie_id']}"

        buttons.append([
            InlineKeyboardButton(
                movie["file_name"][:45],
                url=link
            )
        ])

    if not buttons:
        return

    msg = await update.message.reply_text(
        "🎬 Results:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    asyncio.create_task(
        auto_delete(
            context,
            msg.chat_id,
            msg.message_id,
            300
        )
    )
# ================= CALLBACK =================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    data = q.data

    if data.startswith("check_"):

        movie_id = data.split("_")[1]

        if not await is_joined(update, context):
            await q.message.reply_text(
                "Still not joined channel!"
            )
            return

        movie = files.find_one({"movie_id": movie_id})

        if movie:
            await context.bot.send_document(
                chat_id=q.from_user.id,
                document=movie["file_id"],
                caption=movie["caption"]
            )

    elif data == "status":

        total = users.count_documents({})

        await q.message.reply_text(
            f"👥 Total Users: {total}"
        )

    elif data == "broadcast":

        if q.from_user.id == ADMIN_ID:

            broadcast_mode[q.from_user.id] = True

            await q.message.reply_text(
                "📢 Send broadcast message now..."
            )

    elif data == "close":

        await q.message.delete()


# ================= ADMIN =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    buttons = [
        [InlineKeyboardButton("📊 Sᴛᴀᴛᴜs", callback_data="status")],
        [InlineKeyboardButton("📢 Bʀᴏᴀᴅᴄᴀsᴛ", callback_data="broadcast")]
    ]

    await update.message.reply_text(
        "⚙️ Admin Panel",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= BROADCAST MESSAGE =================
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    if not broadcast_mode.get(user_id):
        return

    text = update.message.text

    users_list = list(users.find())  # IMPORTANT FIX (preload)

    sent = 0

    for u in users_list:
        try:
            await context.bot.send_message(
                chat_id=u["user_id"],
                text=text
            )
            sent += 1
        except:
            pass

    broadcast_mode[user_id] = False

    await update.message.reply_text(f"📢 Sent to {sent} users")

# ================= ADMIN CALLBACK =================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    data = q.data

    if data == "status":
        total = users.count_documents({})
        await q.message.reply_text(f"👥 Total Users: {total}")


# ================= APP =================

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_broadcast
    ),
    group=0
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        search
    ),
    group=1
)

app.add_handler(
    CallbackQueryHandler(callback)
)

print("BOT STARTED 🚀")
app.run_polling()
