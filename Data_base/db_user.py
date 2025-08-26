#from cgitb import text

import aiosqlite

from config import DB_PATH

#Функция проверки нового пользователя на уникальность и добавления его в БД
async def add_user(user_id, full_name, username) -> str:
    async with aiosqlite.connect(DB_PATH) as connect:
        cursor = await connect.cursor()
        check_user = await cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        check_user = await check_user.fetchone()
        if check_user is None:
            await cursor.execute(
                'INSERT INTO users (user_id, full_name, username) VALUES (?, ?, ?)', (user_id, full_name, username)
            )
            await connect.commit()

#Функция вывода всех задач пользователя
async def get_all_tasks(user_id: int):  # Добавляем user_id как аргумент
    async with aiosqlite.connect(DB_PATH) as connect:
        cursor = await connect.cursor()
        #Получить задачи, назначенные этому пользователю
        await cursor.execute("""
            SELECT
                t.task_id,
                t.short_description,
                t.description,
                t.deadline
            FROM tasks t
            JOIN user_tasks ut ON t.task_id = ut.task_id
            WHERE ut.user_id = ? and ut.done is not 1 and t.is_blocker is not 1
        """, (user_id,))
        tasks = await cursor.fetchall()
        if tasks:
            print(f"Задачи для пользователя {user_id}:")
            for task in tasks:
                print(f"  ID: {task[0]}, Краткое описание: {task[1]}, Дедлайн: {task[3]}")
        else:
            print(f"Для пользователя {user_id} задачи не найдены.")
        return tasks

#Флаг закрытия задачи
async def update_task_done_status(done: bool, task_id: int, user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as connect:
        cursor = await connect.cursor()

        #Переводим задачу у пользователя в статус выполнено
        await cursor.execute("""
        update user_tasks 
        set done = ? 
        where task_id = ? and user_id = ?""", (done, task_id, user_id)) #Вот тут вопрос, done или 1
        #Проверяем, выполнена ли задача у всех пользователей
        await connect.commit()

        # Шаг 2: Проверяем, остались ли другие пользователи, у которых задача не завершена
        await cursor.execute("""
        SELECT COUNT(done) 
        FROM user_tasks 
        WHERE task_id = ? AND done IS NOT TRUE AND user_id != ?
        """, (task_id, user_id))

        count = (await cursor.fetchone())[0]

        # Если count > 0, значит, есть ещё незавершенные задачи, и мы выходим
        if count > 0:
            return

        # Если count == 0, значит, все пользователи завершили задачу и можно переводить её в статус проверки.
        await cursor.execute("""
        UPDATE tasks
        SET completed = ? 
        WHERE task_id = ? 
        """, (1, task_id))
        await connect.commit()


#Функция добавления комментария блока и замены флага в задаче
async def add_blocker(task_id: int, user_id: int, comment_text: str) -> None:
    async with aiosqlite.connect(DB_PATH) as connect:
        cursor = await connect.cursor()

        # 1. Запись комментария
        await cursor.execute(
            'INSERT INTO task_comments (task_id, user_id, comment_text) VALUES (?, ?, ?)',
            (task_id, user_id, comment_text)  # <-- Вот так правильно передавать параметры
        )
        await connect.commit()

        # 2. Обновление статуса задачи
        await cursor.execute("""
        UPDATE tasks
        SET is_blocker = ? 
        WHERE task_id = ? 
        """, (1, task_id))
        await connect.commit()