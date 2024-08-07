from create_bot import dp, bot, DB_PATH
from routers import (
    new_advertisement,
    others_routes,
    modify_advertisement,
    delete_advertisement,
    profile_advertisement,
    groups,
)  # pyright:ignore
import asyncio
import logging
import sys
import aiosqlite


async def main():
    dp.include_router(new_advertisement.new_adv_router)
    dp.include_router(others_routes.others_router)
    dp.include_router(modify_advertisement.modify_adv_router)
    dp.include_router(delete_advertisement.delete_adv_router)
    dp.include_router(profile_advertisement.profile_router)
    dp.include_router(groups.groups_router)
    await dp.start_polling(bot)


async def create_tables():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS advertisements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                task_name TEXT NOT NULL UNIQUE,
                image TEXT NOT NULL,
                groups TEXT NOT NULL,
                day_range TEXT NOT NULL,
                night_range TEXT NOT NULL,
                status BOOLEAN NOT NULL,
                last_sent TEXT
            )
        """
        )
        await db.execute(
            """
        CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_range TEXT NOT NULL,
        group_link NEXT NOT NULL
        ) 
        """
        )
        await db.execute("""
        CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT NOT NULL UNIQUE,
        price INTEGER NOT NULL,
        screen_defects INTEGER NOT NULL,
        back_defects INTEGER NOT NULL,
        others_defects INTEGER NOT NULL,
        battery_price INTEGER,
        min_price INTEGER NOT NULL
        )
        """)
        await db.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(create_tables())
    asyncio.run(main())
