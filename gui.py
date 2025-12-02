import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox, scrolledtext
from typing import Optional

from database import DatabaseManager
from importer import DataImporter
from renderer import TemplateRenderer
from templates import seed_templates


def detect_csv_path() -> Optional[str]:
    for candidate in ["Final_data.csv", "Final_data (1).csv"]:
        # 修复文件路径检测逻辑
        try:
            if filedialog and hasattr(filedialog, 'os') and filedialog.os.path.exists(candidate):
                return candidate
        except:
            pass
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
        self.root.geometry("1000x700")  # 增加窗口大小以容纳更多内容

        self.format_var = tk.StringVar(value="text")
        self.user_var = tk.StringVar(value="all")

        self._build_layout()
        self._load_user_list()
        self._load_template_buttons()

    def _build_layout(self) -> None:
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        import_btn = tk.Button(control_frame, text="导入数据 / Import Dataset", command=self.import_dataset)
        import_btn.pack(side=tk.LEFT, padx=5)

        summary_btn = tk.Button(control_frame, text="查看汇总 / Show Summary", command=self.show_summary)
        summary_btn.pack(side=tk.LEFT, padx=5)

        # 新增：刷新模板按钮
        refresh_btn = tk.Button(control_frame, text="刷新模板 / Refresh Templates", command=self._load_template_buttons)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="输出格式 / Output format:").pack(side=tk.LEFT, padx=10)
        for fmt in ["text", "markdown", "html"]:
            tk.Radiobutton(
                control_frame, text=fmt.title(), variable=self.format_var, value=fmt
            ).pack(side=tk.LEFT)
        
        tk.Label(control_frame, text="用户 / User:").pack(side=tk.LEFT, padx=10)
        self.user_combo = tk.ttk.Combobox(control_frame, textvariable=self.user_var, width=15, state="readonly")
        self.user_combo.pack(side=tk.LEFT, padx=5)

        # 左侧模板区域
        left_frame = tk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.templates_frame = tk.LabelFrame(left_frame, text="模板 / Templates")
        self.templates_frame.pack(fill=tk.BOTH, expand=True)

        # 右侧输出区域
        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加输出格式提示
        format_label = tk.Label(right_frame, text="输出内容 / Output:", font=("Arial", 10, "bold"))
        format_label.pack(anchor="w")

        self.output = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=80, height=30)
        self.output.pack(fill=tk.BOTH, expand=True)

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
        
        # 创建滚动区域用于模板按钮
        canvas = tk.Canvas(self.templates_frame)
        scrollbar = tk.Scrollbar(self.templates_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for row in rows:
            btn = tk.Button(
                scrollable_frame,
                text=f"[{row['template_id']}] {row['template_name']}",
                command=lambda tid=row["template_id"]: self.render_template(tid),
                width=35,
                anchor="w",
                wraplength=250  # 允许文本换行
            )
            btn.pack(fill=tk.X, padx=5, pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
            # 导入成功后刷新用户列表和模板按钮
            self._load_user_list()
            self._load_template_buttons()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Import failed", str(exc))

    def _load_user_list(self) -> None:
        """加载用户列表到下拉框"""
        rows = self.db.execute(
            "SELECT user_id FROM users ORDER BY user_id", fetchall=True
        )
        user_options = ["所有用户 (平均值) / All Users (Average)"]
        self.user_id_map = {"所有用户 (平均值) / All Users (Average)": None}
        
        for row in rows or []:
            user_id = row["user_id"]
            user_option = f"用户 {user_id} / User {user_id}"
            user_options.append(user_option)
            self.user_id_map[user_option] = user_id
        
        self.user_combo["values"] = user_options

    def render_template(self, template_id: int) -> None:
        fmt = self.format_var.get()
        selected_user = self.user_var.get()
        user_id = self.user_id_map.get(selected_user) if hasattr(self, 'user_id_map') else None
        
        try:
            rendered = self.renderer.render(template_id, output_format=fmt, user_id=user_id)
            self._set_output(rendered)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Render failed", str(exc))


    def show_summary(self) -> None:
        summary_lines = ["SQL Analytical Summary / SQL分析汇总"]

        # 更新表名和字段名
        rows = self.db.execute(
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
        summary_lines.append("\n按训练类型平均燃烧卡路里 / Average calories burned by workout type:")
        for row in rows or []:
            summary_lines.append(
                f"- {row['workout_type']}: {row['avg_calories']} kcal | {row['avg_duration']} hrs | {row['sessions']} 场/ sessions"
            )

        # 更新表名和字段名
        rows = self.db.execute(
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
        summary_lines.append("\n卡路里赤字排名 / Top caloric deficit users:")
        for row in rows or []:
            summary_lines.append(
                f"- 用户 {row['user_id']} / User {row['user_id']} ({row['gender']}, {row['age']}y): 热量平衡 cal_balance {row['cal_balance']} | 训练 {row['session_duration']} 小时 hrs"
            )

        # 修复：使用正确的字段名 calories 而不是 calories_intake
        row = self.db.execute(
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
            summary_lines.append(
                f"\n平均摄入 / Macro averages: 碳水 carbs {row['carbs']} g | 蛋白 protein {row['proteins']} g | 脂肪 fats {row['fats']} g | 热量 calories {row['calories']} kcal"
            )

        # 新增：训练效率分析
        summary_lines.append("\n训练效率分析 / Training Efficiency Analysis:")
        rows = self.db.execute(
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
            summary_lines.append(
                f"- {row['workout_type']}: 效率 {row['avg_efficiency']} | 专注度 {row['avg_focus']} | 恢复指数 {row['avg_recovery']}"
            )

        # 新增：用户经验等级分布
        summary_lines.append("\n用户经验等级分布 / User Experience Level Distribution:")
        rows = self.db.execute(
            """
            SELECT experience_level, COUNT(*) AS count
            FROM users
            WHERE experience_level IS NOT NULL AND experience_level != ''
            GROUP BY experience_level
            ORDER BY count DESC
            """,
            fetchall=True,
        )
        for row in rows or []:
            summary_lines.append(f"- {row['experience_level']}: {row['count']} 用户/users")

        self._set_output("\n".join(summary_lines))
    

    def _set_output(self, text: str) -> None:
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    gui = InsightGUI()
    gui.run()