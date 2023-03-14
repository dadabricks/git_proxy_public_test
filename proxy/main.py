from http.server import HTTPServer

from proxy.config import ProxyConfig
from proxy.handlers.utils.logger import log_message
from proxy.proxy_server import ProxyRequestHandler


def main():
    server_address = ("", ProxyConfig.PORT)
    log_message(
        f"Data-plane proxy server version {ProxyConfig.VERSION} binding to {server_address} ..."
    )
    log_message(f"ProxyConfig {ProxyConfig.__dict__}")
    httpd = HTTPServer(server_address, ProxyRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
