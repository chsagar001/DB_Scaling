from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database import AsyncSessionLocal, engine
from redis_client import redis_client

import json
import time

router = APIRouter()

@router.get("/user/{email}")
async def get_user(email: str):
    print(engine.pool.status())

    start_time = time.perf_counter()

    cache_key = f"user:{email}"

    # =========================
    # REDIS CHECK
    # =========================

    cached_data = await redis_client.get(cache_key)

    if cached_data:

        end_time = time.perf_counter()

        return {
            "source": "redis",
            "response_time_ms": round(
                (end_time - start_time) * 1000,
                2
            ),
            "data": json.loads(cached_data)
        }

    # =========================
    # ASYNC DB QUERY
    # =========================

    async with AsyncSessionLocal() as db:

        query = text("""
            SELECT * FROM users
            WHERE email = :email
        """)

        result = await db.execute(
            query,
            {"email": email}
        )

        user = result.fetchone()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "city": user.city
    }

    # =========================
    # STORE IN REDIS
    # =========================

    await redis_client.set(cache_key, json.dumps(user_data))

    end_time = time.perf_counter()

    return {
        "source": "postgresql",
        "response_time_ms": round(
            (end_time - start_time) * 1000,
            2
        ),
        "data": user_data
    }