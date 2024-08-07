from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiosqlite
from create_bot import ROOT_ADMIN, DB_PATH
from keyboards import (
    admin_kb,
    cancel_state_callback_kb,
    choose_new_product_brand_kb,
    products_list_kb,
    confirm_deleting_kb,
)
from utils import add_new_product, check_value_identify, get_product_detail
from states import ChangeProduct, CreateUpdate, DeleteProduct

admin_router = Router()


@admin_router.callback_query(F.data.startswith("change_min_price_"))
async def get_new_min_price(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data.split("_")
    product_id = data[-1]
    await callback_query.message.answer(
        "Provide new price: ", reply_markup=await cancel_state_callback_kb()
    )
    await state.set_state(ChangeProduct.CHANGED_ELEMENT)
    await state.update_data(value_identify="min_price")
    await state.update_data(product_id=product_id)


@admin_router.callback_query(F.data == "yes")
async def remove_product(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = data.get("id")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE id = ?", (id,))
        await db.commit()
        await callback_query.message.answer("Product successfully deleted!")
        await callback_query.message.answer(
            "Products:", reply_markup=await products_list_kb()
        )
    await state.clear()


@admin_router.callback_query(F.data.startswith("delete_product_"))
async def get_delete_product(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data
    id = data.split("_")[-1]
    await state.set_state(DeleteProduct.START)
    await state.update_data(id=id)
    await callback_query.message.answer(
        "Confirm deleting", reply_markup=await confirm_deleting_kb()
    )


@admin_router.message(ChangeProduct.CHANGED_ELEMENT)
async def get_changed_value(message: Message, state: FSMContext):
    new_value = message.text
    if new_value.isdigit():
        data = await state.get_data()
        value_identify = data["value_identify"]
        result = await check_value_identify(value_identify)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f"UPDATE products SET {result} = ?", (new_value,))
            await db.commit()
            await message.answer("Product successfully updated!")
            await message.answer("Products:", reply_markup=await admin_kb())
        await state.clear()
    else:
        await message.answer("Error with value!Try again!")


@admin_router.callback_query(F.data.startswith("change_"))
async def changes(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data.split("_")
    id = data[-1]
    value_identify = data[1]
    await state.set_state(ChangeProduct.CHANGED_ELEMENT)
    await state.update_data(product_id=id)
    await state.update_data(value_identify=value_identify)
    await callback_query.message.answer(
        "Provide new value: ", reply_markup=await cancel_state_callback_kb()
    )


@admin_router.callback_query(F.data.startswith("detail_"))
async def detail_product(callback_query: CallbackQuery):
    id = callback_query.data.split("_")[-1]
    product = await get_product_detail(id)
    if product:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"Product price:{product[2]}",
            callback_data=f"change_price_{product[0]}",
        )
        builder.button(
            text=f"Min price: {product[7]}",
            callback_data=f"change_min_price_{product[0]}",
        )
        builder.button(
            text=f"Screen defects price:{product[3]}",
            callback_data=f"change_screen_{product[0]}",
        )
        builder.button(
            text=f"Back defects price:{product[4]}",
            callback_data=f"change_back_{product[0]}",
        )
        builder.button(
            text=f"Others defects price:{product[5]}",
            callback_data=f"change_others_{product[0]}",
        )
        if product[6] is not None:
            builder.button(
                text=f"Battery price: {product[6]}",
                callback_data=f"change_battery_{product[0]}",
            )
        builder.button(text="Delete🗑", callback_data=f"delete_product_{product[0]}")
        builder.button(text="Back⬅", callback_data="back_products")
        builder.adjust(1)
        await callback_query.message.answer("Product", reply_markup=builder.as_markup())


@admin_router.callback_query(F.data == "create_product")
async def create_new_proudct(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.from_user.id == ROOT_ADMIN:
        await callback_query.message.answer(
            "Provide brand: ", reply_markup=await choose_new_product_brand_kb()
        )
        await state.set_state(CreateUpdate.BRAND)


@admin_router.callback_query(F.data.startswith("new_product_brand_"))
async def get_new_product_brand(callback_query: CallbackQuery, state: FSMContext):
    callback_data = callback_query.data.split("_")
    brand = callback_data[-1]
    await callback_query.message.answer(
        "Provide model: ", reply_markup=await cancel_state_callback_kb()
    )
    await state.set_state(CreateUpdate.MODEL)
    await state.update_data(brand=brand)


@admin_router.message(CreateUpdate.BATERY_PRICE)
async def get_battery_price(message: Message, state: FSMContext):
    price = message.text
    if price.isdigit():
        await state.update_data(battery_price=price)
        await message.answer(
            "Provide product price: ", reply_markup=await cancel_state_callback_kb()
        )
        await state.set_state(CreateUpdate.PRICE)


@admin_router.message(CreateUpdate.MODEL)
async def get_model(message: Message, state: FSMContext):
    model = message.text
    data = await state.get_data()
    brand = data.get("brand")
    battery_price = data.get("battery_price")
    await state.update_data(model=model)
    if brand == "iphone" and battery_price is None:
        await message.answer(
            "Provide battery price: ", reply_markup=await cancel_state_callback_kb()
        )
        await state.set_state(CreateUpdate.BATERY_PRICE)
        return

    await message.answer(
        "Provide product price: ", reply_markup=await cancel_state_callback_kb()
    )
    await state.set_state(CreateUpdate.PRICE)


@admin_router.message(CreateUpdate.MIN_PRICE)
async def get_min_price(message: Message, state: FSMContext):
    price = message.text
    if price.isdigit():
        await state.update_data(min_price=price)
        await message.answer(
            "Screen defect price: ", reply_markup=await cancel_state_callback_kb()
        )
        await state.set_state(CreateUpdate.SCREEN_DEFECTS)
    else:
        await message.answer("Error with price!Provide new one")


@admin_router.message(CreateUpdate.PRICE)
async def get_price(message: Message, state: FSMContext):
    price = message.text
    if price.isdigit():
        await state.update_data(price=price)
        await message.answer(
            "Min price: ", reply_markup=await cancel_state_callback_kb()
        )
        await state.set_state(CreateUpdate.MIN_PRICE)
    else:
        await message.answer("Error with price!Provide new one")


@admin_router.message(CreateUpdate.SCREEN_DEFECTS)
async def get_screen_defects(message: Message, state: FSMContext):
    screen_defects = message.text
    if screen_defects.isdigit():
        await state.update_data(screen_defects=screen_defects)
        await message.answer(
            "Back defects price: ", reply_markup=await cancel_state_callback_kb()
        )
        await state.set_state(CreateUpdate.BACK_DEFECTS)
    else:
        await message.answer("Error with screen defects!Try again!")


@admin_router.message(CreateUpdate.BACK_DEFECTS)
async def get_back_defects(message: Message, state: FSMContext):
    back_defects = message.text
    if back_defects.isdigit():
        await state.update_data(back_defects=back_defects)
        await message.answer(
            "Others defects price: ", reply_markup=await cancel_state_callback_kb()
        )
        await state.set_state(CreateUpdate.OTHERS_DEFECTS)
    else:
        await message.answer("Error with back defects!Try again!")


@admin_router.message(CreateUpdate.OTHERS_DEFECTS)
async def get_others_defects(message: Message, state: FSMContext):
    others_defects = message.text
    if others_defects.isdigit():
        await state.update_data(others_defects=others_defects)
        data = await state.get_data()
        if await add_new_product(data):
            await message.answer("New product successfully added!")
            await message.answer("Products:", reply_markup=await admin_kb())
        else:
            await message.answer("Some error.Try add new product again")
        await state.clear()
    else:
        message.answer("Error with others defects.Try again!")


@admin_router.callback_query(F.data == "products")
async def products_list(callback_query: CallbackQuery):
    await callback_query.message.answer(
        "Products:", reply_markup=await products_list_kb()
    )
