import sys
from pathlib import Path
from typing import Optional

from database import DatabaseManager
from importer import DataImporter
from renderer import TemplateRenderer
from templates import seed_templates


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
        FROM workout
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
               ROUND(d.cal_balance, 2) AS cal_balance,
               ROUND(w.session_duration, 2) AS session_duration
        FROM derived_metrics d
        JOIN user u ON u.user_id = d.user_id
        JOIN workout w ON w.user_id = u.user_id
        WHERE d.cal_balance IS NOT NULL
        ORDER BY d.cal_balance ASC
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
               ROUND(AVG(calories_intake), 2) AS calories
        FROM nutrition
        """,
        fetchone=True,
    )
    if row:
        print(
            f"- Carbs {row['carbs']} g, Protein {row['proteins']} g, Fats {row['fats']} g, Calories {row['calories']} kcal"
        )
    print("\n-------------------------------\n")


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
5. Exit
Choose an option: """

    actions = {
        "1": import_dataset,
        "2": list_templates,
        "3": generate_report,
        "4": show_summary,
    }

    try:
        while True:
            choice = input(menu).strip()
            if choice == "5":
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
