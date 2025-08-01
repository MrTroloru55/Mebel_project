from aiogram import types

user_keyboard_1 = [
    [
        types.InlineKeyboardButton(text='Посмотреть мои задачи', callback_data='tasks_check'),
    ]
]
user_keyboard_1 = types.InlineKeyboardMarkup(inline_keyboard=user_keyboard_1)