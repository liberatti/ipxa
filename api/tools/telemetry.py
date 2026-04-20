
import uuid
import requests
from config import SUPABASE_KEY, SUPABASE_URL, APP_VERSION, TELEMETRY_ENABLE
from basic4web.middleware.logging import logger
from api.repository.workspace_model import WorkspaceDao
global hits
hits = 0


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


def register_instance(workspace):
    """
    Registers the instance with the telemetry server.

    Args:
        workspace (dict): The workspace configuration containing 'instance_uid'.
    """
    if not TELEMETRY_ENABLE:
        return
    try:
        requests.post(
            f"{SUPABASE_URL}/ipxa_instances",
            json={
                "instance_uid": workspace['instance_uid'],
                "source_ip": get_source_ip(),
                "version": APP_VERSION.replace("v", "")
            },
            headers={
                "apikey": SUPABASE_KEY
            },
            timeout=10
        )
        logger.info(f"Instance registered successfully with id: {workspace['instance_uid']}")
    except Exception as e:
        logger.error(f"Error registering instance: {e}")


def send_telemetry():
    """
    Sends collected metrics (hits) to the telemetry server.
    """
    global hits
    if not TELEMETRY_ENABLE:
        return
    hd = hits
    hits = 0
    with WorkspaceDao() as dao:
        workspace = dao.get_first()
    if workspace:
        try:
            requests.post(
                f"{SUPABASE_URL}/ipxa_metrics",
                json={
                    "instance_uid": workspace['instance_uid'],
                    "hits": hd
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
    Increments the global hit counter.
    """
    global hits
    hits += 1
