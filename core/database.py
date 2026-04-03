import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

pool = None


async def create_pool():
    global pool

    pool = await asyncpg.create_pool(
        DATABASE_URL,
        statement_cache_size=0,   # 🔥 КРИТИЧЕСКИЙ ФИКС
        max_size=5                # (опционально, но нормально для Railway)
    )

    print("✅ DB pool created")


async def get_pool():
    if not pool:
        raise Exception("❌ Pool not initialized")
    return pool