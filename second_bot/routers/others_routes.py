from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from create_bot import ROOT_ADMIN
from keyboards import (
    admin_kb,
    choose_brand_kb,
    start_kb,
    products_list_kb,
)  # pyright:ignore
from states import DeleteProduct, FormFill  # pyright:ignore
from utils import (
    read_local,
)  # pyright:ignore

others_router = Router()


@others_router.callback_query(F.data == "no")
async def no(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.answer("❌")
    await callback_query.message.answer(
        "Products:", reply_markup=await products_list_kb()
    )


@others_router.callback_query(F.data == "back_menu")
async def back_menu(callback_query: CallbackQuery):
    await callback_query.message.answer("Admin panel", reply_markup=await admin_kb())


@others_router.callback_query(F.data == "back_products")
async def back_products(callback_query: CallbackQuery):
    await callback_query.message.answer(
        "Products:", reply_markup=await products_list_kb()
    )


@others_router.callback_query(F.data == "ru")
async def ru(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(FormFill.BRAND)
    await state.update_data(language="ru")
    product_model = await read_local("ru", "product_brand")
    await callback_query.message.answer(
        product_model, reply_markup=await choose_brand_kb()
    )


@others_router.callback_query(F.data == "en")
async def en(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(FormFill.BRAND)
    await state.update_data(language="en")
    product_model = await read_local("en", "product_brand")
    await callback_query.message.answer(
        product_model, reply_markup=await choose_brand_kb()
    )


@others_router.callback_query(F.data == "lv")
async def lv(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(FormFill.BRAND)
    await state.update_data(language="lv")
    product_model = await read_local("lv", "product_brand")
    await callback_query.message.answer(
        product_model, reply_markup=await choose_brand_kb()
    )


@others_router.callback_query(F.data == "cancel_state")
async def cancel_state(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.answer("❌")


@others_router.callback_query(F.data == "cancel_state_callback")
async def cancel_state_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.answer("❌")
    await callback_query.message.answer("Admin panel", reply_markup=await admin_kb())


@others_router.message(Command("start"))
async def start(message: Message):
    if message.from_user.id == ROOT_ADMIN:
        await message.answer("Hello admin!", reply_markup=await admin_kb())
    else:
        await message.answer(
            "Hi!Use command /flip for start", reply_markup=await start_kb()
        )
