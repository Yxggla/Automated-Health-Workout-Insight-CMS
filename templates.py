DEFAULT_TEMPLATES = [
    {
        "name": "热门训练消耗 / Calories by Popular Workout",
        "old_name": "Calories by Popular Workout",
        "text": (
            "今天最常见的训练类型是 {workout_type}，平均燃烧 {avg_calories} 千卡，平均时长 {avg_duration} 小时。\n"
            "Today, the most common workout type was {workout_type}, averaging {avg_calories} kcal burned over {avg_duration} hours."
        ),
    },
    {
        "name": "热量赤字之最 / Caloric Deficit Leader",
        "old_name": "Caloric Deficit Leader",
        "text": (
            "今日热量赤字最高的用户热量平衡为 {cal_balance}，训练时长 {session_duration} 小时。\n"
            "The user with the highest caloric deficit today recorded a {cal_balance} calorie balance and {session_duration} hours of training."
        ),
    },
    {
        "name": "心率概览 / Heart Health Snapshot",
        "old_name": "Heart Health Snapshot",
        "text": (
            "平均训练心率 {avg_bpm} bpm，峰值 {max_bpm} bpm，静息心率 {resting_bpm} bpm。\n"
            "Average training heart rate is {avg_bpm} bpm with a peak at {max_bpm} bpm and resting at {resting_bpm} bpm."
        ),
    },
    {
        "name": "身体成分 / Body Composition Overview",
        "old_name": "Body Composition Overview",
        "text": (
            "平均 BMI {bmi}，体脂率约 {fat_percentage}% ，瘦体重约 {lean_mass_kg} kg。\n"
            "Average BMI is {bmi} with fat percentage near {fat_percentage}% and lean mass around {lean_mass_kg} kg."
        ),
    },
    {
        "name": "三大营养素 / Macro Intake",
        "old_name": "Macro Intake",
        "text": (
            "日均摄入：碳水 {carbs} g，蛋白 {protein} g，脂肪 {fat} g，总热量 {calories_intake} kcal。\n"
            "Daily macros show carbs {carbs} g, proteins {protein} g, fats {fat} g, and calories {calories_intake} kcal."
        ),
    },
    {
        "name": "补水与心率 / Hydration Pulse",
        "old_name": "Hydration Pulse",
        "text": (
            "平均饮水 {water_intake} 升，支持训练平均心率 {avg_bpm} bpm。\n"
            "Hydration averages {water_intake} liters supporting an average heart rate of {avg_bpm} bpm."
        ),
    },
    {
        "name": "训练时长与消耗 / Workout Time & Burn",
        "old_name": "Workout Time & Burn",
        "text": (
            "每次训练平均 {duration} 小时，总计燃烧 {cal_burned} 千卡。\n"
            "Users spent {duration} hours per session on average while burning {cal_burned} total calories."
        ),
    },
    {
        "name": "效率榜 / Training Efficiency",
        "old_name": "Training Efficiency",
        "text": (
            "最受欢迎的训练类型 {workout_type}，单次平均时长 {avg_duration} 小时，平均燃烧 {avg_calories} 千卡。\n"
            "Top workout type {workout_type} logged {avg_duration} hours per session and {avg_calories} calories burned."
        ),
    },
    {
        "name": "恢复准备度 / Recovery Readiness",
        "old_name": "Recovery Readiness",
        "text": (
            "静息心率 {resting_bpm} bpm，BMI {bmi}，表明稳定的恢复状态。\n"
            "Resting BPM holds at {resting_bpm} bpm while BMI sits at {bmi}, suggesting readiness for steady training."
        ),
    },
    {
        "name": "有氧与体成分 / Cardio vs Composition",
        "old_name": "Cardio vs Composition",
        "text": (
            "平均心率 {avg_bpm} bpm，体脂 {fat_percentage}% ，瘦体重 {lean_mass_kg} kg。\n"
            "With {avg_bpm} bpm average effort and {fat_percentage}% body fat, lean mass trends toward {lean_mass_kg} kg."
        ),
    },
]


def seed_templates(db) -> None:
    """Insert or update templates with bilingual names/text."""
    with db.conn:  # type: ignore[attr-defined]
        for tpl in DEFAULT_TEMPLATES:
            existing = db.execute(
                "SELECT template_id FROM templates WHERE template_name IN (?, ?)",
                (tpl["old_name"], tpl["name"]),
                fetchone=True,
            )
            if existing:
                db.execute(
                    "UPDATE templates SET template_name = ?, template_text = ? WHERE template_id = ?",
                    (tpl["name"], tpl["text"], existing["template_id"]),
                )
            else:
                db.execute(
                    "INSERT INTO templates (template_name, template_text) VALUES (?, ?)",
                    (tpl["name"], tpl["text"]),
                )
