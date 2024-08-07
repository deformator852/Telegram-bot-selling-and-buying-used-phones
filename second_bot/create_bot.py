from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import os

TOKEN = ""
ROOT_ADMIN = 0
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
DB_PATH = os.path.expanduser("~/bot_database/database.db")
dp = Dispatcher()
