import requests
from nxcore.middleware.logging_manager import logger


def get_source_ip():
    """
    Returns the public source IP address of the instance.

    Returns:
        Optional[str]: The public IP address, or None if it cannot be retrieved.
    """
    try:
        ip = requests.get("https://ifconfig.me/ip", timeout=5).text.strip()
        return ip
    except Exception as e:
        logger.error(f"Error getting source IP: {e}")
        return None
