from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from api.wayforpay import create_payment_data
from core.database import get_pool
import os
import requests

router = APIRouter()

BOT_TOKEN = os.getenv("BOT_TOKEN")


# =========================
# СОЗДАНИЕ ПЛАТЕЖА
# =========================
@router.post("/create")
async def create_payment(request: Request):
    try:
        data = await request.json()
    except:
        data = {}

    user_id = data.get("user_id")

    if not user_id:
        print("❌ user_id missing")
        return {"error": "user_id missing"}

    payment_url = f"https://easygoing-spontaneity-production-b362.up.railway.app/api/payment/pay/{user_id}"

    print("✅ CREATE PAYMENT:", user_id, payment_url)

    return {
        "payment_url": payment_url
    }


# =========================
# СТРАНИЦА ОПЛАТЫ
# =========================
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


# =========================
# ВЕБХУК ОПЛАТЫ
# =========================
@router.post("/webhook")
async def payment_webhook(request: Request):
    try:
        data = await request.json()
    except:
        data = {}

    print("📩 WEBHOOK DATA:", data)

    status = data.get("transactionStatus")
    order_reference = data.get("orderReference")

    if status == "Approved" and order_reference:
        try:
            user_id = int(order_reference.split("_")[1])
        except:
            print("❌ Ошибка парсинга orderReference")
            return {"status": "error"}

        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE users
                SET is_paid = true
                WHERE telegram_user_id = $1
            """, user_id)

        # отправка сообщения пользователю
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": user_id,
                    "text": "✅ Оплата прошла!\n\nВот твой доступ:\nhttps://твой_курс"
                }
            )
        except Exception as e:
            print("❌ Ошибка отправки сообщения:", e)

        print("✅ ОПЛАТА УСПЕШНА:", user_id)

    return {"status": "ok"}