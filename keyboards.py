from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Найти отзывы 🌟'), KeyboardButton(text='Оценить место 📝')],
    [KeyboardButton(text='Мой профиль 👤'), KeyboardButton(text='Топ лучших 🏆')],
], resize_keyboard=True, input_field_placeholder='Выберите пункт меню')

inline_return = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='return_to_main')],
])


def generate_rating_keyboard():
    inline_keyboard = []
    for i in range(11):  # Шаг 0.5 (от 0 до 5)
        rating = i * 0.5
        inline_keyboard.append([InlineKeyboardButton(text=f"{rating} ⭐", callback_data=f"rating_{rating}")])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def inline_average_rating_button(city: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Средний рейтинг ⭐", callback_data=f"average_rating_{city}")]
    ])


def generate_moderation_buttons(review_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"moderate_{review_id}_approve"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"moderate_{review_id}_reject")
        ]
    ])
