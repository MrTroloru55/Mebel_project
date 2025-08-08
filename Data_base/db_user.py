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
            WHERE ut.user_id = ?
        """, (user_id,))
        tasks = await cursor.fetchall()
        if tasks:
            print(f"Задачи для пользователя {user_id}:")
            for task in tasks:
                print(f"  ID: {task[0]}, Краткое описание: {task[1]}, Дедлайн: {task[3]}")
        else:
            print(f"Для пользователя {user_id} задачи не найдены.")
        return tasks

async def check_tables_exist():
    async with aiosqlite.connect(DB_PATH) as connect:
        cursor = await connect.cursor()
        await cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = await cursor.fetchall()
        print("Существующие таблицы:", tables)

async def complete_task(user_id: int, task_id: int):
    async with aiosqlite.connect(DB_PATH) as connect:
        cursor = await connect.cursor()
        # Удаляем связь пользователя с задачей
        await cursor.execute(
            "DELETE FROM user_tasks WHERE user_id = ? AND task_id = ?",
            (user_id, task_id)
        )
        # Если задача больше никому не назначена, можно удалить и саму задачу
        await cursor.execute(
            "DELETE FROM tasks WHERE task_id NOT IN (SELECT task_id FROM user_tasks)"
        )
        await connect.commit()