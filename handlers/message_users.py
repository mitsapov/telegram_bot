from aiogram import Router
from aiogram.types import Message
from database import Database
from api import get_response
from handlers.keyboard import KeyboardService

db = Database()
ks = KeyboardService(db)
router = Router()

@router.message()
async def handle_message(message: Message):
    '''Обработчик сообщений пользователя'''
    user_id = message.from_user.id
    user_message = message.text
    
    context = db.get_context(user_id)
    
    # Добавляем новое сообщение в контекст БД
    context.append(user_message)
    
    db.update_context(user_id, context)
    
    response = await get_response(context, user_id)
    
    # Отправляем ответ пользователя
    await message.answer(response, reply_markup=ks.get_keyboard(user_id))