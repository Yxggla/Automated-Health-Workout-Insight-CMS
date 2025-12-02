DEFAULT_TEMPLATES = [
    {
        "name": "心率与恢复 / Heart & Recovery",
        "old_name": "Heart Health Snapshot",
        "text": (
            "平均训练心率 {avg_bpm} bpm，峰值 {max_bpm} bpm，静息心率 {resting_bpm} bpm；结合 BMI {bmi}，心肺负荷与体重管理处于可控区间。\n"
            "Average training HR {avg_bpm} bpm (peak {max_bpm}, resting {resting_bpm}); with BMI {bmi}, overall load stays manageable."
        ),
    },
    {
        "name": "体重体成分 / Weight & Composition",
        "old_name": "Body Composition Overview",
        "text": (
            "平均体重 {weight} kg，身高 {height} m，BMI {bmi}；体脂率 {fat_percentage}% ，瘦体重 {lean_mass_kg} kg，呈现当前体成分状况。\n"
            "Avg weight {weight} kg, height {height} m, BMI {bmi}; body fat {fat_percentage}% and lean mass {lean_mass_kg} kg outline composition."
        ),
    },
    # {
    #     "name": "能量收支 / Energy Balance",
    #     "old_name": "Caloric Deficit Leader",
    #     "text": (
    #         "当前热量平衡 {cal_balance} 千卡，日均摄入 {calories_intake} kcal，对比累计燃烧 {cal_burned} 千卡，收支方向清晰可见。\n"
    #         "Calorie balance stands at {cal_balance} kcal; daily intake {calories_intake} kcal versus total burn {cal_burned} kcal shows the direction."
    #     ),
    # },
    # {
    #     "name": "主力训练输出 / Primary Session Output",
    #     "old_name": "Calories by Popular Workout",
    #     "text": (
    #         "主力训练类型 {workout_type}，单次燃烧 {avg_calories} 千卡，耗时 {avg_duration} 小时；累计贡献 {cal_burned} 千卡，体现核心输出。\n"
    #         "Primary workout {workout_type} burns {avg_calories} kcal over {avg_duration} hours per session, driving {cal_burned} kcal in total."
    #     ),
    # },
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


def seed_templates(db) -> None:
    """Replace templates table with the current default set."""
    with db.conn:  # type: ignore[attr-defined]
        db.execute("DELETE FROM templates")
        for tpl in DEFAULT_TEMPLATES:
            db.execute(
                "INSERT INTO templates (template_name, template_text) VALUES (?, ?)",
                (tpl["name"], tpl["text"]),
            )

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
