import os
import unittest

from proxy.config import ProxyConfig


class TestProxyConfig(unittest.TestCase):
    def test_proxy_config(self):
        # Log file exist
        assert(os.path.exists(ProxyConfig.LOG_FILE_PATH))
