from pathlib import Path
from typing import Dict, List

import pandas as pd

from database import DatabaseManager


class DataImporter:
    """Import and normalize the Kaggle CSV into the SQLite schema."""

    COLUMN_MAP: Dict[str, str] = {
        "user_id": "user_id",  # 如果CSV中有user_id列，将使用它
        "User_ID": "user_id",  # 支持不同大小写
        "User ID": "user_id",
        "UserID": "user_id",
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
        "Calories": "calories",
        "Fat_Percentage": "fat_percentage",
        "Water_Intake (liters)": "water_intake",
        "lean_mass_kg": "lean_mass_kg",
        "cal_balance": "cal_balance",
        "Workout_Frequency (days/week)": "workout_frequency",
        "Experience_Level": "experience_level",
        "Daily meals frequency": "daily_meals_frequency",
        "Name of Exercise": "name_of_exercise",
        "Sets": "sets",
        "Reps": "reps",
        "Benefit": "benefit",
        "Burns Calories (per 30 min)": "burns_calories_per_30min",
        "Target Muscle Group": "target_muscle_group",
        "Equipment Needed": "equipment_needed",
        "Difficulty Level": "difficulty_level",
        "Body Part": "body_part",
        "Type of Muscle": "type_of_muscle",
        "meal_name": "meal_name",
        "meal_type": "meal_type",
        "diet_type": "diet_type",
        "cholesterol_mg": "cholesterol_mg",
        "serving_size_g": "serving_size_g",
        "cooking_method": "cooking_method",
        "prep_time_min": "prep_time_min",
        "cook_time_min": "cook_time_min",
        "rating": "rating",
        "pct_HRR": "pct_hrr",
        "pct_maxHR": "pct_maxhr",
        "expected_burn": "expected_burn",
    }

    REQUIRED_FIELDS: List[str] = list(COLUMN_MAP.values())

    def __init__(self, db: DatabaseManager):
        self.db = db

    def import_csv(self, csv_path: str = "Final_data.csv", clear_existing: bool = True) -> int:
        """Read the CSV, normalize columns, and insert into tables. Returns row count."""
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        df = pd.read_csv(csv_path)
        df = df.rename(columns=self.COLUMN_MAP)

        # 处理数值列
        numeric_columns = [
            "user_id", "age", "height", "weight", "bmi", "session_duration", "calories_burned",
            "max_bpm", "avg_bpm", "resting_bpm", "carbs", "proteins", "fats",
            "sugar_g", "sodium_mg", "calories", "fat_percentage", "water_intake",
            "lean_mass_kg", "cal_balance", "workout_frequency", "daily_meals_frequency",
            "sets", "reps", "burns_calories_per_30min", "cholesterol_mg", "serving_size_g",
            "prep_time_min", "cook_time_min", "rating", "pct_hrr", "pct_maxhr", "expected_burn"
        ]
        
        for numeric_col in numeric_columns:
            if numeric_col in df.columns:
                df[numeric_col] = pd.to_numeric(df[numeric_col], errors="coerce")
            else:
                df[numeric_col] = pd.NA

        # 处理文本列
        text_columns = [
            "gender", "workout_type", "experience_level", "name_of_exercise", 
            "benefit", "target_muscle_group", "equipment_needed", "difficulty_level",
            "body_part", "type_of_muscle", "meal_name", "meal_type", "diet_type", "cooking_method"
        ]
        
        for text_col in text_columns:
            if text_col not in df.columns:
                df[text_col] = ""
            else:
                df[text_col] = df[text_col].fillna("").astype(str)

        # 确保所有必需字段都存在
        for field in self.REQUIRED_FIELDS:
            if field not in df.columns:
                df[field] = pd.NA

        df = df.fillna(pd.NA)

        # 清空现有数据
        if clear_existing:
            self.db.truncate_tables(["users", "workouts", "nutrition", "workout_analysis"])

        user_rows = []
        workout_rows = []
        nutrition_rows = []
        analysis_rows = []

        for idx, row in df.iterrows():
            # 优先使用CSV中的user_id，如果没有则使用行号
            if "user_id" in df.columns and pd.notna(row.get("user_id")):
                user_id = int(row["user_id"])
            else:
                user_id = idx + 1  # 如果没有user_id列，使用行号作为默认ID
            
            # users 表数据
            user_rows.append(
                (
                    user_id,
                    row.get("gender", ""),
                    row.get("age"),
                    row.get("height"),
                    row.get("weight"),
                    row.get("bmi"),
                    row.get("fat_percentage"),
                    row.get("lean_mass_kg"),
                    row.get("experience_level", ""),
                    row.get("workout_frequency"),
                )
            )
            
            # workouts 表数据
            workout_rows.append(
                (
                    user_id,
                    row.get("workout_type", ""),
                    row.get("session_duration"),
                    row.get("calories_burned"),
                    row.get("max_bpm"),
                    row.get("avg_bpm"),
                    row.get("resting_bpm"),
                    row.get("name_of_exercise", ""),
                    row.get("sets"),
                    row.get("reps"),
                    row.get("target_muscle_group", ""),
                    row.get("equipment_needed", ""),
                    row.get("difficulty_level", ""),
                    row.get("body_part", ""),
                )
            )
            
            # nutrition 表数据
            nutrition_rows.append(
                (
                    user_id,
                    row.get("daily_meals_frequency"),
                    row.get("carbs"),
                    row.get("proteins"),
                    row.get("fats"),
                    row.get("calories"),
                    row.get("meal_name", ""),
                    row.get("meal_type", ""),
                    row.get("diet_type", ""),
                    row.get("sugar_g"),
                    row.get("sodium_mg"),
                    row.get("cholesterol_mg"),
                    row.get("serving_size_g"),
                    row.get("cooking_method", ""),
                    row.get("prep_time_min"),
                    row.get("cook_time_min"),
                    row.get("rating"),
                )
            )
            
            # workout_analysis 表数据
            analysis_rows.append(
                (
                    user_id,
                    row.get("pct_hrr"),
                    row.get("pct_maxhr"),
                    row.get("cal_balance"),
                    row.get("expected_burn"),
                    row.get("benefit", ""),
                    row.get("burns_calories_per_30min"),
                    row.get("type_of_muscle", ""),
                    # 计算训练效率 (基于卡路里燃烧和时长)
                    row.get("calories_burned", 0) / max(row.get("session_duration", 1), 0.1) if pd.notna(row.get("calories_burned")) and pd.notna(row.get("session_duration")) else None,
                    # 计算肌肉专注度评分 (基于训练类型和目标肌群)
                    0.8 if row.get("workout_type") == "Strength" else 0.6,  # 简化计算
                    # 计算恢复指数 (基于静息心率和训练频率)
                    (100 - (row.get("resting_bpm", 70) - 60)) / 40 * 100 if pd.notna(row.get("resting_bpm")) else None,
                )
            )

        # 插入数据到各表
        self.db.insert_many(
            "users",
            ["user_id", "gender", "age", "height", "weight", "bmi", "fat_percentage", "lean_mass_kg", "experience_level", "workout_frequency"],
            user_rows,
        )
        
        self.db.insert_many(
            "workouts",
            [
                "user_id", "workout_type", "session_duration", "calories_burned", 
                "max_bpm", "avg_bpm", "resting_bpm", "name_of_exercise", "sets", "reps",
                "target_muscle_group", "equipment_needed", "difficulty_level", "body_part"
            ],
            workout_rows,
        )
        
        self.db.insert_many(
            "nutrition",
            [
                "user_id", "daily_meals_frequency", "carbs", "proteins", "fats", "calories",
                "meal_name", "meal_type", "diet_type", "sugar_g", "sodium_mg", "cholesterol_mg",
                "serving_size_g", "cooking_method", "prep_time_min", "cook_time_min", "rating"
            ],
            nutrition_rows,
        )
        
        self.db.insert_many(
            "workout_analysis",
            [
                "user_id", "pct_hrr", "pct_maxhr", "cal_balance", "expected_burn",
                "benefit", "burns_calories_per_30min", "type_of_muscle",
                "training_efficiency", "muscle_focus_score", "recovery_index"
            ],
            analysis_rows,
        )
        
        return len(df)