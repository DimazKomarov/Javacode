import asyncio
import functools
import json
import logging
from typing import Any, TypedDict

import aiofiles
import aiohttp

MAX_CONCURRENCY = 5
RETRY_COUNT = 3
RETRY_DELAY = 1

ERROR_TIMEOUT_OR_CONNECTION_FAILED = 421
ERROR_UNEXPECTED = 430


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(url)s attempt=%(attempt)d]: %(message)s",
)
logger = logging.getLogger(__name__)


class FetchResult(TypedDict, total=False):
    url: str
    status_code: int
    content: Any
    error: str


async def parse_json(response: aiohttp.ClientResponse) -> Any:
    loop = asyncio.get_running_loop()
    text = await response.text()
    return await loop.run_in_executor(None, json.loads, text)


async def serialize_json(data: Any) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, functools.partial(json.dumps, data, ensure_ascii=False)
    )


async def fetch_url(session: aiohttp.ClientSession, url: str) -> FetchResult:
    for attempt in range(RETRY_COUNT):
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                content = await parse_json(response)  # Парсинг в отдельном потоке
                return {"url": url, "status_code": response.status, "content": content}

        except (asyncio.TimeoutError, aiohttp.ClientConnectionError) as e:
            logger.warning(
                "Timeout or connection error",
                extra={"url": url, "attempt": attempt, "error": str(e)},
                exc_info=True,
            )
            if attempt < RETRY_COUNT - 1:
                await asyncio.sleep(
                    RETRY_DELAY * 2**attempt
                )  # экспоненциальный backoff
            else:
                return {
                    "url": url,
                    "status_code": ERROR_TIMEOUT_OR_CONNECTION_FAILED,
                    "error": f"{type(e).__name__}: {str(e)}",
                }

        except Exception as e:
            logger.error(
                "Unexpected error",
                extra={"url": url, "attempt": attempt, "error": str(e)},
                exc_info=True,
            )
            return {
                "url": url,
                "status_code": ERROR_UNEXPECTED,
                "error": f"unexpected: {e}",
            }


async def worker(
    queue: asyncio.Queue[str],
    session: aiohttp.ClientSession,
    out_file: aiofiles.threadpool.text.AsyncTextIOWrapper,
) -> None:
    while True:
        url = await queue.get()
        if url is None:  # Сигнал остановки
            queue.task_done()
            break

        result = await fetch_url(session, url)

        json_line = (
            await serialize_json(result) + "\n"
        )  # Сериализация в отдельном потоке
        await out_file.write(json_line)

        queue.task_done()


async def producer(input_file: str, queue: asyncio.Queue[str]) -> None:
    async with aiofiles.open(input_file, "r", encoding="utf-8") as in_file:
        async for line in in_file:
            url = line.strip()
            if url:
                await queue.put(url)


async def fetch_urls(input_file: str, output_file: str, concurrency: int = 5) -> None:
    queue = asyncio.Queue(maxsize=concurrency * 2)

    async with aiohttp.ClientSession() as session:
        async with aiofiles.open(output_file, "w", encoding="utf-8") as out_file:
            # Создаем воркеров
            workers = [
                asyncio.create_task(worker(queue, session, out_file))
                for i in range(concurrency)
            ]

            # Запускаем продюсера
            await producer(input_file, queue)

            # Сигнал воркерам завершиться
            for _ in range(concurrency):
                await queue.put(None)

            await queue.join()
            await asyncio.gather(*workers)


if __name__ == "__main__":
    asyncio.run(fetch_urls("urls.txt", "./results_advanced.jsonl"))
