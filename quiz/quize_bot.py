import asyncio
import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# Output the logs
logging.basicConfig(level=logging.INFO)

API_TOKEN = 'BOT_TOKEN'

# Creating a bot object
bot = Bot(token=API_TOKEN)

dp = Dispatcher()

# Handler of the /start command
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Start the game"))
    builder.add(types.KeyboardButton(text="Rating of participants"))

    await message.answer("Welcome to the quiz!", reply_markup=builder.as_markup(resize_keyboard=True))

# The handler of the command /quiz
class QuizStates(StatesGroup):
    waiting_for_name = State()  # User Name Waiting status

# Handler for the "Start Game" button
@dp.message(F.text == "Start the game")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # We check if there is a participant in the table.
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT username FROM quiz_state WHERE user_id = ?', (user_id,))
        result = await cursor.fetchone()

    if result is None:
        # If the participant is not in the table, we request the name
        await message.answer("Please enter your name:")
        await state.set_state(QuizStates.waiting_for_name)  # Setting the name waiting state
    else:
        # If the participant is already in the table, we start the quiz.
        await delete_previous_result(user_id)
        await message.answer("Let's start the quiz!")
        await new_quiz(message)

# Handler for getting the user name
@dp.message(QuizStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.text
    try:
        # Adding the name to the table
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('INSERT INTO quiz_state (user_id, question_index, right_answers, username) VALUES (?, ?, ?, ?)',
                            (user_id, 0, 0, username))
            await db.commit()
        # Completing the name waiting state
        await state.clear()
        # Starting the quiz
        await message.answer(f"Thank you, {username}! Let's start the quiz.")
        await new_quiz(message)
    except aiosqlite.IntegrityError:
        # If the name already exists, please enter another one.
        await message.answer("That name is already taken. Please enter a different name:")

# Handler for the Participant Rating command
@dp.message(Command("top_participants"))
async def cmd_top_participants(message: types.Message):
    participant_list = await get_top_participants()
    await message.answer(f"Top 5 participants:\n{participant_list}")

# Handler for displaying the list of participants
@dp.message(F.text == "Rating of participants")
async def cmd_top_participants(message: types.Message):
    # We get the top 5 participants
    participant_list = await get_top_participants()
    # Sending the result to the user
    await message.answer(participant_list)

# Creating a keyboard with answer options
def generate_options_keyboard(answer_options, right_answer):
    # Creating an Inline keyboard
    builder = InlineKeyboardBuilder()
    # In the loop, we create 4 Inline buttons, or rather Callback buttons
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            # The text on the buttons corresponds to the answer options
            text=option,
            # Assigning data for a callback request
            # If the answer is correct, a callback request with the 'right_answer' data will be generated
            # If the response is incorrect, a callback request with the 'wrong_answer' data will be generated
            callback_data="right_answer" if option == right_answer else "wrong_answer"
        ))
    # We output one button per column
    builder.adjust(1)
    return builder.as_markup()

# Uploading and sending the question to the user
async def get_question(message, user_id):
    # Getting the current question
    current_question_index = await get_quiz_index(user_id)
    print(current_question_index)
    # We get the index of the correct answer
    correct_index = quiz_data[current_question_index]['correct_option']
    # We get all possible answers
    opts = quiz_data[current_question_index]['options']
    # Creating a keyboard with multiple answers
    kb = generate_options_keyboard(opts, opts[correct_index])
    # Sending a question to the user
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

# Launching a new quiz
async def new_quiz(message):
    # Getting the user ID
    user_id = message.from_user.id
    # Setting the index of the current issue
    current_question_index = 0
    # Updating the issue index
    await update_quiz_index(user_id, current_question_index)
    # Uploading and submitting the first question
    await get_question(message, user_id)

# A function for displaying the number of correct answers after completing the quiz
async def display_results(message, user_id):
    # Getting the current number of correct answers
    correct_answers_count = await get_result(user_id)
    # Displaying the results to the user
    await message.answer(f"You answered the {correct_answers_count} questions correctly.")

# Handler for the correct response
@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    await callback.message.answer("Right!")
    await update_right_answers(callback.from_user.id)  # Increasing the number of correct answers
    current_question_index = await get_quiz_index(callback.from_user.id)
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await display_results(callback.message, callback.from_user.id)

# Incorrect response handler
@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    # Getting the current question from the user's status dictionary
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Wrong. Right answer: {quiz_data[current_question_index]['options'][correct_option]}")
    # The number of correct answers does not change
    correct_answers_count = await get_result(callback.from_user.id)
    # Updating the current issue number in the database
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await display_results(callback.message, callback.from_user.id)

# Launching the bot
async def main():

    # Starting the creation of the database table
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())