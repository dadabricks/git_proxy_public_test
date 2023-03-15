from http.server import BaseHTTPRequestHandler
from pprint import pprint

from urllib3 import PoolManager

from proxy.handlers.utils.logger import log_headers
from proxy.handlers.utils.proxy_utils import (
    forward_proxy_response,
    copy_header_proxy_for_destination,
)


def do_proxy_get(handler: BaseHTTPRequestHandler, pool_manager: PoolManager):
    request_headers = copy_header_proxy_for_destination(headers=handler.headers)
    # Proxy to Destination
    log_headers(
        message=f"Outgoing GET {handler.destination_url} headers",
        headers=request_headers,
    )
    response = pool_manager.request(
        method="GET", url=handler.destination_url, headers=request_headers
    )
    # pretty print response
    pprint(response.headers, sort_dicts=True)

    # Proxy to Control Plane
    forward_proxy_response(handler=handler, response=response)
