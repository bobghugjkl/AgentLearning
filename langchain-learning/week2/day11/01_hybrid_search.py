import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
# from langchain.retrievers import EnsembleRetriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever

load_dotenv()

# ── 加载文档和切分 ─────────────────────────────────────
loader = PyPDFLoader("day08/test.pdf")
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
chunks = splitter.split_documents(pages)
print(f"共 {len(chunks)} 个 chunks")

# ── BM25 检索器 ───────────────────────────────────────
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 3
# 测试 BM25
results = bm25_retriever.invoke("CVR number")
print(f"\nBM25 搜索 'CVR number'：")
for doc in results:
    print(f"第{doc.metadata['page']+1}页：{doc.page_content[:100]}")


# ── 向量检索器 ─────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)
vectorstore = Chroma(
    persist_directory="day09/chroma_db",
    embedding_function=embeddings,
)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ── EnsembleRetriever 混合检索 ────────────────────────
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5],  # 两路各占50%权重
)

# ── 对比测试 ──────────────────────────────────────────
query = "CVR number requirements"
print(f"\n查询：{query}")

print("\n--- 纯向量检索 ---")
for doc in vector_retriever.invoke(query):
    print(f"第{doc.metadata['page']+1}页：{doc.page_content[:80]}")

print("\n--- 混合检索 ---")
for doc in ensemble_retriever.invoke(query):
    print(f"第{doc.metadata['page']+1}页：{doc.page_content[:80]}")

seen_pages = set()
unique_docs = []
for doc in ensemble_retriever.invoke(query):
    if doc.metadata['page'] not in seen_pages:
        seen_pages.add(doc.metadata['page'])
        unique_docs.append(doc)

print(unique_docs)