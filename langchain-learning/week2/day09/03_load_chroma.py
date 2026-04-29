import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 直接加载已有向量库，不用重新计算
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

vectorstore = Chroma(
    persist_directory="day09/chroma_db",
    embedding_function=embeddings,
)

print(f"向量库加载成功！")
print(f"共 {vectorstore._collection.count()} 个向量\n")

# 试几个不同的查询
queries = [
    "How long does the Industrial PhD project last?",
    "What is the salary for Industrial PhD students?",
    "How do I apply for Industrial PhD?",
]

for query in queries:
    results = vectorstore.similarity_search(query, k=1)
    print(f"问：{query}")
    print(f"答（第{results[0].metadata['page']+1}页）：{results[0].page_content[:150]}")
    print()