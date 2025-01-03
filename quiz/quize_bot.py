import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# We turn on logging so as not to miss important messages
logging.basicConfig(level=logging.INFO)

API_TOKEN = 'API_TOKEN_BOT'

# Bot Object
bot = Bot(token=API_TOKEN)

dp = Dispatcher()

# Handler for the team /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Creating a keyboard collector of the type Reply
    builder = ReplyKeyboardBuilder()
    # Adding one button to the collector
    builder.add(types.KeyboardButton(text="Start the game"))
    # Attaching the buttons to the message
    await message.answer("Welcome to the quiz!", reply_markup=builder.as_markup(resize_keyboard=True))

# Handler for commands /quiz
@dp.message(F.text=="Start the game")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Sending a new message without buttons
    await message.answer(f"Let's start the quiz!")
    # Launching a new quiz
    await new_quiz(message)

def generate_options_keyboard(answer_options, right_answer):
    # Creating a keyboard collector of the type Inline
    builder = InlineKeyboardBuilder()

    # In the loop, we create 4 Inline buttons, or rather Callback buttons
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            # The text on the buttons corresponds to the answer options
            text=option,
            # Assigning the data for the callback request
            # If the answer is correct, a callback request with data will be generated 'right_answer'
            # If the answer is incorrect, a callback request with data will be generated 'wrong_answer'
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    # We output one button per column
    builder.adjust(1)
    return builder.as_markup()

async def get_question(message, user_id):

    # We request the current index for the question from the database
    current_question_index = await get_quiz_index(user_id)
    # We get the index of the correct answer for the current question
    correct_index = quiz_data[current_question_index]['correct_option']
    # We get a list of possible answers for the current question
    opts = quiz_data[current_question_index]['options']

    # Button generation function for the current quiz question
    # As arguments, we pass the answer options and the value of the correct answer (not the index!)
    kb = generate_options_keyboard(opts, opts[correct_index])
    # We send a message with a question to the chat, attach the generated buttons
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    # we get the ID of the user who sent the message
    user_id = message.from_user.id
    # reset the value of the current index of the quiz question to 0
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)

    # requesting a new question for the quiz
    await get_question(message, user_id)

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    # Editing the current message in order to remove the buttons (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Getting the current question for this user
    current_question_index = await get_quiz_index(callback.from_user.id)

    # We send a message to the chat that the answer is correct
    await callback.message.answer("Right!")

    # Updating the number of the current question in the database
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    # Checking if the end of the quiz has been reached
    if current_question_index < len(quiz_data):
        # Next question
        await get_question(callback.message, callback.from_user.id)
    else:
        # Notification of the end of the quiz
        await callback.message.answer("That was the last question. The quiz is completed!")

@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    # editing the current message in order to remove the buttons (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Getting the current question for this user
    current_question_index = await get_quiz_index(callback.from_user.id)

    correct_option = quiz_data[current_question_index]['correct_option']

    # We send an error message to the chat with the correct answer
    await callback.message.answer(f"Wrong. Right answer: {quiz_data[current_question_index]['options'][correct_option]}")

    # Updating the number of the current question in the database
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    # Checking if the end of the quiz has been reached
    if current_question_index < len(quiz_data):
        # Next question
        await get_question(callback.message, callback.from_user.id)
    else:
        # Notification of the end of the quiz
        await callback.message.answer("That was the last question. The quiz is completed!")

#Starting the process
async def main():

    # Starting the creation of the database table
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
