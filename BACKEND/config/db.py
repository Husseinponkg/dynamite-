import asyncio
import sys
from psycopg import AsyncConnection
from dotenv import load_dotenv
from pathlib import Path
import os

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv(Path(__file__).parent.parent / ".env")


async def connection():
    conn = await AsyncConnection.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dbname=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT"),
        sslmode="require"
    )

    print("Successfully connected to:", os.getenv("DB_NAME"))
    return conn
