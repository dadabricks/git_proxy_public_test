from http.server import BaseHTTPRequestHandler

from urllib3 import PoolManager

from proxy.handlers.utils.logger import log_headers
from proxy.handlers.utils.proxy_utils import (
    forward_proxy_response,
    copy_header_proxy_for_destination,
)


def do_proxy_post(handler: BaseHTTPRequestHandler, pool_manager: PoolManager):
    content_len = int(handler.headers.get("Content-Length", 0))
    post_body = handler.rfile.read(content_len)
    request_headers = copy_header_proxy_for_destination(headers=handler.headers)

    log_headers(
        message=f"Outgoing POST {handler.destination_url} headers",
        headers=request_headers,
    )
    response = pool_manager.request(
        method="POST",
        url=handler.destination_url,
        headers=request_headers,
        body=post_body,
    )

    # Proxy to Control Plane
    forward_proxy_response(handler=handler, response=response)
