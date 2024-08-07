from create_bot import DB_PATH, ROOT_ADMIN, bot
import aiofiles
import json
import os
import aiosqlite


async def memory_calculate(memory, price) -> int:
    if memory == "128":
        return price + 10
    elif memory == "256":
        return price + 20
    elif memory == "512":
        return price + 30
    elif memory == "1000":
        return price + 35
    else:
        return price


async def finish_form(callback, data, language, product_model):
    calculated_price, initial_price = await count_product_price(data)
    answer_first = await read_local(language, "price_answer") + str(calculated_price)
    answer_second = await read_local(language, "price_answer2")
    await callback.message.answer(answer_first)
    await callback.message.answer(
        answer_second + f"<a href='tg://user?id={ROOT_ADMIN}'>seller</a>",
        parse_mode="HTML",
    )
    await bot.send_message(
        ROOT_ADMIN,
        f"""New product from user:<a href='tg://user?id={callback.from_user.id}'>{callback.from_user.full_name}</a>
Product - {product_model}
Initial price - {initial_price}
Calculated price - {calculated_price}
""",
        parse_mode="HTML",
    )


async def count_product_price(data) -> tuple:
    product_model = data.get("product_model")
    screen_defects = data.get("screen_defects")
    back_problems = data.get("back_problems")
    others_defects = data.get("others_defects")
    memory = data.get("memory")
    battery = data.get("battery")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            f"SELECT * FROM products WHERE model = ?", (product_model,)
        ) as cursor:
            result = await cursor.fetchone()
            screen_price = int(result[3])
            back_price = int(result[4])
            others_price = int(result[5])
            product_price = int(result[2])
            battery_price = result[6]
            min_price = int(result[7])
            if screen_defects:
                product_price = product_price - screen_price
            if back_problems:
                product_price = product_price - back_price
            if others_defects:
                product_price = product_price - others_price
            if battery is False:
                if battery_price is not None:
                    product_price = product_price - int(battery_price)
            product_price = await memory_calculate(memory, product_price)
            if product_price < min_price:
                product_price = min_price
            return (product_price, result[2])


async def check_value_identify(value):
    if value == "price":
        return "price"
    elif value == "screen":
        return "screen_defects"
    elif value == "back":
        return "back_defects"
    elif value == "others":
        return "others_defects"
    elif value == "battery":
        return "battery_price"
    elif value == "min_price":
        return "min_price"


async def get_product_detail(id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(f"SELECT * FROM products WHERE id = {id}") as cursor:
            result = await cursor.fetchone()
            return result


async def add_new_product(data):
    model = data.get("model")
    brand = data.get("brand")
    memory = data.get("memory")
    price = int(data.get("price"))
    price = await memory_calculate(memory, price)
    battery_price = data.get("battery_price")
    screen_defects = data.get("screen_defects")
    back_defects = data.get("back_defects")
    others_defects = data.get("others_defects")
    min_price = data.get("min_price")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            if brand == "iphone":
                await db.execute(
                    "INSERT INTO products (model,price,screen_defects,back_defects,others_defects,battery_price,min_price) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (
                        model,
                        price,
                        screen_defects,
                        back_defects,
                        others_defects,
                        battery_price,
                        min_price,
                    ),
                )
                await db.commit()
                return True
            else:
                await db.execute(
                    "INSERT INTO products (model,price,screen_defects,back_defects,others_defects,min_price) VALUES(?, ?, ?, ?, ?, ?)",
                    (
                        model,
                        price,
                        screen_defects,
                        back_defects,
                        others_defects,
                        min_price,
                    ),
                )
            await db.commit()
            return True
    except Exception as e:
        print(e)
        return False


async def get_format_products_list():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT model FROM products") as cursor:
            result = await cursor.fetchall()
            answer = ""
            for product in result:
                answer += product[0] + "\n"
            return answer


async def get_products_list():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT model FROM products") as cursor:
            result = await cursor.fetchall()
            return result


async def check_defects(answer):
    if answer.lower() in ["jā", "yes", "да"]:
        return 1
    elif answer.lower() in ["nē", "no", "нет"]:
        return 0
    else:
        return False


async def read_local(language, key):
    localization_path = os.path.join("localization", language + ".json")
    async with aiofiles.open(localization_path, "r") as file:
        content = await file.read()
        data = json.loads(content)
        return data[key]
