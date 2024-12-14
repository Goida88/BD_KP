import asyncio
import asyncpg

async def create_table():
    conn = await asyncpg.connect(
        database="postgres",
        user="postgres",
        password="Galifloh1488",
        host="localhost",
        port=5432
    )
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            address TEXT NOT NULL,
            review TEXT NOT NULL,
            rating REAL DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    print("Таблица создана (если её не было ранее).")
    await conn.close()

async def alter_table():
    conn = await asyncpg.connect(
        database="postgres",
        user="postgres",
        password="Galifloh1488",
        host="localhost",
        port=5432
    )
    await conn.execute('''
        ALTER TABLE reviews
        DROP COLUMN IF EXISTS address;
    ''')
    await conn.execute('''
        ALTER TABLE reviews
        ADD COLUMN IF NOT EXISTS city TEXT,
        ADD COLUMN IF NOT EXISTS street TEXT,
        ADD COLUMN IF NOT EXISTS house TEXT;
    ''')
    print("Таблица обновлена. Поля city, street и house добавлены.")
    await conn.close()

asyncio.run(create_table())
asyncio.run(alter_table())


async def create_moderation_table():
    conn = await asyncpg.connect(
        database="postgres",
        user="postgres",
        password="Galifloh1488",
        host="localhost",
        port=5432
    )
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS moderation (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            city TEXT NOT NULL,
            street TEXT NOT NULL,
            house TEXT NOT NULL,
            review TEXT NOT NULL,
            status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    print("Таблица для модерации создана (если её не было ранее).")
    await conn.close()

asyncio.run(create_moderation_table())


async def alter_moderation_table():
    conn = await asyncpg.connect(
        database="postgres",
        user="postgres",
        password="Galifloh1488",
        host="localhost",
        port=5432
    )
    await conn.execute('''
        ALTER TABLE moderation
        ADD COLUMN IF NOT EXISTS rating REAL;
    ''')
    print("Таблица moderation обновлена: добавлено поле rating.")
    await conn.close()

asyncio.run(alter_moderation_table())
