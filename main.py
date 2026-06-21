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
    CallbackQueryHandler,
    filters
)

from pymongo import MongoClient
import os
import uuid


# =============== CONFIG ===============

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

ADMIN_ID = 5565826679

BOT_USERNAME = "Gezxbot"

SEARCH_GROUP = "https://t.me/+0sWBTplLi4s3ODM9"



# =============== DATABASE ===============


client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)


db = client["autofilter"]


files = db["files"]

users = db["users"]



try:

    client.server_info()

    print("MongoDB Connected")

except Exception as e:

    print("Mongo Error:", e)




# =============== SAVE USERS ===============


async def save_user(update):

    if not update.effective_user:

        return


    users.update_one(

        {
            "user_id":
            update.effective_user.id
        },

        {
            "$set":
            {
                "user_id":
                update.effective_user.id
            }
        },

        upsert=True

    )





# =============== START ===============


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):


    await save_user(update)



    # ADMIN PANEL


    if update.effective_user.id == ADMIN_ID:


        buttons = [

            [

                InlineKeyboardButton(
                    "📊 Status",
                    callback_data="status"
                )

            ],

            [

                InlineKeyboardButton(
                    "📢 Broadcast",
                    callback_data="broadcast"
                )

            ]

        ]



        await update.message.reply_text(

            "👑 Welcome Admin",

            reply_markup=
            InlineKeyboardMarkup(buttons)

        )

        return




    args = context.args



    # SEND FILE


    if args:


        movie_id = args[0]



        movie = files.find_one(

            {
                "movie_id":
                movie_id
            }

        )



        if movie:



            caption = movie.get(

                "caption",

                movie["file_name"]

            )



            await context.bot.send_document(

                chat_id=
                update.effective_user.id,

                document=
                movie["file_id"],

                caption=
                f"<b>{caption}</b>",

                parse_mode=
                "HTML"

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






# =============== STORAGE CHANNEL ===============


async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):


    if not update.channel_post:

        return



    doc = update.channel_post.document



    if not doc:

        return




    movie_id = str(uuid.uuid4())[:8]



    caption = (

        update.channel_post.caption

        if update.channel_post.caption

        else doc.file_name

    )



    files.insert_one(

        {

            "movie_id":
            movie_id,

            "file_id":
            doc.file_id,

            "file_name":
            doc.file_name,

            "caption":
            caption

        }

    )



    print(

        "Saved:",
        caption

    )







# =============== SEARCH ===============


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):


    await save_user(update)



    query = update.message.text



    results = files.find(

        {

            "file_name":

            {

                "$regex":
                query,

                "$options":
                "i"

            }

        }

    ).limit(10)



    buttons = []


    count = 0



    for movie in results:


        count += 1



        link = (

            f"https://t.me/"

            f"{BOT_USERNAME}"

            f"?start={movie['movie_id']}"

        )



        buttons.append(

            [

                InlineKeyboardButton(

                    "📁 "
                    + movie["file_name"][:50],

                    url=link

                )

            ]

        )






    if count == 0:


        await update.message.reply_text(

            "❌ No results found"

        )

        return




    await update.message.reply_text(

        f"🎬 Results for: {query}",

        reply_markup=
        InlineKeyboardMarkup(buttons)

    )






# =============== ADMIN BUTTONS ===============


async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):


    query = update.callback_query


    await query.answer()



    if query.data == "status":


        total = users.count_documents({})


        await query.message.reply_text(

            f"📊 Total Users: {total}"

        )




    elif query.data == "broadcast":


        context.user_data["broadcast"] = True



        await query.message.reply_text(

            "📢 Send message to broadcast"

        )







# =============== BROADCAST ===============


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):


    if update.effective_user.id != ADMIN_ID:

        return



    if context.user_data.get("broadcast"):


        msg = update.message.text



        sent = 0



        for user in users.find():

            try:


                await context.bot.send_message(

                    user["user_id"],

                    msg

                )


                sent += 1


            except:

                pass




        context.user_data["broadcast"] = False



        await update.message.reply_text(

            f"✅ Broadcast sent to {sent} users"

        )








# =============== UNKNOWN MESSAGE ===============


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):


    await save_user(update)


    await update.message.reply_text(

        "⚠️ Please use /start command"

    )







# =============== BOT ===============


app = ApplicationBuilder().token(TOKEN).build()



app.add_handler(

    CommandHandler(

        "start",

        start

    )

)



app.add_handler(

    MessageHandler(

        filters.UpdateType.CHANNEL_POST,

        save_file

    )

)



app.add_handler(

    MessageHandler(

        filters.TEXT & ~filters.COMMAND,

        search

    )

)



app.add_handler(

    CallbackQueryHandler(

        admin_buttons

    )

)



app.add_handler(

    MessageHandler(

        filters.TEXT,

        broadcast

    )

)



app.add_handler(

    MessageHandler(

        filters.ALL,

        unknown

    )

)



print("BOT STARTED 🚀")


app.run_polling()
