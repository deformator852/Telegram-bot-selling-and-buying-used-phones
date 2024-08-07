from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from create_bot import DB_PATH
from enums import Memory  # pyright:ignore
from utils import get_products_list
import aiosqlite


async def choose_new_product_brand_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Apple", callback_data="new_product_brand_iphone")
    builder.button(text="Samsung", callback_data="new_product_brand_samsung")
    return builder.as_markup()


async def choose_brand_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Apple", callback_data="choose_brand_iphone")
    builder.button(text="Samsung", callback_data="choose_brand_samsung")
    return builder.as_markup()


async def choose_new_memory_kb():
    builder = InlineKeyboardBuilder()
    for m in Memory:
        builder.button(text=f"{m.value}GB", callback_data=f"choose_memory_{m.value}")
    builder.adjust(1)
    return builder.as_markup()


async def choose_memory_kb():
    builder = InlineKeyboardBuilder()
    for m in Memory:
        builder.button(text=f"{m.value}GB", callback_data=f"choose_defect_{m.value}")
    builder.adjust(1)
    return builder.as_markup()


async def choose_product_kb(brand):
    products = await get_products_list()
    builder = InlineKeyboardBuilder()
    for product in products:
        if brand in product[0].lower():
            builder.button(
                text=product[0].title(), callback_data=f"choose_product_{product[0]}"
            )
    builder.adjust(1)
    return builder.as_markup()


async def yes_no_kb(language):
    builder = InlineKeyboardBuilder()
    yes = ""
    no = ""
    if language == "ru":
        yes = "Да"
        no = "Нет"
    elif language == "en":
        yes = "Yes"
        no = "No"
    elif language == "lv":
        yes = "Jā"
        no = "Nē"
    builder.button(text=yes, callback_data="choose_defect_1")
    builder.button(text=no, callback_data="choose_defect_0")
    builder.adjust(2)
    return builder.as_markup()


async def confirm_deleting_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅", callback_data="yes")
    builder.button(text="❌", callback_data="no")
    builder.adjust(2)
    return builder.as_markup()


async def cancel_state_callback_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌", callback_data="cancel_state_callback")
    return builder.as_markup()


async def products_list_kb():
    builder = InlineKeyboardBuilder()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id,model FROM products") as cursor:
            result = await cursor.fetchall()
            for model in result:
                builder.button(text=model[1], callback_data=f"detail_{model[0]}")
            builder.button(text="Back⬅", callback_data="back_menu")
            builder.adjust(1)
            return builder.as_markup()


async def admin_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Create new product", callback_data="create_product")
    builder.button(text="Products", callback_data="products")
    builder.adjust(1)
    return builder.as_markup()


async def cancel_state_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌", callback_data="cancel_state")
    return builder.as_markup()


async def choose_language():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇱🇻", callback_data="lv")
    builder.button(text="🇬🇧󠁧󠁢󠁥󠁮󠁧󠁿", callback_data="en")
    builder.button(text="🇷🇺", callback_data="ru")
    builder.adjust(3)
    return builder.as_markup()


async def start_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="/flip")
    return builder.as_markup()
