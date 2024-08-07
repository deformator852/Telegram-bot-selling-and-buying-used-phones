from aiogram.filters import Filter
from aiogram.types import Message
from create_bot import ROOT_ADMIN


class IsAdminFilter(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ROOT_ADMIN
