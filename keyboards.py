from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_categories_keyboard():
    builder = InlineKeyboardBuilder()
    categories = ["Еда", "Транспорт", "Развлечения", "Другое"]
    for cat in categories:
        builder.button(text=cat, callback_data=f"category_{cat}")
    builder.adjust(2)
    return builder.as_markup()