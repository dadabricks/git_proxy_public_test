import subprocess
import tempfile
from base64 import b64encode, b64decode

from tests.test_base_cls import TestHandlerBaseClass


def build_git_clone_commands(
    repo_url: str, username: str, token: str, path: str, allowed_headers: list
):
    allowed_headers_config = f'''http.extraHeader="x-databricks-allowed-headers:{','.join(allowed_headers)}"'''
    basic_auth_token = b64encode(bytes(username + ":" + token, "ascii")).decode("ascii")
    forward_headers_config = f'http.extraHeader=x-databricks-forward-header-Authorization:"Basic {basic_auth_token}"'
    commands = [
        "GIT_CURL_VERBOSE=1",
        "git",
        "clone",
        "-c",
        allowed_headers_config,
        "-c",
        forward_headers_config,
        repo_url,
        path,
    ]
    return commands


def clone(
    provider: str, username: str, readonly_token: str, url: str, allowed_headers: list
):
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing Provider: {provider}")
        commands = build_git_clone_commands(
            repo_url=url,
            username=username,
            token=readonly_token,
            path=temp_dir,
            allowed_headers=allowed_headers,
        )
        cmd = [" ".join(commands)]
        print(cmd)
        output = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, timeout=10
        )
        print(output)


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
            allowed_headers=[
                "Accept",
                "Accept-Encoding",
                "Accept-Language",
                "Cache-Control",
                "Connection",
                "Content-Encoding",
                "Content-Length",
                "Content-Type",
                "Pragma",
                "User-Agent",
                "git-protocol",
            ],
        )

    def test_clone_azure(self):
        clone(
            provider="Azure",
            username="repos.databricks",
            readonly_token="7aaegeltki5gngjrxptf2km4yfhdesz5tsnoi6df65cswyrlzoxa",
            url=self.to_proxy_url(
                "https://repos-databricks@dev.azure.com/repos-databricks/repos/_git/integration-small"
            ),
            allowed_headers=[
                "Accept",
                "Accept-Encoding",
                "Accept-Language",
                "Cache-Control",
                "Connection",
                "Content-Encoding",
                "Content-Length",
                "Content-Type",
                "Pragma",
                "User-Agent",
                "git-protocol",
            ],
        )

    # TODO: Fix this test
    def test_clone_gitlab(self):
        clone(
            provider="Gitlab",
            username="repos-databricks",
            readonly_token="glpat-bjxsUQhzSt2YBcVXyGd-",
            url=self.to_proxy_url(
                "https://gitlab.com/repos-databricks/integration-small.git"
            ),
            # Gitlab will fail with Accept-Encoding header
            allowed_headers=[
                "Accept",
                "Accept-Language",
                "Cache-Control",
                "Connection",
                "Content-Encoding",
                "Content-Length",
                "Content-Type",
                "Pragma",
                "User-Agent",
                "git-protocol",
            ],
        )

    def test_clone_bitbucket(self):
        clone(
            provider="BitBucket",
            username="repos-databricks",
            readonly_token="ATBBqBstfPxQRGxGhwmJsZ46HmWx7B32B65E",
            url=self.to_proxy_url(
                "https://repos-databricks@bitbucket.org/dadabricks/integration-small.git"
            ),
            allowed_headers=[
                "Accept",
                "Accept-Encoding",
                "Accept-Language",
                "Cache-Control",
                "Connection",
                "Content-Encoding",
                "Content-Length",
                "Content-Type",
                "Pragma",
                "User-Agent",
                "git-protocol",
            ],
        )
