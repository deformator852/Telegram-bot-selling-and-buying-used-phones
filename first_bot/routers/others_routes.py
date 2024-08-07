from aiogram import Router, F
from aiogram.filters.logic import and_f
from custom_filters import IsAdminFilter  # pyright:ignore
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.filters import Command
from keyboards import menu_kb, tasks_list_kb  # pyright:ignore
from aiogram.fsm.context import FSMContext
from create_bot import DB_PATH
import aiosqlite

others_router = Router()

@others_router.callback_query(F.data == "back_task_list")
async def back_task_list(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer(
        "Advertisements list: ",
        reply_markup=await tasks_list_kb(callback_query.message),
    )


@others_router.message(and_f(IsAdminFilter(F.message), Command("menu")))
@others_router.message(and_f(IsAdminFilter(F.message), Command("start")))
async def start(message: Message):
    await message.delete()
    await message.answer(
        "Advertisements list: ", reply_markup=await tasks_list_kb(message)
    )


@others_router.callback_query(F.data == "cancel_state")
async def cancel_state(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.delete()
    await callback_query.message.answer(
        "Advertisements list: ", reply_markup=await tasks_list_kb(callback_query.message)
    )


@others_router.message(and_f(IsAdminFilter(F.message), F.text == "List advertisement"))
async def advertisement_list(message: Message):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                f"SELECT description,iphone_type,image from advertisements"
            ) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    photo = FSInputFile(row[2], filename="element")
                    await message.answer_photo(
                        photo=photo, caption=f"{row[0]}\nModel: {row[1]}"
                    )
    except Exception as e:
        print(e)
        await message.answer("Some problem with access to database!")
