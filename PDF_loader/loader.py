import json
from openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from neo4j import GraphDatabase
import requests


# ----------------------------
# 使用 DeepSeek API 进行知识抽取（基于官方样例）
# ----------------------------
def deepseek_extract_knowledge(text):
    """
    调用 DeepSeek API 从文本中抽取知识，并返回处理后的 JSON 格式知识条目字符串。
    请确保替换 <DeepSeek API Key> 和 API URL 为实际值。
    """
    prompt = (
            "请从以下文本中抽取出所有的重要知识点及它们之间的关系，\n"
            "并以 JSON 格式返回，每个条目包含 \"subject\"、\"relation\" 和 \"object\" 字段，格式如下：\n"
            "[\n"
            "  {\"subject\": \"主体1\", \"relation\": \"关系1\", \"object\": \"客体1\"},\n"
            "  {\"subject\": \"主体2\", \"relation\": \"关系2\", \"object\": \"客体2\"}\n"
            "]\n"
            "文本内容：\n" + text
    )

    client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    raw_output = response.choices[0].message.content
    print("DeepSeek 返回原始内容：", raw_output)
    return raw_output


def parse_json_from_output(output):
    """
    清理返回字符串中的 Markdown 包裹，并解析为 JSON 对象。
    """
    output = output.strip()
    if output.startswith("```") and output.endswith("```"):
        output = output[3:-3].strip()
    if output.startswith("json"):
        output = "\n".join(output.splitlines()[1:]).strip()
    return json.loads(output)


# ----------------------------
# Neo4j 连接及图谱更新函数
# ----------------------------
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "neo4j"  # 请修改为你的 Neo4j 密码

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def create_knowledge_graph(knowledge_entries):
    with driver.session() as session:
        for entry in knowledge_entries:
            subject = entry.get("subject")
            relation = entry.get("relation")
            object_ = entry.get("object")
            session.execute_write(create_relationship, subject, relation, object_)
    print("Neo4j 知识图谱更新完成！")


def create_relationship(tx, subject, relation, object_):
    query = (
        "MERGE (s:Entity {name: $subject}) "
        "MERGE (o:Entity {name: $object}) "
        "MERGE (s)-[r:RELATION {name: $relation}]->(o)"
    )
    tx.run(query, subject=subject, relation=relation, object=object_)


# ----------------------------
# 主流程：从 PDF 提取文本、按页分块进行知识抽取、构建图谱
# ----------------------------
def main():
    pdf_path = "C://Users//郭倍宁//Desktop//论文//PETFormer.pdf"  # 替换为实际 PDF 路径
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()  # 每个 Document 对象代表一页或一部分内容
    print("PDF 文本提取完成！共提取 {} 页文本。".format(len(documents)))

    all_knowledge_entries = []
    # 遍历每一页，进行知识抽取
    for i, doc in enumerate(documents):
        page_text = doc.page_content
        print(f"开始处理第 {i + 1} 页...")
        try:
            raw_output = deepseek_extract_knowledge(page_text)
            page_knowledge = parse_json_from_output(raw_output)
            print(f"第 {i + 1} 页抽取到的知识条目：", page_knowledge)
            all_knowledge_entries.extend(page_knowledge)
        except Exception as e:
            print(f"解析第 {i + 1} 页 JSON 数据出错，请检查返回格式。错误信息：{e}")
            print("返回内容：", raw_output)

    if not all_knowledge_entries:
        print("没有抽取到任何知识条目，退出程序。")
        return

    # 选项：可以进一步对 all_knowledge_entries 去重、整理等
    create_knowledge_graph(all_knowledge_entries)


if __name__ == "__main__":
    main()
