async def auto_delete(context, chat_id, message_id, seconds=900):
    await asyncio.sleep(seconds)
    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except Exception as e:
        print("AUTO DELETE ERROR:", e)
