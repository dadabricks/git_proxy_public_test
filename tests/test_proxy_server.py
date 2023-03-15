import subprocess
import tempfile
from base64 import b64encode

from tests.test_base_cls import TestHandlerBaseClass


def build_git_clone_commands(repo_url: str, username: str, token: str, path: str):
    allowed_headers = [
        "Accept",
        "Accept-Encoding",
        "Accept-Language",
        "Cache-Control",
        "Connection",
        "Content-Encoding",
        "Content-Type",
        "Pragma",
        "User-Agent",
        "git-protocol",
    ]
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


def clone(provider: str, username: str, readonly_token: str, url: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing Provider: {provider}")
        commands = build_git_clone_commands(
            repo_url=url,
            username=username,
            token=readonly_token,
            path=temp_dir,
        )
        cmd = [" ".join(commands)]
        print(cmd)
        output = subprocess.run(cmd, shell=True, check=True, capture_output=True)
        print(output)


class TestProxyRequestHandler(TestHandlerBaseClass):
    def test_clone_github(self):
        clone(
            provider="Github",
            username="dadabricks",
            readonly_token="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",
            url=self.to_proxy_url(
                "https://github.com/dadabricks/integration-small.git"
            ),
        )

    def test_clone_azure(self):
        clone(
            provider="Azure",
            username="repos.databricks",
            readonly_token="7aaegeltki5gngjrxptf2km4yfhdesz5tsnoi6df65cswyrlzoxa",
            url=self.to_proxy_url(
                "https://repos-databricks@dev.azure.com/repos-databricks/repos/_git/integration-small"
            ),
        )

    # TODO: Fix this test
    # def test_clone_gitlab(self):
    #     clone(
    #         provider="Gitlab",
    #         username="repos-databricks",
    #         readonly_token="glpat-bjxsUQhzSt2YBcVXyGd-",
    #         url=self.to_proxy_url(
    #             "https://gitlab.com/repos-databricks/integration-small.git"
    #         ),
    #     )

    def test_clone_bitbucket(self):
        clone(
            provider="BitBucket",
            username="repos-databricks",
            readonly_token="ATBBqBstfPxQRGxGhwmJsZ46HmWx7B32B65E",
            url=self.to_proxy_url(
                "https://repos-databricks@bitbucket.org/dadabricks/integration-small.git"
            ),
        )
