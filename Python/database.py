from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

PYTHON_DIR = Path(__file__).resolve().parent
DB_PATH = PYTHON_DIR / "fiber_analyzer.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS system_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                updated_at TEXT NOT NULL,
                connection TEXT NOT NULL DEFAULT 'DISCONNECTED',
                adc_status TEXT NOT NULL DEFAULT 'UNKNOWN',
                dac_status TEXT NOT NULL DEFAULT 'UNKNOWN',
                serial_status TEXT NOT NULL DEFAULT 'IDLE'
            )
            '''
        )

        conn.execute(
            '''
            INSERT INTO system_state (
                id, updated_at, connection, adc_status, dac_status, serial_status
            )
            VALUES (1, datetime('now', 'localtime'), 'DISCONNECTED', 'UNKNOWN', 'UNKNOWN', 'IDLE')
            ON CONFLICT(id) DO NOTHING
            '''
        )

        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                adc12 INTEGER,
                adc13 INTEGER,
                dac1 INTEGER,
                dac2 INTEGER,
                source TEXT NOT NULL DEFAULT 'STM32'
            )
            '''
        )

        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                value TEXT,
                detail TEXT
            )
            '''
        )

        conn.commit()
    finally:
        conn.close()


def get_status() -> Optional[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM system_state WHERE id = 1"
        ).fetchone()
    finally:
        conn.close()


def get_measurements(limit: int = 20):
    limit = max(1, min(int(limit), 200))
    conn = get_connection()
    try:
        return conn.execute(
            '''
            SELECT id, timestamp, adc12, adc13, dac1, dac2, source
            FROM measurements
            ORDER BY id DESC
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()
    finally:
        conn.close()


def get_events(limit: int = 20):
    limit = max(1, min(int(limit), 200))
    conn = get_connection()
    try:
        return conn.execute(
            '''
            SELECT id, timestamp, event_type, value, detail
            FROM events
            ORDER BY id DESC
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()
    finally:
        conn.close()
def update_system_state(
    connection: str,
    adc_status: str,
    dac_status: str,
    serial_status: str,
    updated_at: str | None = None,
) -> None:
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO system_state(
                id,
                updated_at,
                connection,
                adc_status,
                dac_status,
                serial_status
            )
            VALUES(
                1,
                COALESCE(?, datetime('now', 'localtime')),
                ?,
                ?,
                ?,
                ?
            )
            ON CONFLICT(id) DO UPDATE SET
                updated_at = excluded.updated_at,
                connection = excluded.connection,
                adc_status = excluded.adc_status,
                dac_status = excluded.dac_status,
                serial_status = excluded.serial_status
            """,
            (
                updated_at,
                connection,
                adc_status,
                dac_status,
                serial_status,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def insert_measurement(
    adc12: int | None,
    adc13: int | None,
    dac1: int | None,
    dac2: int | None,
    source: str = "STM32",
    timestamp: str | None = None,
) -> None:

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO measurements(
                timestamp,
                adc12,
                adc13,
                dac1,
                dac2,
                source
            )
            VALUES(
                COALESCE(?, datetime('now', 'localtime')),
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                timestamp,
                adc12,
                adc13,
                dac1,
                dac2,
                source,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def insert_event(
    event_type: str,
    value: str | None = None,
    detail: str | None = None,
    timestamp: str | None = None,
) -> None:

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO events(
                timestamp,
                event_type,
                value,
                detail
            )
            VALUES(
                COALESCE(?, datetime('now', 'localtime')),
                ?,
                ?,
                ?
            )
            """,
            (
                timestamp,
                event_type,
                value,
                detail,
            ),
        )

        conn.commit()

    finally:
        conn.close()