import os
import tempfile
from distutils.util import strtobool


class ProxyConfig:
    VERSION = "0.0.14"
    PORT = os.environ.get("PROXY_PORT", 8000)
    LOG_FILE_PATH = os.environ.get(
        "LOG_FILE_PATH", tempfile.NamedTemporaryFile(delete=False).name
    )
    ENABLE_SSL_VERIFICATION = strtobool(
        os.environ.get("ENABLE_SSL_VERIFICATION", "True")
    )
    ENABLE_LOGGING = strtobool(os.environ.get("ENABLE_DB_REPOS_PROXY", "False"))
    CA_CERT_PATH = os.environ.get("CA_CERT_PATH", "")
