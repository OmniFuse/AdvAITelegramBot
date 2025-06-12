import datetime
from typing import Optional
from yookassa_api import AsyncClient
from yookassa_api.schemas.payment import PaymentAmount
from yookassa_api.schemas.confirmation import Confirmation
from config import YOOKASSA_SHOP_ID, YOOKASSA_API_KEY, BOT_NAME, OWNER_ID
from modules.core.database import db_service
from modules.user.premium_management import add_premium_status

# Collection for storing payment records
payments_col = db_service.get_collection('yoo_payments')

# Single async client instance
_yoo_client: Optional[AsyncClient] = None

def get_client() -> AsyncClient:
    global _yoo_client
    if _yoo_client is None:
        _yoo_client = AsyncClient(YOOKASSA_API_KEY, int(YOOKASSA_SHOP_ID))
    return _yoo_client

async def create_payment(user_id: int, amount: int, days: int) -> tuple[str, str]:
    """Create a payment and store record. Returns confirmation URL and payment ID."""
    client = get_client()
    payment = await client.create_payment(
        amount=PaymentAmount(amount=amount, currency='RUB'),
        description=f'Premium for {days} days',
        confirmation=Confirmation(type='redirect', return_url=f'https://t.me/{BOT_NAME}'),
        capture=True
    )
    payments_col.insert_one({
        'payment_id': payment.id,
        'user_id': user_id,
        'days': days,
        'amount': amount,
        'status': payment.status,
        'created_at': datetime.datetime.utcnow(),
        'processed': False
    })
    return payment.confirmation.confirmation_url, payment.id

async def verify_payment(payment_id: str) -> bool:
    """Check payment status and grant premium if succeeded."""
    client = get_client()
    record = payments_col.find_one({'payment_id': payment_id})
    if not record:
        return False
    payment = await client.get_payment(payment_id)
    payments_col.update_one({'payment_id': payment_id}, {'$set': {'status': payment.status}})
    if payment.status == 'succeeded' and not record.get('processed'):
        await add_premium_status(record['user_id'], OWNER_ID, record['days'])
        payments_col.update_one({'payment_id': payment_id}, {'$set': {'processed': True}})
        return True
    return payment.status == 'succeeded'
