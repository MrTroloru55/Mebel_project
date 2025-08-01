import asyncio

from aiogram import Bot, Dispatcher
# Импортируем роутеры
from Handlers.user_handlers import user_router

# Импортируем конфигурацию
from config import BOT_TOKEN

# Инициализируем Бот и Диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher() # Возможно, вам захочется добавить сюда хранилище для FSM, например, Dispatcher(storage=MemoryStorage())


async def main():
    # Сначала включаем роутеры
    dp.include_router(user_router)
    # Затем начинаем процесс опроса
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Запускаем основную асинхронную функцию
    asyncio.run(main())