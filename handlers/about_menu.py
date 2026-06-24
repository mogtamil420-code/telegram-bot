from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ABOUT_IMAGE

async def about_menu(update, context):

    me = await context.bot.get_me()

    text = (
        f"🤖 Mʏ Nᴀᴍᴇ: @{me.username}\n"
        f"👨‍💻 Cʀᴇᴀᴛᴏʀ: {ADMIN_ID}\n"
        "📚 Lɪʙʀᴀʀʏ: Python Telegram Bot v20\n"
        "⚙️ Lᴀɴɢᴜᴀɢᴇ: Python 3\n"
        "🗄 DᴀᴛᴀBᴀsᴇ: MongoDB\n"
        "🚂 Bᴏᴛ Sᴇʀᴠᴇʀ: Railway\n"
        "🛠 Bᴜɪʟᴅ Sᴛᴀᴛᴜs: v1.0 Stable"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "• Sᴏᴜʀᴄᴇ Cᴏᴅᴇ •",
                callback_data="source_code"
            ),
            InlineKeyboardButton(
                "❗ Dɪsᴄʟᴀɪᴍᴇʀ ❗",
                callback_data="disclaimer"
            )
        ],
        [
            InlineKeyboardButton(
                "« Bᴀᴄᴋ",
                callback_data="back_start"
            ),
            InlineKeyboardButton(
                "Cʟᴏsᴇ",
                callback_data="close"
            )
        ]
    ]

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=ABOUT_IMAGE,
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
