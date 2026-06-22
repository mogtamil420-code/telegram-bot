from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pymongo import MongoClient
import os, uuid, asyncio

============== CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

ADMIN_ID = 5565826679
BOT_USERNAME = "Gezxbot"

SEARCH_GROUP = "https://t.me/+0sWBTplLi4s3ODM9"

# 🔒 ONLY YOUR STORAGE CHANNEL (IMPORTANT SECURITY FIX)
ALLOWED_CHANNEL = -1001234567890  # <-- replace with your channel ID


# ================= DB =================

client = MongoClient(MONGO_URL)
db = client["autofilter"]

files = db["files"]
users = db["users"]


# ================= UTIL =================

async def save_user(update):
    if update.effective_user:
        users.update_one(
            {"user_id": update.effective_user.id},
            {"$set": {"user_id": update.effective_user.id}},
            upsert=True
        )


async def auto_delete(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass


# ================= START (WITH IMAGES UI) =================

WELCOME_IMAGES = [
    "https://i.imgur.com/1.jpg",
    "https://i.imgur.com/2.jpg",
    "https://i.imgur.com/3.jpg"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)
    args = context.args

    # ================= FILE DELIVERY =================
    if args:
        movie_id = args[0]
        movie = files.find_one({"movie_id": movie_id})

        if not movie:
            await update.message.reply_text("File not found")
            return

        # 🔒 USER LOCK SYSTEM
        if movie.get("locked_user") != update.effective_user.id:
            await update.message.reply_text(
                "⚠️ This is not your request.\nSearch your own movie."
            )
            return

        file_msg = await context.bot.send_document(
            chat_id=update.effective_user.id,
            document=movie["file_id"],
            caption=f"<b>{movie['caption']}</b>",
            parse_mode="HTML"
        )

        warn_msg = await update.message.reply_text(
            "⚠️ ᴀꜰᴛᴇʀ 15 ᴍɪɴᴜᴛᴇꜱ ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ 🗑️\n"
            "⚠️ ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴛᴏ ʏᴏᴜʀ ꜱᴀᴠᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ"
        )

        asyncio.create_task(auto_delete(file_msg, 900))
        asyncio.create_task(auto_delete(warn_msg, 900))
        return


    # ================= WELCOME IMAGE UI =================

    btn = [
        [InlineKeyboardButton("SEARCH MOVIES", url=SEARCH_GROUP)],
        [InlineKeyboardButton("HOW TO USE", callback_data="help")]
    ]

    await update.message.reply_photo(
        photo=WELCOME_IMAGES[0],
        caption=(
            "🎬 <b>WELCOME TO MOVIE BOT</b>\n\n"
            "🔎 Search movies in group\n"
            "📥 Get instant download links\n"
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pymongo import MongoClient
import os, uuid, asyncio


# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

ADMIN_ID = 5565826679
BOT_USERNAME = "Gezxbot"

SEARCH_GROUP = "https://t.me/+0sWBTplLi4s3ODM9"

# 🔒 ONLY YOUR STORAGE CHANNEL (IMPORTANT SECURITY FIX)
ALLOWED_CHANNEL = -1001234567890  # <-- replace with your channel ID


# ================= DB =================

client = MongoClient(MONGO_URL)
db = client["autofilter"]

files = db["files"]
users = db["users"]


# ================= UTIL =================

async def save_user(update):
    if update.effective_user:
        users.update_one(
            {"user_id": update.effective_user.id},
            {"$set": {"user_id": update.effective_user.id}},
            upsert=True
        )


async def auto_delete(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass


# ================= START (WITH IMAGES UI) =================

WELCOME_IMAGES = [
    "https://i.imgur.com/1.jpg",
    "https://i.imgur.com/2.jpg",
    "https://i.imgur.com/3.jpg"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)
    args = context.args

    # ================= FILE DELIVERY =================
    if args:
        movie_id = args[0]
        movie = files.find_one({"movie_id": movie_id})

        if not movie:
            await update.message.reply_text("File not found")
            return

        # 🔒 USER LOCK SYSTEM
        if movie.get("locked_user") != update.effective_user.id:
            await update.message.reply_text(
                "⚠️ This is not your request.\nSearch your own movie."
            )
            return

        file_msg = await context.bot.send_document(
            chat_id=update.effective_user.id,
            document=movie["file_id"],
            caption=f"<b>{movie['caption']}</b>",
            parse_mode="HTML"
        )

        warn_msg = await update.message.reply_text(
            "⚠️ ᴀꜰᴛᴇʀ 15 ᴍɪɴᴜᴛᴇꜱ ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ 🗑️\n"
            "⚠️ ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴛᴏ ʏᴏᴜʀ ꜱᴀᴠᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ"
        )

        asyncio.create_task(auto_delete(file_msg, 900))
        asyncio.create_task(auto_delete(warn_msg, 900))
        return


    # ================= WELCOME IMAGE UI =================

    btn = [
        [InlineKeyboardButton("SEARCH MOVIES", url=SEARCH_GROUP)],
        [InlineKeyboardButton("HOW TO USE", callback_data="help")]
    ]

    await update.message.reply_photo(
        photo=WELCOME_IMAGES[0],
        caption=(
            "🎬 <b>WELCOME TO MOVIE BOT</b>\n\n"
            "🔎 Search movies in group\n"
            "📥 Get instant download links\n"
            "⚡ Fast & Auto Filter System"
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ================= SAVE FILE FROM CHANNEL =================

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.channel_post:
        return

    msg = update.channel_post

    # 🔒 SECURITY: ONLY YOUR CHANNEL
    if msg.chat_id != ALLOWED_CHANNEL:
        return

    doc = msg.document or msg.video or (msg.photo[-1] if msg.photo else None)

    if not doc:
        return

    movie_id = str(uuid.uuid4())[:8]
    caption = msg.caption if msg.caption else "No Caption"

    files.insert_one({
        "movie_id": movie_id,
        "file_id": doc.file_id,
        "file_name": caption,
        "caption": caption,
        "locked_user": None
    })

    print("Saved:", movie_id)


# ================= SEARCH =================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await save_user(update)

    query = update.message.text

    results = list(files.find({
        "file_name": {"$regex": query, "$options": "i"}
    }).limit(10))

    if not results:
        await update.message.reply_text("No results found")
        return

    buttons = []

    for movie in results:

        # LOCK TO USER
        files.update_one(
            {"movie_id": movie["movie_id"]},
            {"$set": {"locked_user": update.effective_user.id}}
        )

        link = f"https://t.me/{BOT_USERNAME}?start={movie['movie_id']}"

        buttons.append([
            InlineKeyboardButton(movie["file_name"][:45], url=link)
        ])

    msg = await update.message.reply_text(
        f"🎬 Results for: {query}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    asyncio.create_task(auto_delete(msg, 300))


# ================= CALLBACK =================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    if q.data == "help":
        await q.message.reply_text(
            "1. Go to group\n2. Search movie\n3. Click button\n4. Get file in PM"
        )


# ================= ADMIN =================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    btn = [
        [InlineKeyboardButton("Status", callback_data="status")],
        [InlineKeyboardButton("Broadcast", callback_data="broadcast")]
    ]

    await update.message.reply_text(
        "ADMIN PANEL",
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))

app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, save_file))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
app.add_handler(CallbackQueryHandler(callback))

print("BOT STARTED 🚀")
app.run_polling()￼Enter    "⚡ Fast & Auto Filter System"
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ================= SAVE FILE FROM CHANNEL =================

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
