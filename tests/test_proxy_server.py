from base64 import b64decode

from proxy.doctor import clone, ALLOWED_HEADERS
from tests.test_base_cls import TestHandlerBaseClass


class TestProxyRequestHandler(TestHandlerBaseClass):
    def test_clone_github(self):
        clone(
            provider="Github",
            username="dadabricks",
            readonly_token=b64decode(
                b"Z2l0aHViX3BhdF8xMUFORklQNkEwQmtqNjExVUY0NFFOX2JOQ3pWblo0cDhqemhOMXlaYWw1UVRZRnlVeXlUQ2pQN0NQV2FxM3B4SlVZTkxZTTRCQkFxbm5xTUZP"
            ).decode(),
            url=self.to_proxy_url(
                "https://github.com/dadabricks/integration-small.git"
            ),
            allowed_headers=ALLOWED_HEADERS,
        )

    def test_clone_azure(self):
        clone(
            provider="Azure",
            username="repos.databricks",
            readonly_token=b64decode(
                b"ejV2bjJlNXZtc2FpbmIzbGg2MzJtbWM0M3o1NW5vczRycnc0Z3U3dzZlN3NqNHZ3dDJjYQ=="
            ).decode(),
            url=self.to_proxy_url(
                "https://repos-databricks@dev.azure.com/repos-databricks/repos/_git/integration-small"
            ),
            allowed_headers=ALLOWED_HEADERS,
        )

    def test_clone_gitlab(self):
        clone(
            provider="Gitlab",
            username="repos-databricks",
            readonly_token="glpat-bjxsUQhzSt2YBcVXyGd-",
            url=self.to_proxy_url(
                "https://gitlab.com/repos-databricks/integration-small.git"
            ),
            # Gitlab will fail with Accept-Encoding header
            allowed_headers=ALLOWED_HEADERS,
        )

    def test_clone_bitbucket(self):
        clone(
            provider="BitBucket",
            username="repos-databricks",
            readonly_token="ATBBqBstfPxQRGxGhwmJsZ46HmWx7B32B65E",
            url=self.to_proxy_url(
                "https://repos-databricks@bitbucket.org/dadabricks/integration-small.git"
            ),
            allowed_headers=ALLOWED_HEADERS,
        )
