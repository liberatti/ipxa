import ipaddress
import socket
from typing import List, Optional

from basic4web.middleware.logging import logger


class NetworkTool:

    @classmethod
    def nslookup(cls, ns: str) -> Optional[str]:
        """
        Performs a DNS lookup to resolve a hostname to an IP address.

        Args:
            ns (str): The hostname to resolve.

        Returns:
            Optional[str]: The resolved IP address, or None if resolution fails.
        """
        try:
            return socket.gethostbyname(ns)
        except socket.gaierror as e:
            logger.error(f"Name resolution failed for '{ns}': {e}")
            return None

    @classmethod
    def is_host(cls, ip: str) -> bool:
        """
        Checks if a string represents a valid IP address.

        Args:
            ip (str): The IP address string to check.

        Returns:
            bool: True if it is a valid IP address, False otherwise.
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except Exception:
            return False

    @classmethod
    def is_network(cls, net: str) -> bool:
        """
        Checks if a string represents a valid network (CIDR notation).

        Args:
            net (str): The network string to check.

        Returns:
            bool: True if it is a valid network, False otherwise.
        """
        try:
            ipaddress.ip_network(net, strict=False)
            return True
        except ipaddress.NetmaskValueError:
            return False
        except ValueError:
            return False

    @classmethod
    def aggregate(cls, addr_list: List[str]) -> List[str]:
        """
        Aggregates a list of IP addresses or networks into a minimal list of CIDR networks.

        Args:
            addr_list (List[str]): List of IP addresses or network strings.

        Returns:
            List[str]: List of aggregated CIDR network strings.
        """
        nets = [ipaddress.ip_network(ip) for ip in addr_list]
        nets = set(nets)
        nets = sorted(nets, key=lambda n1: n1.prefixlen)
        uq_nets = []
        while nets:
            n = nets.pop(0)
            if not any(n.subnet_of(un) for un in uq_nets):
                uq_nets.append(n)
        return [str(r) for r in uq_nets]

    @classmethod
    def hosts_from_net(cls, masked_ip: str) -> List[str]:
        """
        Returns a list of all host IP addresses within a given network.

        Args:
            masked_ip (str): The network in CIDR notation.

        Returns:
            List[str]: A list of host IP addresses.
        """
        try:
            network = ipaddress.IPv4Network(masked_ip, strict=False)
            return [str(ip) for ip in network.hosts()]
        except Exception as e:
            logger.error(f"Failed to get hosts from network {masked_ip}: {e}")
            return []

    @classmethod
    def is_ipv4(cls, ip: str) -> bool:
        """
        Checks if an IP address or network string is IPv4.

        Args:
            ip (str): The IP address or network string.

        Returns:
            bool: True if it is IPv4, False otherwise.
        """
        try:
            return ipaddress.ip_network(ip, strict=False).version == 4
        except Exception:
            return False

    @classmethod
    def expand_ip(cls, ip):
        """
        Expands an IP address to its full representation (e.g., zero-filled for IPv4).

        Args:
            ip (str): The IP address to expand.

        Returns:
            str: The expanded IP address string.
        """
        if cls.is_ipv4(ip):
            parts = ip.split(".")
            parts_with_zero = [part.zfill(3) for part in parts]
            return ".".join(parts_with_zero)
        return str(ipaddress.ip_address(ip).exploded)

    @classmethod
    def calc_len_from_network(cls, addr: str, netmask: str) -> int:
        """
        Calculates the prefix length from an IP address and a netmask.

        Args:
            addr (str): The IP address.
            netmask (str): The netmask.

        Returns:
            int: The prefix length.
        """
        return ipaddress.ip_network(f"{addr}/{netmask}", strict=False).prefixlen

    @classmethod
    def extract_network_info(cls, addr, prefix=32) -> dict:
        """
        Extracts detailed information about a network given an address and prefix.

        Args:
            addr (str): The network address.
            prefix (int, optional): The prefix length. Defaults to 32.

        Returns:
            dict: A dictionary containing network information (prefix, version, network, broadcast, etc.).
        """
        net = f"{addr}/{prefix}"
        i = {
            "prefix": prefix,
            "version": 6
        }
        if cls.is_ipv4(net):
            i.update({"version": 4})
            rede = ipaddress.IPv4Network(net, strict=False)
        else:
            rede = ipaddress.IPv6Network(net, strict=False)
        i.update({
            "network": str(rede.network_address),
            "broadcast": str(rede.broadcast_address),
            "idx_s": rede.network_address.packed,
            "idx_e": rede.broadcast_address.packed
        })
        return i

    @classmethod
    def calc_prefix_from_range(cls, addr_ini, addr_end):
        """
        Calculates the prefix length for a range of IP addresses.

        Args:
            addr_ini (ipaddress.IPv4Address or ipaddress.IPv6Address): Start IP address.
            addr_end (ipaddress.IPv4Address or ipaddress.IPv6Address): End IP address.

        Returns:
            int: The prefix length.

        Raises:
            ValueError: If addr_ini is greater than addr_end or version is unsupported.
        """
        addr_total = int(addr_end) - int(addr_ini) + 1
        if addr_total <= 0:
            raise ValueError(f"{addr_ini} is greater than {addr_end}")
        num_bits = addr_total - 1
        if addr_ini.version == 4:
            prefix = 32 - num_bits.bit_length()
        elif addr_ini.version == 6:
            prefix = 128 - num_bits.bit_length()
        else:
            raise ValueError("Unsupported IP version")
        return prefix
<<<<<<< HEAD

    @classmethod
    def in_network(cls, ip: str, ignore_list: str) -> bool:
        """
        Checks if an IP address is within any of the networks in the ignore list.

        Args:
            ip (str): The IP address to check.
            ignore_list (str): Comma-separated list of networks in CIDR notation.

        Returns:
            bool: True if the IP is within any of the networks, False otherwise.
        """
        for net in ignore_list.split(","):
            if ipaddress.ip_network(net.strip(), strict=False).overlaps(ipaddress.ip_network(ip, strict=False)):
                return True
        return False
=======
>>>>>>> main
