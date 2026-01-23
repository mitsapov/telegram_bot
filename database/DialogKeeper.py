import sqlite3 as sql
import logging
import json

class Database:
    
    def __init__(self, db_name: str = 'database/DialogKeeper.db'):
        self.db_name = db_name
    
    def _query(self, query: str, params: tuple = (), commit: bool=False):
        '''Вспомогательный метод для выполнения SQL-запросов'''
        with sql.connect(self.db_name) as conn:
            conn.row_factory = sql.Row    # Включаем поиск по именам, чтобы результат возвращался как словарь, а не кортеж по умолчанию
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
                return None
            else:
                return cursor.fetchone()    # Для запросов SELECT
    
    def create_table(self):
        '''Создаем таблицу Users, если она еще не созданна'''
        self._query('''
                    CREATE TABLE IF NOT EXISTS Users (
                    user_id INTEGER PRIMARY KEY, --- id пользователя
                    username TEXT NOT NULL,      --- имя пользователя
                    api_key TEXT,                --- ключ OpenAI
                    context TEXT DEFAULT '[]'    --- JSON-массив сообщений
                    )''',
                    commit=True
                    )
    
    def add_user(self, user_id: int, user_name, api_key=None, context: list = []):
        '''Добавляем нового пользователя'''  
        context_json = json.dumps(context, ensure_ascii=False, indent=None)
        self._query('INSERT INTO Users (user_id, username, api_key, context) VALUES (?, ?, ?, ?)',
                    (user_id, user_name, api_key, context_json),
                    commit=True
                    )
        logging.info(f"Пользователь {user_name} с {user_id} добавлен в БД")
    
    def update_context(self, user_id: int, context: list):
        '''Обновляем контекс диалога
        Если элемент из списка - строки, конвертируем их в объекты role/content 
        '''
        # 1. Проверяем и преобразуем элементы списка
        processed_messages = []
        for msg in context:
            
            if isinstance(msg, dict):
                # Уже объект: проверяем наличие нужных полей
                if "role" in msg and "content" in msg:
                    processed_messages.append(msg)
                else:
                    # Неполный объект - пропускаем или отправляем исключение
                    raise logging.error(f"Некорректный объект в контексте: {msg}")
            
            elif isinstance(msg, str):
                # Строка - конвертируем в объект (предполагаем, что это сообщение пользователя)
                processed_messages.append({
                    "role": "user",
                    "content": msg
                })
            
            else:
                raise logging.error(f"Недопустимый тип элемента: {type(msg)}")
        
        # 2. Конвертируем в JSON
        context_json = json.dumps(processed_messages, ensure_ascii=False)
        
        # 3. Сораняем в БД
        self._query('UPDATE Users SET context = ? WHERE user_id = ?', 
                    (context_json, user_id),
                    commit=True
                    )
        logging.info(f'Контекст диалога успешно обновлен для пользователя {user_id}')
    
    
    def update_api_key(self, api_key, user_id: int):
        '''Обновляем ключ Open_AI'''
        self._query('UPDATE Users SET api_key = ? WHERE user_id = ?', 
                            (api_key, user_id),
                            commit=True
                            )
        logging.info(f'API-ключ успешно обновлен для пользователя {user_id}')

    
    def get_context(self, user_id: int):
        '''Получаем контекст сообщений пользователя'''
        
        result = self._query('SELECT context FROM Users WHERE user_id = ?',
                    (user_id,),    # Метод execute ожидает кортеж(несколько элементов) для корректной работы user_id ставим запятую после него или заключаем в []
                    commit=False
                    )
        
        if result and result[0]:    # Если контекст есть преобразуем
            return json.loads(result[0])
        return []    # Если нет пустой контекст
    
    def get_api(self, user_id: int):
        '''Получаем api-ключ пользователя'''
        result = self._query('SELECT api_key FROM Users WHERE user_id = ?',
                    [user_id],
                    commit=False
                    )
        return result['api_key'] if result else None
    
    def user_exists(self, user_id: int):
        '''Проверяем наличие user_id в БД'''
        result = self._query('SELECT user_id FROM Users WHERE user_id = ?',
                    (user_id,),
                    commit=False
                    ) 
        # Проверяем: если результат НЕ равен None, значит пользователь найден
        return result is not None