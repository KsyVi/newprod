import asyncio

log_buffer = asyncio.Queue()

async def add_log_to_buffer(request_id, query, start_time, end_time, cache_hit, details):
    log_entry = {
        "request_id": request_id,
        "query": query,
        "start_time": start_time,
        "end_time": end_time,
        "duration": end_time - start_time,
        "cache_hit": cache_hit,
        "details": details,
    }
    await log_buffer.put(log_entry)
