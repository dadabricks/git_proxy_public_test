from http.server import BaseHTTPRequestHandler

from proxy.config import ProxyConfig
from proxy.handlers.utils.handler_utils import (
    set_status_code,
    set_headers,
    get_url_param,
    set_text_body,
)


def read_last_n_lines(file_path: str, n: int):
    with open(file_path, "r") as f:
        return "".join(f.readlines()[-n:])


def do_log(handler: BaseHTTPRequestHandler):
    set_status_code(200, handler)
    headers = {
        "Content-type": "text/plain",
    }
    set_headers(headers=headers, handler=handler)
    line_count = int(get_url_param(url=handler.path, param="n", default=10))
    log_str = read_last_n_lines(file_path=ProxyConfig.LOG_FILE_PATH, n=line_count)
    set_text_body(data=log_str, handler=handler)
