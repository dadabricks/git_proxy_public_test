import json
from urllib import request

from proxy.config import ProxyConfig
from proxy.proxy_server_utils import DB_VERSION_HEADER_KEY, HEALTH_PATH

from tests.test_base_cls import TestHandlerBaseClass


class TestHealthHandler(TestHandlerBaseClass):
#     def test_version_header(self):
#         example_url = self.to_proxy_url("https://example.com/")
#         response = request.urlopen(url=example_url)
#         assert response.headers.get(DB_VERSION_HEADER_KEY) == ProxyConfig.VERSION

    def test_health_endpoint(self):
        health_url = self.to_proxy_url(HEALTH_PATH)
        response = request.urlopen(url=health_url)
        # parse JSON response to object
        response_data = json.loads(response.read().decode("utf-8"))
        assert response_data["status"] == "ok"
        assert response_data["version"] == ProxyConfig.VERSION
