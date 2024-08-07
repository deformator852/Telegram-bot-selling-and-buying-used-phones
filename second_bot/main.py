from create_bot import dp, bot
from routers import fill_form, others_routes, admin  # pyright:ignore
import asyncio
import logging
import sys


async def main():
    dp.include_router(fill_form.fill_form_router)
    dp.include_router(others_routes.others_router)
    dp.include_router(admin.admin_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
