import asyncio
import logging
import asyncpg

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router, set_db_pool

bot = Bot(token=TOKEN)
dp = Dispatcher()

db_pool = None

async def create_db_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        user='postgres',
        password='Galifloh1488',
        database='postgres',
        host='localhost'
    )
    set_db_pool(db_pool)

async def main():
    await create_db_pool()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
