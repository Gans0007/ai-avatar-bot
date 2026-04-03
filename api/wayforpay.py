import hashlib
import hmac
import time

MERCHANT_ACCOUNT = "t_me_10acd"
MERCHANT_SECRET = "ТВОЙ_СЕКРЕТ"

DOMAIN = "easygoing-spontaneity-production-b362.up.railway.app"

def generate_signature(data: list):
    sign_str = ";".join(data)
    return hmac.new(
        MERCHANT_SECRET.encode(),
        sign_str.encode(),
        hashlib.md5
    ).hexdigest()


def create_payment_data(user_id: int):
    order_reference = f"order_{user_id}_{int(time.time())}"
    order_date = int(time.time())

    amount = "190"
    currency = "UAH"

    product_name = ["AI Avatar"]
    product_count = ["1"]
    product_price = ["190"]

    data = [
        MERCHANT_ACCOUNT,
        DOMAIN,
        order_reference,
        str(order_date),
        amount,
        currency,
        *product_name,
        *product_count,
        *product_price
    ]

    signature = generate_signature(data)

    return {
        "merchantAccount": MERCHANT_ACCOUNT,
        "merchantDomainName": DOMAIN,
        "orderReference": order_reference,
        "orderDate": order_date,
        "amount": amount,
        "currency": currency,
        "productName": product_name,
        "productCount": product_count,
        "productPrice": product_price,
        "merchantSignature": signature
    }