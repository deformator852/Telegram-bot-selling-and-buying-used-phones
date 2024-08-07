from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from keyboards import (
    cancel_state_kb,
    choose_language,
    choose_memory_kb,
    choose_product_kb,
    yes_no_kb,
)  # pyright:ignore
from create_bot import ROOT_ADMIN, bot
from utils import read_local, count_product_price
from states import FormFill

fill_form_router = Router()


@fill_form_router.callback_query(F.data.startswith("choose_defect_"))
async def get_choose(callback_query: CallbackQuery, state: FSMContext):
    state_value = await state.get_state()
    state_data = await state.get_data()
    callback_data = callback_query.data.split("_")
    language = state_data.get("language")
    defect = int(callback_data[-1])
    if "MEMORY" in state_value:
        if "iphone" in state_data.get("brand"):
            await state.set_state(FormFill.BATERY)
            answer = await read_local(language, "iphone_batery")
            await callback_query.message.answer(answer, reply_markup=await yes_no_kb(language))
        else:
            answer = await read_local(language,"screen_defects")
            await callback_query.message.answer(answer,reply_markup=await yes_no_kb(language))
            await state.set_state(FormFill.SCREEN_DEFECTS)
        await state.update_data(memory=callback_data[-1])
        await callback_query.message.delete()
    elif "BATERY" in state_value:
        answer = await read_local(language, "screen_defects")
        if defect == 1:
          await state.update_data(battery=True)
        else:
            await state.update_data(battery=False)
        await callback_query.message.answer(answer, reply_markup=await yes_no_kb(language))
        await state.set_state(FormFill.SCREEN_DEFECTS)
        await callback_query.message.delete()
    elif "SCREEN_DEFECTS" in state_value:
        answer = await read_local(language, "back_problems")
        await callback_query.message.answer(answer, reply_markup=await yes_no_kb(language))
        await state.set_state(FormFill.BACK_PROBLEMS)
        if defect == 1:
            await state.update_data(screen_defects=True)
        else:
            await state.update_data(screen_defects=False)
        await callback_query.message.delete()
    elif "BACK_PROBLEMS" in state_value:
        answer = await read_local(language, "others_defects")
        await callback_query.message.answer(answer, reply_markup=await yes_no_kb(language))
        await state.set_state(FormFill.OTHERS_DEFECTS)
        if defect == 1:
            await state.update_data(back_problems=True)
        else:
            await state.update_data(back_problems=False)
        await callback_query.message.delete()
    elif "OTHERS_DEFECTS" in state_value:
        if defect == 1:
            await state.update_data(others_defects=True)
        else:
            await state.update_data(others_defects=False)
        product_model = state_data.get("product_model")
        calculated_price, initial_price = await count_product_price(state_data)
        answer_first = (
            await read_local(language, "price_answer") + str(calculated_price) + "€"
        )
        answer_second = await read_local(language, "price_answer2")
        await callback_query.message.answer(answer_first)
        await callback_query.message.answer(
            answer_second + f"<a href='tg://user?id={ROOT_ADMIN}'>@Flip</a>",
            parse_mode="HTML",
        )
        defects_answer = ""
        state_data = await state.get_data()
        if state_data.get("screen_defects"):
            defects_answer += "Screen defects:✅\n"
        else:
            defects_answer += "Screen defects:❌\n"
        if state_data.get("back_problems"):
            defects_answer += "Back defects:✅\n"
        else:
            defects_answer += "Back defects:❌\n"
        if state_data.get("others_defects"):
            defects_answer += "Others defects:✅\n"
        else:
            defects_answer += "Others defects:❌\n"
        battery = state_data.get("battery")
        if battery is not None:
            if battery:
              defects_answer += "Battery health:✅\n"
            else:
                defects_answer += "Battery health:❌"
        await bot.send_message(
            ROOT_ADMIN,
            f"""New product from user:<a href='tg://user?id={callback_query.from_user.id}'>{callback_query.from_user.full_name}</a>
Product - {product_model}
Initial price - {initial_price}
Calculated price - {calculated_price}
Memory - {state_data.get("memory")}GB
{defects_answer}
""",
            parse_mode="HTML",
        )
        await state.clear()
        await callback_query.message.delete()


@fill_form_router.callback_query(F.data.startswith("choose_brand_"))
async def get_brand(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data.split("_")
    state_data = await state.get_data()
    brand = data[-1].lower()
    await state.update_data(brand=brand)
    language = state_data.get("language")
    answer = await read_local(language, "product_model")
    await callback_query.message.answer(
        answer, reply_markup=await choose_product_kb(brand)
    )
    await callback_query.message.delete()


@fill_form_router.callback_query(F.data.startswith("choose_product_"))
async def get_product(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_data = callback_query.data.split("_")
    product_model = state_data[-1]
    language = data.get("language")
    answer = await read_local(language, "memory")
    await callback_query.message.delete()
    await callback_query.message.answer(answer, reply_markup=await choose_memory_kb())
    await state.update_data(product_model=product_model)
    await state.set_state(FormFill.MEMORY)


@fill_form_router.message(Command("flip"))
async def form(message: Message):
    await message.answer(
        "Before start,choose your language: ", reply_markup=await choose_language()
    )
