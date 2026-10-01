import sys
import requests
from api.tasks import install_task, update_task
import config


def health_check():

    try:
        response = requests.get(f"http://localhost:5000{config.APP_CONTEXT}", timeout=5)
        if response.status_code == 200:
            sys.exit(0)
        else:
            print(f"Health check failed with status: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python cli.py <update> [options]")
        sys.exit(1)

    switch = {
        "install": install_task,
        "update": update_task,
        "health_check": health_check,
    }

    fn = switch.get(sys.argv[1])
    fn()
