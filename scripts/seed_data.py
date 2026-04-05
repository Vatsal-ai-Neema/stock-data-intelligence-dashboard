from app.database import initialize_database
from app.services.seed import ensure_seed_data


def main() -> None:
    initialize_database()
    ensure_seed_data()
    print("Seed data is ready in data/stocks.db")


if __name__ == "__main__":
    main()
