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
        [InlineKeyboardButton(text="💳 Купить за 190 грн", callback_data="buy")]
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

        print("STATUS:", res.status_code)
        print("TEXT:", res.text)

        payment = res.json()

        payment_url = payment.get("payment_url")

        if not payment_url:
            await callback.message.answer(
                f"❌ Ошибка сервера:\n{payment}"
            )
            return

        await callback.message.answer(
            f"👉 Оплати доступ:\n{payment_url}"
        )

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")

async def main():
    await create_pool()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())