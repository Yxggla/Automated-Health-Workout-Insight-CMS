# Automated Health & Workout Insight CMS

Python + SQLite project that ingests the Kaggle **Smart Fitness & Nutrition Analytics Dataset** (`Final_data.csv`) and generates daily fitness/nutrition insights via templates.

## Requirements
- Python 3.9+
- `pandas` (built-in `sqlite3` is used; no other deps)

## Files
- `main.py` — CLI entrypoint (menu).
- `gui.py` — Tkinter GUI with template buttons and report display.
- `database.py` — schema and SQLite helper.
- `importer.py` — CSV importer -> normalized tables.
- `renderer.py` — template rendering (text/markdown/html).
- `templates.py` — default insight templates.

## Quickstart
1. Place the dataset CSV at `Final_data.csv` in this folder (or keep your existing `Final_data (1).csv`).
2. Install pandas if needed:
   ```bash
   pip install pandas
   ```
3a. Run the CLI:
   ```bash
   python main.py
   ```
3b. Run the GUI:
   ```bash
   python gui.py
   ```

## 运行环境说明（含可能情况）
- **推荐使用虚拟环境**：
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- **Tk 依赖（GUI 需要，CLI 不需要）**：
  - 官方 Python 安装包通常自带 Tk，直接建 venv 即可。
  - Homebrew 环境下需安装并暴露 Tcl/Tk：
    ```bash
    brew install tcl-tk python-tk@3.12
    export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"
    export LDFLAGS="-L/opt/homebrew/opt/tcl-tk/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk/include"
    ```
    然后再创建/激活 venv。
  - 检查 Tk 是否可用：`python3.12 -m tkinter`（弹出小窗口即正常）。
- **如果只想用 CLI**：不装 Tk 也能运行 `python main.py`，GUI 则需要 Tk。
- **每次新终端**：如果用 Homebrew+Tk，上面导出的 `PATH/CPPFLAGS/LDFLAGS` 需重新执行，或写入 shell 配置文件。
- **依赖列表**：`requirements.txt` 仅包含 `pandas`，其余为标准库。

## Menu Actions
1) **Import dataset into SQLite**  
   - Accepts a path prompt; defaults to `Final_data.csv` (auto-detects `Final_data (1).csv`).
2) **List templates**  
   - Shows seeded template IDs and names.
3) **Generate a report**  
   - Enter `template_id` and choose format: `text`, `markdown`, or `html`.
4) **Show SQL analytical summary**  
   - Prints aggregate stats (calories by workout type, top caloric deficit, macro averages).
5) **Exit**

## Output Notes
- Reports fill placeholders (e.g., `{avg_bpm}`, `{cal_balance}`, `{workout_type}`) via SQL aggregates, joins, and subqueries.
- HTML/Markdown options are simple wrappers; extend in `renderer.py` if you want richer styling.

## GUI Notes
- Buttons for each template (renders to the right panel).
- Output format selector (text/markdown/html).
- “Import Dataset” button opens a file picker; “Show Summary” prints aggregate stats to the panel.

## Resetting Data
- Re-running “Import dataset” clears and reloads the `user`, `workout`, `nutrition`, and `derived_metrics` tables.
