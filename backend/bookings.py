"""Persistent local booking store for the Masar web application."""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from backend.paths import DATA_DIR

DB_PATH = DATA_DIR / "masar_bookings.sqlite3"


def _connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY,
            rider_id TEXT NOT NULL,
            rider_name TEXT NOT NULL,
            trip_id TEXT NOT NULL,
            route_code TEXT NOT NULL DEFAULT '',
            origin_name TEXT NOT NULL DEFAULT '',
            destination_name TEXT NOT NULL DEFAULT '',
            origin_sequence INTEGER NOT NULL,
            destination_sequence INTEGER NOT NULL,
            passenger_count INTEGER NOT NULL,
            assistance INTEGER NOT NULL DEFAULT 0,
            payment_method TEXT NOT NULL DEFAULT 'mada',
            eta_minutes INTEGER NOT NULL,
            fare_sar REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            driver_note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    columns = {row[1] for row in connection.execute("PRAGMA table_info(bookings)")}
    if "payment_method" not in columns:
        connection.execute("ALTER TABLE bookings ADD COLUMN payment_method TEXT NOT NULL DEFAULT 'mada'")
    if "route_code" not in columns:
        connection.execute("ALTER TABLE bookings ADD COLUMN route_code TEXT NOT NULL DEFAULT ''")
    if "origin_name" not in columns:
        connection.execute("ALTER TABLE bookings ADD COLUMN origin_name TEXT NOT NULL DEFAULT ''")
    if "destination_name" not in columns:
        connection.execute("ALTER TABLE bookings ADD COLUMN destination_name TEXT NOT NULL DEFAULT ''")
    connection.execute("UPDATE bookings SET fare_sar = ROUND(3.45 * passenger_count, 2) WHERE fare_sar != ROUND(3.45 * passenger_count, 2)")
    return connection


def create_booking(payload: dict) -> dict:
    booking = {
        "id": f"MSR-{uuid.uuid4().hex[:8].upper()}",
        **payload,
        "status": "pending",
        "driver_note": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with _connection() as connection:
        columns = tuple(booking)
        values = ", ".join(f":{column}" for column in columns)
        connection.execute(f"INSERT INTO bookings ({', '.join(columns)}) VALUES ({values})", booking)
    return booking


def list_bookings(rider_id: str | None = None, status: str | None = None) -> list[dict]:
    clauses, values = [], []
    if rider_id:
        clauses.append("rider_id = ?")
        values.append(rider_id)
    if status:
        clauses.append("status = ?")
        values.append(status)
    query = "SELECT * FROM bookings"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY created_at DESC"
    with _connection() as connection:
        return [dict(row) for row in connection.execute(query, values).fetchall()]


def update_booking(booking_id: str, status: str, driver_note: str = "") -> dict | None:
    now = datetime.now(timezone.utc).isoformat()
    with _connection() as connection:
        cursor = connection.execute(
            "UPDATE bookings SET status = ?, driver_note = ?, updated_at = ? WHERE id = ?",
            (status, driver_note.strip(), now, booking_id),
        )
        if cursor.rowcount == 0:
            return None
        return dict(connection.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone())
