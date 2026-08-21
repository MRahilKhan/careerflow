from pathlib import Path

from alembic import command
from alembic.config import Config


BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    config = Config(str(BASE_DIR / "alembic.ini"))
    command.upgrade(config, "head")


if __name__ == "__main__":
    main()
