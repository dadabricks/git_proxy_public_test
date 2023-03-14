from http.server import BaseHTTPRequestHandler

from proxy.handlers.proxy_get_handler import do_proxy_get
from proxy.handlers.proxy_post_handler import do_proxy_post
from proxy.handlers.utils.handler_utils import get_route_handler
from proxy.handlers.utils.logger import log_message, log_headers
from proxy.proxy_server_utils import get_pool_manager, get_path_to_handler

http = get_pool_manager()


class ProxyRequestHandler(BaseHTTPRequestHandler):
    @property
    def destination_url(self):
        return "https:/{}".format(self.path)

    def do_GET(self):
        log_message(f"do_GET: {self.destination_url}")
        log_headers(message="Incoming GET headers", headers=self.headers)
        matched_handler = get_route_handler(
            path=self.path,
            path_to_handler=get_path_to_handler(),
        )
        if matched_handler:
            return matched_handler(self)
        do_proxy_get(handler=self, pool_manager=http)

    def do_POST(self):
        log_message(f"do_POST: {self.destination_url}")
        log_headers(message="Incoming POST headers", headers=self.headers)
        do_proxy_post(handler=self, pool_manager=http)

    def do_HEAD(self):
        log_message(f"do_HEAD: {self.destination_url}")
        raise Exception(f"HEAD not supported {self.destination_url}")
