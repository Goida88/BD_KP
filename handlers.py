from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from config import TOKEN

import app.keyboards as kb
from app.database import save_review, get_review, save_review_rating, get_top_reviews, get_average_rating, approve_review
from app.keyboards import generate_rating_keyboard, inline_average_rating_button
from app.database import save_review_for_moderation, get_pending_reviews, update_review_status

router = Router()

user_data = {}

db_pool = None


# Создаём объект бота для отправки уведомлений
bot = Bot(token=TOKEN)  # Замените YOUR_BOT_TOKEN на ваш токен

def set_db_pool(pool):
    global db_pool
    db_pool = pool

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!', reply_markup=kb.main)

MODERATORS = {426327797}  # Замените на реальные user_id модераторов

@router.message(F.text == '/moderate')
async def moderate_reviews(message: Message):
    if message.from_user.id not in MODERATORS:
        await message.answer("У вас нет прав модератора.")
        return

    pending_reviews = await get_pending_reviews(db_pool)
    if not pending_reviews:
        await message.answer("Нет отзывов, ожидающих модерации.")
        return

    for review in pending_reviews:
        await message.answer(
            f"<b>Город:</b> {review['city']}\n"
            f"<b>Улица:</b> {review['street']}\n"
            f"<b>Дом:</b> {review['house']}\n"
            f"<b>Отзыв:</b> {review['review']}",
            parse_mode="HTML",
            reply_markup=kb.generate_moderation_buttons(review['id'])
        )


@router.callback_query(lambda c: c.data and c.data.startswith("moderate_"))
@router.callback_query(lambda c: c.data and c.data.startswith("moderate_"))
async def handle_moderation(callback_query: CallbackQuery):
    _, review_id, action = callback_query.data.split("_")
    review_id = int(review_id)

    if action == 'approve':
        await approve_review(db_pool, review_id)
        await callback_query.answer("Отзыв одобрен и добавлен в базу.")
    elif action == 'reject':
        # Отклоняем отзыв и получаем user_id
        user_id = await update_review_status(db_pool, review_id, 'rejected')
        await callback_query.answer("Отзыв отклонён.")

        # Отправляем уведомление пользователю
        if user_id:
            await bot.send_message(
                chat_id=user_id,
                text="К сожалению, ваш отзыв был отклонён модератором."
            )



@router.message(F.text == 'Оценить место 📝')
async def start_review(message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {'action': 'add_review', 'city': None, 'street': None, 'house': None, 'review': None}
    await message.answer("Введите город в формате:\nГород Москва")

@router.message(F.text == 'Найти отзывы 🌟')
async def start_find_reviews(message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {'action': 'find_review', 'city': None, 'street': None, 'house': None}
    await message.answer("Введите город в формате:\nГород Москва")

@router.message(F.text == 'Топ лучших 🏆')
async def start_top_best(message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {'action': 'top_best', 'city': None}
    await message.answer("Введите город, чтобы узнать топ лучших мест:\nПример: Город Москва")


@router.message()
async def handle_user_input(message: Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    action = user_data[user_id].get('action')

    if action == 'add_review':
        if user_data[user_id]['city'] is None:
            user_data[user_id]['city'] = message.text.strip()
            await message.answer("Введите улицу в формате:\nУлица Бехтерева")
        elif user_data[user_id]['street'] is None:
            user_data[user_id]['street'] = message.text.strip()
            await message.answer("Введите номер дома в формате:\nДом 5")
        elif user_data[user_id]['house'] is None:
            user_data[user_id]['house'] = message.text.strip()
            await message.answer("Напишите отзыв:")
        elif user_data[user_id]['review'] is None:
            user_data[user_id]['review'] = message.text.strip()
            await message.answer(
                "Спасибо за отзыв! Теперь поставьте оценку:",
                reply_markup=kb.generate_rating_keyboard()
            )

    elif action == 'find_review':
        if user_data[user_id]['city'] is None:
            user_data[user_id]['city'] = message.text.strip()
            await message.answer("Введите улицу в формате:\nУлица Бехтерева")
        elif user_data[user_id]['street'] is None:
            user_data[user_id]['street'] = message.text.strip()
            await message.answer("Введите номер дома в формате:\nДом 5")
        elif user_data[user_id]['house'] is None:
            user_data[user_id]['house'] = message.text.strip()
            reviews = await get_review(
                db_pool,
                user_data[user_id]['city'],
                user_data[user_id]['street'],
                user_data[user_id]['house']
            )
            if reviews:
                reviews_text = "\n\n".join([
                    f"Отзыв: {review['review']}\nРейтинг: {review['rating']} ⭐" if review['rating'] is not None
                    else f"Отзыв: {review['review']}\nРейтинг: не указан"
                    for review in reviews
                ])
                await message.answer(
                    f"Вот что мы нашли для адреса:\n\n"
                    f"<b>Город:</b> {user_data[user_id]['city']}\n"
                    f"<b>Улица:</b> {user_data[user_id]['street']}\n"
                    f"<b>Дом:</b> {user_data[user_id]['house']}\n\n{reviews_text}",
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    f"К сожалению, отзывов для указанного адреса пока нет.",
                    parse_mode="HTML"
                )
            del user_data[user_id]

    elif action == 'top_best':
        if user_data[user_id]['city'] is None:
            user_data[user_id]['city'] = message.text.strip()
            top_reviews = await get_top_reviews(db_pool, user_data[user_id]['city'])
            if top_reviews:
                reviews_text = "\n\n".join([
                    f"<b>Адрес:</b> {review['city']}, {review['street']}, {review['house']}\n"
                    f"<b>Рейтинг:</b> {review['rating']} ⭐\n"
                    f"<b>Отзыв:</b> {review['review']}"
                    for review in top_reviews
                ])
                await message.answer(
                    f"Топ-10 лучших мест в городе {user_data[user_id]['city']}:\n\n{reviews_text}",
                    parse_mode="HTML",
                    reply_markup=kb.inline_average_rating_button(user_data[user_id]['city'])
                )
            else:
                await message.answer(
                    f"К сожалению, в городе {user_data[user_id]['city']} пока нет отзывов.",
                    parse_mode="HTML"
                )
            del user_data[user_id]

@router.callback_query(lambda c: c.data and c.data.startswith("rating_"))
async def handle_rating(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    rating = float(callback_query.data.split("_")[1])

    if user_id not in user_data or user_data[user_id].get('action') != 'add_review':
        await callback_query.answer("Что-то пошло не так. Попробуйте снова.")
        return

    # Сохраняем отзыв с рейтингом в таблицу модерации
    await save_review_for_moderation(
        db_pool,
        user_id=user_id,
        city=user_data[user_id]['city'],
        street=user_data[user_id]['street'],
        house=user_data[user_id]['house'],
        review=user_data[user_id]['review'],
        rating=rating
    )
    await callback_query.answer("Спасибо за ваш отзыв! Он отправлен на модерацию.")
    await callback_query.message.edit_text(
        "Ваш отзыв и оценка отправлены на модерацию. Спасибо!"
    )
    del user_data[user_id]


@router.callback_query(lambda c: c.data and c.data.startswith("average_rating_"))
async def handle_average_rating(callback_query: CallbackQuery):
    city = callback_query.data.split("_")[2]
    average_rating = await get_average_rating(db_pool, city)

    # Закрываем всплывающее уведомление
    await callback_query.answer()

    if average_rating is not None:
        # Форматирование для удаления лишних нулей
        formatted_rating = f"{average_rating:.2f}".rstrip('0').rstrip('.')
        await callback_query.message.answer(
            f"Средний рейтинг в городе {city}: {formatted_rating} ⭐",
            parse_mode="HTML"
        )
    else:
        await callback_query.message.answer(
            f"К сожалению, в городе {city} пока нет отзывов с рейтингами.",
            parse_mode="HTML"
        )
