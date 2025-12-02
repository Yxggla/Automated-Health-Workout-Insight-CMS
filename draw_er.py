import sqlite3
import graphviz
import os

# 尝试导入 IPython.display，仅在 notebook 环境中使用
try:
    from IPython.display import display, HTML
    from IPython import get_ipython
    IN_NOTEBOOK = get_ipython() is not None and hasattr(get_ipython(), 'kernel')
except (ImportError, AttributeError):
    IN_NOTEBOOK = False

# 数据库文件名称
db_file = 'fitness.db'

# 1. 连接数据库并提取结构
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 提取表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [table[0] for table in cursor.fetchall()]

table_schemas = {}
relationships = []

# 提取每个表的列信息和外键关系
for table_name in tables:
    # 获取列信息 (cid, name, type, notnull, default_value, pk)
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    # 存储 (name, type, is_pk)
    table_schemas[table_name] = [
        (col[1], col[2], bool(col[5]))
        for col in columns
    ]

    # 获取外键信息 (id, seq, table, from, to, on_update, on_delete, match)
    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
    foreign_keys = cursor.fetchall()
    
    for fk in foreign_keys:
        # source_table, target_table, source_column, target_column
        relationships.append((table_name, fk[2], fk[3], fk[4]))

conn.close()

# 2. 使用 graphviz 生成 DOT 代码
dot = graphviz.Digraph(
    'ERD_fitness_db',
    comment='Fitness Database ER Diagram',
    graph_attr={'rankdir': 'LR', 'bgcolor': 'white'},
    node_attr={'shape': 'plaintext', 'fontname': 'Arial'},
    edge_attr={'fontname': 'Arial', 'fontsize': '10'}
)

# 添加实体（表）节点
for table_name, columns in table_schemas.items():
    # 使用 HTML-like 标签来格式化表结构
    label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
        <TR><TD COLSPAN="2" BGCOLOR="#3498DB" ALIGN="CENTER"><FONT COLOR="WHITE"><B>{table_name}</B></FONT></TD></TR>'''

    for col_name, col_type, is_pk in columns:
        pk_marker = "<B>PK</B>" if is_pk else "" # 标记主键
        col_display = f'<FONT COLOR="#1E8449">{col_name}</FONT>'
        
        # 检查是否为外键
        is_fk = any(r[0] == table_name and r[2] == col_name for r in relationships)
        if is_fk:
            col_display = f'<FONT COLOR="#C0392B">{col_name}</FONT>' # 标记外键 (红色)

        label += f'''
            <TR>
                <TD ALIGN="LEFT">{col_display}</TD>
                <TD ALIGN="LEFT"><FONT POINT-SIZE="10">{col_type} {pk_marker}</FONT></TD>
            </TR>'''
    
    label += '</TABLE>>'
    
    dot.node(table_name, label=label)

# 3. 添加关系（边）
# 在 Graphviz 中，我们可以使用 `crow` 箭头来模拟乌鸦脚（Crow's Foot）表示法中的“多”端。
# 我们知道所有关系都是 1 (users) -> M (其他表)。
for source_table, target_table, source_column, target_column in relationships:
    # target_table (users) 是 1 端
    # source_table (其他表) 是 M 端
    dot.edge(
        target_table, # 从 1 端 (users) 
        source_table, # 到 M 端 (其他表)
        headlabel='1', # 1 端的标签
        taillabel='M', # M 端的标签
        label=f'FK: {source_column} -> {target_column}',
        arrowhead='crow', # 使用 Crow's Foot 符号
        arrowtail='none',
        dir='forward' # 箭头方向从 1 指向 M
    )

# 4. 生成和显示/保存图表
if IN_NOTEBOOK:
    # 在 notebook 环境中直接显示
    display(graphviz.Source(dot.source))
else:
    # 在命令行环境中保存为文件
    output_file = 'ERD_fitness_db'
    print("正在生成 ER 图...")
    
    try:
        # 渲染为 PNG 格式
        result = dot.render(output_file, format='png', cleanup=True)
        if result:
            print(f"✅ ER 图已保存为: {output_file}.png")
        
        # 渲染为 SVG 格式
        result = dot.render(output_file, format='svg', cleanup=True)
        if result:
            print(f"✅ ER 图已保存为: {output_file}.svg")
        
        # 渲染为 PDF 格式
        result = dot.render(output_file, format='pdf', cleanup=True)
        if result:
            print(f"✅ ER 图已保存为: {output_file}.pdf")
        
        print(f"\n📁 文件已保存在当前目录: {os.getcwd()}")
    except Exception as e:
        print(f"\n❌ 生成图表时出错: {e}")
        print("\n提示: 请确保已安装系统级别的 graphviz:")
        print("  - macOS: brew install graphviz")
        print("  - Ubuntu/Debian: sudo apt-get install graphviz")
        print("  - Windows: 下载并安装 https://graphviz.org/download/")