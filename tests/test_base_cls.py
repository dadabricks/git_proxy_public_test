import unittest
from http.server import HTTPServer
from threading import Thread

from proxy.proxy_server import ProxyRequestHandler

SERVER_ADDRESS = ("", 8000)


class TestHandlerBaseClass(unittest.TestCase):
    @classmethod
    def to_proxy_url(cls, repo_url):
        return f"http://localhost:8000/{repo_url.replace('https://', '')}"

    @classmethod
    def setUpClass(cls) -> None:
        cls.httpd = HTTPServer(SERVER_ADDRESS, ProxyRequestHandler)
        cls.server_thread = Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.httpd.shutdown()
