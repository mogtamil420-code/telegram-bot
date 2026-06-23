from config import FORCE_CHANNEL_ID

async def is_joined(user_id, bot):
    try:
        member = await bot.get_chat_member(
            FORCE_CHANNEL_ID,
            user_id
        )

        return member.status not in ["left", "kicked"]

    except:
        return False
