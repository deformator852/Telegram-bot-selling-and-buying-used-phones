from create_bot import DB_PATH, bot


async def change_last(text, keyboard, callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    await bot.edit_message_text(
        chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard,
    )


async def remove_current_answer(state,message):
    data = await state.get_data()
    last_answer = data.get("current_answer")
    await last_answer.delete()
    await message.delete()
