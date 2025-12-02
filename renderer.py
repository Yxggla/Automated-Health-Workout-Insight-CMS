import re
from typing import Dict, Optional

from database import DatabaseManager


class TemplateRenderer:
    """Render templates with SQL-backed placeholders."""

    PLACEHOLDER_QUERIES: Dict[str, str] = {
        "avg_bpm": "SELECT ROUND(AVG(avg_bpm), 2) AS val FROM workouts",
        "max_bpm": "SELECT ROUND(MAX(max_bpm), 2) AS val FROM workouts",
        "resting_bpm": "SELECT ROUND(AVG(resting_bpm), 2) AS val FROM workouts",
        "cal_burned": "SELECT ROUND(SUM(calories_burned), 2) AS val FROM workouts",
        "avg_calories": """
            SELECT ROUND(AVG(calories_burned), 2) AS val
            FROM workouts
            WHERE workout_type = (
                SELECT workout_type
                FROM workouts
                GROUP BY workout_type
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )
        """,
        "bmi": "SELECT ROUND(AVG(bmi), 2) AS val FROM users",
        "cal_balance": """
            SELECT ROUND(cal_balance, 2) AS val
            FROM workout_analysis
            WHERE user_id = (
                SELECT user_id
                FROM workout_analysis
                ORDER BY cal_balance ASC
                LIMIT 1
            )
            LIMIT 1
        """,
        "workout_type": """
            SELECT workout_type AS val
            FROM workouts
            GROUP BY workout_type
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "duration": "SELECT ROUND(AVG(session_duration), 2) AS val FROM workouts",
        "avg_duration": """
            SELECT ROUND(AVG(session_duration), 2) AS val
            FROM workouts
            WHERE workout_type = (
                SELECT workout_type
                FROM workouts
                GROUP BY workout_type
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )
        """,
        "protein": "SELECT ROUND(AVG(proteins), 2) AS val FROM nutrition",
        "carbs": "SELECT ROUND(AVG(carbs), 2) AS val FROM nutrition",
        "fat": "SELECT ROUND(AVG(fats), 2) AS val FROM nutrition",
        # 修复：使用 calories 而不是 calories_intake
        "calories_intake": "SELECT ROUND(AVG(calories), 2) AS val FROM nutrition",
        
        "water_intake": "SELECT ROUND(AVG(water_intake), 2) AS val FROM users",

        "fat_percentage": "SELECT ROUND(AVG(fat_percentage), 2) AS val FROM users",
        "lean_mass_kg": "SELECT ROUND(AVG(lean_mass_kg), 2) AS val FROM users",
        "weight": "SELECT ROUND(AVG(weight), 2) AS val FROM users",
        "height": "SELECT ROUND(AVG(height), 2) AS val FROM users",
        "age": "SELECT ROUND(AVG(age), 2) AS val FROM users",
        "gender": """
            SELECT gender AS val
            FROM users
            WHERE gender IS NOT NULL AND gender != ''
            GROUP BY gender
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "session_duration": """
            SELECT ROUND(session_duration, 2) AS val
            FROM workouts
            WHERE user_id = (
                SELECT user_id FROM workout_analysis ORDER BY cal_balance ASC LIMIT 1
            )
            ORDER BY calories_burned DESC
            LIMIT 1
        """,
        # 新增占位符查询
        "training_efficiency": "SELECT ROUND(AVG(training_efficiency), 2) AS val FROM workout_analysis",
        "muscle_focus_score": "SELECT ROUND(AVG(muscle_focus_score), 2) AS val FROM workout_analysis",
        "recovery_index": "SELECT ROUND(AVG(recovery_index), 2) AS val FROM workout_analysis",
        "workout_frequency": "SELECT ROUND(AVG(workout_frequency), 2) AS val FROM users",
        "experience_level": """
            SELECT experience_level AS val
            FROM users
            GROUP BY experience_level
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "daily_meals_frequency": "SELECT ROUND(AVG(daily_meals_frequency), 2) AS val FROM nutrition",
        "sets": "SELECT ROUND(AVG(sets), 2) AS val FROM workouts",
        "reps": "SELECT ROUND(AVG(reps), 2) AS val FROM workouts",
        "name_of_exercise": """
            SELECT name_of_exercise AS val
            FROM workouts
            GROUP BY name_of_exercise
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "target_muscle_group": """
            SELECT target_muscle_group AS val
            FROM workouts
            GROUP BY target_muscle_group
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "equipment_needed": """
            SELECT equipment_needed AS val
            FROM workouts
            GROUP BY equipment_needed
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "difficulty_level": """
            SELECT difficulty_level AS val
            FROM workouts
            GROUP BY difficulty_level
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "body_part": """
            SELECT body_part AS val
            FROM workouts
            GROUP BY body_part
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "type_of_muscle": """
            SELECT type_of_muscle AS val
            FROM workout_analysis
            GROUP BY type_of_muscle
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,

        # 修复：meal_name 在 nutrition 表中
        "meal_name": """
            SELECT meal_name AS val
            FROM nutrition
            WHERE meal_name IS NOT NULL AND meal_name != ''
            GROUP BY meal_name
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "meal_type": """
            SELECT meal_type AS val
            FROM nutrition
            GROUP BY meal_type
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "diet_type": """
            SELECT diet_type AS val
            FROM nutrition
            GROUP BY diet_type
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
       
        # 修复：cooking_method 在 nutrition 表中
        "cooking_method": """
            SELECT cooking_method AS val
            FROM nutrition
            WHERE cooking_method IS NOT NULL AND cooking_method != ''
            GROUP BY cooking_method
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "pct_hrr": "SELECT ROUND(AVG(pct_hrr), 2) AS val FROM workout_analysis",
        "pct_maxhr": "SELECT ROUND(AVG(pct_maxhr), 2) AS val FROM workout_analysis",
        "expected_burn": "SELECT ROUND(AVG(expected_burn), 2) AS val FROM workout_analysis",
        "training_zone": """
            SELECT CASE 
                WHEN AVG(pct_maxhr) < 0.6 THEN '恢复区'
                WHEN AVG(pct_maxhr) BETWEEN 0.6 AND 0.7 THEN '脂肪燃烧区'
                WHEN AVG(pct_maxhr) BETWEEN 0.7 AND 0.8 THEN '有氧区'
                WHEN AVG(pct_maxhr) BETWEEN 0.8 AND 0.9 THEN '无氧区'
                ELSE '极限区'
            END AS val FROM workout_analysis
        """,
        "training_benefit": """
            SELECT CASE 
                WHEN AVG(pct_maxhr) < 0.7 THEN '脂肪燃烧和恢复'
                WHEN AVG(pct_maxhr) BETWEEN 0.7 AND 0.8 THEN '心血管健康'
                WHEN AVG(pct_maxhr) BETWEEN 0.8 AND 0.9 THEN '耐力提升'
                ELSE '极限表现'
            END AS val FROM workout_analysis
        """,
        # 修复：cardiovascular_level 查询 - 确保所有使用的列都存在
        "cardiovascular_level": """
            SELECT CASE 
                WHEN AVG(u.resting_bpm) < 60 AND AVG(wa.pct_hrr) > 0.7 THEN '优秀'
                WHEN AVG(u.resting_bpm) < 70 AND AVG(wa.pct_hrr) > 0.6 THEN '良好'
                WHEN AVG(u.resting_bpm) < 80 AND AVG(wa.pct_hrr) > 0.5 THEN '一般'
                ELSE '需要改善'
            END AS val 
            FROM users u 
            JOIN workout_analysis wa ON u.user_id = wa.user_id
            WHERE u.resting_bpm IS NOT NULL AND wa.pct_hrr IS NOT NULL
        """,
        "weight_goal": """
            SELECT CASE 
                WHEN AVG(cal_balance) < -500 THEN '减重'
                WHEN AVG(cal_balance) BETWEEN -500 AND 500 THEN '维持'
                ELSE '增重'
            END AS val FROM workout_analysis
        """,
        "calorie_recommendation": """
            SELECT CASE 
                WHEN AVG(cal_balance) < -500 THEN '适当增加200-300千卡摄入'
                WHEN AVG(cal_balance) BETWEEN -500 AND 500 THEN '保持当前摄入水平'
                ELSE '考虑减少300-500千卡摄入'
            END AS val FROM workout_analysis
        """,
        "suggested_reps": """
            SELECT CASE 
                WHEN AVG(reps) < 8 THEN CAST(AVG(reps) + 2 AS TEXT)
                WHEN AVG(reps) BETWEEN 8 AND 12 THEN CAST(AVG(reps) + 1 AS TEXT)
                ELSE '保持当前次数，增加重量'
            END AS val FROM workouts
        """,
        "protein_per_kg": """
            SELECT ROUND(AVG(proteins / weight), 2) AS val 
            FROM nutrition n JOIN users u ON n.user_id = u.user_id
        """,
        # 新增字段查询
        "age": "SELECT ROUND(AVG(age), 1) AS val FROM users",
        "gender": """
            SELECT gender AS val
            FROM users
            GROUP BY gender
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "height": "SELECT ROUND(AVG(height), 2) AS val FROM users",
        "weight": "SELECT ROUND(AVG(weight), 2) AS val FROM users",
        "sugar_g": "SELECT ROUND(AVG(sugar_g), 2) AS val FROM nutrition",
        "sodium_mg": "SELECT ROUND(AVG(sodium_mg), 2) AS val FROM nutrition",
        "cholesterol_mg": "SELECT ROUND(AVG(cholesterol_mg), 2) AS val FROM nutrition",
        "serving_size_g": "SELECT ROUND(AVG(serving_size_g), 2) AS val FROM nutrition",
        "benefit": """
            SELECT benefit AS val
            FROM workout_analysis
            WHERE benefit IS NOT NULL AND benefit != ''
            GROUP BY benefit
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """,
        "burns_calories_per_30min": "SELECT ROUND(AVG(burns_calories_per_30min), 2) AS val FROM workout_analysis",
    }

    def __init__(self, db: DatabaseManager):
        self.db = db

    def _fetch_value(self, placeholder: str, user_id: Optional[int] = None) -> Optional[str]:
        if placeholder == "water_intake":
            return self._fetch_water_intake(user_id)

        query = self.PLACEHOLDER_QUERIES.get(placeholder)
        if not query:
            return None
        try:
            # 如果提供了 user_id，修改查询以支持用户过滤
            if user_id is not None and placeholder != "water_intake":
                query = self._add_user_filter(query, user_id)
            
            row = self.db.execute(query, fetchone=True)
            value = row["val"] if row else None

            # water_intake 兜底：如果 users 没有数据，尝试 derived_metrics
            if placeholder == "water_intake" and (value is None or value == ""):
                try:
                    row_dm = self.db.execute(
                        "SELECT ROUND(AVG(water_intake), 2) AS val FROM derived_metrics WHERE water_intake IS NOT NULL",
                        fetchone=True,
                    )
                    value = row_dm["val"] if row_dm else value
                except Exception:
                    pass

            if value is None:
                return "0"
            return str(value)
        except Exception as e:
            print(f"Error fetching placeholder '{placeholder}': {e}")
            return "N/A"

    def _fetch_water_intake(self, user_id: Optional[int]) -> str:
        """专门处理补水，容错缺表/缺数据，用户过滤可选。"""
        # 优先 derived_metrics
        try:
            q = "SELECT ROUND(AVG(water_intake), 2) AS val FROM derived_metrics WHERE water_intake IS NOT NULL"
            if user_id is not None:
                q += f" AND user_id = {user_id}"
            row = self.db.execute(q, fetchone=True)
            if row and row["val"] is not None:
                return str(row["val"])
        except Exception:
            pass

        # 回退 users
        try:
            q = "SELECT ROUND(AVG(water_intake), 2) AS val FROM users WHERE water_intake IS NOT NULL"
            if user_id is not None:
                q += f" AND user_id = {user_id}"
            row = self.db.execute(q, fetchone=True)
            if row and row["val"] is not None:
                return str(row["val"])
        except Exception:
            pass

        return "0"

    def _add_user_filter(self, query: str, user_id: int) -> str:
        """在查询中添加用户过滤条件，将全局查询转换为个性化查询"""
        query_lower = query.lower()

        # 含 JOIN 的查询逻辑复杂，避免自动插入过滤以免破坏语法
        if " join " in query_lower:
            return query
        
        # 如果查询已经包含 user_id 条件，直接返回
        if f"user_id = {user_id}" in query or f"user_id={user_id}" in query or f".user_id = {user_id}" in query:
            return query
        
        # 对于包含子查询的复杂查询，直接返回，避免破坏语法
        if query_lower.count("select") > 1:
            return query
        
        # 简单查询：直接在主查询中添加 WHERE
        return self._add_filter_to_simple_query(query, user_id)
    
    def _add_filter_to_simple_query(self, query: str, user_id: int) -> str:
        """为简单查询添加用户过滤"""
        query_lower = query.lower()
        
        # 找到主表
        tables_to_check = [
            ("from workouts", "workouts", None),
            ("from users", "users", None),
            ("from nutrition", "nutrition", None),
            ("from workout_analysis", "workout_analysis", None),
        ]
        
        for pattern, table_name, alias in tables_to_check:
            if pattern in query_lower:
                # 找到表的位置
                idx = query_lower.find(pattern)
                after_from = query[idx + len(pattern):].strip()
                after_from_lower = after_from.lower()
                
                # 检查是否已有 WHERE
                if "where" in after_from_lower:
                    # 找到 WHERE 的位置，在其后添加 AND user_id = ?
                    where_pos = after_from_lower.find("where")
                    insert_pos = idx + len(pattern) + where_pos + 5
                    # 检查是否已有 user_id 过滤
                    if "user_id" not in after_from_lower[where_pos:where_pos+50]:
                        query = query[:insert_pos] + f" user_id = {user_id} AND " + query[insert_pos:]
                else:
                    # 没有 WHERE，在合适位置添加
                    # 找到下一个关键字（GROUP BY, ORDER BY, LIMIT, JOIN）
                    end_pos = idx + len(pattern)
                    for keyword in ["group by", "order by", "limit", "join"]:
                        keyword_pos = after_from_lower.find(keyword)
                        if keyword_pos != -1:
                            end_pos = idx + len(pattern) + keyword_pos
                            break
                    query = query[:end_pos] + f" WHERE user_id = {user_id}" + query[end_pos:]
                return query
        
        return query
    
    def _add_filter_to_complex_query(self, query: str, user_id: int) -> str:
        """为复杂查询（包含子查询）添加用户过滤"""
        query_lower = query.lower()
        
        # 对于 JOIN 查询，尝试在主表添加过滤
        if "join" in query_lower:
            # 找到主表的别名
            alias_map = {
                "from users u": "u.user_id",
                "from workouts w": "w.user_id",
                "from nutrition n": "n.user_id",
                "from workout_analysis wa": "wa.user_id",
            }
            
            for pattern, user_id_col in alias_map.items():
                if pattern in query_lower:
                    if "where" not in query_lower:
                        query += f" WHERE {user_id_col} = {user_id}"
                    elif user_id_col.split(".")[0] + ".user_id" not in query_lower:
                        query = query.replace("WHERE", f"WHERE {user_id_col} = {user_id} AND", 1)
                    return query
        
        # 对于其他复杂查询，尝试在主查询的 FROM 后添加
        return self._add_filter_to_simple_query(query, user_id)

    def _collect_placeholder_values(self, template_text: str, user_id: Optional[int] = None) -> Dict[str, str]:
        placeholders = set(re.findall(r"{(.*?)}", template_text))
        filled: Dict[str, str] = {}
        for key in placeholders:
            filled[key] = self._fetch_value(key, user_id) or "N/A"
        return filled

    def render(self, template_id: int, output_format: str = "text", user_id: Optional[int] = None) -> str:
        tpl_row = self.db.execute(
            "SELECT template_text FROM templates WHERE template_id = ?", (template_id,), fetchone=True
        )
        if not tpl_row:
            raise ValueError(f"Template {template_id} not found.")

        template_text = tpl_row["template_text"]
        values = self._collect_placeholder_values(template_text, user_id)

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
