from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pymongo import MongoClient
import os
from collections import defaultdict


# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

ADMIN_ID = 5565826679
BOT_USERNAME = "Gezxbot"

FORCE_CHANNEL = "https://t.me/+SZWfXlte9ddkMTJl"


# ================= DB =================

client = MongoClient(MONGO_URL)
db = client["autofilter"]

files = db["files"]
users = db["users"]


# ================= MEMORY STORE (IMPORTANT FIX) =================

pending_requests = {}   # user_id -> movie_id


# ================= UTIL =================

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
            chat_id="@SZWfXlte9ddkMTJl",
            user_id=update.effective_user.id
        )

        return member.status not in ["left", "kicked"]

    except:
        return False


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    args = context.args

    user_id = update.effective_user.id

    # ================= FILE REQUEST FLOW =================
    if args:

        movie_id = args[0]

        # SAVE REQUEST (IMPORTANT FIX)
        pending_requests[user_id] = movie_id

        # FORCE JOIN CHECK
        if not await is_joined(update, context):

            btn = [
                [InlineKeyboardButton("Jᴏɪɴ", url=FORCE_CHANNEL)],
                [InlineKeyboardButton("Tʀʏ ᴀɢᴀɪɴ", callback_data="retry")]
            ]

            await update.message.reply_text(
                "⚠️ Yᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴄᴏᴜɴᴛɪɴᴜᴇ",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return

        # if already joined → send file
        return await send_file(update, context, movie_id)

    # normal start
    await update.message.reply_text("🎬 Welcome! Search movies in group")


# ================= SEND FILE FUNCTION =================

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


# ================= CALLBACK =================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id

    if q.data == "retry":

        # GET STORED REQUEST (IMPORTANT FIX)
        movie_id = pending_requests.get(user_id)

        if not movie_id:
            await q.message.reply_text("No request found. Use /start again")
            return

        if await is_joined(update, context):

            await send_file(update, context, movie_id)

        else:

            await q.message.reply_text("Still not joined channel")



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

    await update.message.reply_text(
        "Results:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
app.add_handler(CallbackQueryHandler(callback))

print("BOT FIXED 🚀")
app.run_polling()
