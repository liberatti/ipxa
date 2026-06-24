import threading

from nxcore.middleware.logging import logger

import config as _config

stop_event = threading.Event()


def when_ready(server):
    """
    Gunicorn hook called when the server is ready to handle requests.

    Args:
        server: The Gunicorn server instance.
    """
    logger.info("IPXa started.")


def on_reload(server):
    """
    Gunicorn hook called before reloading the server.

    Args:
        server: The Gunicorn server instance.
    """
    stop_event.set()
    when_ready(server)


def on_exit(server):
    """
    Gunicorn hook called when the server is exiting.

    Args:
        server: The Gunicorn server instance.
    """
    stop_event.set()
    logger.info("IPXa stopped")


workers = _config.WORKERS
threads = _config.THREADS
preload_app = False
bind = "0.0.0.0:5000"
accesslog = "-" if _config.LOGLEVEL in ["DEBUG", "INFO"] else None
errorlog = "-"
loglevel = _config.LOGLEVEL
