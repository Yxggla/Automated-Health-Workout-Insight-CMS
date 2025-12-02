# 健身洞察 Web（Django + SQLite）

基于 Kaggle “Smart Fitness & Nutrition Analytics” 数据集的洞察系统。前端：Django + Tailwind；功能：模板渲染（文本输出）、用户筛选、汇总查看。业务库：`fitness.db`；Django 系统库：`db.sqlite3`（两者分离）。

## 快速启动（全新环境）
1) 准备环境
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2) 清理并创建数据库
   ```bash
   rm -f fitness.db db.sqlite3
   python manage.py migrate             # 仅在 db.sqlite3 中创建 Django 系统表
   ```

3) 导入业务数据到 fitness.db（确保 CSV 在根目录，如 Final_data (1).csv）
   ```bash
   python - <<'PY'
   from database import DatabaseManager
   from templates import seed_templates
   from importer import DataImporter
   db = DatabaseManager("fitness.db"); db.create_tables()
   seed_templates(db)
   DataImporter(db).import_csv("Final_data (1).csv", clear_existing=True)  # 或 Final_data.csv
   print("users rows:", db.execute("SELECT COUNT(*) AS c FROM users", fetchone=True)["c"])
   db.close()
   PY
   ```

4) 启动 Web 前端
   ```bash
   python manage.py runserver  # 默认 http://127.0.0.1:8000
   ```
   - 左侧：刷新模板、用户筛选、模板列表（点击即渲染）
   - 右侧：文本输出、汇总（可刷新）

## 主要文件
- fitness_site/settings.py：Django 配置（系统库 db.sqlite3）
- insights/views.py / insights/urls.py：接口与路由（使用 fitness.db）
- templates/insights/index.html：前端界面（Tailwind CDN）
- database.py：业务 SQLite schema/连接
- importer.py：CSV 导入到业务表
- renderer.py：模板渲染（占位符 → SQL）
- templates.py：默认模板及 seed
- user_manager.py：用户管理模块（CRUD 操作）

## 用户管理功能

### 命令行界面（main.py）
运行 `python main.py`，选择菜单选项 5 进入用户管理：
- 列出所有用户
- 查看用户详情（包括统计信息）
- 创建新用户
- 更新用户信息
- 删除用户（支持级联删除关联数据）

### GUI 界面（gui.py）
运行 `python gui.py`，点击"用户管理"按钮：
- 可视化用户列表（表格形式）
- 实时查看用户详情和统计信息
- 通过对话框创建/更新用户
- 删除用户（带确认提示）

### 编程接口（user_manager.py）
```python
from database import DatabaseManager
from user_manager import UserManager

db = DatabaseManager()
manager = UserManager(db)

# 创建用户
user_id = manager.create_user(
    age=25, gender="M", weight=70, height=175,
    experience_level="Intermediate"
)

# 查询用户
user = manager.get_user(user_id)
users = manager.list_users(limit=10)

# 更新用户
manager.update_user(user_id, weight=72, workout_frequency=4)

# 删除用户
manager.delete_user(user_id, cascade=True)  # cascade=True 会删除关联数据

# 获取用户统计信息
stats = manager.get_user_statistics(user_id)
```

## 备注
- 旧的 CLI/GUI 文件仍在，但当前推荐使用 Web 前端。
- 重置模板可在页面点击"刷新模板"或在代码中调用 `seed_templates(db)`。
- 用户管理功能已集成到 CLI 和 GUI 界面中，可直接使用。
