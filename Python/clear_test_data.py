"""Delete only temporary TEST data from the local SQLite database."""

from database import get_connection, init_db


def main() -> None:
    init_db()
    conn = get_connection()
    try:
        measurements = conn.execute(
            "DELETE FROM measurements WHERE source = ?",
            ("TEST",),
        ).rowcount

        events = conn.execute(
            """
            DELETE FROM events
            WHERE detail = ?
               OR event_type = ?
            """,
            ("Temporary TEST protocol", "TEST_ERROR"),
        ).rowcount

        conn.commit()
        print(f"Deleted TEST measurements: {measurements}")
        print(f"Deleted TEST events: {events}")
        print("Cleanup completed.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
