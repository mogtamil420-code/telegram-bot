from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_ID
from database import users

async def admin_panel(update, context):

    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "Status",
                callback_data="status"
            )
        ],
        [
            InlineKeyboardButton(
                "Broadcast",
                callback_data="broadcast"
            )
        ]
    ]

    await update.message.reply_text(
        "Admin Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
