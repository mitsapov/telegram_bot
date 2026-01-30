from database import Database
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

class KeyboardService:
    def __init__(self, db: Database):
        self.db = db
    
    def should_show_clear_button(self, user_id: int):
        '''Проверяем наличие API-ключа и не пуст ли контекст'''
        return bool(self.db.get_api(user_id)) and len(self.db.get_context(user_id)) > 0
    
    def get_keyboard(self, user_id: int) -> ReplyKeyboardMarkup:
        '''Формируем клавиатуру с условной кнопкой'''
        buttons = []
        if self.should_show_clear_button(user_id):
            buttons.append([KeyboardButton(text="Очистить контекст")])
        buttons.extend([
            [KeyboardButton(text="Команды")],
            [KeyboardButton(text="Ввести/изменить API-ключ")]
        ])
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)