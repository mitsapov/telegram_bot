
from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message

router = Router()

@router.message(Command("help"))
@router.message(F.text == "Команды")
async def cmd_help(message: Message):
    help_text = "Список доступных команд:\n/start - запуск бота и очистка истории чата\n/help - список команд\n/post_api_key - ввод API ключа"
    await message.answer(help_text)