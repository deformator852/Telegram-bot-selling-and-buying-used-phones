from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from create_bot import DB_PATH
from enums import GroupRange
import aiosqlite


async def menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="/menu")
    return builder.as_markup()


async def new_group_range_kb():
    builder = InlineKeyboardBuilder()
    for group in GroupRange:
        builder.button(text=group.value, callback_data=f"new_group_range_{group.value}")
    builder.adjust(1)
    return builder.as_markup()


async def group_modify_range_kb():
    builder = InlineKeyboardBuilder()
    for group in GroupRange:
        builder.button(text=group.value, callback_data=f"modify_range_{group.value}")
    builder.adjust(1)
    return builder.as_markup()


async def group_range_kb():
    builder = InlineKeyboardBuilder()
    for group in GroupRange:
        builder.button(text=group.value, callback_data=f"choose_group_{group.value}")
    builder.adjust(1)
    return builder.as_markup()


async def confirm_delete_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Yes✅", callback_data="yes_delete")
    builder.button(text="No❌", callback_data="no_delete")
    builder.adjust(2)
    return builder.as_markup()


async def profile_adv_kb(row, task_id):
    kb = []
    if row[7] == 0:
        kb.append(
            [
                InlineKeyboardButton(
                    text="   ⚡Run task⚡   ",
                    callback_data=f"run_{task_id}",
                )
            ]
        )
    else:
        kb.append(
            [
                InlineKeyboardButton(
                    text="   🛑Stop task🛑   ", callback_data=f"stop_{task_id}"
                )
            ]
        )
    kb.append(
        [
            InlineKeyboardButton(
                text="Night range", callback_data=f"nightrangemodify_{row[0]}"
            ),
            InlineKeyboardButton(text=row[6], callback_data="1"),
        ]
    )
    kb.append(
        [
            InlineKeyboardButton(
                text="Day range", callback_data=f"dayrangemodify_{row[0]}"
            ),
            InlineKeyboardButton(text=row[5], callback_data="1"),
        ]
    )
    kb.append(
        [
            InlineKeyboardButton(text="Groups", callback_data=f"changegroups_{row[0]}"),
            InlineKeyboardButton(text=row[4], callback_data="1"),
        ]
    )
    kb.append(
        [
            InlineKeyboardButton(
                text="Description", callback_data=f"descriptiontext_{row[0]}"
            ),
        ]
    )
    kb.append(
        [
            InlineKeyboardButton(
                text="Change image", callback_data=f"imagemodify_{row[0]}"
            )
        ]
    )
    kb.append(
        [
            InlineKeyboardButton(
                text="Remove💀", callback_data=f"deletetask_{task_id}"
            ),
            InlineKeyboardButton(text="Back⬅", callback_data="back_task_list"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=kb)


async def tasks_list_kb(message):
    builder = InlineKeyboardBuilder()
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f"SELECT id,task_name FROM advertisements") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    builder.button(text=row[1], callback_data=f"task_{row[0]}")
                match len(rows):
                    case 0:
                        builder.button(text="➖", callback_data="1")
                        builder.button(text="➖", callback_data="1")
                        builder.button(text="➖", callback_data="1")
                    case 1:
                        builder.button(text="➖", callback_data="1")
                        builder.button(text="➖", callback_data="1")
                    case 2:
                        builder.button(text="➖", callback_data="1")
                    case _:
                        pass

    except Exception as e:
        await message.answer("Some problem with access to database!")
    finally:
        builder.button(text="➕Create task➕", callback_data="create_task")
        builder.button(text="➕New group ➕", callback_data="add_new_group")
        builder.button(text="➕Delete group➕", callback_data="delete_group")
        builder.button(text="➕Groups list➕", callback_data="groups_list")
        builder.adjust(1)
        return builder.as_markup()


async def cancel_state_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="cancel", callback_data="cancel_state")
    return builder.as_markup()
