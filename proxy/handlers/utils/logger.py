import logging
from pathlib import Path

from proxy.config import ProxyConfig

# Make LOG_FILE_PATH directory if it doesn't exist
Path(ProxyConfig.LOG_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(ProxyConfig.LOG_FILE_PATH),
        logging.StreamHandler(),
    ],
)


def log_message(message):
    logger.info(f"Version: {ProxyConfig.VERSION} {message}")


def log_headers(message: str = "", headers: dict = {}):
    _HEADER_DENY_LIST = set("authorizations")
    header_strs = []
    for k, v in headers.items():
        if k.lower() not in _HEADER_DENY_LIST:
            header_strs.append(f"{k}: {v}")
    header_str = " ".join(header_strs)
    logger.info(
        f"Version: {ProxyConfig.VERSION} Message: {message} Headers: {header_str}",
    )
