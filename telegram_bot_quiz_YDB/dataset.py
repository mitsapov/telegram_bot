import aiosqlite
#service.py
from  database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from database import quiz_data

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

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()



async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]


async def update_quiz_index(user_id, question_index):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `question_index`)
        VALUES ($user_id, $question_index);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
    )