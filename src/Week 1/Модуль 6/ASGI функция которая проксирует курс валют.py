import asyncio
from typing import Any, Callable

import httpx


async def currency_asgi_app(
    scope: dict[str, Any], receive: Callable, send: Callable
) -> None:
    assert scope["type"] == "http"

    path = scope.get("path", "/").lstrip("/")
    if not path:
        body = b"Please provide currency in path, e.g. /USD"
        await send(
            {
                "type": "http.response.start",
                "status": 400,
                "headers": [(b"content-type", b"text/plain")],
            }
        )
        await send({"type": "http.response.body", "body": body})
        return

    currency = path.upper()
    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            content = response.content

            await send(
                {
                    "type": "http.response.start",
                    "status": response.status_code,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send({"type": "http.response.body", "body": content})

    except Exception as e:
        error = f"Error fetching rates: {e}".encode()
        await send(
            {
                "type": "http.response.start",
                "status": 502,
                "headers": [(b"content-type", b"text/plain")],
            }
        )
        await send({"type": "http.response.body", "body": error})


async def run_asgi_server(
    host: str = "127.0.0.1", port: int = 8000, app: Callable = None
) -> None:
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, app), host, port
    )
    print(f"Serving ASGI app on http://{host}:{port}")
    async with server:
        await server.serve_forever()


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, app: Callable
) -> None:
    request_data = await reader.read(1024)
    if not request_data:
        writer.close()
        await writer.wait_closed()
        return

    request_line = request_data.decode(errors="ignore").splitlines()[0]
    try:
        method, path, _ = request_line.split()
    except ValueError:
        writer.close()
        await writer.wait_closed()
        return

    scope = {"type": "http", "method": method, "path": path}

    async def send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.start":
            status = message["status"]
            headers = message.get("headers", [])
            response = [f"HTTP/1.1 {status} OK\r\n".encode()]
            for name, value in headers:
                response.append(name + b": " + value + b"\r\n")
            response.append(b"\r\n")
            writer.writelines(response)
        elif message["type"] == "http.response.body":
            writer.write(message["body"])
            await writer.drain()
            writer.close()
            await writer.wait_closed()

    async def receive() -> dict[str, str]:
        return {"type": "http.request"}

    await app(scope, receive, send)


if __name__ == "__main__":
    asyncio.run(run_asgi_server(app=currency_asgi_app))
