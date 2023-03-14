import urllib3

from proxy.config import ProxyConfig
from proxy.handlers.health_get_handler import do_health
from proxy.handlers.log_get_handler import do_log

DB_VERSION_HEADER_KEY = "X-Databricks-Proxy-Server-Version"
HEALTH_PATH = "/databricks/health"
LOG_PATH = "/databricks/logs"


def get_pool_manager():
    _pool_manager_config = {}
    if ProxyConfig.ENABLE_SSL_VERIFICATION is False:
        _pool_manager_config["cert_reqs"] = "CERT_NONE"
    elif ProxyConfig.CA_CERT_PATH:
        _pool_manager_config["ca_certs"] = ProxyConfig.CA_CERT_PATH
    return urllib3.PoolManager(**_pool_manager_config)


def get_path_to_handler():
    path_to_handler = {
        HEALTH_PATH: do_health,
    }
    if ProxyConfig.ENABLE_LOGGING:
        path_to_handler[LOG_PATH] = do_log
    return path_to_handler
