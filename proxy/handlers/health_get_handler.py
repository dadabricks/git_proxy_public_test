from http.server import BaseHTTPRequestHandler

from proxy.config import ProxyConfig
from proxy.handlers.utils.handler_utils import (
    set_status_code,
    set_headers,
    set_json_body,
)


def do_health(handler: BaseHTTPRequestHandler):
    set_status_code(200, handler)
    headers = {
        "Content-type": "application/json",
    }
    set_headers(headers=headers, handler=handler)
    data = {
        "status": "ok",
        "version": ProxyConfig.VERSION,
    }
    set_json_body(data=data, handler=handler)
