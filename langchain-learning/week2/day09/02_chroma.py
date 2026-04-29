import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# ── 加载并切分文档 ─────────────────────────────────────
loader = PyPDFLoader("day08/test.pdf")
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
chunks = splitter.split_documents(pages)
print(f"共 {len(chunks)} 个 chunks")

# ── 初始化 Embedding 模型 ──────────────────────────────
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

# ── 把 chunks 存进 Chroma 向量库 ───────────────────────
# persist_directory 指定存储位置，下次直接加载不用重新计算
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="day09/chroma_db",
)

print(f"向量库创建完成！")
print(f"存储位置：day09/chroma_db")

# ── 语义检索 ──────────────────────────────────────────
query = "What are the grade requirements for applicants?"

# 找最相关的3块内容
results = vectorstore.similarity_search(query, k=3)

print(f"\n查询：{query}")
print(f"找到 {len(results)} 个相关块\n")

for i, doc in enumerate(results):
    print(f"=== 第{i+1}个结果 ===")
    print(f"来源：第{doc.metadata['page']+1}页")
    print(f"内容：{doc.page_content[:200]}")
    print()