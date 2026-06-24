from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import HELP_IMAGE

async def help_menu(update, context):

    user = update.effective_user

    text = (
        f"Hᴇʏ {user.mention_html()},\n\n"
        "Hᴇʀᴇ Is Tʜᴇ Mʏ Cᴏᴍᴍᴀɴᴅs Fᴏʀ Hᴇʟᴘ."
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "• Fɪʟᴇ Sᴛᴏʀᴇ •",
                callback_data="file_store"
            ),
            InlineKeyboardButton(
                "• Exᴛʀᴀ Mᴏᴅs •",
                callback_data="extra_mods"
            )
        ],
        [
            InlineKeyboardButton(
                "• Rᴜʟᴇs •",
                callback_data="rules"
            ),
            InlineKeyboardButton(
                "• Sᴜᴘᴘᴏʀᴛ •",
                url="https://t.me/Tamil_Movies_Gez"
            )
        ],
        [
            InlineKeyboardButton(
                "« Bᴀᴄᴋ",
                callback_data="back_start"
            )
        ]
    ]

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=HELP_IMAGE,
        caption=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
