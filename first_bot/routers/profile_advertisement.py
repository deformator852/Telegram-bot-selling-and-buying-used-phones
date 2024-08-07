from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from custom_filters import IsAdminFilter
from aiogram.filters.logic import and_f
from create_bot import DB_PATH, bot
from keyboards import profile_adv_kb
import aiosqlite

profile_router = Router()


@profile_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("task_"))
)
async def profile_advertisement(callback_query: CallbackQuery):
    task_id = callback_query.data.split("_")[-1]
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            f"SELECT * FROM advertisements WHERE id = {task_id}"
        ) as cursor:
            await callback_query.message.delete()
            row = await cursor.fetchone()
            kb = await profile_adv_kb(row, task_id)
            photo = FSInputFile(row[3], filename="adv")
            await callback_query.message.answer_photo(
                caption=f"Task {row[2]}", photo=photo, reply_markup=kb
            )


@profile_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("run_"))
)
async def run_task(callback_query: CallbackQuery):
    task_id = callback_query.data.split("_")[-1]
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                f"UPDATE advertisements SET status = 1 WHERE id = {task_id}"
            )
            await db.commit()
            await callback_query.message.answer("Task ran")
    except Exception as e:
        print(e)
        await callback_query.message.answer("Error with task run")


@profile_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("stop_"))
)
async def stop_task(callback_query: CallbackQuery):
    task_id = callback_query.data.split("_")[-1]
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                f"UPDATE advertisements SET status = 0 WHERE id = {task_id}"
            )
            await db.commit()
            await callback_query.message.answer("Task stopped")

    except Exception as e:
        print(e)
        await callback_query.message.answer("Error with task stoping")
        return False


@profile_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("descriptiontext_"))
)
async def description(callback_query: CallbackQuery):
    list_data = callback_query.data.split("_")
    id = list_data[-1]
    description_text = ""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            f"SELECT description FROM advertisements WHERE id = {id}"
        ) as cursor:
            result = await cursor.fetchone()
            description_text = result[0]
    kb = InlineKeyboardBuilder()
    kb.button(text="Change", callback_data=f"descriptionmodify_{id}")
    kb.button(text="Back⬅",callback_data=f"task_{id}")
    await callback_query.message.delete()
    await callback_query.message.answer(description_text, reply_markup=kb.as_markup())
