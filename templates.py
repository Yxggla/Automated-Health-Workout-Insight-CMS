DEFAULT_TEMPLATES = [
    {
        "name": "体重体成分 / Weight & Composition",
        "old_name": "Body Composition Overview",
        "text": (
            "平均体重 {weight} kg，身高 {height} m，BMI {bmi}；体脂率 {fat_percentage}% ，瘦体重 {lean_mass_kg} kg，呈现当前体成分状况。\n"
            "Avg weight {weight} kg, height {height} m, BMI {bmi}; body fat {fat_percentage}% and lean mass {lean_mass_kg} kg outline composition."
        ),
    },
    {
        "name": "心率与恢复 / Heart & Recovery",
        "old_name": "Heart Health Snapshot",
        "text": (
            "平均训练心率 {avg_bpm} bpm，峰值 {max_bpm} bpm，静息心率 {resting_bpm} bpm；结合 BMI {bmi}，心肺负荷与体重管理处于可控区间。\n"
            "Average training HR {avg_bpm} bpm (peak {max_bpm}, resting {resting_bpm}); with BMI {bmi}, overall load stays manageable."
        ),
    },
    
    {
        "name": "营养水化与餐食 / Nutrition & Meals",
        "old_name": "Macro Intake",
        "text": (
            "日均 {daily_meals_frequency} 餐，餐型以 {meal_type} 为主；摄入碳水 {carbs} g、蛋白 {protein} g、脂肪 {fat} g，总热量 {calories_intake} kcal，糖 {sugar_g} g、钠 {sodium_mg} mg；饮水 {water_intake} 升支撑训练与恢复。\n"
            "{daily_meals_frequency} meals/day with {meal_type}; intake carbs {carbs} g, protein {protein} g, fats {fat} g, total {calories_intake} kcal, sugar {sugar_g} g, sodium {sodium_mg} mg; hydration {water_intake} L supports training and recovery."
        ),
    },
    {
        "name": "训练节奏与频率 / Rhythm & Frequency",
        "old_name": "Calorie Burn Expectation Comparison",
        "text": (
            "每周训练 {workout_frequency} 天，每次约 {duration} 小时；常见训练 {workout_type} 心率 {avg_bpm} bpm（峰值 {max_bpm}），热门类型时长 {avg_duration} 小时，便于规划强度与间隔。\n"
            "{workout_frequency} sessions/week at ~{duration} hours each; typical {workout_type} runs {avg_bpm} bpm (peaks {max_bpm}), popular types last {avg_duration} hours—useful for planning intensity and rest."
        ),
    },
    {
        "name": "性别与器材建议 / Gender & Equipment Plan",
        "old_name": "Gender-Based Workout Recommendation",
        "text": (
            "当前人群以 {gender} 为主，常做 {workout_type}；建议动作 {name_of_exercise}，难度 {difficulty_level}，{sets} 组 x {reps} 次，器材 {equipment_needed}，主攻 {target_muscle_group}。\n"
            "Cohort skews {gender}, often doing {workout_type}; recommended move {name_of_exercise}, {difficulty_level} level, {sets} sets x {reps} reps, using {equipment_needed}, targeting {target_muscle_group}."
        ),
    },
    {
        "name": "心血管健康评估 / Cardiovascular Health",
        "old_name": "Cardiovascular Health Assessment",
        "text": (
            "静息心率 {resting_bpm} bpm，心率储备使用率 {pct_hrr}% ，心血管健康水平为 {cardiovascular_level}。\n"
            "Resting HR {resting_bpm} bpm, {pct_hrr}% HR reserve usage, cardiovascular health level: {cardiovascular_level}."
        ),
    },
    {
        "name": "蛋白质摄入与体重比例 / Protein Intake per Body Weight",
        "old_name": "Protein Intake per Body Weight",
        "text": (
            "您的蛋白质摄入{protein}g，体重{weight}公斤，每公斤体重蛋白质{protein_per_kg}g/kg，{weight_goal}目标建议{calorie_recommendation}。\n"
            "Your protein intake {protein}g, weight {weight}kg, {protein_per_kg}g/kg body weight, for {weight_goal} goal: {calorie_recommendation}."
        ),
    },
]


DEFAULT_QUERIES = {
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
    "experience_level": """
            SELECT experience_level AS val
            FROM users
            GROUP BY experience_level
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
    "training_efficiency": "SELECT ROUND(AVG(training_efficiency), 2) AS val FROM workout_analysis",
    "muscle_focus_score": "SELECT ROUND(AVG(muscle_focus_score), 2) AS val FROM workout_analysis",
    "recovery_index": "SELECT ROUND(AVG(recovery_index), 2) AS val FROM workout_analysis",
    "workout_frequency": "SELECT ROUND(AVG(workout_frequency), 2) AS val FROM users",
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
    "sugar_g": "SELECT ROUND(AVG(sugar_g), 2) AS val FROM nutrition",
    "sodium_mg": "SELECT ROUND(AVG(sodium_mg), 2) AS val FROM nutrition",
    "cholesterol_mg": "SELECT ROUND(AVG(cholesterol_mg), 2) AS val FROM nutrition",
    "serving_size_g": "SELECT ROUND(AVG(serving_size_g), 2) AS val FROM nutrition",
    "prep_time_min": "SELECT ROUND(AVG(prep_time_min), 2) AS val FROM nutrition",
    "cook_time_min": "SELECT ROUND(AVG(cook_time_min), 2) AS val FROM nutrition",
    "rating": "SELECT ROUND(AVG(rating), 2) AS val FROM nutrition",
    "burns_calories_per_30min": "SELECT ROUND(AVG(burns_calories_per_30min), 2) AS val FROM workouts",
    "expected_burn_user": """
            SELECT ROUND(expected_burn, 2) AS val
            FROM workout_analysis
            WHERE user_id = (
                SELECT user_id FROM workout_analysis ORDER BY expected_burn DESC LIMIT 1
            )
        """,
}


def seed_templates(db) -> None:
    """Replace templates table with the current default set."""
    with db.conn:  # type: ignore[attr-defined]
        db.execute("DELETE FROM templates")
        for tpl in DEFAULT_TEMPLATES:
            db.execute(
                "INSERT INTO templates (template_name, template_text) VALUES (?, ?)",
                (tpl["name"], tpl["text"]),
            )


def seed_templates_if_empty(db) -> None:
    """Only seed defaults when templates table is empty."""
    row = db.execute("SELECT COUNT(*) AS c FROM templates", fetchone=True)
    count = row["c"] if row else 0
    if count and count > 0:
        return
    seed_templates(db)


def seed_queries(db) -> None:
    """Replace queries table with the current default set."""
    with db.conn:  # type: ignore[attr-defined]
        db.execute("DELETE FROM queries")
        for key, sql in DEFAULT_QUERIES.items():
            db.execute(
                "INSERT INTO queries (query_key, query_sql) VALUES (?, ?)",
                (key, sql),
            )


def seed_queries_if_empty(db) -> None:
    row = db.execute("SELECT COUNT(*) AS c FROM queries", fetchone=True)
    count = row["c"] if row else 0
    if count and count > 0:
        return
    seed_queries(db)

"""
个性化训练计划：利用经验等级和训练频率提供个性化建议

心率训练区间：分析心率区间和对应的训练效益

训练效率分析：展示训练效率、肌肉专注度和恢复指数的综合评分

营养与训练平衡：结合餐食频率和训练效益提供营养建议

肌肉生长潜力：基于瘦体重和肌群类型分析肌肉生长潜力

训练难度进阶：根据当前难度和设备使用提供进阶建议

心血管健康评估：综合评估心血管健康水平

热量管理建议：基于热量平衡提供体重管理建议

烹饪营养优化：分析烹饪方法对营养的影响

全面健康洞察：提供整体健康评分的综合报告
"""
