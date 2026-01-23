from openai import OpenAI
from database import Database

db = Database()

async def get_response(prompt: str, user_id: int) -> str:
    '''Отправляет запрос в API и возвращает ответ модели'''
    
    # получаем API-ключ VseGPT пользователя из базы данных
    api_key = (db.get_api(user_id) or "").strip()
    if not api_key:
        return "Ошибка: API-ключ отсутствует."
    
    try:
        client = OpenAI(
            api_key=api_key, 
            base_url="https://api.vsegpt.ru/v1"
        )
        
        # Получаем контекст из БД
        context = db.get_context(user_id)
        if context is None:
            context = []
        
        # добавляем новое сообщение пользователя
        context.append({"role": "user", "content": prompt})
        
        # отправляем запрос в API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # id модели из списка [моделей](https://vsegpt.ru/Docs/Models)  - можно использовать OpenAI, Anthropic и пр. меняя только этот параметр
            messages=context,
            temperature=0.7,
            max_tokens=1500, # максимальное число ВЫХОДНЫХ токенов. Для большинства моделей не должно превышать 4096
        )
        
        bot_reply = response.choices[0].message.content
        
        # добавляем ответ бота в контекст
        context.append({"role": "assistant", "content": bot_reply})
        
        # сохраняем обновленный контекст в БД
        db.update_context(user_id, context)
        
        return bot_reply
    
    except Exception as e:
        return f"Ошибка API: {str(e)}"

