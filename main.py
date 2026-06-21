from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from pymongo import MongoClient
import os
import uuid


# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

ADMIN_ID = 5565826679

BOT_USERNAME = "Gezxbot"

SEARCH_GROUP = "https://t.me/+0sWBTplLi4s3ODM9"


# ================= DATABASE =================

client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)

db = client["autofilter"]

files = db["files"]


try:
    client.server_info()
    print("MongoDB Connected")
except Exception as e:
    print("MongoDB Error:", e)



# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    args = context.args


    # Send file from deep link

    if args:

        movie_id = args[0]

        movie = files.find_one(
            {
                "movie_id": movie_id
            }
        )


        if movie:

            await context.bot.send_document(

                chat_id=update.effective_user.id,

                document=movie["file_id"],

                caption=
                f"🎬 {movie['file_name']}\n\n"
                "Enjoy your movie ❤️"

            )

            return



    buttons = [

        [

            InlineKeyboardButton(

                "🔎 Search Movies Group",

                url=SEARCH_GROUP

            )

        ]

    ]


    await update.message.reply_text(

        "⚠️ ꜱᴏʀʀʏ ɪ ᴄᴀɴ'ᴛ ᴡᴏʀᴋ ɪɴ ᴘᴍ\n\n"

        "ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇꜱ ɪɴ ᴏᴜʀ ᴍᴏᴠɪᴇ ꜱᴇᴀʀᴄʜ ɢʀᴏᴜᴘ.",

        reply_markup=
        InlineKeyboardMarkup(buttons)

    )





# ================= ADMIN UPLOAD =================


def is_admin(update):

    return (
        update.effective_user and
        update.effective_user.id == ADMIN_ID
    )



async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):


    if not is_admin(update):

        return



    if not update.message:

        return



    doc = update.message.document



    if not doc:

        return



    movie_id = str(uuid.uuid4())[:8]



    files.insert_one(

        {

            "movie_id": movie_id,

            "file_name": doc.file_name,

            "file_id": doc.file_id

        }

    )


    await update.message.reply_text(

        f"✅ Saved\n\n"
        f"🎬 {doc.file_name}\n"
        f"🔗 ID: {movie_id}"

    )


    print(
        "Saved:",
        doc.file_name,
        movie_id
    )





# ================= SEARCH =================


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):


    if not update.message:

        return



    query = update.message.text



    result = files.find(

        {

            "file_name":

            {

                "$regex": query,

                "$options": "i"

            }

        }

    ).limit(10)



    buttons = []

    count = 0



    for movie in result:


        count += 1


        link = (

            f"https://t.me/"
            f"{BOT_USERNAME}"
            f"?start={movie['movie_id']}"

        )


        buttons.append(

            [

                InlineKeyboardButton(

                    f" {movie['file_name'][:45]}",

                    url=link

                )

            ]

        )




    if count == 0:


        await update.message.reply_text(

            "❌ Movie not found"

        )

        return



    await update.message.reply_text(

        f"🎬 Results for: {query}",

        reply_markup=
        InlineKeyboardMarkup(buttons)

    )






# ================= RUN =================


app = ApplicationBuilder().token(TOKEN).build()



app.add_handler(

    CommandHandler(
        "start",
        start
    )

)


app.add_handler(

    MessageHandler(

        filters.Document.ALL,

        save_file

    )

)



app.add_handler(

    MessageHandler(

        filters.TEXT &
        ~filters.COMMAND,

        search

    )

)



print("Bot Started Successfully 🚀")


app.run_polling()
