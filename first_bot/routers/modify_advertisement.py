from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile
from custom_filters import IsAdminFilter
from aiogram.filters.logic import and_f
from create_bot import DB_PATH, bot
from enums import GroupRange
from utils import remove_current_answer
from states import (
    ChangeDescription,
    ChangeImage,
    ChangeDayRange,
    ChangeNightRange,
    ChangeGroupsList,
)
from keyboards import group_modify_range_kb, tasks_list_kb
import aiosqlite
import uuid
import os

modify_adv_router = Router()


@modify_adv_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("imagemodify_"))
)
async def change_image(callback_query: CallbackQuery, state: FSMContext):
    id = callback_query.data.split("_")[-1]  # pyright:ignore
    await callback_query.message.delete()  # pyright:ignore
    await state.update_data(id=id)
    answer = await callback_query.message.answer("Provide an image: ")
    await state.update_data(current_answer=answer)
    await state.set_state(ChangeImage.IMAGE)


@modify_adv_router.message(and_f(IsAdminFilter(F.message), ChangeImage.IMAGE))
async def get_image(message: Message, state: FSMContext):
    data = await state.get_data()
    id = data.get("id")
    if message.document:
        photo_id = message.document.file_id
        new_photo_path = await download_photo(photo_id)
        result = await update_photo_path(new_photo_path, id)
        if result:
            await remove_current_answer(state, message)
            await message.answer("Successfully changed image")
            await message.answer(
                "Advertisements list: ", reply_markup=await tasks_list_kb(message)
            )
        else:
            await message.answer("Some error with changing image")
        await state.clear()
    elif message.photo:
        photo_id = message.photo[-1].file_id
        new_photo_path = await download_photo(photo_id)
        result = await update_photo_path(new_photo_path, id)
        if result:
            await remove_current_answer(state, message)
            await message.answer("Successfully changed image")
            await message.answer(
                "Advertisements list: ", reply_markup=await tasks_list_kb(message)
            )
        else:
            await message.answer("Some error with changing image")
        await state.clear()
    else:
        await message.answer("Please provide an image!")


@modify_adv_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("changegroups_"))
)
async def change_groups(callback_query: CallbackQuery, state: FSMContext):
    id = callback_query.data.split("_")[-1]  # pyright:ignore
    await callback_query.message.delete()  # pyright:ignore
    await state.update_data(id=id)
    answer_text = "Choose group range:"
    await callback_query.message.answer(answer_text,reply_markup=await group_modify_range_kb())
    await state.set_state(ChangeGroupsList.GROUPS_LIST)


@modify_adv_router.callback_query(F.data.startswith("modify_range_"))
async def get_group(callback_query: CallbackQuery, state: FSMContext):
    print("work")
    data = callback_query.data
    groups_range = data.split("_")[-1]
    state_data = await state.get_data()
    await callback_query.message.delete()
    id = state_data.get("id")
    print(id)
    for group in GroupRange:
        if group.value == groups_range:
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute(
                        "UPDATE advertisements SET groups = ? WHERE id = ?",
                        (
                            groups_range,
                            id,
                        ),
                    )
                    await db.commit()
                    await callback_query.message.answer(
                        "Successfully changed groups list"
                    )
                    await callback_query.message.answer(
                        "Advertisements list: ",
                        reply_markup=await tasks_list_kb(callback_query.message),
                    )

            except Exception as e:
                print(e)
                await callback_query.message.answer("Error with update groups range")
            finally:
                await state.clear()
                return
    await callback_query.message.answer("Error with update groups range")

# @modify_adv_router.message(
#     and_f(IsAdminFilter(F.message), ChangeGroupsList.GROUPS_LIST)
# )
# async def get_new_groups_list(message: Message, state: FSMContext):
#     data = await state.get_data()
#     id = data.get("id")
#     groups_list = message.text
#     if "-" in groups_list:
#         for group in GroupRange:
#             if group.value == groups_list:
#                 try:
#                     async with aiosqlite.connect(DB_PATH) as db:
#                         await db.execute(
#                             "UPDATE advertisements SET groups = ? WHERE id = ?",
#                             (
#                                 message.text,
#                                 id,
#                             ),
#                         )
#                         await remove_current_answer(state, message)
#                         await db.commit()
#                         await message.answer("Successfully changed groups list")
#                         await message.answer(
#                             "Advertisements list: ",
#                             reply_markup=await tasks_list_kb(message),
#                         )
#
#                 except Exception as e:
#                     print(e)
#                     await message.answer("Error with update day range")
#                 finally:
#                     await state.clear()
#                     return
#             await message.answer("Error!Try provide groups again")
#     else:
#         await message.answer("Try provide groups again")


@modify_adv_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("dayrangemodify_"))
)
async def change_day_range(callback_query: CallbackQuery, state: FSMContext):
    id = callback_query.data.split("_")[-1]  # pyright:ignore
    await callback_query.message.delete()  # pyright:ignore
    await state.update_data(id=id)
    answer = await callback_query.message.answer("Provide a day range: ")
    await state.update_data(current_answer=answer)
    await state.set_state(ChangeDayRange.DAY_RANGE)


@modify_adv_router.message(and_f(IsAdminFilter(F.message), ChangeDayRange.DAY_RANGE))
async def get_new_day_range(message: Message, state: FSMContext):
    data = await state.get_data()
    day_range = message.text
    id = data.get("id")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE advertisements SET day_range = ? WHERE id = ?",
                (
                    day_range,
                    id,
                ),
            )
            await remove_current_answer(state, message)
            await db.commit()
            await message.answer("Successfully changed day range")
            await message.answer(
                "Advertisements list: ", reply_markup=await tasks_list_kb(message)
            )

    except Exception as e:
        print(e)
        await message.answer("Error with update day range")
    finally:
        await state.clear()


@modify_adv_router.message(
    and_f(IsAdminFilter(F.message), ChangeNightRange.NIGHT_RANGE)
)
async def get_new_night_range(message: Message, state: FSMContext):
    data = await state.get_data()
    night_range = message.text
    id = data.get("id")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE advertisements SET night_range = ? WHERE id = ?",
                (
                    night_range,
                    id,
                ),
            )
            await remove_current_answer(state, message)
            await db.commit()
            await message.answer("Successfully changed night range")
            await message.answer(
                "Advertisements list: ", reply_markup=await tasks_list_kb(message)
            )

    except Exception as e:
        print(e)
        await message.answer("Error with update night range")
    finally:
        await state.clear()


@modify_adv_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("nightrangemodify_"))
)
async def change_nigth_range(callback_query: CallbackQuery, state: FSMContext):
    id = callback_query.data.split("_")[-1]
    await state.update_data(id=id)
    await callback_query.message.delete()
    answer = await callback_query.message.answer("Provide a night range: ")
    await state.update_data(current_answer=answer)
    await state.set_state(ChangeNightRange.NIGHT_RANGE)


@modify_adv_router.callback_query(
    and_f(IsAdminFilter(F.message), F.data.startswith("descriptionmodify_"))
)
async def change_description(callback_query: CallbackQuery, state: FSMContext):
    id = callback_query.data.split("_")[-1]
    await state.update_data(id=id)
    await callback_query.message.delete()
    answer = await callback_query.message.answer("Provide an description: ")
    await state.update_data(current_answer=answer)
    await state.set_state(ChangeDescription.DESCRIPTION)


@modify_adv_router.message(
    and_f(IsAdminFilter(F.message), ChangeDescription.DESCRIPTION)
)
async def get_description(message: Message, state: FSMContext):
    data = await state.get_data()
    description = message.text
    id = data.get("id")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE advertisements SET description = ? WHERE id = ?",
                (
                    description,
                    id,
                ),
            )
            await remove_current_answer(state, message)
            await db.commit()
            await message.answer("Successfully changed description")
            await message.answer(
                "Advertisements list: ", reply_markup=await tasks_list_kb(message)
            )

    except Exception as e:
        print(e)
        await message.answer("Error with update description")
    finally:
        await state.clear()


async def download_photo(photo_id):
    file = await bot.get_file(photo_id)
    save_path = os.path.expanduser("~/bot_database/images")
    file_extension = file.file_path.split("/")[-1]
    file_name = f"{str(uuid.uuid4())}{file_extension}"
    destination_path = os.path.join(save_path, file_name)
    await bot.download_file(file_path=file.file_path, destination=destination_path)
    return destination_path


async def update_photo_path(new_photo_path, id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE advertisements SET image = ? WHERE id = ?", (new_photo_path, id)
            )
            await db.commit()
            return True
    except:
        return False
