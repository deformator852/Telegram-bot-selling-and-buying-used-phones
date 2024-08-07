from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from custom_filters import IsAdminFilter  # pyright:ignore
from aiogram.filters.logic import and_f
from enums import GroupRange
from utils import remove_current_answer
from keyboards import cancel_state_kb, group_range_kb, tasks_list_kb  # pyright:ignore
from states import AddNewAdvertisement  # pyright:ignore
from aiogram.fsm.context import FSMContext
from create_bot import bot, DB_PATH
import os
import uuid
import aiosqlite

new_adv_router = Router()


@new_adv_router.callback_query(and_f(IsAdminFilter(F.message), F.data == "create_task"))
async def new_adertisement(callback_query: CallbackQuery, state: FSMContext):
    answer = await callback_query.message.answer(
        "Provide a task name: ", reply_markup=await cancel_state_kb()
    )
    await state.update_data(current_answer=answer)
    await state.set_state(AddNewAdvertisement.TASK_NAME)


@new_adv_router.message(AddNewAdvertisement.TASK_NAME)
async def get_task_name(message: Message, state: FSMContext):
    await remove_current_answer(state, message)
    task_name = message.text
    await state.update_data(task_name=task_name)
    answer = await message.answer("Provide an image: ")
    await state.update_data(current_answer=answer)
    await state.set_state(AddNewAdvertisement.IMAGE)


@new_adv_router.message(AddNewAdvertisement.IMAGE)
async def get_image(message: Message, state: FSMContext):
    if message.document:
        photo_id = message.document.file_id
        await state.update_data(photo_id=photo_id)
        await remove_current_answer(state, message)
        answer = await message.answer("Provide a description: ")
        await state.update_data(current_answer=answer)
        await state.set_state(AddNewAdvertisement.DESCRIPTION)
    elif message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)
        await remove_current_answer(state, message)
        answer = await message.answer("Provide a description: ")
        await state.update_data(current_answer=answer)
        await state.set_state(AddNewAdvertisement.DESCRIPTION)

    else:
        await message.answer("Send photo please!")


@new_adv_router.message(AddNewAdvertisement.DESCRIPTION)
async def get_description(message: Message, state: FSMContext):
    await remove_current_answer(state, message)
    await state.update_data(description=message.text)
    answer_text = "Choose group range:\n"
    answer = await message.answer(answer_text,reply_markup=await group_range_kb())
    await state.update_data(current_answer=answer)
    await state.set_state(AddNewAdvertisement.GROUPS)


@new_adv_router.callback_query(F.data.startswith("choose_group_"))
async def get_group(callback_query:CallbackQuery,state:FSMContext):
    data = callback_query.data
    groups_range = data.split("_")[-1]
    if "-" in groups_range:
        for group in GroupRange:
            if group.value == groups_range:
                await callback_query.message.delete()
                await state.update_data(groups=groups_range)
                answer = await callback_query.message.answer("Provide day range(60,90,etc): ")
                await state.update_data(current_answer=answer)
                await state.set_state(AddNewAdvertisement.DAY_RANGE)
                return
        await callback_query.message.answer("Error!Provide group range again.")
    else:
        await callback_query.message.answer("Error!Provide group range again.")

# @new_adv_router.message(AddNewAdvertisement.GROUPS)
# async def get_groups_list(message: Message, state: FSMContext):
#     groups_range = message.text
#     if "-" in groups_range:
#         for group in GroupRange:
#             if group.value == groups_range:
#                 await remove_current_answer(state, message)
#                 await state.update_data(groups=groups_range)
#                 answer = await message.answer("Provide day range(60,90,etc): ")
#                 await state.update_data(current_answer=answer)
#                 await state.set_state(AddNewAdvertisement.DAY_RANGE)
#                 return
#         await message.answer("Error!Provide group range again.")
#     else:
#         await message.answer("Error!Provide group range again.")


@new_adv_router.message(AddNewAdvertisement.DAY_RANGE)
async def get_day_range(message: Message, state: FSMContext):
    day_range = message.text
    if day_range.isdigit():
        await remove_current_answer(state, message)
        await state.update_data(day_range=day_range)
        answer = await message.answer("Provide night time(60,90,etc): ")
        await state.update_data(current_answer=answer)
        await state.set_state(AddNewAdvertisement.NIGHT_RANGE)
    else:
        await message.answer("It's not number,try again")


@new_adv_router.message(AddNewAdvertisement.NIGHT_RANGE)
async def get_night_range(message: Message, state: FSMContext):
    night_range = message.text
    if night_range.isdigit():
        await remove_current_answer(state, message)
        await state.update_data(night_range=night_range)
        data = await state.get_data()
        photo_id = data.get("photo_id")
        photo_path = await download_photo(photo_id)
        result = await save_new_adv(data, photo_path)
        if result:
            await message.answer("New advertisement successfully added!")
            await message.answer(
                "Advertisements list: ", reply_markup=await tasks_list_kb(message)
            )
        else:
            await message.answer("Error with advertisement creating!Try again!")
            await message.answer(
                "Advertisements list: ", reply_markup=await tasks_list_kb(message)
            )
        await state.clear()
    else:
        await message.answer("It's not number,try again")


async def save_new_adv(data, image):
    description = data.get("description")
    groups = data.get("groups")
    day_range = data.get("day_range")
    night_range = data.get("night_range")
    task_name = data.get("task_name")
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                """
            INSERT INTO advertisements (description, image,groups,day_range,night_range,task_name,status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
                (
                    description,
                    image,
                    groups,
                    day_range,
                    night_range,
                    task_name,
                    True,
                ),
            )
            await db.commit()
            return True
        except Exception as e:
            print(e)
            return False


async def download_photo(photo_id):
    file = await bot.get_file(photo_id)
    save_path = os.path.expanduser("~/bot_database/images")
    file_extension = file.file_path.split("/")[-1]
    file_name = f"{str(uuid.uuid4())}{file_extension}"
    destination_path = os.path.join(save_path, file_name)
    await bot.download_file(file_path=file.file_path, destination=destination_path)
    return destination_path
