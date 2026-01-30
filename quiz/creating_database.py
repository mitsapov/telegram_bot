import aiosqlite

# Setting a name for the database
DB_NAME = 'NAME_BD.db'

# Creating a table
async def create_table():
    async with aiosqlite.connect('NAME_BD.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
            user_id INTEGER PRIMARY KEY,
            question_index INTEGER,
            right_answers INTEGER,
            username TEXT UNIQUE
        )''')
        await db.commit()

# Managing the user's status
async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        # Checking if the record exists
        cursor = await db.execute('SELECT right_answers FROM quiz_state WHERE user_id = ?', (user_id,))
        result = await cursor.fetchone()
        if result is None:
            # If there is no record, create a new one with right_answers = 0
            await db.execute('INSERT INTO quiz_state (user_id, question_index, right_answers) VALUES (?, ?, ?)', (user_id, index, 0))
        else:
            # If there is an entry, we update only question_index.
            await db.execute('UPDATE quiz_state SET question_index = ? WHERE user_id = ?', (index, user_id))
        await db.commit()

# Defining the current stage of the quiz by the user
async def get_quiz_index(user_id):
    # Connecting to the database
    async with aiosqlite.connect(DB_NAME) as db:
        # Getting a record for this user
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Returning the result
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

# We reset the user's previous result
async def delete_previous_result(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        # Updating question_index and right_answers, but keeping username
        await db.execute('UPDATE quiz_state SET question_index = 0, right_answers = 0 WHERE user_id = ?', (user_id,))
        await db.commit()

# Increasing the number of correct user responses
async def update_right_answers(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE quiz_state SET right_answers = right_answers + 1 WHERE user_id = ?', (user_id,))
        await db.commit()

# We get the number of correct user responses
async def get_result(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT right_answers FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

# We will get the top 5 participants in terms of the number of correct answers
async def get_top_participants():
    async with aiosqlite.connect(DB_NAME) as db:
        # We get the top 5 participants with names
        cursor = await db.execute('SELECT username, right_answers FROM quiz_state ORDER BY right_answers DESC LIMIT 5')
        participant_list = []
        for row in await cursor.fetchall():
            username, right_answers = row
            participant_list.append(f"{username}: {right_answers} correct answers")
        
        # If the list is empty, we return a message about missing data.
        if not participant_list:
            return "The participant rating is empty. No one has passed the quiz yet."
        
        # Returning the formatted list
        return "Top 5 participants:\n" + "\n".join(participant_list)
