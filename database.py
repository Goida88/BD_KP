import asyncpg

async def save_review(pool, user_id: int, city: str, street: str, house: str, review: str):
    """
    Сохраняем отзыв в базу данных PostgreSQL.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO reviews (user_id, city, street, house, review)
            VALUES ($1, $2, $3, $4, $5)
            """,
            user_id, city, street, house, review
        )


async def get_review(pool, city: str, street: str, house: str):
    """
    Ищет отзывы по городу, улице и дому, включая имя пользователя.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT r.review, r.rating, u.username
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.city = $1 AND r.street = $2 AND r.house = $3
        ''', city, street, house)
        return [{"review": row["review"], "rating": row["rating"], "username": row["username"]} for row in rows]


async def save_review_rating(pool, user_id: int, rating: float):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE reviews
            SET rating = $1
            WHERE id = (
                SELECT id
                FROM reviews
                WHERE user_id = $2
                ORDER BY created_at DESC
                LIMIT 1
            )
            """,
            rating, user_id
        )

async def get_top_reviews(pool, city: str):
    """
    Получает топ-10 лучших отзывов по рейтингу для заданного города с логином пользователя.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT r.city, r.street, r.house, r.review, r.rating, u.username
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.city = $1 AND r.rating IS NOT NULL
            ORDER BY r.rating DESC
            LIMIT 10
        ''', city)
        return [{"city": row["city"], "street": row["street"], "house": row["house"],
                 "review": row["review"], "rating": row["rating"], "username": row["username"]} for row in rows]


async def get_average_rating(pool, city: str):
    """
    Получает средний рейтинг для указанного города.
    """
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            """
            SELECT AVG(rating)
            FROM reviews
            WHERE city = $1 AND rating IS NOT NULL
            """,
            city
        )
        return result


async def save_review_for_moderation(pool, user_id: int, city: str, street: str, house: str, review: str, rating: float):
    """
    Сохраняем отзыв в таблицу модерации с рейтингом.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO moderation (user_id, city, street, house, review, rating)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            user_id, city, street, house, review, rating
        )


async def get_pending_reviews(pool):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, city, street, house, review
            FROM moderation
            WHERE status = 'pending'
            """
        )
        return [dict(row) for row in rows]

async def update_review_status(pool, review_id: int, status: str):
    """
    Обновляет статус отзыва и возвращает user_id для уведомления.
    """
    async with pool.acquire() as conn:
        # Обновляем статус
        await conn.execute(
            """
            UPDATE moderation
            SET status = $1
            WHERE id = $2
            """,
            status, review_id
        )
        # Получаем user_id
        user_id = await conn.fetchval(
            """
            SELECT user_id
            FROM moderation
            WHERE id = $1
            """,
            review_id
        )
        return user_id
async def approve_review(pool, review_id: int):
    """
    Переносит отзыв из таблицы модерации в основную таблицу.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO reviews (user_id, city, street, house, review, rating, created_at)
            SELECT user_id, city, street, house, review, rating, CURRENT_TIMESTAMP
            FROM moderation
            WHERE id = $1
            """,
            review_id
        )
        await conn.execute(
            "DELETE FROM moderation WHERE id = $1",
            review_id
        )


async def save_user(pool, user_id: int, username: str) -> bool:
    """
    Сохраняет пользователя в таблицу users. Проверяет уникальность логина.
    Возвращает True, если сохранение успешно, иначе False.
    """
    async with pool.acquire() as conn:
        # Проверка на уникальность логина
        existing_user = await conn.fetchval('''
            SELECT id FROM users WHERE username = $1
        ''', username)
        if existing_user:
            return False  # Логин уже занят

        # Сохраняем пользователя
        await conn.execute('''
            INSERT INTO users (id, username)
            VALUES ($1, $2)
        ''', user_id, username)
        return True

async def get_user_profile(pool, user_id: int):
    """
    Получает информацию о пользователе и количество оставленных им отзывов.
    """
    async with pool.acquire() as conn:
        # Получаем имя пользователя и количество отзывов
        result = await conn.fetchrow('''
            SELECT u.username, COUNT(r.id) AS reviews_count
            FROM users u
            LEFT JOIN reviews r ON u.id = r.user_id
            WHERE u.id = $1
            GROUP BY u.username
        ''', user_id)
        if result:
            return {"username": result["username"], "reviews_count": result["reviews_count"]}
        else:
            return None

async def save_comment(pool, review_id: int, user_id: int, comment: str):
    async with pool.acquire() as conn:
        await conn.execute('''
        INSERT INTO comments (review_id, user_id, comment)
        VALUES ($1, $2, $3)
        ''', review_id, user_id, comment)

async def get_comments(pool, review_id: int):
    async with pool.acquire() as conn:
        rows = await conn.fetch('''
        SELECT user_id, comment, created_at
        FROM comments
        WHERE review_id = $1
        ''', review_id)
        return rows

async def add_like(pool, review_id: int, user_id: int):
    async with pool.acquire() as conn:
        await conn.execute('''
        INSERT INTO likes (review_id, user_id)
        VALUES ($1, $2)
        ''', review_id, user_id)

async def report_review(pool, review_id: int, user_id: int, reason: str):
    async with pool.acquire() as conn:
        await conn.execute('''
        INSERT INTO reports (review_id, user_id, reason)
        VALUES ($1, $2, $3)
        ''', review_id, user_id, reason)

async def add_to_favorites(pool, user_id: int, review_id: int):
    async with pool.acquire() as conn:
        await conn.execute('''
        INSERT INTO favorites (user_id, review_id)
        VALUES ($1, $2)
        ''', user_id, review_id)

async def get_favorites(pool, user_id: int):
    async with pool.acquire() as conn:
        rows = await conn.fetch('''
        SELECT review_id, added_at
        FROM favorites
        WHERE user_id = $1
        ''', user_id)
        return rows
