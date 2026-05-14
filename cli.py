import sys

from api.tasks import install_task, update_task


def health_check():
    try:
        with urllib.request.urlopen('http://localhost:5000') as response:
            if response.getcode() != 200:
                print("Health check failed")
            else:
                print("Health check passed")
    except Exception as e:
        print(f"Health check failed: {e}")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python cli.py <update> [options]")
        sys.exit(1)

    switch = {
        "install": install_task,
        "update": update_task,
        "health_check": health_check
    }

    fn = switch.get(sys.argv[1])
    fn()
