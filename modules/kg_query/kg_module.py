from neo4j import GraphDatabase

# 修改以下连接参数为你实际的 Neo4j 连接信息
NEO4J_URI = "bolt://172.20.3.117:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "neo4jneo4j"  # 请修改为你的 Neo4j 密码

# 创建 Neo4j 驱动
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def query_knowledge_graph(candidate_name: str) -> str:
    """
    根据候选矿物名称从 Neo4j 知识图谱中查询详细信息，
    返回格式化的字符串描述。如果未找到，则返回默认描述。

    参数:
      candidate_name (str): 矿物名称。

    返回:
      str: 格式化的详细描述信息。
    """
    try:
        with driver.session() as session:
            result = session.execute_read(_query_entity, candidate_name)
            if result is None:
                return "暂无详细信息"
            else:
                return result
    except Exception as e:
        print(f"查询知识图谱时出错: {e}")
        return "查询失败"


def _query_entity(tx, candidate_name: str):
    query = """
    MATCH (n {name: $name})-[r]-(m) 
    RETURN n, collect({relation: type(r), target: coalesce(m.name, '未知节点'), properties: properties(m)}) as relations 
    LIMIT 1
    """
    result = tx.run(query, name=candidate_name)
    record = result.single()

    if record is None:
        return "暂无详细信息"

    node = record["n"]
    relations = record["relations"]

    # 提取节点的基本信息
    properties = dict(node)
    name = properties.get("name", candidate_name)
    description = properties.get("description", "无描述信息")
    image = properties.get("image", "无图片")
    chemical = properties.get("chemical", "无化学信息")
    physical = properties.get("physical", "无物理信息")

    # 格式化基本信息
    node_info = f"**名称:** {name}\n**描述:** {description}\n**图片:** {image}\n**化学成分:** {chemical}\n**物理特性:** {physical}"

    # 处理关系信息
    relation_info_list = []
    for rel in relations:
        relation_type = rel["relation"]
        target_name = rel["target"]
        target_properties = rel["properties"]

        # 处理目标节点信息
        target_info = f"- **{relation_type}** -> {target_name}"
        if target_properties:
            prop_details = ", ".join(f"{k}: {v}" for k, v in target_properties.items())
            target_info += f" ({prop_details})"

        relation_info_list.append(target_info)

    relation_info = "\n".join(relation_info_list) if relation_info_list else "无关联信息"

    return f"{node_info}\n\n**关联关系:**\n{relation_info}"




if __name__ == "__main__":
    candidate = "孔雀石"  # 替换为你在图谱中存在的矿物名称
    info = query_knowledge_graph(candidate)
    print(f"知识图谱查询 [{candidate}]: {info}")
