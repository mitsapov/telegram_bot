# Telegram-бот с интеграцией языковой модели OpenAI GPT-4o Mini

## Описание проекта

Этот проект представляет собой Telegram-бота с интеграцией с языковой моделью OpenAI GPT-4o Mini через API VseGPT. Бот позволяет пользователям взаимодействовать с языковой моделью, сохраняет контекст диалога и предоставляет удобный интерфейс для управления настройками.

## Инструкции по установке и запуску

1. Клонируйте репозиторий:
   ```
   git clone <url-репозитория>
   cd bot_gpt
   ```

2. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

3. Создайте файл `.env` в корневой директории проекта и добавьте необходимые переменные окружения:
   ```
   BOT_TOKEN=ваш_токен_бота
   ```

4. Запустите бота:
   ```
   python main.py
   ```

## Примеры использования

1. Запустите бота командой `/start`
2. Установите API-ключ через `/post_api_key`
3. Начните общение с ботом
4. Используйте команду `/start` или нажмите  кнопку `Очистить контекст` для очистки контекста диалога.

## Список зависимостей

Основные зависимости проекта перечислены в файле requirements.txt:
- python==3.13.5
- aiogram==3.22.0
- python-dotenv==1.2.1

Работа с базой данных:
- sqlite3==3.51.0

Работа с API
- openai==2.8.1

## Лицензия

MIT License

Copyright (c) 2026 Telegram Bot with GPT Integration

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.