import asyncio
import json

import aiofiles
import aiohttp


async def fetch_url(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
) -> dict[str, str | int]:
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as response:
                content = await response.json()
                return {"url": url, "content": content}

        except asyncio.TimeoutError:
            return {"url": url, "status_code": 0, "error": "timeout"}
        except aiohttp.ClientConnectionError:
            return {"url": url, "status_code": 0, "error": "connection failed"}
        except Exception as e:
            return {"url": url, "status_code": 0, "error": f"unexpected: {e}"}


async def fetch_urls(
    input_file: str,
    output_file: str,
) -> None:
    semaphore = asyncio.Semaphore(5)

    async with aiohttp.ClientSession() as session:
        async with (
            aiofiles.open(input_file, "r", encoding="utf-8") as in_file,
            aiofiles.open(output_file, "w", encoding="utf-8") as out_file,
        ):
            tasks = [
                fetch_url(session, url.strip(), semaphore)
                async for url in in_file
                if url.strip()
            ]
            for coroutine in asyncio.as_completed(tasks):
                result = await coroutine
                await out_file.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    asyncio.run(fetch_urls("./urls.txt", "./results_advanced.jsonl"))
