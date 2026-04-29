import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from sentence_transformers import CrossEncoder

load_dotenv()

# ── 初始化所有组件 ─────────────────────────────────────
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)
vectorstore = Chroma(
    persist_directory="day09/chroma_db",
    embedding_function=embeddings,
)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

loader = PyPDFLoader("day08/test.pdf")
chunks = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50
).split_documents(loader.load())

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 6

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5],
)

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个文档问答助手。
只根据提供的文档内容回答，没有相关信息就说"文档中未找到"。
不要编造内容。

文档内容：
{context}"""),
    ("human", "{question}"),
])


# ── 完整 RAG Pipeline ─────────────────────────────────
def advanced_rag(question: str) -> dict:
    # 第一步：混合检索
    candidates = ensemble_retriever.invoke(question)

    # 第二步：Reranker 重排
    pairs = [[question, doc.page_content] for doc in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    top_docs = [doc for score, doc in ranked[:3]]

    # 第三步：去重
    seen, unique = set(), []
    for doc in top_docs:
        if doc.metadata['page'] not in seen:
            seen.add(doc.metadata['page'])
            unique.append(doc)

    # 第四步：拼接 context
    context = "\n\n".join([
        f"[第{doc.metadata['page'] + 1}页]\n{doc.page_content}"
        for doc in unique
    ])

    # 第五步：LLM 生成
    chain = prompt | model
    print("回答：", end="", flush=True)
    full_response = ""
    for chunk in chain.stream({"context": context, "question": question}):
        print(chunk.content, end="", flush=True)
        full_response += chunk.content
    print()

    return {
        "answer": full_response,
        "sources": [f"第{doc.metadata['page'] + 1}页" for doc in unique],
    }


# ── 测试 ──────────────────────────────────────────────
result = advanced_rag("What are the grade requirements for PhD candidates?")
print(f"\n来源：{result['sources']}")