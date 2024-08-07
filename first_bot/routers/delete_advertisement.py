from aiogram import F, Router
from aiogram.filters.logic import and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from custom_filters import IsAdminFilter
from create_bot import DB_PATH
from keyboards import confirm_delete_kb, tasks_list_kb
from states import DeleteTask
import aiosqlite
import os


delete_adv_router = Router()


@delete_adv_router.callback_query(
    and_f(
        IsAdminFilter(F.message),
        F.data == "no_delete",
    )
)
async def cancel_delete(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_answer = data.get("current_answer")
    current_answer.delete()
    await callback_query.message.delete()
    await callback_query.message.answer("❌")
    await callback_query.message.answer(
        "Advertisements list: ",
        reply_markup=await tasks_list_kb(callback_query.message),
    )
    await state.clear()


@delete_adv_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("deletetask_"))
)
async def delete_adv_callback(callback_query: CallbackQuery, state: FSMContext):
    id: str = callback_query.data.split("_")[1]
    if id.isdigit():
        answer = await callback_query.message.answer(
            "Confirm deleting", reply_markup=await confirm_delete_kb()
        )
        await state.set_state(DeleteTask.TASK_ID)
        await state.update_data(current_answer=answer)
        await state.update_data(id=id)


@delete_adv_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data == "yes_delete")
)
async def delete_task(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = data.get("id")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                f"SELECT image from advertisements WHERE id = {id}"
            ) as cursor:
                row = await cursor.fetchone()
                image_path = row[0]
                await db.execute(f"DELETE FROM advertisements WHERE id = {id}")
                if os.path.exists(image_path):
                    os.remove(image_path)
                else:
                    await callback_query.message.answer("Error!Not exist image")
                await db.commit()
                current_answer = data.get("current_answer")
                current_answer.delete()
                await callback_query.message.delete()
                await callback_query.message.answer("✅")
                await callback_query.message.answer(
                    "Advertisements list: ",
                    reply_markup=await tasks_list_kb(callback_query.message),
                )
                await state.clear()
    except Exception as e:
        print(e)
        await callback_query.message.answer("Some problem with deleting!")
