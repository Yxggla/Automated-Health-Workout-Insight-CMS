import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox, scrolledtext
from typing import Optional

from database import DatabaseManager
from importer import DataImporter
from renderer import TemplateRenderer
from templates import seed_templates
from user_manager import UserManager


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

        user_mgmt_btn = tk.Button(control_frame, text="用户管理 / User Management", command=self.open_user_management)
        user_mgmt_btn.pack(side=tk.LEFT, padx=5)

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

    def open_user_management(self) -> None:
        """打开用户管理窗口"""
        UserManagementWindow(self.db, self)

    def run(self) -> None:
        self.root.mainloop()


class UserManagementWindow:
    """用户管理窗口"""

    def __init__(self, db: DatabaseManager, parent: InsightGUI) -> None:
        self.db = db
        self.parent = parent
        self.manager = UserManager(db)

        self.window = tk.Toplevel(parent.root)
        self.window.title("用户管理 / User Management")
        self.window.geometry("900x600")

        self._build_layout()
        self._refresh_user_list()

    def _build_layout(self) -> None:
        # 顶部按钮区域
        button_frame = tk.Frame(self.window)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="刷新列表 / Refresh", command=self._refresh_user_list).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="创建用户 / Create User", command=self._create_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="查看详情 / View Details", command=self._view_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="更新用户 / Update User", command=self._update_user).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="删除用户 / Delete User", command=self._delete_user).pack(side=tk.LEFT, padx=5)

        # 用户列表区域
        list_frame = tk.Frame(self.window)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(list_frame, text="用户列表 / User List", font=("Arial", 12, "bold")).pack(anchor="w")

        # 创建 Treeview 显示用户列表
        columns = ("ID", "Age", "Gender", "Weight", "Height", "BMI", "Experience")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 详情显示区域
        detail_frame = tk.LabelFrame(self.window, text="用户详情 / User Details")
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, width=40, height=25)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self._on_user_select)

    def _refresh_user_list(self) -> None:
        """刷新用户列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 加载用户数据
        users = self.manager.list_users(limit=100)
        for user in users:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    user["user_id"],
                    user["age"] or "N/A",
                    user["gender"] or "N/A",
                    user["weight"] or "N/A",
                    user["height"] or "N/A",
                    user["bmi"] or "N/A",
                    user["experience_level"] or "N/A",
                ),
            )

    def _on_user_select(self, event) -> None:
        """当选择用户时显示详情"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        user_id = item["values"][0]

        user = self.manager.get_user(user_id)
        if not user:
            return

        # 显示用户详情
        detail_lines = [f"用户 ID / User ID: {user_id}\n"]
        detail_lines.append("-" * 40)
        for key, value in user.items():
            if key != "user_id":
                detail_lines.append(f"{key}: {value or 'N/A'}")

        # 显示统计信息
        stats = self.manager.get_user_statistics(user_id)
        if stats:
            detail_lines.append("\n--- 统计信息 / Statistics ---")
            if stats.get("workout_stats"):
                detail_lines.append("\n训练统计 / Workout Stats:")
                for k, v in stats["workout_stats"].items():
                    detail_lines.append(f"  {k}: {v}")
            if stats.get("nutrition_stats"):
                detail_lines.append("\n营养统计 / Nutrition Stats:")
                for k, v in stats["nutrition_stats"].items():
                    detail_lines.append(f"  {k}: {v}")
            if stats.get("analysis_stats"):
                detail_lines.append("\n分析统计 / Analysis Stats:")
                for k, v in stats["analysis_stats"].items():
                    detail_lines.append(f"  {k}: {v}")

        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, "\n".join(detail_lines))

    def _create_user(self) -> None:
        """创建新用户对话框"""
        dialog = UserFormDialog(self.window, "创建用户 / Create User")
        if dialog.result:
            try:
                user_id = self.manager.create_user(**dialog.result)
                messagebox.showinfo("成功 / Success", f"用户创建成功！ID: {user_id}\nUser created successfully! ID: {user_id}")
                self._refresh_user_list()
                if hasattr(self.parent, "_load_user_list"):
                    self.parent._load_user_list()
            except Exception as e:
                messagebox.showerror("错误 / Error", f"创建失败: {e}\nFailed to create: {e}")

    def _view_user(self) -> None:
        """查看用户详情"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告 / Warning", "请先选择一个用户 / Please select a user first")
            return

        item = self.tree.item(selection[0])
        user_id = item["values"][0]
        self._on_user_select(None)

    def _update_user(self) -> None:
        """更新用户信息"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告 / Warning", "请先选择一个用户 / Please select a user first")
            return

        item = self.tree.item(selection[0])
        user_id = item["values"][0]

        user = self.manager.get_user(user_id)
        if not user:
            messagebox.showerror("错误 / Error", f"用户 {user_id} 不存在 / User {user_id} not found")
            return

        dialog = UserFormDialog(self.window, "更新用户 / Update User", initial_data=user)
        if dialog.result:
            try:
                success = self.manager.update_user(user_id, **dialog.result)
                if success:
                    messagebox.showinfo("成功 / Success", f"用户 {user_id} 更新成功！\nUser {user_id} updated successfully!")
                    self._refresh_user_list()
                    if hasattr(self.parent, "_load_user_list"):
                        self.parent._load_user_list()
                else:
                    messagebox.showerror("错误 / Error", "更新失败 / Update failed")
            except Exception as e:
                messagebox.showerror("错误 / Error", f"更新失败: {e}\nUpdate failed: {e}")

    def _delete_user(self) -> None:
        """删除用户"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告 / Warning", "请先选择一个用户 / Please select a user first")
            return

        item = self.tree.item(selection[0])
        user_id = item["values"][0]

        confirm = messagebox.askyesno(
            "确认删除 / Confirm Delete",
            f"确定要删除用户 {user_id} 吗？\nAre you sure you want to delete user {user_id}?",
        )
        if not confirm:
            return

        cascade = messagebox.askyesno(
            "级联删除 / Cascade Delete",
            "是否同时删除关联数据（训练、营养等）？\nDelete associated data (workouts, nutrition, etc.)?",
        )

        try:
            success = self.manager.delete_user(user_id, cascade=cascade)
            if success:
                messagebox.showinfo("成功 / Success", f"用户 {user_id} 已删除\nUser {user_id} deleted")
                self._refresh_user_list()
                if hasattr(self.parent, "_load_user_list"):
                    self.parent._load_user_list()
            else:
                messagebox.showerror("错误 / Error", "删除失败 / Delete failed")
        except Exception as e:
            messagebox.showerror("错误 / Error", f"删除失败: {e}\nDelete failed: {e}")


class UserFormDialog:
    """用户表单对话框"""

    def __init__(self, parent, title: str, initial_data: Optional[dict] = None) -> None:
        self.result = None
        self.initial_data = initial_data or {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._build_form()

    def _build_form(self) -> None:
        frame = tk.Frame(self.dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        fields = [
            ("age", "Age", float),
            ("gender", "Gender", str),
            ("weight", "Weight (kg)", float),
            ("height", "Height (cm)", float),
            ("fat_percentage", "Fat Percentage", float),
            ("lean_mass_kg", "Lean Mass (kg)", float),
            ("experience_level", "Experience Level", str),
            ("workout_frequency", "Workout Frequency", float),
            ("water_intake", "Water Intake (L)", float),
            ("resting_bpm", "Resting BPM", float),
        ]

        self.entries = {}
        for field_name, label, field_type in fields:
            row = tk.Frame(frame)
            row.pack(fill=tk.X, pady=5)

            tk.Label(row, text=f"{label}:", width=20, anchor="w").pack(side=tk.LEFT)
            entry = tk.Entry(row)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # 填充初始值
            if field_name in self.initial_data and self.initial_data[field_name] is not None:
                entry.insert(0, str(self.initial_data[field_name]))

            self.entries[field_name] = (entry, field_type)

        # 按钮
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=20)

        tk.Button(button_frame, text="确定 / OK", command=self._ok).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消 / Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)

    def _ok(self) -> None:
        """确定按钮处理"""
        self.result = {}
        for field_name, (entry, field_type) in self.entries.items():
            value = entry.get().strip()
            if value:
                try:
                    if field_type == float:
                        self.result[field_name] = float(value)
                    else:
                        self.result[field_name] = value
                except ValueError:
                    messagebox.showerror("错误 / Error", f"无效的 {field_name} 值 / Invalid {field_name} value")
                    return
            else:
                # 空值不添加到结果中（使用 None 表示跳过）
                pass

        self.dialog.destroy()

    def _cancel(self) -> None:
        """取消按钮处理"""
        self.dialog.destroy()


if __name__ == "__main__":
    gui = InsightGUI()
    gui.run()