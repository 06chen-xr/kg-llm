from neo4j import GraphDatabase
import pandas as pd

# Neo4j 配置
uri = "bolt://localhost:7687"  # 替换为你的 Neo4j 地址
username = "neo4j"
password = "12345678"

# 创建数据库驱动
driver = GraphDatabase.driver(uri, auth=(username, password))


# 定义查询函数
def query_neo4j_and_export_to_excel(query, output_file):
    # 开启会话
    with driver.session() as session:
        # 执行 Cypher 查询
        result = session.run(query)

        # 获取查询结果
        data = []
        columns = result.keys()
        for record in result:
            data.append([record[key] for key in columns])

        # 将结果转换为 DataFrame
        df = pd.DataFrame(data, columns=columns)

        # 导出到 Excel 文件
        df.to_excel(output_file, index=False)
        print(f"数据已成功导出到 {output_file}")


# 定义 Cypher 查询
cypher_query = """
MATCH (e1)-[r]->(e2)
RETURN e1.name AS from_name, labels(e1) AS from_labels, type(r) AS rel_type, e2.name AS to_name, labels(e2) AS to_labels
"""

# 导出结果到 Excel 文件
output_file = "graph_database_export.xlsx"
query_neo4j_and_export_to_excel(cypher_query, output_file)

# 关闭数据库连接
driver.close()