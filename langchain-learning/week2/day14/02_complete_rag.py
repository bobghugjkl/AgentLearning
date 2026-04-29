import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

# ── 初始化 ─────────────────────────────────────────────
loader = PyPDFLoader("day08/test.pdf")
chunks = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50
).split_documents(loader.load())

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 5

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

# HyDE chain
hyde_chain = ChatPromptTemplate.from_messages([
    ("system", "根据问题生成一个可能的英文答案，语气正式，只输出答案。"),
    ("human", "{question}"),
]) | model | StrOutputParser()

# RAG prompt
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是文档问答助手。
只根据文档内容回答，没有相关信息就说"文档中未找到"。
不要编造内容。

文档内容：
{context}"""),
    ("human", "{question}"),
])

# ── 完整 RAG Pipeline ──────────────────────────────────
def complete_rag(question: str, use_hyde: bool = True) -> dict:
    # 第一步：HyDE
    search_query = question
    if use_hyde:
        search_query = hyde_chain.invoke({"question": question})
        print(f"HyDE假答案：{search_query[:80]}...")

    # 第二步：BM25 检索
    docs = bm25_retriever.invoke(search_query)

    # 第三步：去重
    seen, unique = set(), []
    for doc in docs:
        if doc.metadata['page'] not in seen:
            seen.add(doc.metadata['page'])
            unique.append(doc)

    # 第四步：生成
    context = "\n\n".join([
        f"[第{doc.metadata['page']+1}页]\n{doc.page_content}"
        for doc in unique
    ])
    chain = rag_prompt | model | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    return {
        "answer": answer,
        "sources": [f"第{doc.metadata['page']+1}页" for doc in unique],
    }

# ── FastAPI ────────────────────────────────────────────
app = FastAPI(title="Complete RAG System")

class Question(BaseModel):
    question: str
    use_hyde: bool = True

@app.post("/ask")
def ask(body: Question):
    return complete_rag(body.question, body.use_hyde)

@app.post("/ask/stream")
def ask_stream(body: Question):
    search_query = body.question
    if body.use_hyde:
        search_query = hyde_chain.invoke({"question": body.question})

    docs = bm25_retriever.invoke(search_query)
    seen, unique = set(), []
    for doc in docs:
        if doc.metadata['page'] not in seen:
            seen.add(doc.metadata['page'])
            unique.append(doc)

    context = "\n\n".join([
        f"[第{doc.metadata['page']+1}页]\n{doc.page_content}"
        for doc in unique
    ])

    def generate():
        chain = rag_prompt | model
        for chunk in chain.stream({"context": context, "question": body.question}):
            yield chunk.content

    return StreamingResponse(generate(), media_type="text/plain")

# ── 命令行测试 ─────────────────────────────────────────
if __name__ == "__main__":
    print("=== Week 2 收官项目：完整 RAG 系统 ===\n")

    questions = [
        "工业博士项目一般持续多长时间？",
        "What are the grade requirements?",
        "申请费用是多少？",  # 文档里没有，测试幻觉防御
    ]

    for q in questions:
        print(f"问：{q}")
        result = complete_rag(q)
        print(f"答：{result['answer'][:200]}")
        print(f"来源：{result['sources']}")
        print()