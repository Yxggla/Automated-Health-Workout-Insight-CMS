from pathlib import Path
from typing import Dict, List

import pandas as pd

from database import DatabaseManager


class DataImporter:
    """Import and normalize the Kaggle CSV into the SQLite schema."""

    COLUMN_MAP: Dict[str, str] = {
        "Age": "age",
        "Gender": "gender",
        "Height (m)": "height",
        "Weight (kg)": "weight",
        "BMI": "bmi",
        "Workout_Type": "workout_type",
        "Session_Duration (hours)": "session_duration",
        "Calories_Burned": "calories_burned",
        "Max_BPM": "max_bpm",
        "Avg_BPM": "avg_bpm",
        "Resting_BPM": "resting_bpm",
        "Carbs": "carbs",
        "Proteins": "proteins",
        "Fats": "fats",
        "sugar_g": "sugar_g",
        "sodium_mg": "sodium_mg",
        "Calories": "calories_intake",
        "Fat_Percentage": "fat_percentage",
        "Water_Intake (liters)": "water_intake",
        "lean_mass_kg": "lean_mass_kg",
        "cal_balance": "cal_balance",
    }

    REQUIRED_FIELDS: List[str] = list(COLUMN_MAP.values())

    def __init__(self, db: DatabaseManager):
        self.db = db

    def import_csv(self, csv_path: str = "Final_data.csv", clear_existing: bool = True) -> int:
        """Read the CSV, normalize columns, and insert into tables. Returns row count."""
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        df = pd.read_csv(path)
        df = df.rename(columns=self.COLUMN_MAP)

        for numeric_col in [
            "age",
            "height",
            "weight",
            "bmi",
            "session_duration",
            "calories_burned",
            "max_bpm",
            "avg_bpm",
            "resting_bpm",
            "carbs",
            "proteins",
            "fats",
            "sugar_g",
            "sodium_mg",
            "calories_intake",
            "fat_percentage",
            "water_intake",
            "lean_mass_kg",
            "cal_balance",
        ]:
            if numeric_col in df.columns:
                df[numeric_col] = pd.to_numeric(df[numeric_col], errors="coerce")
            else:
                df[numeric_col] = pd.NA

        for text_col in ["gender", "workout_type"]:
            if text_col not in df.columns:
                df[text_col] = ""

        df = df[self.REQUIRED_FIELDS]
        df = df.fillna(pd.NA)

        if clear_existing:
            self.db.truncate_tables(["user", "workout", "nutrition", "derived_metrics"])

        user_rows = []
        workout_rows = []
        nutrition_rows = []
        metrics_rows = []

        for idx, row in df.iterrows():
            user_id = idx + 1  # deterministic pseudo user id per row
            user_rows.append(
                (
                    user_id,
                    row.get("gender"),
                    row.get("age"),
                    row.get("height"),
                    row.get("weight"),
                    row.get("bmi"),
                )
            )
            workout_rows.append(
                (
                    user_id,
                    row.get("workout_type"),
                    row.get("session_duration"),
                    row.get("calories_burned"),
                    row.get("max_bpm"),
                    row.get("avg_bpm"),
                    row.get("resting_bpm"),
                )
            )
            nutrition_rows.append(
                (
                    user_id,
                    row.get("carbs"),
                    row.get("proteins"),
                    row.get("fats"),
                    row.get("sugar_g"),
                    row.get("sodium_mg"),
                    row.get("calories_intake"),
                )
            )
            metrics_rows.append(
                (
                    user_id,
                    row.get("fat_percentage"),
                    row.get("water_intake"),
                    row.get("lean_mass_kg"),
                    row.get("cal_balance"),
                )
            )

        self.db.insert_many(
            "user",
            ["user_id", "gender", "age", "height", "weight", "bmi"],
            user_rows,
        )
        self.db.insert_many(
            "workout",
            [
                "user_id",
                "workout_type",
                "session_duration",
                "calories_burned",
                "max_bpm",
                "avg_bpm",
                "resting_bpm",
            ],
            workout_rows,
        )
        self.db.insert_many(
            "nutrition",
            ["user_id", "carbs", "proteins", "fats", "sugar_g", "sodium_mg", "calories_intake"],
            nutrition_rows,
        )
        self.db.insert_many(
            "derived_metrics",
            ["user_id", "fat_percentage", "water_intake", "lean_mass_kg", "cal_balance"],
            metrics_rows,
        )

        return len(df)
