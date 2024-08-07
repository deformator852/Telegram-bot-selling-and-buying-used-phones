from aiogram import F, Router
from aiogram.filters import callback_data
from aiogram.filters.logic import and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from custom_filters import IsAdminFilter
from create_bot import DB_PATH
from utils import remove_current_answer
from enums import GroupRange
from keyboards import cancel_state_kb, new_group_range_kb, tasks_list_kb
from states import AddNewGroup, DeleteGroup
import aiosqlite

groups_router = Router()


@groups_router.callback_query(F.data.startswith("delete_grp_"))
async def get_delete_group(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    id = callback_query.data.split("_")[-1]
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f"DELETE FROM groups WHERE id = {id}") as cursor:
                await db.commit()
                await callback_query.message.answer("Group successfully deleted!")
                await callback_query.message.answer(
                    "Advertisements list: ",
                    reply_markup=await tasks_list_kb(callback_query.message),
                )
    except Exception:
        await callback_query.message.answer("Error with deleting!Try again!")
        await callback_query.message.answer(
            "Advertisements list: ",
            reply_markup=await tasks_list_kb(callback_query.message),
        )
    finally:
        await state.clear()


@groups_router.callback_query(and_f(IsAdminFilter(F.message), F.data == "delete_group"))
async def delete_group(callback_query: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="Cancel", callback_data="cancel_state")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id,group_link FROM groups") as cursor:
            result = await cursor.fetchall()
            for group in result:
                builder.button(text=group[1], callback_data=f"delete_grp_{group[0]}")
            builder.adjust(1)
            answer = await callback_query.message.answer(
                "Groups: ", reply_markup=builder.as_markup()
            )
            await callback_query.message.delete()
            await state.set_state(DeleteGroup.GROUP)
            await state.update_data(current_answer=answer)


@groups_router.callback_query(and_f(IsAdminFilter(F.message), F.data == "groups_list"))
async def groups_list(callback_query: CallbackQuery):
    await callback_query.message.delete()
    answer = ""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM groups") as cursor:
            result = await cursor.fetchall()
            range1 = "0-2500\n"
            range2 = "25001-15000\n"
            range3 = "15001-1000000\n"
            for group in result:
                if group[1] == "0-2500":
                    range1 += f"{group[2]}\n"
                elif group[1] == "2501-15000":
                    range2 += f"{group[2]}\n"
                else:
                    range3 += f"{group[2]}\n"
            answer = range1 + "\n" + range2 + "\n" + range3
            builder = InlineKeyboardBuilder()
            builder.button(text="Back⬅", callback_data="back_task_list")
            await callback_query.message.answer(
                answer, reply_markup=builder.as_markup()
            )


@groups_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data == "add_new_group")
)
async def add_new_group(callback_query: CallbackQuery, state: FSMContext):
    answer = "Provide one of this group range:\n"
    answer = await callback_query.message.answer(
        answer, reply_markup=await new_group_range_kb()
    )
    await state.set_state(AddNewGroup.GROUP_RANGE)
    await state.update_data(current_answer=answer)


@groups_router.callback_query(F.data.startswith("new_group_range_"))
async def get_group_range(callback_query: Message, state: FSMContext):
    callback_data = callback_query.data.split("_")
    group_range = callback_data[-1]
    for group in GroupRange:
        if group.value == group_range:
            await state.update_data(group_range=group_range)
            answer = await callback_query.message.answer(
                "Provide group link: ", reply_markup=await cancel_state_kb()
            )
            await state.update_data(current_answer=answer)
            await state.set_state(AddNewGroup.GROUP_LINK)
            return
    await callback_query.message.answer("Error!Provide another range!")


@groups_router.message(and_f(IsAdminFilter(F.message), AddNewGroup.GROUP_LINK))
async def get_group_link(message: Message, state: FSMContext):
    group_link = message.text
    if group_link.startswith("https://"):
        data = await state.get_data()
        group_range = data.get("group_range")
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    "INSERT INTO groups(group_range,group_link) VALUES (?, ?) ",
                    (group_range, group_link),
                )
                await remove_current_answer(state, message)
                await db.commit()
                await message.answer("New group successfully added!")
                await message.answer(
                    "Advertisements list: ", reply_markup=await tasks_list_kb(message)
                )
        except:
            await message.answer("Error with adding new group!")
        finally:
            await state.clear()
    else:
        await message.answer("Error!Provide another link")
