import asyncio
import asyncpg
import json
import time
import uuid
import logging
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, Response
from schemas import SearchQuery
from cache import cache as redis_cache
from services.kafka_producer import kafka_producer
from services.db import save_search_results_to_db, get_db_connection
from services.log_buffer import add_log_to_buffer


app = FastAPI()

TIMEOUT = 3.0  # секунды

logger = logging.getLogger("search_handler")

@app.on_event("startup")
async def startup():
    await redis_cache.init()
    #await kafka_producer.init()

@app.on_event("shutdown")
async def shutdown():
    await kafka_producer.close()

@app.post("/search", response_model=dict)
async def search_handler(
    search_query: SearchQuery,
    response: Response,
    background_tasks: BackgroundTasks,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    start_time = time.perf_counter()
    logger.info(f"Received search request: {search_query.query}")

    cache_key = f"search:{search_query.query}"
    cache_start_time = time.perf_counter()

    cached_result = await redis_cache.get(cache_key)
    if cached_result:
        response.status_code = 200
        cached_data = json.loads(cached_result)
        request_id = cached_data.get("request_id", str(uuid.uuid4()))
        games_data = [g['game_id'] for g in cached_data.get('games', [])]
        providers_data = [
            p['provider_id'] for p in cached_data.get('providers', [])
            if isinstance(p, dict) and 'provider_id' in p
        ]

        elapsed = time.perf_counter() - start_time
        logger.info(f"Cache hit for '{search_query.query}' in {elapsed:.4f}s")

        if 'add_log_to_buffer' in globals():
            await add_log_to_buffer(
                request_id,
                search_query.query,
                cache_start_time,
                time.perf_counter(),
                True,
                {"games": games_data, "providers": providers_data}
            )

        try:
            await save_search_results_to_db(search_query.query, games_data, providers_data)
        except Exception as e:
            logger.error(f"DB save error (cached): {e}")

        return {
            "request_id": request_id,
            "games": games_data,
            "providers": providers_data
        }

    request_id = str(uuid.uuid4())
    query_data = search_query.dict()
    query_data["request_id"] = request_id

    await kafka_producer.send_search_task(query_data)
    logger.info(f"Sent to Kafka: {query_data}")

    polling_start = time.perf_counter()
    polling_interval = 0.01  # 10ms

    while True:
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            data = json.loads(cached_result)
            games = [g["game_id"] for g in data.get("games", [])]
            providers = [p["provider_id"] for p in data.get("providers", []) if isinstance(p, dict) and "provider_id" in p]

            try:
                await save_search_results_to_db(search_query.query, games, providers)
            except Exception as e:
                logger.error(f"DB save error (polled): {e}")

            return {
                "request_id": request_id,
                "games": games,
                "providers": providers
            }

        if (time.perf_counter() - polling_start) > TIMEOUT:
            response.status_code = 504
            logger.error(f"Search timed out for query: {search_query.query}")
            raise HTTPException(status_code=504, detail="Search task timed out")

        await asyncio.sleep(polling_interval)

