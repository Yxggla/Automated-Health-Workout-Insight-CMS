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
        CREATE TABLE IF NOT EXISTS derived_metrics (
            metric_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            fat_percentage REAL,
            water_intake REAL,
            lean_mass_kg REAL,
            cal_balance REAL,
            FOREIGN KEY (user_id) REFERENCES user(user_id)
        );
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            age REAL,
            gender TEXT,
            weight REAL,
            height REAL,
            bmi REAL,
            fat_percentage REAL,
            lean_mass_kg REAL,
            experience_level TEXT,
            workout_frequency REAL,
            water_intake REAL,
            resting_bpm REAL    
        );
        CREATE TABLE IF NOT EXISTS workouts (
            workout_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            workout_type TEXT,
            session_duration REAL,
            calories_burned REAL,
            max_bpm REAL,
            avg_bpm REAL,
            resting_bpm REAL,
            name_of_exercise TEXT,
            sets REAL,
            reps REAL,
            target_muscle_group TEXT,
            equipment_needed TEXT,
            difficulty_level TEXT,
            body_part TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        CREATE TABLE IF NOT EXISTS nutrition (
            nutrition_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            daily_meals_frequency REAL,
            carbs REAL,
            proteins REAL,
            fats REAL,
            calories REAL,
            meal_name TEXT,
            meal_type TEXT,
            diet_type TEXT,
            sugar_g REAL,
            sodium_mg REAL,
            cholesterol_mg REAL,
            serving_size_g REAL,
            cooking_method TEXT,
            prep_time_min REAL,
            cook_time_min REAL,
            rating REAL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        CREATE TABLE IF NOT EXISTS workout_analysis (
            analysis_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            pct_hrr REAL,
            pct_maxhr REAL,
            cal_balance REAL,
            expected_burn REAL,
            benefit TEXT,
            burns_calories_per_30min REAL,
            type_of_muscle TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        CREATE TABLE IF NOT EXISTS templates (
            template_id INTEGER PRIMARY KEY,
            template_name TEXT,
            template_text TEXT
        );
        """
        with self.conn:
            self.conn.executescript(schema)
        
        # 添加新增的分析指标字段
        self._add_analysis_columns()

    def _add_analysis_columns(self) -> None:
        """为 workout_analysis 表添加分析指标字段"""
        try:
            with self.conn:
                # 检查并添加 training_efficiency 列
                self.conn.execute("""
                    ALTER TABLE workout_analysis ADD COLUMN training_efficiency REAL
                """)
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        try:
            with self.conn:
                # 检查并添加 muscle_focus_score 列
                self.conn.execute("""
                    ALTER TABLE workout_analysis ADD COLUMN muscle_focus_score REAL
                """)
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        try:
            with self.conn:
                # 检查并添加 recovery_index 列
                self.conn.execute("""
                    ALTER TABLE workout_analysis ADD COLUMN recovery_index REAL
                """)
        except sqlite3.OperationalError:
            pass  # 列已存在

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
