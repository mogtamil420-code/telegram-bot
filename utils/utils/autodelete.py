import asyncio

async def auto_delete(bot, chat_id, message_id, seconds=300):

    await asyncio.sleep(seconds)

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except:
        pass
