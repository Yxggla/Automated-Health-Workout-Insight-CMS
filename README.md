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

## 备注
- 旧的 CLI/GUI 文件仍在，但当前推荐使用 Web 前端。
- 重置模板可在页面点击“刷新模板”或在代码中调用 `seed_templates(db)`。
