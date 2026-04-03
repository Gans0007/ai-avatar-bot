import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

from fastapi import FastAPI
from core.database import create_pool
from core.users import create_user
from api.payments_routes import router as payment_router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

app.include_router(payment_router, prefix="/api/payment")


def get_buy_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить за 190 грн", callback_data="buy")],
        [InlineKeyboardButton(text="🔍 Проверить оплату", callback_data="check_payment")]
    ])


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await create_user(
        telegram_user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    await message.answer(
        "🔥 AI Avatar Intensive\n\nОплати доступ 👇",
        reply_markup=get_buy_keyboard()
    )

from aiogram.types import CallbackQuery

@dp.callback_query(lambda c: c.data == "buy")
async def buy_handler(callback: CallbackQuery):
    try:
        res = requests.post(
            "https://easygoing-spontaneity-production-b362.up.railway.app/api/payment/create",
            json={"user_id": callback.from_user.id},
            timeout=10
        )

        payment = res.json()
        payment_url = payment.get("payment_url")

        if not payment_url:
            await callback.message.answer("❌ Ошибка создания платежа")
            return

        # 🔥 КНОПКА СРАЗУ С ОПЛАТОЙ
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=payment_url)]
        ])

        await callback.message.answer(
            "🔥 Нажми чтобы оплатить:",
            reply_markup=keyboard
        )

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")

@dp.callback_query(lambda c: c.data == "check_payment")
async def check_payment_handler(callback: CallbackQuery):
    try:
        res = requests.get(
            f"https://easygoing-spontaneity-production-b362.up.railway.app/api/payment/check/{callback.from_user.id}",
            timeout=10
        )

        data = res.json()

        if data.get("is_paid"):
            await callback.message.answer(
                "✅ Оплата найдена!\n\n🚀 Доступ:\nhttps://t.me/yourambitions"
            )
        else:
            await callback.message.answer(
                "❌ Оплата не найдена\n\nПопробуй ещё раз через несколько секунд"
            )

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")

async def main():
    await create_pool()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())