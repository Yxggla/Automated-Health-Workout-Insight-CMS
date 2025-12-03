from typing import Dict, List, Optional
from database import DatabaseManager


class UserManager:
    """用户管理类，提供用户的 CRUD 操作"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_user(self, user_id: int) -> Optional[Dict]:
        """根据 user_id 查询单个用户信息"""
        row = self.db.execute(
            """
            SELECT user_id, age, gender, weight, height, bmi, 
                   fat_percentage, lean_mass_kg, 
                   workout_frequency, water_intake, resting_bpm
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
            fetchone=True,
        )
        if not row:
            return None
        return dict(row)

    def list_users(
        self, 
        limit: Optional[int] = None, 
        offset: int = 0,
        search: Optional[str] = None,
        order_desc: bool = False,
    ) -> List[Dict]:
        """查询用户列表
        
        Args:
            limit: 返回的最大记录数
            offset: 偏移量
            search: 搜索关键词（在 gender 中搜索）
        """
        query = """
            SELECT user_id, age, gender, weight, height, bmi, 
                   fat_percentage, lean_mass_kg, 
                   workout_frequency, water_intake, resting_bpm
            FROM users
        """
        params = []
        
        if search:
            query += " WHERE gender LIKE ?"
            search_pattern = f"%{search}%"
            params.append(search_pattern)
        
        query += " ORDER BY user_id " + ("DESC" if order_desc else "ASC")
        
        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        rows = self.db.execute(query, tuple(params), fetchall=True)
        return [dict(row) for row in rows or []]

    def create_user(
        self,
        age: Optional[float] = None,
        gender: Optional[str] = None,
        weight: Optional[float] = None,
        height: Optional[float] = None,
        bmi: Optional[float] = None,
        fat_percentage: Optional[float] = None,
        lean_mass_kg: Optional[float] = None,
        workout_frequency: Optional[float] = None,
        water_intake: Optional[float] = None,
        resting_bpm: Optional[float] = None,
    ) -> int:
        """创建新用户
        
        Returns:
            新创建用户的 user_id
        """
        # 如果提供了 weight 和 height，自动计算 BMI
        if bmi is None and weight is not None and height is not None and height > 0:
            bmi = weight / (height ** 2)
        
        columns = []
        values = []
        placeholders = []
        
        if age is not None:
            columns.append("age")
            values.append(age)
            placeholders.append("?")
        if gender is not None:
            columns.append("gender")
            values.append(gender)
            placeholders.append("?")
        if weight is not None:
            columns.append("weight")
            values.append(weight)
            placeholders.append("?")
        if height is not None:
            columns.append("height")
            values.append(height)
            placeholders.append("?")
        if bmi is not None:
            columns.append("bmi")
            values.append(bmi)
            placeholders.append("?")
        if fat_percentage is not None:
            columns.append("fat_percentage")
            values.append(fat_percentage)
            placeholders.append("?")
        if lean_mass_kg is not None:
            columns.append("lean_mass_kg")
            values.append(lean_mass_kg)
            placeholders.append("?")
        if workout_frequency is not None:
            columns.append("workout_frequency")
            values.append(workout_frequency)
            placeholders.append("?")
        if water_intake is not None:
            columns.append("water_intake")
            values.append(water_intake)
            placeholders.append("?")
        if resting_bpm is not None:
            columns.append("resting_bpm")
            values.append(resting_bpm)
            placeholders.append("?")

        if not columns:
            # 没有字段时插入空记录，仅生成自增 user_id
            cursor = self.db.execute("INSERT INTO users DEFAULT VALUES")
            self.db.conn.commit()
            return cursor.lastrowid

        cols_str = ", ".join(columns)
        placeholders_str = ", ".join(placeholders)
        
        query = f"INSERT INTO users ({cols_str}) VALUES ({placeholders_str})"
        
        cursor = self.db.execute(query, tuple(values))
        self.db.conn.commit()
        
        return cursor.lastrowid

    def update_user(
        self,
        user_id: int,
        age: Optional[float] = None,
        gender: Optional[str] = None,
        weight: Optional[float] = None,
        height: Optional[float] = None,
        bmi: Optional[float] = None,
        fat_percentage: Optional[float] = None,
        lean_mass_kg: Optional[float] = None,
        workout_frequency: Optional[float] = None,
        water_intake: Optional[float] = None,
        resting_bpm: Optional[float] = None,
    ) -> bool:
        """更新用户信息
        
        Returns:
            是否成功更新（如果用户不存在返回 False）
        """
        # 检查用户是否存在
        if not self.get_user(user_id):
            return False
        
        # 如果更新了 weight 或 height，重新计算 BMI
        if bmi is None and (weight is not None or height is not None):
            user = self.get_user(user_id)
            if user:
                current_weight = weight if weight is not None else user.get("weight")
                current_height = height if height is not None else user.get("height")
                if current_weight is not None and current_height is not None and current_height > 0:
                    bmi = current_weight / (current_height ** 2)
        
        updates = []
        values = []
        
        if age is not None:
            updates.append("age = ?")
            values.append(age)
        if gender is not None:
            updates.append("gender = ?")
            values.append(gender)
        if weight is not None:
            updates.append("weight = ?")
            values.append(weight)
        if height is not None:
            updates.append("height = ?")
            values.append(height)
        if bmi is not None:
            updates.append("bmi = ?")
            values.append(bmi)
        if fat_percentage is not None:
            updates.append("fat_percentage = ?")
            values.append(fat_percentage)
        if lean_mass_kg is not None:
            updates.append("lean_mass_kg = ?")
            values.append(lean_mass_kg)
        if workout_frequency is not None:
            updates.append("workout_frequency = ?")
            values.append(workout_frequency)
        if water_intake is not None:
            updates.append("water_intake = ?")
            values.append(water_intake)
        if resting_bpm is not None:
            updates.append("resting_bpm = ?")
            values.append(resting_bpm)
        
        if not updates:
            return False

        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
        
        self.db.execute(query, tuple(values))
        self.db.conn.commit()
        return True

    def delete_user(self, user_id: int, cascade: bool = False) -> bool:
        """删除用户
        
        Args:
            user_id: 要删除的用户 ID
            cascade: 是否级联删除关联数据（workouts, nutrition, workout_analysis）
        
        Returns:
            是否成功删除（如果用户不存在返回 False）
        """
        try:
            with self.db.conn:
                if cascade:
                    # 级联删除关联数据
                    self.db.execute("DELETE FROM workout_analysis WHERE user_id = ?", (user_id,))
                    self.db.execute("DELETE FROM nutrition WHERE user_id = ?", (user_id,))
                    self.db.execute("DELETE FROM workouts WHERE user_id = ?", (user_id,))
                    self.db.execute("DELETE FROM derived_metrics WHERE user_id = ?", (user_id,))
                cur = self.db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                deleted = cur.rowcount if cur else 0
                return deleted > 0
        except Exception as e:
            print(f"删除用户时出错: {e}")
            self.db.conn.rollback()
            return False

    def get_user_statistics(self, user_id: int) -> Optional[Dict]:
        """获取用户的统计信息（包括关联的训练、营养数据）"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        stats = {"user_info": user}
        
        # 训练统计（精简字段）
        workout_stats = self.db.execute(
            """
            SELECT 
                ROUND(SUM(calories_burned), 2) AS total_calories,
                ROUND(AVG(calories_burned), 2) AS avg_calories,
                ROUND(AVG(session_duration), 2) AS avg_duration
            FROM workouts
            WHERE user_id = ?
            """,
            (user_id,),
            fetchone=True,
        )
        stats["workout_stats"] = dict(workout_stats) if workout_stats else {}
        
        # 营养统计（精简字段）
        nutrition_stats = self.db.execute(
            """
            SELECT 
                ROUND(AVG(calories), 2) AS avg_calories,
                ROUND(AVG(proteins), 2) AS avg_proteins,
                ROUND(AVG(carbs), 2) AS avg_carbs,
                ROUND(AVG(fats), 2) AS avg_fats
            FROM nutrition
            WHERE user_id = ?
            """,
            (user_id,),
            fetchone=True,
        )
        stats["nutrition_stats"] = dict(nutrition_stats) if nutrition_stats else {}
        
        # 分析统计（精简字段）
        analysis_stats = self.db.execute(
            """
            SELECT 
                ROUND(AVG(cal_balance), 2) AS avg_cal_balance,
                ROUND(AVG(training_efficiency), 2) AS avg_training_efficiency,
                ROUND(AVG(recovery_index), 2) AS avg_recovery_index
            FROM workout_analysis
            WHERE user_id = ?
            """,
            (user_id,),
            fetchone=True,
        )
        stats["analysis_stats"] = dict(analysis_stats) if analysis_stats else {}
        
        return stats

    def count_users(self) -> int:
        """返回用户总数"""
        row = self.db.execute("SELECT COUNT(*) AS count FROM users", fetchone=True)
        return row["count"] if row else 0
