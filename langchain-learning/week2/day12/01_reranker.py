import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from sentence_transformers import CrossEncoder

load_dotenv()

# ── 加载已有向量库 ─────────────────────────────────────
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)
vectorstore = Chroma(
    persist_directory="day09/chroma_db",
    embedding_function=embeddings,
)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

# ── 重新加载 chunks 给 BM25 用 ────────────────────────
loader = PyPDFLoader("day08/test.pdf")
pages = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(pages)

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 6

# ── 混合检索 ──────────────────────────────────────────
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5],
)

# ── Reranker 模型 ─────────────────────────────────────
# CrossEncoder：同时看问题和文档，深度理解关系
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
)

print("初始化完成！")


def rerank_search(query: str, top_n: int = 3) -> list:
    """
    混合检索 + Reranker 重排序
    """
    # 第一步：混合检索，先拿 top10
    candidates = ensemble_retriever.invoke(query)
    print(f"混合检索到 {len(candidates)} 个候选块")

    # 第二步：用 Reranker 对每个块打分
    # CrossEncoder 同时输入 [问题, 文档块]，输出相关性分数
    pairs = [[query, doc.page_content] for doc in candidates]
    scores = reranker.predict(pairs)

    # 第三步：按分数重新排序
    ranked = sorted(
        zip(scores, candidates),
        key=lambda x: x[0],
        reverse=True,  # 分数高的排前面
    )

    # 第四步：取前 top_n 个
    return [doc for score, doc in ranked[:top_n]]


# ── 对比测试 ──────────────────────────────────────────
query = "What are the grade requirements for PhD candidates?"

print(f"\n查询：{query}")

print("\n--- 混合检索（未重排）---")
for doc in ensemble_retriever.invoke(query)[:3]:
    print(f"第{doc.metadata['page'] + 1}页：{doc.page_content[:100]}")

print("\n--- 混合检索 + Reranker ---")
for doc in rerank_search(query):
    print(f"第{doc.metadata['page'] + 1}页：{doc.page_content[:100]}")