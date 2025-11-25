import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from typing import Optional

from database import DatabaseManager
from importer import DataImporter
from renderer import TemplateRenderer
from templates import seed_templates


def detect_csv_path() -> Optional[str]:
    for candidate in ["Final_data.csv", "Final_data (1).csv"]:
        if filedialog and filedialog.os.path.exists(candidate):  # type: ignore[attr-defined]
            return candidate
    return None


class InsightGUI:
    def __init__(self) -> None:
        self.db = DatabaseManager()
        self.db.create_tables()
        seed_templates(self.db)
        self.importer = DataImporter(self.db)
        self.renderer = TemplateRenderer(self.db)

        self.root = tk.Tk()
        self.root.title("自动化健身洞察 CMS | Automated Health & Workout Insight CMS")
        self.root.geometry("900x600")

        self.format_var = tk.StringVar(value="text")

        self._build_layout()
        self._load_template_buttons()

    def _build_layout(self) -> None:
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        import_btn = tk.Button(control_frame, text="导入数据 / Import Dataset", command=self.import_dataset)
        import_btn.pack(side=tk.LEFT, padx=5)

        summary_btn = tk.Button(control_frame, text="查看汇总 / Show Summary", command=self.show_summary)
        summary_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="输出格式 / Output format:").pack(side=tk.LEFT, padx=10)
        for fmt in ["text", "markdown", "html"]:
            tk.Radiobutton(
                control_frame, text=fmt.title(), variable=self.format_var, value=fmt
            ).pack(side=tk.LEFT)

        self.templates_frame = tk.LabelFrame(self.root, text="模板 / Templates")
        self.templates_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80)
        self.output.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _clear_template_buttons(self) -> None:
        for child in self.templates_frame.winfo_children():
            child.destroy()

    def _load_template_buttons(self) -> None:
        self._clear_template_buttons()
        rows = self.db.execute(
            "SELECT template_id, template_name FROM templates ORDER BY template_id", fetchall=True
        )
        if not rows:
            tk.Label(self.templates_frame, text="No templates found.").pack(anchor="w", padx=5, pady=5)
            return
        for row in rows:
            btn = tk.Button(
                self.templates_frame,
                text=f"[{row['template_id']}] {row['template_name']}",
                command=lambda tid=row["template_id"]: self.render_template(tid),
                width=30,
                anchor="w",
            )
            btn.pack(fill=tk.X, padx=5, pady=2)

    def import_dataset(self) -> None:
        initial = detect_csv_path()
        csv_path = filedialog.askopenfilename(
            title="Select dataset CSV",
            initialfile=initial or "Final_data.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not csv_path:
            return
        try:
            rows = self.importer.import_csv(csv_path)
            messagebox.showinfo("Import complete", f"Imported {rows} rows from {csv_path}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Import failed", str(exc))

    def render_template(self, template_id: int) -> None:
        fmt = self.format_var.get()
        try:
            rendered = self.renderer.render(template_id, output_format=fmt)
            self._set_output(rendered)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Render failed", str(exc))

    def show_summary(self) -> None:
        summary_lines = ["SQL Analytical Summary"]

        rows = self.db.execute(
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
        summary_lines.append("\nAverage calories burned by workout type:")
        for row in rows or []:
            summary_lines.append(
                f"- {row['workout_type']}: {row['avg_calories']} kcal | {row['avg_duration']} hrs | {row['sessions']} 场/ sessions"
            )

        rows = self.db.execute(
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
        summary_lines.append("\n卡路里赤字排名 / Top caloric deficit users:")
        for row in rows or []:
            summary_lines.append(
                f"- 用户 {row['user_id']} / User {row['user_id']} ({row['gender']}, {row['age']}y): 热量平衡 cal_balance {row['cal_balance']} | 训练 {row['session_duration']} 小时 hrs"
            )

        row = self.db.execute(
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
            summary_lines.append(
                f"\n平均摄入 / Macro averages: 碳水 carbs {row['carbs']} g | 蛋白 protein {row['proteins']} g | 脂肪 fats {row['fats']} g | 热量 calories {row['calories']} kcal"
            )

        self._set_output("\n".join(summary_lines))

    def _set_output(self, text: str) -> None:
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    gui = InsightGUI()
    gui.run()
