
import uuid
import requests
from config import SUPABASE_KEY, SUPABASE_URL, APP_VERSION
from basic4web.middleware.logging import logger
from api.repository.workspace_model import WorkspaceDao
from config import tlc


def get_instance_uid():
    """
    Returns a unique identifier for the instance.

    Returns:
        str: A unique identifier (UUID string).
    """
    return str(uuid.uuid4())


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


def send_telemetry():
    """
    Sends collected metrics (hits) to the telemetry server.
    """
    hd = tlc.get('hits', 0)
    tlc['hits'] = 0
    with WorkspaceDao() as dao:
        workspace = dao.get_first()
        try:
            if workspace:
                requests.post(
                    f"{SUPABASE_URL}/ipxa_metrics",
                    json={
                        "instance_uid": workspace['instance_uid'],
                        "hits": hd,
                        "source_ip": get_source_ip(),
                        "version": APP_VERSION.replace("v", "")
                    },
                    headers={
                        "apikey": SUPABASE_KEY
                    },
                    timeout=10
                )
                logger.info(f"Telemetry sent successfully with data: {workspace['instance_uid']}:{hd}")
        except Exception as e:
            logger.error(f"Error sending telemetry: {e}")


def register_hit():
    """
    Increments the hit counter.
    """
    tlc['hits'] = tlc.get('hits', 0) + 1
