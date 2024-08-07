from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import os

TOKEN = ""
ROOT_ADMIN = 0
DB_PATH = os.path.expanduser("~/bot_database/database.db")
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()



