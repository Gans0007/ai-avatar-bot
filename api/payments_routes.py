from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from api.wayforpay import create_payment_data
from core.database import get_pool
import os
import requests

router = APIRouter()

BOT_TOKEN = os.getenv("BOT_TOKEN")


@router.post("/create")
async def create_payment(request: Request):
    data = await request.json()
    user_id = data.get("user_id")

    return {
        "payment_url": f"https://easygoing-spontaneity-production-b362.up.railway.app/api/payment/pay/{user_id}"
    }


@router.get("/pay/{user_id}", response_class=HTMLResponse)
async def pay_page(user_id: int):
    payment = create_payment_data(user_id)

    form_html = f"""
    <html>
    <body onload="document.forms[0].submit()">
        <form method="POST" action="https://secure.wayforpay.com/pay">
            {''.join([f'<input type="hidden" name="{k}" value="{v}">' for k, v in payment.items()])}
        </form>
    </body>
    </html>
    """

    return HTMLResponse(content=form_html)


@router.post("/webhook")
async def payment_webhook(request: Request):
    data = await request.json()

    print("WEBHOOK DATA:", data)

    status = data.get("transactionStatus")
    order_reference = data.get("orderReference")

    if status == "Approved":
        user_id = order_reference.split("_")[1]

        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE users
                SET is_paid = true
                WHERE telegram_user_id = $1
            """, int(user_id))

        # отправка пользователю
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": int(user_id),
                "text": "✅ Оплата прошла!\n\nВот твой доступ:\nhttps://твой_курс"
            }
        )

        print("✅ Оплата прошла:", user_id)

    return {"status": "ok"}