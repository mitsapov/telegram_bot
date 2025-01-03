import aiosqlite

# Let's set the name of the database
DB_NAME = 'db'

async def create_table():
    # Creating a connection to the database (if it does not exist, it will be created)
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Executing an SQL query to the database
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
            user_id INTEGER PRIMARY KEY,
            question_index INTEGER,
            right_answers INTEGER
        )''')
        # Saving the changes
        await db.commit()

async def update_quiz_index(user_id, index):
    # Creating a connection to the database (if it does not exist, it will be created)
    async with aiosqlite.connect(DB_NAME) as db:
        # Insert a new record or replace it if the given user_id already exists
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, right_answers) VALUES (?, ?, ?)', (user_id, index, 0))
        # Saving the changes
        await db.commit()

async def get_quiz_index(user_id):
    # Connecting to the database
    async with aiosqlite.connect(DB_NAME) as db:
        # Getting an entry for a given user
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Returning the result
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def delete_previous_result(user_id):
    # Connecting to the database
    async with aiosqlite.connect(DB_NAME) as db:
        # Deleting the previous record for this user
        await db.execute('DELETE FROM quiz_state WHERE user_id = ?', (user_id, ))
        # Saving the changes
        await db.commit()

async def update_right_answers(user_id, right_answers):
    # Connecting to the database
    async with aiosqlite.connect(DB_NAME) as db:
        # Updating the number of correct answers
        await db.execute('UPDATE quiz_state SET right_answers = ? WHERE user_id = ?', (right_answers, user_id))
        # Saving the changes
        await db.commit()

# Getting the number of correct answers for a given user
async def get_result(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT right_answers FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
