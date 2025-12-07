import re
from typing import Dict, Optional

from database import DatabaseManager


class TemplateRenderer:
    """Render templates with SQL-backed placeholders.

    All placeholder queries are stored in the database `queries` table.
    """

    PLACEHOLDER_PATTERN = re.compile(r"{(.*?)}")

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.queries = self._load_queries()

    def _load_queries(self) -> Dict[str, str]:
        rows = self.db.execute("SELECT query_key, query_sql FROM queries", fetchall=True)
        if not rows:
            return {}
        return {r["query_key"]: r["query_sql"] for r in rows}

    def _render_placeholder(self, placeholder: str, user_id: Optional[int] = None) -> str:
        sql = self.queries.get(placeholder)
        if not sql:
            return "N/A"

        params: tuple = ()
        if user_id is not None:
            sql, params = self._apply_user_filter(sql, user_id)

        try:
            row = self.db.execute(sql, params, fetchone=True)
        except Exception as exc:  # noqa: BLE001
            return f"ERR: {exc}"

        if not row:
            return "N/A"

        # 优先取别名 val，否则取第一列
        if hasattr(row, "keys") and "val" in row.keys():
            val = row["val"]
        else:
            # sqlite Row 可使用索引访问
            val = row[0]

        if val is None:
            return "N/A"
        if isinstance(val, (int, float)):
            return str(round(val, 2))
        return str(val)

    def _apply_user_filter(self, sql: str, user_id: int) -> tuple[str, tuple]:
        """Attach user filter when possible.

        优先使用显式占位符 {user_id}；如果原 SQL 已含 user_id 列或多表复杂 join，则保持不变。
        对简单单表查询（users/workouts/nutrition/workout_analysis），注入 user_id 条件。
        """
        if "{user_id}" in sql:
            return sql.replace("{user_id}", "?"), (user_id,)

        lower_sql = sql.lower()
        if "user_id" in lower_sql:
            return sql, ()  # 已处理

        # 仅对常用单表查询尝试注入过滤
        target_tables = [" from users", " from workouts", " from nutrition", " from workout_analysis"]
        if not any(t in lower_sql for t in target_tables):
            return sql, ()

        # 已有 WHERE，追加
        if " where " in lower_sql:
            sql_with_filter = re.sub(
                r"\bwhere\b",
                "WHERE user_id = ? AND",
                sql,
                count=1,
                flags=re.IGNORECASE,
            )
            # 如果未替换成功则避免绑定错误
            if sql_with_filter == sql:
                return sql, ()
            return sql_with_filter, (user_id,)

        # 无 WHERE，在分组/排序/限制前插入
        insert_before = [" group by", " order by", " limit", " offset"]
        for kw in insert_before:
            idx = lower_sql.find(kw)
            if idx != -1:
                return sql[:idx] + " WHERE user_id = ?" + sql[idx:], (user_id,)

        # 直接追加 WHERE
        return sql + " WHERE user_id = ?", (user_id,)

    def _emphasize_numbers(self, text: str, fmt: str) -> str:
        """Highlight numeric values for markdown/html rendering."""
        import re

        if fmt == "markdown":
            return re.sub(r"(\d+(?:\.\d+)?)", r"**\g<1>**", text)
        if fmt == "html":
            return re.sub(r"(\d+(?:\.\d+)?)", r"<strong>\g<1></strong>", text)
        return text

    def render(self, template_id: int, output_format: str = "text", user_id: Optional[int] = None) -> str:
        tpl = self.db.execute(
            "SELECT template_text FROM templates WHERE template_id = ?",
            (template_id,),
            fetchone=True,
        )
        if not tpl:
            raise ValueError("Template not found")

        content = tpl["template_text"]
        placeholders = set(self.PLACEHOLDER_PATTERN.findall(content))
        for ph in placeholders:
            rendered = self._render_placeholder(ph, user_id=user_id)
            content = content.replace(f"{{{ph}}}", rendered)

        if output_format == "markdown":
            emphasized = self._emphasize_numbers(content, "markdown")
            return "## Fitness Report\n\n" + emphasized.replace("\n", "\n\n")

        if output_format == "html":
            emphasized = self._emphasize_numbers(content, "html")
            paragraphs = "".join(
                f"<p>{p.strip()}</p>" for p in emphasized.split("\n") if p.strip()
            )
            return paragraphs or emphasized.replace("\n", "<br>")

        return content
