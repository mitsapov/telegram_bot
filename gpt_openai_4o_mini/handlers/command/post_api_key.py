from aiogram import Router, F
from database import Database
from handlers.keyboard import KeyboardService
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

db = Database()

ks = KeyboardService(db)

class ApiKeyStates(StatesGroup):
    waiting_for_key = State()

@router.message(Command("post_api_key"))
@router.message(F.text == "Ввести/изменить API-ключ")
async def cmd_get_api_key(message: Message, state: FSMContext):
    '''Обработчик команды /post_api_key
        Ввод/Замена ключа от OpenAI'''
    await message.answer("Введите API-ключ")    
    await state.set_state(ApiKeyStates.waiting_for_key)

@router.message(ApiKeyStates.waiting_for_key, F.text)
async def process_api_key(message: Message, state: FSMContext):
    '''Обрабатываем введеный API-ключ'''
    user_id = message.from_user.id
    api_key = message.text.strip()    # берем текст сообщения
    db.update_api_key(api_key, user_id)
    await message.delete()    # Удаляем сообщение пользователя с ключом
    await message.answer("API-ключ успешно сохранен!", reply_markup=ks.get_keyboard(user_id))
    await state.clear()    # Очищаем состояние