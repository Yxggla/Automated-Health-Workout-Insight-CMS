import sqlite3
from contextlib import closing
from typing import Iterable, List, Sequence


class DatabaseManager:
    """Lightweight SQLite helper for schema creation and simple CRUD."""

    def __init__(self, db_path: str = "fitness.db") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def create_tables(self) -> None:
        """Create required tables if they do not exist."""
        schema = """
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY,
            gender TEXT,
            age REAL,
            height REAL,
            weight REAL,
            bmi REAL
        );
        CREATE TABLE IF NOT EXISTS workout (
            workout_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            workout_type TEXT,
            session_duration REAL,
            calories_burned REAL,
            max_bpm REAL,
            avg_bpm REAL,
            resting_bpm REAL,
            FOREIGN KEY (user_id) REFERENCES user(user_id)
        );
        CREATE TABLE IF NOT EXISTS nutrition (
            nutrition_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            carbs REAL,
            proteins REAL,
            fats REAL,
            sugar_g REAL,
            sodium_mg REAL,
            calories_intake REAL,
            FOREIGN KEY (user_id) REFERENCES user(user_id)
        );
        CREATE TABLE IF NOT EXISTS derived_metrics (
            metric_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            fat_percentage REAL,
            water_intake REAL,
            lean_mass_kg REAL,
            cal_balance REAL,
            FOREIGN KEY (user_id) REFERENCES user(user_id)
        );
        CREATE TABLE IF NOT EXISTS templates (
            template_id INTEGER PRIMARY KEY,
            template_name TEXT,
            template_text TEXT
        );
        """
        with self.conn:
            self.conn.executescript(schema)

    def execute(
        self,
        sql: str,
        params: Sequence = (),
        fetchone: bool = False,
        fetchall: bool = False,
    ):
        """Run a SQL statement, optionally returning rows."""
        cur = self.conn.execute(sql, params)
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()
        return cur

    def executemany(self, sql: str, rows: Iterable[Sequence]) -> None:
        with self.conn:
            self.conn.executemany(sql, rows)

    def insert_many(self, table: str, columns: List[str], rows: Iterable[Sequence]) -> None:
        placeholders = ", ".join(["?"] * len(columns))
        cols = ", ".join(columns)
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        self.executemany(sql, rows)

    def truncate_tables(self, tables: Sequence[str]) -> None:
        with self.conn:
            for table in tables:
                self.conn.execute(f"DELETE FROM {table}")

    def close(self) -> None:
        with closing(self.conn):
            self.conn.close()
