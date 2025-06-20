import sys
from src import app


def main():
    try:
        app.run_in_browser()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)