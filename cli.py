import sys

from api.tasks import install_task, update_task

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python cli.py <update> [options]")
        sys.exit(1)

    switch = {"install": install_task, "update": update_task}

    fn = switch.get(sys.argv[1])
    fn()
