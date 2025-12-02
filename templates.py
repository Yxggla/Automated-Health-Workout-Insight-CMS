DEFAULT_TEMPLATES = [
    {
        "name": "热门训练消耗 / Calories by Popular Workout",
        "old_name": "Calories by Popular Workout",
        "text": (
            "您最常进行的训练类型是 {workout_type}，平均燃烧 {avg_calories} 千卡，平均时长 {avg_duration} 小时。\n"
            "Your most frequent workout type is {workout_type}, averaging {avg_calories} kcal burned over {avg_duration} hours."
        ),
    },
    {
        "name": "热量赤字之最 / Caloric Deficit Leader",
        "old_name": "Caloric Deficit Leader",
        "text": (
            "您的热量平衡为 {cal_balance} 千卡，训练时长 {session_duration} 小时。\n"
            "Your caloric balance is {cal_balance} kcal with {session_duration} hours of training."
        ),
    },
    {
        "name": "心率概览 / Heart Health Snapshot",
        "old_name": "Heart Health Snapshot",
        "text": (
            "您的训练心率 {avg_bpm} bpm，峰值 {max_bpm} bpm，静息心率 {resting_bpm} bpm。\n"
            "Your training heart rate is {avg_bpm} bpm with a peak at {max_bpm} bpm and resting at {resting_bpm} bpm."
        ),
    },
    {
        "name": "身体成分 / Body Composition Overview",
        "old_name": "Body Composition Overview",
        "text": (
            "您的 BMI {bmi}，体脂率约 {fat_percentage}% ，瘦体重约 {lean_mass_kg} kg。\n"
            "Your BMI is {bmi} with fat percentage near {fat_percentage}% and lean mass around {lean_mass_kg} kg."
        ),
    },
    {
        "name": "三大营养素 / Macro Intake",
        "old_name": "Macro Intake",
        "text": (
            "您的日均摄入：碳水 {carbs} g，蛋白 {protein} g，脂肪 {fat} g，总热量 {calories_intake} kcal。\n"
            "Your daily macros show carbs {carbs} g, proteins {protein} g, fats {fat} g, and calories {calories_intake} kcal."
        ),
    },
    {
        "name": "补水与心率 / Hydration Pulse",
        "old_name": "Hydration Pulse",
        "text": (
            "您平均饮水 {water_intake} 升，训练平均心率 {avg_bpm} bpm。\n"
            "Your hydration averages {water_intake} liters supporting a training heart rate of {avg_bpm} bpm."
        ),
    },
    {
        "name": "训练时长与消耗 / Workout Time & Burn",
        "old_name": "Workout Time & Burn",
        "text": (
            "您每次训练平均 {duration} 小时，总计燃烧 {cal_burned} 千卡。\n"
            "You spent {duration} hours per session on average while burning {cal_burned} total calories."
        ),
    },
    {
        "name": "效率榜 / Training Efficiency",
        "old_name": "Training Efficiency",
        "text": (
            "您最常进行的训练类型 {workout_type}，单次平均时长 {avg_duration} 小时，平均燃烧 {avg_calories} 千卡。\n"
            "Your top workout type {workout_type} logged {avg_duration} hours per session and {avg_calories} calories burned."
        ),
    },
    {
        "name": "恢复准备度 / Recovery Readiness",
        "old_name": "Recovery Readiness",
        "text": (
            "您的静息心率 {resting_bpm} bpm，BMI {bmi}，表明稳定的恢复状态。\n"
            "Your resting BPM holds at {resting_bpm} bpm while BMI sits at {bmi}, suggesting readiness for steady training."
        ),
    },
    {
        "name": "有氧与体成分 / Cardio vs Composition",
        "old_name": "Cardio vs Composition",
        "text": (
            "您的心率 {avg_bpm} bpm，体脂 {fat_percentage}% ，瘦体重 {lean_mass_kg} kg。\n"
            "With your {avg_bpm} bpm average effort and {fat_percentage}% body fat, lean mass trends toward {lean_mass_kg} kg."
        ),
    },
    # 新增模板开始
    {
        "name": "个性化训练计划 / Personalized Training Plan",
        "old_name": "Personalized Training Plan",
        "text": (
            "基于您的{experience_level}水平和每周{workout_frequency}天的训练频率，建议{workout_type}训练，每组{reps}次，共{sets}组。\n"
            "Based on your {experience_level} level and {workout_frequency} days/week training frequency, we recommend {workout_type} with {sets} sets of {reps} reps each."
        ),
    },
    {
        "name": "心率训练区间 / Heart Rate Training Zone",
        "old_name": "Heart Rate Training Zone",
        "text": (
            "您的训练中心率达到{avg_bpm}bpm，占最大心率{pct_maxhr}%，处于{training_zone}区间，最适合{training_benefit}。\n"
            "Your training heart rate reached {avg_bpm}bpm, {pct_maxhr}% of max, in the {training_zone} zone, ideal for {training_benefit}."
        ),
    },
    {
        "name": "训练效率分析 / Training Efficiency Analysis",
        "old_name": "Training Efficiency Analysis",
        "text": (
            "您的训练效率评分{training_efficiency}，肌肉专注度{muscle_focus_score}，恢复指数{recovery_index}。\n"
            "Your training efficiency scored {training_efficiency}, muscle focus {muscle_focus_score}, recovery index {recovery_index}."
        ),
    },
    {
        "name": "营养与训练平衡 / Nutrition Workout Balance",
        "old_name": "Nutrition Workout Balance",
        "text": (
            "您每日{daily_meals_frequency}餐，{meal_type}摄入{carbs}g碳水，建议增加{protein_per_kg}g/kg蛋白质以优化训练效果。\n"
            "With your {daily_meals_frequency} meals daily, {meal_type} intake includes {carbs}g carbs; consider adding {protein_per_kg}g/kg protein to optimize training results."
        ),
    },
    {
        "name": "肌肉生长潜力 / Muscle Growth Potential",
        "old_name": "Muscle Growth Potential",
        "text": (
            "您当前瘦体重{lean_mass_kg}kg，针对{type_of_muscle}肌群，{target_muscle_group}训练效果显著。\n"
            "Your current lean mass {lean_mass_kg}kg, {type_of_muscle} muscle focus shows significant {target_muscle_group} training results."
        ),
    },
    {
        "name": "训练难度进阶 / Training Difficulty Progression",
        "old_name": "Training Difficulty Progression",
        "text": (
            "您的{difficulty_level}难度{name_of_exercise}训练，使用{equipment_needed}，建议进阶到{suggested_reps}次。\n"
            "Your {difficulty_level} level {name_of_exercise} using {equipment_needed}, consider progressing to {suggested_reps} reps."
        ),
    },
    {
        "name": "心血管健康评估 / Cardiovascular Health Assessment",
        "old_name": "Cardiovascular Health Assessment",
        "text": (
            "您的静息心率{resting_bpm}bpm，心率储备使用率{pct_hrr}%，心血管健康水平为{cardiovascular_level}。\n"
            "Your resting HR {resting_bpm}bpm, {pct_hrr}% HR reserve usage, cardiovascular health level: {cardiovascular_level}."
        ),
    },
    {
        "name": "热量管理建议 / Calorie Management Advice",
        "old_name": "Calorie Management Advice",
        "text": (
            "您的热量平衡{cal_balance}千卡，预期消耗{expected_burn}千卡，建议{calorie_recommendation}以实现{weight_goal}。\n"
            "Your caloric balance {cal_balance}kcal, expected burn {expected_burn}kcal; {calorie_recommendation} for {weight_goal}."
        ),
    },
    {
        "name": "烹饪营养优化 / Cooking Nutrition Optimization",
        "old_name": "Cooking Nutrition Optimization",
        "text": (
            "您的{meal_name}使用{cooking_method}方式烹饪，准备{prep_time_min}分钟，烹饪{cook_time_min}分钟，营养评分{rating}。\n"
            "Your {meal_name} prepared via {cooking_method} in {prep_time_min}min prep, {cook_time_min}min cook, nutrition rating {rating}."
        ),
    },
    {
        "name": "全面健康洞察 / Comprehensive Health Insight",
        "old_name": "Comprehensive Health Insight",
        "text": (
            "您的综合评分：训练效率{training_efficiency}，肌肉专注{muscle_focus_score}，恢复指数{recovery_index}，心血管{cardiovascular_level}。\n"
            "Your overall scores: Training efficiency {training_efficiency}, muscle focus {muscle_focus_score}, recovery {recovery_index}, cardiovascular {cardiovascular_level}."
        ),
    },
    # 基于数据集新增的个性化模板
    {
        "name": "年龄与训练强度匹配 / Age-Training Intensity Match",
        "old_name": "Age-Training Intensity Match",
        "text": (
            "您当前{age}岁，静息心率{resting_bpm}bpm，训练心率{avg_bpm}bpm，训练强度与年龄匹配度良好。\n"
            "At {age} years old, your resting HR {resting_bpm}bpm and training HR {avg_bpm}bpm show good age-intensity match."
        ),
    },
    {
        "name": "性别与训练类型建议 / Gender-Based Workout Recommendation",
        "old_name": "Gender-Based Workout Recommendation",
        "text": (
            "作为{gender}性，您最常进行{workout_type}训练，平均燃烧{avg_calories}千卡，训练效果显著。\n"
            "As a {gender}, your most frequent {workout_type} workouts burn {avg_calories} kcal on average, showing effective results."
        ),
    },
    {
        "name": "身高体重比例分析 / Height-Weight Ratio Analysis",
        "old_name": "Height-Weight Ratio Analysis",
        "text": (
            "您的身高{height}米，体重{weight}公斤，BMI指数{bmi}，体脂率{fat_percentage}%，瘦体重{lean_mass_kg}公斤。\n"
            "Your height {height}m, weight {weight}kg, BMI {bmi}, body fat {fat_percentage}%, and lean mass {lean_mass_kg}kg."
        ),
    },
    {
        "name": "营养元素详细分析 / Detailed Nutrient Analysis",
        "old_name": "Detailed Nutrient Analysis",
        "text": (
            "您的日常营养：碳水{carbs}g，蛋白质{protein}g，脂肪{fat}g，总热量{calories_intake}kcal，糖分{sugar_g}g，钠{sodium_mg}mg，胆固醇{cholesterol_mg}mg。\n"
            "Your daily nutrition: carbs {carbs}g, protein {protein}g, fats {fat}g, total {calories_intake}kcal, sugar {sugar_g}g, sodium {sodium_mg}mg, cholesterol {cholesterol_mg}mg."
        ),
    },
    {
        "name": "训练动作与效果 / Exercise Benefits Analysis",
        "old_name": "Exercise Benefits Analysis",
        "text": (
            "您最常进行的训练动作是{name_of_exercise}，训练益处为{benefit}，每30分钟可燃烧{burns_calories_per_30min}千卡。\n"
            "Your most frequent exercise is {name_of_exercise}, which provides {benefit} and burns {burns_calories_per_30min} kcal per 30 minutes."
        ),
    },
    {
        "name": "餐食类型与营养搭配 / Meal Type Nutrition Balance",
        "old_name": "Meal Type Nutrition Balance",
        "text": (
            "您的{meal_type}采用{diet_type}饮食，使用{cooking_method}方式烹饪，份量{serving_size_g}g，营养评分{rating}分。\n"
            "Your {meal_type} follows {diet_type} diet, cooked via {cooking_method}, serving size {serving_size_g}g, nutrition rating {rating}."
        ),
    },
    {
        "name": "训练器材与难度评估 / Equipment and Difficulty Assessment",
        "old_name": "Equipment and Difficulty Assessment",
        "text": (
            "您使用{equipment_needed}进行{difficulty_level}难度的{name_of_exercise}训练，每组{reps}次，共{sets}组，针对{target_muscle_group}肌群。\n"
            "You use {equipment_needed} for {difficulty_level} level {name_of_exercise} with {sets} sets of {reps} reps, targeting {target_muscle_group}."
        ),
    },
    {
        "name": "身体部位与肌肉类型 / Body Part and Muscle Type",
        "old_name": "Body Part and Muscle Type",
        "text": (
            "您主要训练{body_part}部位，专注{type_of_muscle}肌肉类型，目标肌群为{target_muscle_group}。\n"
            "You primarily train {body_part} area, focusing on {type_of_muscle} muscle type, targeting {target_muscle_group}."
        ),
    },
    {
        "name": "烹饪时间与营养优化 / Cooking Time Nutrition Optimization",
        "old_name": "Cooking Time Nutrition Optimization",
        "text": (
            "您的{meal_name}准备时间{prep_time_min}分钟，烹饪时间{cook_time_min}分钟，营养评分{rating}分，建议优化烹饪时间以保留更多营养。\n"
            "Your {meal_name} takes {prep_time_min}min prep and {cook_time_min}min cooking, rated {rating}, consider optimizing cooking time to preserve nutrients."
        ),
    },
    {
        "name": "心率区间深度分析 / Heart Rate Zone Deep Analysis",
        "old_name": "Heart Rate Zone Deep Analysis",
        "text": (
            "您的训练心率{avg_bpm}bpm，最大心率{max_bpm}bpm，静息心率{resting_bpm}bpm，心率储备使用率{pct_hrr}%，最大心率百分比{pct_maxhr}%，处于{training_zone}训练区间。\n"
            "Your training HR {avg_bpm}bpm, max HR {max_bpm}bpm, resting HR {resting_bpm}bpm, HR reserve {pct_hrr}%, max HR {pct_maxhr}%, in {training_zone} zone."
        ),
    },
    {
        "name": "训练频率与经验匹配 / Training Frequency Experience Match",
        "old_name": "Training Frequency Experience Match",
        "text": (
            "您的经验等级为{experience_level}，每周训练{workout_frequency}天，每次训练平均{duration}小时，符合您的训练水平。\n"
            "Your experience level {experience_level}, training {workout_frequency} days/week, {duration} hours per session, matching your fitness level."
        ),
    },
    {
        "name": "热量消耗预期对比 / Calorie Burn Expectation Comparison",
        "old_name": "Calorie Burn Expectation Comparison",
        "text": (
            "您实际燃烧{cal_burned}千卡，预期消耗{expected_burn}千卡，热量平衡{cal_balance}千卡，训练效率{training_efficiency}。\n"
            "You burned {cal_burned}kcal, expected {expected_burn}kcal, balance {cal_balance}kcal, efficiency {training_efficiency}."
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