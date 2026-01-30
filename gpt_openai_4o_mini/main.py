import asyncio    # модуль для работы с асинхронным кодом
import os    # модуль для работы с переменными окружения
import logging
from dotenv import load_dotenv  # функция для загрузки переменных окружения
from aiogram import Bot, Dispatcher
from database import Database
from handlers import message_users
from handlers.command import help, post_api_key, start
from handlers.keyboard import clear_context

logging.basicConfig(level=logging.INFO)

# загрузка переменных окружения
load_dotenv()

async def main():
    
    bot = Bot(token=os.getenv('bot_token'))    #  Берется из файла .env, который содержит токен бота
    
    db = Database()
    db.create_table()
    
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(post_api_key.router)
    dp.include_router(clear_context.router)
    dp.include_router(message_users.router)
    
    
    await bot.delete_webhook(drop_pending_updates=True)   # Удаляем накопившиеся запросы к боту

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())