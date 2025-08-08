from aiogram import types

user_keyboard_start = [
    [
        types.InlineKeyboardButton(text='Посмотреть мои задачи', callback_data='tasks_list')
    ]
]
user_keyboard_start = types.InlineKeyboardMarkup(inline_keyboard=user_keyboard_start)

user_keyboard_close_task = [
    [
        types.InlineKeyboardButton(text='Закрыть задачу', callback_data='task_done')
    ],
    [
        types.InlineKeyboardButton(text='Невозможно выполнить', callback_data='task_failure'),
    ]
]
user_keyboard_close_task = types.InlineKeyboardMarkup(inline_keyboard=user_keyboard_close_task)

def get_confirmation_keyboard(task_id: int):
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text='Подтвердить', callback_data=f'confirm_{task_id}'),
            types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        ]
    ])