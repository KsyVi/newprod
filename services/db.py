import asyncpg
from config import DATABASE_URL 

async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

async def save_search_results_to_db(query, games, providers):

    pass
