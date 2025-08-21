from aiogram import Router, types, F
from aiogram.dispatcher import router
from aiogram.filters import Command
from aiogram.enums import ParseMode # Убедитесь, что этот импорт присутствует
import re
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery


from Data_base.db_user import add_user, get_all_tasks, update_task_done_status, add_blocker
from Keyboards.user_keyboard import user_keyboard_start, user_keyboard_close_task, get_confirmation_keyboard

user_router = Router()

class Block(StatesGroup):
    comment = State()

#Реакция на кнопку старт
@user_router.message(Command('start'))
async def start(message: types.Message):
    await add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer('Добро пожаловать в бота', reply_markup=user_keyboard_start)


def escape_markdown_v2(text: str) -> str:
    """
    Экранирует специальные символы для форматирования MarkdownV2.
    """
    # Список всех специальных символов MarkdownV2, которые нужно экранировать
    # Порядок важен: экранируем обратный слэш первым!
    special_chars = r"[_*\[\]()~`>#+-=|{}.!]"
    return re.sub(special_chars, r"\\\g<0>", text)

#Запрос задач пользователя
@user_router.callback_query(F.data == 'tasks_list')
async def tasks_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    tasks = await get_all_tasks(user_id)

    await callback_query.answer(text="Задачи получены!")

    if tasks:
        # Заголовок сообщения
        # Сам заголовок (Ваши задачи) может содержать Markdown, поэтому его часть тоже можно экранировать
        # или просто оставить как есть, если уверены, что там нет спецсимволов.
        response_message = f"**Ваши задачи:**\n\n"

        for task in tasks:
            task_id, short_description, description, deadline = task

            # Экранируем каждую строку, которая берется из БД и будет выводиться как обычный текст.
            # task_id обычно число, но если вывести как строку в моноширинном шрифте (`task_id`),
            # то там экранирование не нужно.
            escaped_short_description = escape_markdown_v2(short_description)
            # Если description тоже выводится, его тоже нужно экранировать
            # escaped_description = escape_markdown_v2(description)
            escaped_deadline = escape_markdown_v2(
                str(deadline))  # Дедлайн может быть объектом Date, преобразуем в строку

            response_message += (
                f"• **ID:** `{task_id}`\n"  # ID в моноширинном шрифте не требует экранирования
                f"  **Что сделать:** {escaped_short_description}\n"  # Используем экранированное краткое описание
                f"  **Дедлайн:** {escaped_deadline}\n\n" # Используем экранированный дедлайн
            )

        await callback_query.message.answer(response_message,
                                            parse_mode=ParseMode.MARKDOWN_V2,
                                            reply_markup=user_keyboard_close_task
                                            )
    else:
        await callback_query.message.answer("У вас пока нет назначенных задач.")

#Изменения статуса задачи (Кнопка "Завершить задачу")_1
@user_router.callback_query(F.data == 'task_done')
async def task_success_finish(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        tasks = await get_all_tasks(user_id)

        if not tasks:
            await callback_query.answer("У вас нет задач для завершения!", show_alert=True)
            return

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        for task in tasks:
            if len(task) >= 2:
                task_id, short_description = task[0], task[1]
                keyboard.inline_keyboard.append([
                    types.InlineKeyboardButton(
                        text=f"Завершить: {short_description[:30]}" + ("..." if len(short_description) > 30 else ""),
                        callback_data=f"complete_{task_id}"
                    )
                ])

        await callback_query.message.answer(
            "Выберите задачу для завершения:",
            reply_markup=keyboard
        )
        await callback_query.answer()
    except Exception as e:
        print(f"Ошибка в task_success_finish: {str(e)}")
        await callback_query.answer("Ошибка при загрузке задач", show_alert=True)

#Завершение задачи_шаг_2
@user_router.callback_query(F.data.startswith('complete_'))
async def select_task_handler(callback_query: types.CallbackQuery):
    try:
        task_id = int(callback_query.data.split('_')[1])
        await callback_query.message.answer(
            f"Вы уверены, что хотите завершить задачу #{task_id}?",
            reply_markup=get_confirmation_keyboard(task_id)
        )
        await callback_query.answer()
    except Exception as e:
        print(f"Ошибка при выборе задачи: {str(e)}")
        await callback_query.answer("Ошибка при выборе задачи", show_alert=True)

#Завершение задачи шаг 3 (Реакция на get_confirmation_keyboard "Подтвердить")
@user_router.callback_query(F.data.startswith('confirm_'))
async def confirm_task_completion(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        task_id = int(callback_query.data.split('_')[1])

        await update_task_done_status(True, task_id, user_id)
        # Получаем обновленный список задач
        tasks = await get_all_tasks(user_id)

        # Создаем новую клавиатуру
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        for task in tasks:
            if len(task) >= 2:
                current_id, short_description = task[0], task[1]
                keyboard.inline_keyboard.append([
                    types.InlineKeyboardButton(
                        text=f"Завершить: {short_description[:30]}" + ("..." if len(short_description) > 30 else ""),
                        callback_data=f"complete_{current_id}"
                    )
                ])

        # Удаляем сообщение с подтверждением
        await callback_query.message.delete()

        # Обновляем исходное сообщение с задачами
        if keyboard.inline_keyboard:
            await callback_query.message.answer(
                "Список задач обновлен:",
                reply_markup=keyboard
            )
        else:
            await callback_query.message.answer("🎉 Все задачи завершены!")

        await callback_query.answer(f"Задача {task_id} успешно завершена!")
    except Exception as e:
        print(f"Ошибка при подтверждении: {str(e)}")
        await callback_query.answer("Ошибка при завершении задачи", show_alert=True)

# Обработчик отмены
@user_router.callback_query(F.data == 'cancel')
async def cancel_task_completion(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await callback_query.answer("Действие отменено")

#Кнопка "Невозможно выполнить"
@user_router.callback_query(F.data == 'task_failure')
async def task_success_finish(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        tasks = await get_all_tasks(user_id)

        if not tasks:
            await callback_query.answer("У вас нет задач для завершения!", show_alert=True)
            return

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        for task in tasks:
            if len(task) >= 2:
                task_id, short_description = task[0], task[1]
                keyboard.inline_keyboard.append([
                    types.InlineKeyboardButton(
                        text=f"Блокер в задаче: {short_description[:30]}" + ("..." if len(short_description) > 30 else ""),
                        callback_data=f"blocker_{task_id}"
                    )
                ])

        await callback_query.message.answer(
            "Выберите задачу, которую невозможно выполнить:",
            reply_markup=keyboard
        )
        await callback_query.answer()
    except Exception as e:
        print(f"Ошибка в task_success_finish: {str(e)}")
        await callback_query.answer("Ошибка при загрузке задач", show_alert=True)


@user_router.callback_query(F.data.startswith('blocker_'))
async def select_task_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    try:
        task_id = int(callback_query.data.split('_')[1])

        await callback_query.answer()
    except Exception as e:
        print(f"Ошибка при выборе задачи: {str(e)}")
        await callback_query.answer("Ошибка при выборе задачи", show_alert=True)

    await state.update_data(task_id=task_id, user_id=user_id)
    await state.set_state(Block.comment)
    await callback_query.message.answer('Введите блокер')


@user_router.message(Block.comment)
async def task_failure_two(message: types.Message, state: FSMContext):
    # Получаем все данные из FSM, включая task_id и user_id
    data = await state.get_data()
    task_id = data.get('task_id')
    user_id = data.get('user_id')
    comment_text = message.text
    # Проверяем, что данные существуют
    if task_id is None or user_id is None:
        await message.answer('Произошла ошибка, данные задачи не найдены.')
        await state.clear()
        return
    # Вызываем функцию для записи данных в БД
    await add_blocker(task_id, user_id, comment_text)
    await message.answer(f'Блокер сохранен: {comment_text}')
    await state.clear()

# #Прием блокера
# @user_router.callback_query(F.data.startswith('task_failure'))
# async def task_failure_one(callback_query: types.CallbackQuery, state: FSMContext):
#     user_id = callback_query.from_user.id
#
#     # 1. Сначала выведите весь callback_data
#     print(f"Полные данные из кнопки: {callback_query.data}")
#
#     try:
#         # 2. Попробуйте вывести то, что получается после split
#         parts = callback_query.data.split('_')
#         print(f"Разбитые части данных: {parts}")
#
#         # 3. Затем получите и выведите task_id
#         task_id = int(parts[2])  # Обратите внимание на индекс!
#         print(f"Полученный task_id: {task_id}")
#
#     except (ValueError, IndexError):
#         await callback_query.message.answer('Произошла ошибка. Пожалуйста, попробуйте еще раз.')
#         return
#     # Сохраняем user_id и task_id в состоянии FSM
#     await state.update_data(task_id=task_id, user_id=user_id)
#     await state.set_state(Block.comment)
#     await callback_query.message.answer('Введите блокер')
#
#
# @user_router.message(Block.comment)
# async def task_failure_two(message: types.Message, state: FSMContext):
#     # Получаем все данные из FSM, включая task_id и user_id
#     data = await state.get_data()
#     task_id = data.get('task_id')
#     user_id = data.get('user_id')
#     comment_text = message.text
#     # Проверяем, что данные существуют
#     if task_id is None or user_id is None:
#         await message.answer('Произошла ошибка, данные задачи не найдены.')
#         await state.clear()
#         return
#     # Вызываем функцию для записи данных в БД
#     await add_blocker(task_id, user_id, comment_text)
#     await message.answer(f'Блокер сохранен: {comment_text}')
#     await state.clear()