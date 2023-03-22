import json
import subprocess
import tempfile
from base64 import b64encode, b64decode

from proxy.config import ProxyConfig
from proxy.proxy_server_utils import HEALTH_PATH
from urllib import request

ALLOWED_HEADERS = [
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
]


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
            cmd, shell=True, check=True, capture_output=True, timeout=60
        )
        print(output)


def _to_proxy_url(repo_url):
    return f"http://localhost:8000/{repo_url.replace('https://', '')}"


def test_health_endpoint():
    health_url = _to_proxy_url(HEALTH_PATH)
    response = request.urlopen(url=health_url)
    # parse JSON response to object
    response_data = json.loads(response.read().decode("utf-8"))
    assert response_data["status"] == "ok"
    assert response_data["version"] == ProxyConfig.VERSION
    return response_data


def test_external_clone():
    """Test external clone"""
    clone(
        provider="Github",
        username="dadabricks",
        readonly_token=b64decode(
            b"Z2l0aHViX3BhdF8xMUFORklQNkEwQmtqNjExVUY0NFFOX2JOQ3pWblo0cDhqemhOMXlaYWw1UVRZRnlVeXlUQ2pQN0NQV2FxM3B4SlVZTkxZTTRCQkFxbm5xTUZP"
        ).decode(),
        url=_to_proxy_url("https://github.com/dadabricks/integration-small.git"),
        allowed_headers=ALLOWED_HEADERS,
    )

    clone(
        provider="Azure",
        username="repos.databricks",
        readonly_token=b64decode(
            b"ejV2bjJlNXZtc2FpbmIzbGg2MzJtbWM0M3o1NW5vczRycnc0Z3U3dzZlN3NqNHZ3dDJjYQ=="
        ).decode(),
        url=_to_proxy_url(
            "https://repos-databricks@dev.azure.com/repos-databricks/repos/_git/integration-small"
        ),
        allowed_headers=ALLOWED_HEADERS,
    )

    clone(
        provider="Gitlab",
        username="repos-databricks",
        readonly_token="glpat-bjxsUQhzSt2YBcVXyGd-",
        url=_to_proxy_url("https://gitlab.com/repos-databricks/integration-small.git"),
        # Gitlab will fail with Accept-Encoding header
        allowed_headers=ALLOWED_HEADERS,
    )

    clone(
        provider="BitBucket",
        username="repos-databricks",
        readonly_token="ATBBqBstfPxQRGxGhwmJsZ46HmWx7B32B65E",
        url=_to_proxy_url(
            "https://repos-databricks@bitbucket.org/dadabricks/integration-small.git"
        ),
        allowed_headers=ALLOWED_HEADERS,
    )


def doctor():
    """Check if the proxy server is running"""
    print(ProxyConfig.__dict__)
    try:
        response_data = test_health_endpoint()
        print(f"Proxy server is running, health check passed {response_data}")
    except Exception as e:
        print("Can not connect to proxy server")
        print(e)
        return

    try:
        test_external_clone()
        print(f"External clone passed")
    except Exception as e:
        print("Can not clone external repo")
        print(e)
        return
