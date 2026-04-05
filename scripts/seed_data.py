import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import initialize_database
from app.services.seed import ensure_seed_data


def main() -> None:
    initialize_database()
    ensure_seed_data()
    print("Seed data is ready in data/stocks.db")


if __name__ == "__main__":
    main()
