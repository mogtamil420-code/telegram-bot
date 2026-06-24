from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import START_IMAGE, SEARCH_GROUP_LINK

async def start_menu(update, context):

    user = update.effective_user

    text = (
        f"Hᴇʟʟᴏ {user.mention_html()},\n\n"
        "I Cᴀɴ Pʀᴏᴠɪᴅᴇ Mᴏᴠɪᴇs,\n"
        "Jᴜsᴛ Jᴏɪɴ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ Aɴᴅ Eɴᴊᴏʏ"
    )

    keyboard = [
        [
            InlineKeyboardButton("Hᴇʟᴘ", callback_data="help"),
            InlineKeyboardButton("Aʙᴏᴜᴛ", callback_data="about")
        ],
        [
            InlineKeyboardButton("Jᴏɪɴ Gʀᴏᴜᴘ", url=SEARCH_GROUP_LINK)
        ],
        [
            InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")
        ]
    ]

    await update.message.reply_text(
    text,
    parse_mode="HTML",
    reply_markup=InlineKeyboardMarkup(keyboard)
)
