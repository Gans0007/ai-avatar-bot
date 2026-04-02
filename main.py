import asyncio
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

from fastapi import FastAPI
from core.database import create_pool
from core.users import create_user
from api.payment_routes import router as payment_router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# подключаем роуты
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


@dp.callback_query(lambda c: c.data == "buy")
async def buy_handler(callback: types.CallbackQuery):
    res = requests.post(
        "https://api.youramb.digital/api/payment/create",
        json={"user_id": callback.from_user.id}
    )

    payment = res.json()

    # создаем HTML форму
    form_html = f"""
    <html>
    <body onload="document.forms[0].submit()">
        <form method="POST" action="https://secure.wayforpay.com/pay">
            {''.join([f'<input type="hidden" name="{k}" value="{v}">' for k, v in payment.items()])}
        </form>
    </body>
    </html>
    """

    with open("payment.html", "w", encoding="utf-8") as f:
        f.write(form_html)

    await callback.message.answer("👉 Открой файл payment.html для оплаты")


async def main():
    await create_pool()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())