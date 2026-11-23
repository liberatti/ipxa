import pytest

from api.tools.network_tool import NetworkTool


@pytest.mark.unit
class TestNetworkTool:
    @pytest.mark.parametrize(
        "ip,expected",
        [
            ("8.8.8.8", True),
            ("1.1.1.1", True),
            ("127.0.0.1", True),
            ("::1", True),
            ("2001:db8::1", True),
            ("999.999.999.999", False),
            ("8.8.8.8a", False),
            ("invalid_ip", False),
            ("", False),
        ],
    )
    def test_is_host_validation(self, ip: str, expected: bool):
        assert NetworkTool.is_host(ip) is expected

    @pytest.mark.parametrize(
        "network,expected",
        [
            ("192.168.1.0/24", True),
            ("10.0.0.0/8", True),
            ("192.168.1.0/33", False),
            ("invalid/24", False),
        ],
    )
    def test_is_network_validation(self, network: str, expected: bool):
        assert NetworkTool.is_network(network) is expected

    @pytest.mark.parametrize(
        "target,expected",
        [
            ("8.8.8.8", True),
            ("192.168.1.0/24", True),
            ("::1", False),
            ("not-an-ip", False),
        ],
    )
    def test_is_ipv4(self, target: str, expected: bool):
        assert NetworkTool.is_ipv4(target) is expected
