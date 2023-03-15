import unittest
from http.server import HTTPServer
from threading import Thread

from proxy.proxy_server import ProxyRequestHandler

SERVER_ADDRESS = ("", 8000)


def is_port_in_use(port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


class TestHandlerBaseClass(unittest.TestCase):
    @classmethod
    def to_proxy_url(cls, repo_url):
        return f"http://localhost:8000/{repo_url.replace('https://', '')}"

    @classmethod
    def setUpClass(cls) -> None:
        if is_port_in_use(SERVER_ADDRESS[1]):
            print(
                f"Proxy server failed to start. Port {SERVER_ADDRESS[1]} is already in use"
            )
        else:
            cls.httpd = HTTPServer(SERVER_ADDRESS, ProxyRequestHandler)
            cls.keep_alive = True

            def server_while():
                while cls.keep_alive:
                    cls.httpd.handle_request()

            cls.server_thread = Thread(target=server_while)
            cls.server_thread.daemon = True
            cls.server_thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.keep_alive = False
        if hasattr(cls, "httpd"):
            cls.httpd.server_close()
