from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import Expense
from keyboards import get_categories_keyboard
import db

router = Router()

# Инициализация БД при старте
db.init_db()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я помогу вести учёт расходов. Вот что я умею:\n"
        "/add — Добавить расход\n"
        "/stats — Статистика\n"
        "/cancel — Отмена"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.")


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    await state.set_state(Expense.waiting_for_amount)
    await message.answer("Введите сумму расхода:")


@router.message(Expense.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        await state.update_data(amount=amount)
        await state.set_state(Expense.waiting_for_category)
        await message.answer(
            "Выберите категорию:",
            reply_markup=get_categories_keyboard()
        )
    except ValueError:
        await message.answer("Пожалуйста, введите число (например, 150 или 99.99)")


@router.callback_query(F.data.startswith("category_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace("category_", "")
    user_data = await state.get_data()
    amount = user_data.get("amount")

    db.add_expense(callback.from_user.id, amount, category)
    await callback.message.edit_text(f"✅ Расход {amount} грн. ({category}) добавлен!")
    await state.clear()
    await callback.answer()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    # Показываем статистику за неделю
    stats = db.get_stats(message.from_user.id, days=7)
    if not stats:
        await message.answer("За последнюю неделю расходов не найдено.")
    else:
        total = sum(amount for _, amount in stats)
        lines = [f"*Расходы за неделю (всего: {total:.2f} грн.)*"]
        for cat, amount in stats:
            lines.append(f"• {cat}: {amount:.2f} грн.")
        await message.answer("\n".join(lines), parse_mode="Markdown")