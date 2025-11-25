import re
from typing import Dict, Optional

from database import DatabaseManager


class TemplateRenderer:
    """Render templates with SQL-backed placeholders."""

    PLACEHOLDER_QUERIES: Dict[str, str] = {
        "avg_bpm": "SELECT ROUND(AVG(avg_bpm), 2) AS val FROM workout",
        "max_bpm": "SELECT ROUND(MAX(max_bpm), 2) AS val FROM workout",
        "resting_bpm": "SELECT ROUND(AVG(resting_bpm), 2) AS val FROM workout",
        "cal_burned": "SELECT ROUND(SUM(calories_burned), 2) AS val FROM workout",
        "avg_calories": """
            SELECT ROUND(AVG(calories_burned), 2) AS val
            FROM workout
            WHERE workout_type = (
                SELECT workout_type
                FROM workout
                GROUP BY workout_type
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )
        """,
        "bmi": "SELECT ROUND(AVG(bmi), 2) AS val FROM user",
        "cal_balance": """
            SELECT ROUND(cal_balance, 2) AS val
            FROM derived_metrics
            WHERE user_id = (
                SELECT user_id
                FROM derived_metrics
                ORDER BY cal_balance ASC
                LIMIT 1
            )
            LIMIT 1
        """,
        "workout_type": """
            SELECT workout_type AS val
            FROM workout
            GROUP BY workout_type
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "duration": "SELECT ROUND(AVG(session_duration), 2) AS val FROM workout",
        "avg_duration": """
            SELECT ROUND(AVG(session_duration), 2) AS val
            FROM workout
            WHERE workout_type = (
                SELECT workout_type
                FROM workout
                GROUP BY workout_type
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )
        """,
        "protein": "SELECT ROUND(AVG(proteins), 2) AS val FROM nutrition",
        "carbs": "SELECT ROUND(AVG(carbs), 2) AS val FROM nutrition",
        "fat": "SELECT ROUND(AVG(fats), 2) AS val FROM nutrition",
        "calories_intake": "SELECT ROUND(AVG(calories_intake), 2) AS val FROM nutrition",
        "water_intake": "SELECT ROUND(AVG(water_intake), 2) AS val FROM derived_metrics",
        "fat_percentage": "SELECT ROUND(AVG(fat_percentage), 2) AS val FROM derived_metrics",
        "lean_mass_kg": "SELECT ROUND(AVG(lean_mass_kg), 2) AS val FROM derived_metrics",
        "session_duration": """
            SELECT ROUND(session_duration, 2) AS val
            FROM workout
            WHERE user_id = (
                SELECT user_id FROM derived_metrics ORDER BY cal_balance ASC LIMIT 1
            )
            ORDER BY calories_burned DESC
            LIMIT 1
        """,
    }

    def __init__(self, db: DatabaseManager):
        self.db = db

    def _fetch_value(self, placeholder: str) -> Optional[str]:
        query = self.PLACEHOLDER_QUERIES.get(placeholder)
        if not query:
            return None
        row = self.db.execute(query, fetchone=True)
        if not row:
            return None
        value = row["val"]
        return "N/A" if value is None else str(value)

    def _collect_placeholder_values(self, template_text: str) -> Dict[str, str]:
        placeholders = set(re.findall(r"{(.*?)}", template_text))
        filled: Dict[str, str] = {}
        for key in placeholders:
            filled[key] = self._fetch_value(key) or "N/A"
        return filled

    def render(self, template_id: int, output_format: str = "text") -> str:
        tpl_row = self.db.execute(
            "SELECT template_text FROM templates WHERE template_id = ?", (template_id,), fetchone=True
        )
        if not tpl_row:
            raise ValueError(f"Template {template_id} not found.")

        template_text = tpl_row["template_text"]
        values = self._collect_placeholder_values(template_text)

        rendered = template_text
        for placeholder, value in values.items():
            rendered = rendered.replace(f"{{{placeholder}}}", value)

        return self._format_output(rendered.strip(), output_format)

    @staticmethod
    def _format_output(text: str, output_format: str) -> str:
        output_format = output_format.lower()
        if output_format == "markdown":
            return f"### Daily Insight\n\n{text}"
        if output_format == "html":
            safe_text = text.replace("\n", "<br />")
            return f"<html><body><p>{safe_text}</p></body></html>"
        return text
