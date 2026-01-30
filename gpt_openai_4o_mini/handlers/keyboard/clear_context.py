from aiogram import Router
from database import Database
from handlers.keyboard import KeyboardService
from aiogram.types import Message

router = Router()
db = Database()
ks = KeyboardService(db)

@router.message(lambda m: m.text == "Очистить контекст")
async def clr_context(message: Message):
    '''Обработчик кнопки "Очистить контекст"'''
    user_id = message.from_user.id
    db.update_context(user_id, [])
    await message.answer("Контекст очищен. Можно начинать новый чат.", reply_markup=ks.get_keyboard(user_id))