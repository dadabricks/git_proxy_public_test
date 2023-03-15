from http.server import BaseHTTPRequestHandler

from urllib3.request import RequestMethods

from proxy.config import ProxyConfig
from proxy.handlers.utils.handler_utils import (
    set_status_code,
    set_headers,
    set_binary_body,
)
from proxy.handlers.utils.logger import log_headers, log_message
from proxy.proxy_server_utils import DB_VERSION_HEADER_KEY


# Disable chunking
def disable_chunking_headers(headers):
    for k, v in headers.items():
        if k.lower() == "transfer-encoding":
            headers[k] = "identity"
        if k.lower() == "connection":
            headers[k] = "close"
    return headers


def copy_request_headers(headers, allowed_list=[]):
    lowercase_allowed_list = [x.lower() for x in allowed_list]
    copied_headers = {}
    for header_key, header_value in headers.items():
        if header_key.lower() in lowercase_allowed_list:
            copied_headers[header_key] = header_value
    return disable_chunking_headers(copied_headers)


def copy_response_headers(headers):
    copied_headers = {}
    for header_key, header_value in headers.items():
        if header_key.lower() != "Content-Encoding".lower():
            copied_headers[header_key] = header_value
    return disable_chunking_headers(copied_headers)


DB_FORWARD_HEADER_PREFIX = "x-databricks-forward-header-"
DB_FORWARD_HEADER_KEYS = "x-databricks-allowed-headers"

DELIMITER = ","


def copy_header_proxy_for_destination(headers):
    allowed_header_keys = []
    if DB_FORWARD_HEADER_KEYS in headers:
        allowed_header_value = headers[DB_FORWARD_HEADER_KEYS]
        for allowed_header_key in allowed_header_value.split(DELIMITER):
            allowed_header_keys.append(allowed_header_key)
    response_headers = copy_request_headers(headers, allowed_list=allowed_header_keys)

    new_headers = {}
    for header_key in headers.keys():
        if header_key.lower().startswith(DB_FORWARD_HEADER_PREFIX):
            new_header_key = header_key[len(DB_FORWARD_HEADER_PREFIX):]
            if len(new_header_key):
                new_headers[new_header_key] = headers[header_key]

    # Forward headers always supersede strip headers
    response_headers.update(new_headers)

    for org_key in headers.keys():
        if org_key not in response_headers:
            log_message("Stripped header: {}".format(org_key))

    if "Accept-Encoding" in response_headers:
        del response_headers["Accept-Encoding"]
    return response_headers


# Forward response from destination to control plane
def forward_proxy_response(handler: BaseHTTPRequestHandler, response: RequestMethods):
    set_status_code(code=response.status, handler=handler)
    response_headers = copy_response_headers(response.headers)
    response_headers[DB_VERSION_HEADER_KEY] = ProxyConfig.VERSION
    set_headers(headers=response_headers, handler=handler)
    log_headers(message="Forward headers", headers=handler.headers)
    set_binary_body(data=response.data, handler=handler)
