from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode # Убедитесь, что этот импорт присутствует
import re

from Data_base.db_user import add_user, get_all_tasks
from Keyboards.user_keyboard import user_keyboard_1

user_router = Router()

#Реакция на кнопку старт
@user_router.message(Command('start'))
async def start(message: types.Message):
    await add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer('Добро пожаловать в бота', reply_markup=user_keyboard_1)


def escape_markdown_v2(text: str) -> str:
    """
    Экранирует специальные символы для форматирования MarkdownV2.
    """
    # Список всех специальных символов MarkdownV2, которые нужно экранировать
    # Порядок важен: экранируем обратный слэш первым!
    special_chars = r"[_*\[\]()~`>#+-=|{}.!]"
    return re.sub(special_chars, r"\\\g<0>", text)


@user_router.callback_query(F.data == 'tasks_check')
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
                f"  **Дедлайн:** {escaped_deadline}\n\n"  # Используем экранированный дедлайн
            )

        await callback_query.message.answer(response_message, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await callback_query.message.answer("У вас пока нет назначенных задач.")