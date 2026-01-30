from aiogram import Router
from database import Database
from handlers.keyboard import KeyboardService
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

db = Database()

ks = KeyboardService(db)

@router.message(CommandStart()) 
async def cmd_start(message: Message) -> None:
    '''Обработчик команды /start
    Добавляем пользователя в БД
    Приветствуем пользователя'''
    
    # получаем id пользователя
    user_id = message.from_user.id
    
    # получаем имя пользователя
    user_name = message.from_user.first_name
    
    if not db.user_exists(user_id):
        db.add_user(user_id, user_name)
        welcome_text = (
            f"Добро пожаловать {user_name}!\n"
            "Список доступных команд\n"
            "/start - запуск бота и очистка истории чата с AI\n"
            "/help - список команд\n"
            "/post_api_key - ввод API ключа"
        )
    else:
        welcome_text = (
            f"История чата очищенна, можно начать новый чат!\n"
            "Список доступных команд:\n"
            "/start - запуск бота и очистка истории чата с ИИ\n"
            "/help - список команд\n"
            "/post_api_key - ввод API ключа"
        )
    
    # очищаем контекст пользователя
    db.update_context(user_id, [])
    
    # отправляем приветсвие
    await message.answer(welcome_text, reply_markup=ks.get_keyboard(user_id))