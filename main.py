import sys
from pathlib import Path
from typing import Optional

from database import DatabaseManager
from importer import DataImporter
from renderer import TemplateRenderer
from templates import seed_templates
from user_manager import UserManager


def detect_csv_path() -> Optional[str]:
    for candidate in ["Final_data.csv", "Final_data (1).csv"]:
        if Path(candidate).exists():
            return candidate
    return None


def import_dataset(db: DatabaseManager) -> None:
    default_path = detect_csv_path() or "Final_data.csv"
    user_input = input(f"Path to CSV [{default_path}]: ").strip()
    csv_path = user_input or default_path

    importer = DataImporter(db)
    try:
        rows = importer.import_csv(csv_path)
        print(f"Imported {rows} rows from {csv_path}.")
    except Exception as exc:  # noqa: BLE001
        print(f"Import failed: {exc}")


def list_templates(db: DatabaseManager) -> None:
    rows = db.execute("SELECT template_id, template_name FROM templates ORDER BY template_id", fetchall=True)
    if not rows:
        print("No templates found.")
        return
    for row in rows:
        print(f"[{row['template_id']}] {row['template_name']}")


def generate_report(db: DatabaseManager) -> None:
    list_templates(db)
    try:
        template_id = int(input("Enter template_id to render: ").strip())
    except ValueError:
        print("Invalid template id.")
        return
    fmt = input("Output format (text/markdown/html) [text]: ").strip().lower() or "text"

    renderer = TemplateRenderer(db)
    try:
        report = renderer.render(template_id, output_format=fmt)
        print("\n--- Report ---")
        print(report)
        print("--------------\n")
    except Exception as exc:  # noqa: BLE001
        print(f"Rendering failed: {exc}")


def show_summary(db: DatabaseManager) -> None:
    print("\n--- SQL Analytical Summary ---")

    print("\nAverage calories burned by workout type:")
    rows = db.execute(
        """
        SELECT workout_type,
               ROUND(AVG(calories_burned), 2) AS avg_calories,
               ROUND(AVG(session_duration), 2) AS avg_duration,
               COUNT(*) AS sessions
        FROM workouts
        GROUP BY workout_type
        ORDER BY avg_calories DESC
        LIMIT 5
        """,
        fetchall=True,
    )
    for row in rows or []:
        print(
            f"- {row['workout_type']}: {row['avg_calories']} kcal (duration {row['avg_duration']} hrs across {row['sessions']} sessions)"
        )

    print("\nTop caloric deficit users:")
    rows = db.execute(
        """
        SELECT u.user_id,
               u.gender,
               ROUND(u.age, 1) AS age,
               ROUND(wa.cal_balance, 2) AS cal_balance,
               ROUND(w.session_duration, 2) AS session_duration
        FROM workout_analysis wa
        JOIN users u ON u.user_id = wa.user_id
        JOIN workouts w ON w.user_id = u.user_id
        WHERE wa.cal_balance IS NOT NULL
        ORDER BY wa.cal_balance ASC
        LIMIT 5
        """,
        fetchall=True,
    )
    for row in rows or []:
        print(
            f"- User {row['user_id']} ({row['gender']}, {row['age']}y): cal_balance {row['cal_balance']} with {row['session_duration']} hrs training"
        )

    print("\nMacro intake overview (averages):")
    row = db.execute(
        """
        SELECT ROUND(AVG(carbs), 2) AS carbs,
               ROUND(AVG(proteins), 2) AS proteins,
               ROUND(AVG(fats), 2) AS fats,
               ROUND(AVG(calories), 2) AS calories
        FROM nutrition
        """,
        fetchone=True,
    )
    if row:
        print(
            f"- Carbs {row['carbs']} g, Protein {row['proteins']} g, Fats {row['fats']} g, Calories {row['calories']} kcal"
        )

    # 新增：训练效率分析
    print("\nTraining efficiency analysis:")
    rows = db.execute(
        """
        SELECT w.workout_type,
               ROUND(AVG(wa.training_efficiency), 2) AS avg_efficiency,
               ROUND(AVG(wa.muscle_focus_score), 2) AS avg_focus,
               ROUND(AVG(wa.recovery_index), 2) AS avg_recovery
        FROM workouts w
        JOIN workout_analysis wa ON w.user_id = wa.user_id
        WHERE wa.training_efficiency IS NOT NULL
        GROUP BY w.workout_type
        ORDER BY avg_efficiency DESC
        LIMIT 5
        """,
        fetchall=True,
    )
    for row in rows or []:
        print(
            f"- {row['workout_type']}: Efficiency {row['avg_efficiency']}, Focus {row['avg_focus']}, Recovery {row['avg_recovery']}"
        )

    print("\n-------------------------------\n")


def list_users(db: DatabaseManager) -> None:
    """列出所有用户"""
    manager = UserManager(db)
    users = manager.list_users(limit=50)
    
    if not users:
        print("No users found.")
        return
    
    print(f"\n--- Users ({len(users)} found) ---")
    print(f"{'ID':<6} {'Age':<6} {'Gender':<8} {'Weight':<8} {'Height':<8} {'BMI':<6} {'Experience':<12}")
    print("-" * 70)
    for user in users:
        print(
            f"{user['user_id']:<6} "
            f"{user['age'] or 'N/A':<6} "
            f"{user['gender'] or 'N/A':<8} "
            f"{user['weight'] or 'N/A':<8} "
            f"{user['height'] or 'N/A':<8} "
            f"{user['bmi'] or 'N/A':<6} "
            f"{user['experience_level'] or 'N/A':<12}"
        )
    print()


def view_user(db: DatabaseManager) -> None:
    """查看单个用户详细信息"""
    try:
        user_id = int(input("Enter user_id to view: ").strip())
    except ValueError:
        print("Invalid user id.")
        return
    
    manager = UserManager(db)
    user = manager.get_user(user_id)
    
    if not user:
        print(f"User {user_id} not found.")
        return
    
    print(f"\n--- User {user_id} Details ---")
    for key, value in user.items():
        print(f"{key}: {value}")
    
    # 显示统计信息
    stats = manager.get_user_statistics(user_id)
    if stats:
        print("\n--- Statistics ---")
        if stats.get("workout_stats"):
            print("Workout Stats:")
            for k, v in stats["workout_stats"].items():
                print(f"  {k}: {v}")
        if stats.get("nutrition_stats"):
            print("Nutrition Stats:")
            for k, v in stats["nutrition_stats"].items():
                print(f"  {k}: {v}")
        if stats.get("analysis_stats"):
            print("Analysis Stats:")
            for k, v in stats["analysis_stats"].items():
                print(f"  {k}: {v}")
    print()


def create_user(db: DatabaseManager) -> None:
    """创建新用户"""
    manager = UserManager(db)
    
    print("\n--- Create New User ---")
    print("Enter user information (press Enter to skip optional fields):")
    
    try:
        age = input("Age: ").strip()
        age = float(age) if age else None
        
        gender = input("Gender (M/F/Other): ").strip() or None
        
        weight = input("Weight (kg): ").strip()
        weight = float(weight) if weight else None
        
        height = input("Height (cm): ").strip()
        height = float(height) if height else None
        
        fat_percentage = input("Fat Percentage: ").strip()
        fat_percentage = float(fat_percentage) if fat_percentage else None
        
        lean_mass_kg = input("Lean Mass (kg): ").strip()
        lean_mass_kg = float(lean_mass_kg) if lean_mass_kg else None
        
        experience_level = input("Experience Level (Beginner/Intermediate/Advanced): ").strip() or None
        
        workout_frequency = input("Workout Frequency (per week): ").strip()
        workout_frequency = float(workout_frequency) if workout_frequency else None
        
        water_intake = input("Water Intake (L): ").strip()
        water_intake = float(water_intake) if water_intake else None
        
        resting_bpm = input("Resting BPM: ").strip()
        resting_bpm = float(resting_bpm) if resting_bpm else None
        
        user_id = manager.create_user(
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            fat_percentage=fat_percentage,
            lean_mass_kg=lean_mass_kg,
            experience_level=experience_level,
            workout_frequency=workout_frequency,
            water_intake=water_intake,
            resting_bpm=resting_bpm,
        )
        print(f"User created successfully with ID: {user_id}")
    except ValueError as e:
        print(f"Invalid input: {e}")
    except Exception as e:
        print(f"Failed to create user: {e}")


def update_user(db: DatabaseManager) -> None:
    """更新用户信息"""
    try:
        user_id = int(input("Enter user_id to update: ").strip())
    except ValueError:
        print("Invalid user id.")
        return
    
    manager = UserManager(db)
    
    if not manager.get_user(user_id):
        print(f"User {user_id} not found.")
        return
    
    print(f"\n--- Update User {user_id} ---")
    print("Enter new values (press Enter to skip):")
    
    try:
        age = input("Age: ").strip()
        age = float(age) if age else None
        
        gender = input("Gender (M/F/Other): ").strip() or None
        
        weight = input("Weight (kg): ").strip()
        weight = float(weight) if weight else None
        
        height = input("Height (cm): ").strip()
        height = float(height) if height else None
        
        fat_percentage = input("Fat Percentage: ").strip()
        fat_percentage = float(fat_percentage) if fat_percentage else None
        
        lean_mass_kg = input("Lean Mass (kg): ").strip()
        lean_mass_kg = float(lean_mass_kg) if lean_mass_kg else None
        
        experience_level = input("Experience Level: ").strip() or None
        
        workout_frequency = input("Workout Frequency: ").strip()
        workout_frequency = float(workout_frequency) if workout_frequency else None
        
        water_intake = input("Water Intake (L): ").strip()
        water_intake = float(water_intake) if water_intake else None
        
        resting_bpm = input("Resting BPM: ").strip()
        resting_bpm = float(resting_bpm) if resting_bpm else None
        
        success = manager.update_user(
            user_id=user_id,
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            fat_percentage=fat_percentage,
            lean_mass_kg=lean_mass_kg,
            experience_level=experience_level,
            workout_frequency=workout_frequency,
            water_intake=water_intake,
            resting_bpm=resting_bpm,
        )
        
        if success:
            print(f"User {user_id} updated successfully.")
        else:
            print(f"Failed to update user {user_id}.")
    except ValueError as e:
        print(f"Invalid input: {e}")
    except Exception as e:
        print(f"Failed to update user: {e}")


def delete_user(db: DatabaseManager) -> None:
    """删除用户"""
    try:
        user_id = int(input("Enter user_id to delete: ").strip())
    except ValueError:
        print("Invalid user id.")
        return
    
    manager = UserManager(db)
    
    if not manager.get_user(user_id):
        print(f"User {user_id} not found.")
        return
    
    cascade = input("Delete associated data (workouts, nutrition, etc.)? (y/N): ").strip().lower() == "y"
    
    confirm = input(f"Are you sure you want to delete user {user_id}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Deletion cancelled.")
        return
    
    success = manager.delete_user(user_id, cascade=cascade)
    if success:
        print(f"User {user_id} deleted successfully.")
    else:
        print(f"Failed to delete user {user_id}.")


def user_management_menu(db: DatabaseManager) -> None:
    """用户管理子菜单"""
    menu = """
User Management
1. List all users
2. View user details
3. Create new user
4. Update user
5. Delete user
6. Back to main menu
Choose an option: """
    
    actions = {
        "1": list_users,
        "2": view_user,
        "3": create_user,
        "4": update_user,
        "5": delete_user,
    }
    
    while True:
        choice = input(menu).strip()
        if choice == "6":
            break
        action = actions.get(choice)
        if not action:
            print("Invalid choice. Try again.")
            continue
        action(db)


def main() -> None:
    db = DatabaseManager()
    db.create_tables()
    seed_templates(db)

    menu = """
Automated Health & Workout Insight CMS
1. Import dataset into SQLite
2. List templates
3. Generate a report using template_id
4. Show SQL analytical summary
5. User Management
6. Exit
Choose an option: """

    actions = {
        "1": import_dataset,
        "2": list_templates,
        "3": generate_report,
        "4": show_summary,
        "5": user_management_menu,
    }

    try:
        while True:
            choice = input(menu).strip()
            if choice == "6":
                print("Goodbye.")
                break
            action = actions.get(choice)
            if not action:
                print("Invalid choice. Try again.")
                continue
            action(db)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        db.close()
        sys.exit(0)


if __name__ == "__main__":
    main()