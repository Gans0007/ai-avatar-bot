from fastapi import APIRouter, Request
from api.wayforpay import create_payment_data
from core.database import get_pool

router = APIRouter()


@router.post("/create")
async def create_payment(request: Request):
    data = await request.json()
    user_id = data.get("user_id")

    payment = create_payment_data(user_id)

    return payment


@router.post("/webhook")
async def payment_webhook(request: Request):
    data = await request.json()

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

        print("✅ Оплата прошла:", user_id)

    return {"status": "ok"}