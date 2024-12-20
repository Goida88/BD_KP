import asyncpg

DB_CONFIG = {
    'database': "postgres",
    'user': "postgres",
    'password': "Galifloh1488",
    'host': "localhost",
    'port': 5432
}

async def execute_query(query):
    conn = await asyncpg.connect(**DB_CONFIG)  # Устанавливаем соединение
    try:
        await conn.execute(query)  # Выполняем запрос
    finally:
        await conn.close()  # Закрываем соединение

async def create_table():
    await execute_query('''
    CREATE TABLE IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        address TEXT NOT NULL,
        review TEXT NOT NULL,
        rating REAL DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    print("Таблица reviews создана.")

async def alter_table():
    await execute_query('''
    ALTER TABLE reviews
    DROP COLUMN IF EXISTS address;
    ''')
    await execute_query('''
    ALTER TABLE reviews
    ADD COLUMN IF NOT EXISTS city TEXT,
    ADD COLUMN IF NOT EXISTS street TEXT,
    ADD COLUMN IF NOT EXISTS house TEXT;
    ''')
    print("Таблица reviews обновлена.")

async def create_moderation_table():
    await execute_query('''
    CREATE TABLE IF NOT EXISTS moderation (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        city TEXT NOT NULL,
        street TEXT NOT NULL,
        house TEXT NOT NULL,
        review TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    print("Таблица moderation создана.")

async def alter_moderation_table():
    await execute_query('''
    ALTER TABLE moderation
    ADD COLUMN IF NOT EXISTS rating REAL;
    ''')
    print("Таблица moderation обновлена.")

async def create_users_table():
    await execute_query('''
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    print("Таблица users создана.")

async def create_comments_table():
    await execute_query('''
    CREATE TABLE IF NOT EXISTS comments (
        id SERIAL PRIMARY KEY,
        review_id INT NOT NULL,
        user_id BIGINT NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    print("Таблица comments создана.")

async def create_likes_table():
    await execute_query('''
    CREATE TABLE IF NOT EXISTS likes (
        id SERIAL PRIMARY KEY,
        review_id INT NOT NULL,
        user_id BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    print("Таблица likes создана.")

async def create_reports_table():
    await execute_query('''
    CREATE TABLE IF NOT EXISTS reports (
        id SERIAL PRIMARY KEY,
        review_id INT NOT NULL,
        user_id BIGINT NOT NULL,
        reason TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    print("Таблица reports создана.")

async def create_favorites_table():
    await execute_query('''
    CREATE TABLE IF NOT EXISTS favorites (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        review_id INT NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    print("Таблица favorites создана.")

async def create_all_tables():
    await create_table()
    await alter_table()
    await create_moderation_table()
    await alter_moderation_table()
    await create_users_table()
    await create_comments_table()
    await create_likes_table()
    await create_reports_table()
    await create_favorites_table()
