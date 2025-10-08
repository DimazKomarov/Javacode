import asyncio
import json

import aiohttp


async def fetch_url(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
) -> dict[str, str | int]:
    async with semaphore:
        try:
            async with session.get(url, timeout=5) as response:
                return {"url": url, "status_code": response.status}

        except asyncio.TimeoutError:
            return {"url": url, "status_code": 0, "error": "timeout"}
        except aiohttp.ClientConnectionError:
            return {"url": url, "status_code": 0, "error": "connection failed"}
        except Exception as e:
            return {"url": url, "status_code": 0, "error": f"unexpected: {e}"}


async def fetch_urls(
    urls: list[str],
    file_path: str,
) -> None:
    semaphore = asyncio.Semaphore(5)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks)

    with open(file_path, "w", encoding="utf-8") as file:
        for result in results:
            file.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    urls = [
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url",
    ]
    asyncio.run(fetch_urls(urls, "results.jsonl"))
