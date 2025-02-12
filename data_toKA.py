from neo4j import GraphDatabase
import json


# Neo4j 数据库连接
class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_entity(self, entity_name, entity_type):
        with self.driver.session() as session:
            query = """
            MERGE (e:Entity {name: $entity_name})
            ON CREATE SET e.type = $entity_type
            RETURN e
            """
            session.run(query, entity_name=entity_name, entity_type=entity_type)

    def create_relationship(self, start_entity, rel_type, end_entity):
        with self.driver.session() as session:
            query = """
            MATCH (a:Entity {name: $start_entity})
            MATCH (b:Entity {name: $end_entity})
            MERGE (a)-[r:RELATION {type: $rel_type}]->(b)
            RETURN r
            """
            session.run(query, start_entity=start_entity, rel_type=rel_type, end_entity=end_entity)


# 解析 JSON 文件
def parse_json(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data['实体列表'], data['关系列表']


# 将实体和关系插入到图数据库
def import_to_neo4j(neo4j_handler, entities, relationships):
    # 插入实体
    for entity in entities:
        neo4j_handler.create_entity(entity['实体名称'], entity['实体类型'])

    # 插入关系
    for relationship in relationships:
        neo4j_handler.create_relationship(
            relationship['起始实体'],
            relationship['关系类型'],
            relationship['目标实体']
        )

from neo4j import GraphDatabase

# Connect to Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"  # Replace with your password

driver = GraphDatabase.driver(uri, auth=(username, password))

# Create function to add relationships
def create_graph(session, triples):
    for triple in triples:
        session.run(
            """
            MERGE (a:Entity {name: $start})
            MERGE (b:Entity {name: $end})
            MERGE (a)-[:$relation]->(b)
            """,
            start=triple["StartEntity"],
            end=triple["TargetEntity"],
            relation=triple["Relation"]
        )



print("Graphs created successfully!")
# 主程序
if __name__ == "__main__":

    def json_to_neo4j(path):
        # Neo4j 数据库连接参数
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "12345678"

        # 连接到 Neo4j
        neo4j_handler = Neo4jHandler(uri, user, password)

        # 解析 JSON 文件
        entities, relationships = parse_json("data.json")

        # 将数据插入到图数据库
        import_to_neo4j(neo4j_handler, entities, relationships)

        # 关闭数据库连接
        neo4j_handler.close()


    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"

    # Define all triple sets
    dataset1 = [
  {
    "StartEntity": "Typhoon",
    "Relation": "Causes",
    "TargetEntity": "High Heat"
  },
  {
    "StartEntity": "Typhoon",
    "Relation": "Causes",
    "TargetEntity": "Local Severe Convective Weather"
  },
  {
    "StartEntity": "Typhoon",
    "Relation": "Causes",
    "TargetEntity": "Thunderstorm Weather"
  },
  {
    "StartEntity": "Typhoon",
    "Relation": "Causes",
    "TargetEntity": "Ozone Pollution"
  },
  {
    "StartEntity": "Typhoon",
    "Relation": "Causes",
    "TargetEntity": "Haze"
  },
  {
    "StartEntity": "High Heat",
    "Relation": "Causes",
    "TargetEntity": "Hot Thunderstorms"
  },
  {
    "StartEntity": "Thunderstorm Weather",
    "Relation": "Causes",
    "TargetEntity": "Short-Term Gusts"
  }
]
    datasets = [dataset1]

    # Use Neo4j to create graphs
    with driver.session() as session:
        for i, dataset in enumerate(datasets, start=1):
            print(f"Creating graph {i}...")
            create_graph(session, dataset)