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
    Ищет все отзывы в базе данных по указанному городу, улице и дому.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT review, rating
            FROM reviews
            WHERE city = $1 AND street = $2 AND house = $3
            """,
            city, street, house
        )
        return [{"review": row["review"], "rating": row["rating"]} for row in rows]


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
    Получает топ-10 лучших отзывов по рейтингу для заданного города.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT city, street, house, review, rating
            FROM reviews
            WHERE city = $1 AND rating IS NOT NULL
            ORDER BY rating DESC
            LIMIT 10
            """,
            city
        )
        return [{"city": row["city"], "street": row["street"], "house": row["house"], "review": row["review"], "rating": row["rating"]} for row in rows]


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
