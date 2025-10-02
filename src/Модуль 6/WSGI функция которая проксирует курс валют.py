import socket
import urllib.request
from typing import Callable, Iterable


def currency_wsgi_app(
    environ: dict[str, str],
    start_response: Callable[[str, list[tuple[str, str]]], None],
) -> Iterable[bytes]:
    path = environ.get("PATH_INFO", "/").lstrip("/")
    if not path:
        start_response("400 Bad Request", [("Content-Type", "text/plain")])
        return [b"Please provide currency in path, e.g. /USD"]

    currency = path.upper()
    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            start_response("200 OK", [("Content-Type", "application/json")])
            return [data]
    except Exception as e:
        start_response("502 Bad Gateway", [("Content-Type", "text/plain")])
        return [f"Error fetching rates: {e}".encode()]


def run_wsgi_app(app: Callable, environ: dict[str, str]) -> bytes:
    status_line = ""
    headers = []

    def start_response(status, response_headers):
        nonlocal status_line, headers
        status_line = status
        headers = response_headers

    response_body = app(environ, start_response)

    response = [f"HTTP/1.1 {status_line}\r\n".encode()]
    for header in headers:
        response.append(f"{header[0]}: {header[1]}\r\n".encode())
    response.append(b"\r\n")
    response.extend(response_body)

    return b"".join(response)


def run_wsgi_server(
    host: str = "127.0.0.1", port: int = 8000, app: Callable = None
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Serving WSGI app on http://{host}:{port}")

        while True:
            client_socket, address = server_socket.accept()
            with client_socket:
                request_data = client_socket.recv(1024).decode()

                if not request_data:
                    continue

                request_line = request_data.splitlines()[0]
                method, path, _ = request_line.split()

                environ = {
                    "REQUEST_METHOD": method,
                    "PATH_INFO": path,
                    "SERVER_NAME": host,
                    "SERVER_PORT": str(port),
                }

                response = run_wsgi_app(app, environ)
                client_socket.sendall(response)


if __name__ == "__main__":
    run_wsgi_server(app=currency_wsgi_app)
