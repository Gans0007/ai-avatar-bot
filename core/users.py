from core.database import get_pool


async def create_user(telegram_user_id, username, first_name):
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
            insert into users (telegram_user_id, username, first_name)
            values ($1, $2, $3)
            on conflict (telegram_user_id) do nothing
        """, telegram_user_id, username, first_name)