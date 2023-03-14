import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def set_headers(headers: dict, handler: BaseHTTPRequestHandler):
    for k, v in headers.items():
        handler.send_header(k, v)
    handler.end_headers()


def set_json_body(data: dict, handler: BaseHTTPRequestHandler):
    handler.wfile.write(json.dumps(data).encode())


def set_text_body(data: str, handler: BaseHTTPRequestHandler):
    handler.wfile.write(data.encode())


def set_binary_body(data: bin, handler: BaseHTTPRequestHandler):
    handler.wfile.write(data)


def set_status_code(code: int, handler: BaseHTTPRequestHandler):
    handler.send_response(code)


def get_route_handler(path: str, path_to_handler: dict):
    for route, handler in path_to_handler.items():
        if path.startswith(route):
            return handler
    return None


def get_url_param(url: str, param: str, default=None):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    return qs.get(param, [default])[0]
