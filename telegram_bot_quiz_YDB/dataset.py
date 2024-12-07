import aiosqlite

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'

quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Как называется основной интерпретатор Python?',
        'options': ['Python', 'Cython', 'PyPy', 'CPython'],
        'correct_option': 0
    },
    {
        'question': 'Что такое PEP в контексте Python?',
        'options': ['Пакет расширений Python', 'Предложение по улучшению Python', 'Программа для редактирования Python-кода', 'Плагин для Python'],
        'correct_option': 1
    },
    {
        'question': 'Какой оператор используется для сравнения двух значений в Python?',
        'options': ['==', '<>', '<=', '>='],
        'correct_option': 0
    },
    {
        'question': 'Какая функция используется для вывода текста в консоль в Python?',
        'options': ['print()', 'show()', 'output()', 'console()'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения дробных чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 2
    },
    {
        'question': 'Что такое цикл for в Python?',
        'options': ['Оператор, который позволяет выполнять код многократно', 'Функция, которая возвращает значение', 'Условный оператор, который проверяет условие', 'Метод, который изменяет значение переменной'],
        'correct_option': 0
    },
    {
        'question': 'Что такое список в Python?',
        'options': ['Тип данных, который хранит упорядоченный набор элементов', 'Оператор, который выполняет код многократно', 'Функция, которая выводит текст в консоль', 'Объект, который представляет собой строку'],
        'correct_option': 0
    },
    {
        'question': 'Что такое словарь в Python?',
        'options': ['Тип данных, который хранит неупорядоченный набор пар ключ-значение', 'Оператор, который сравнивает два значения', 'Функция, которая принимает аргументы', 'Объект, который является экземпляром класса'],
        'correct_option': 0
    }
]

async def create_table():
    # Создаем соединение с базой данных (если она не существует, то она будет создана)
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Выполняем SQL-запрос к базе данных
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
            user_id INTEGER PRIMARY KEY,
            question_index INTEGER,
            right_answers INTEGER
        )''')
        # Сохраняем изменения
        await db.commit()

async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, right_answers) VALUES (?, ?, ?)', (user_id, index, 0))
        # Сохраняем изменения
        await db.commit()

async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def delete_previous_result(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Удаляем предыдущую запись для данного пользователя
        await db.execute('DELETE FROM quiz_state WHERE user_id = ?', (user_id, ))
        # Сохраняем изменения
        await db.commit()

async def update_right_answers(user_id, right_answers):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Обновляем количество правильных ответов
        await db.execute('UPDATE quiz_state SET right_answers = ? WHERE user_id = ?', (right_answers, user_id))
        # Сохраняем изменения
        await db.commit()

# Получение количества правильных ответов для данного пользователя
async def get_result(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT right_answers FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0