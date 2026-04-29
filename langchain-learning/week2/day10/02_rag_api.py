import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

app = FastAPI()

# ── 初始化（启动时加载一次）────────────────────────────
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)
vectorstore = Chroma(
    persist_directory="day09/chroma_db",
    embedding_function=embeddings,
)
model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个文档问答助手。
只根据提供的文档内容回答，没有相关信息就说"文档中未找到"。

文档内容：
{context}"""),
    ("human", "{question}"),
])

# ── 请求体 ────────────────────────────────────────────
class Question(BaseModel):
    question: str
    k: int = 3  # 检索几个块，默认3

# ── 流式接口 ──────────────────────────────────────────
@app.post("/rag/stream")
def rag_stream(body: Question):
    # 检索 + 去重
    docs = vectorstore.similarity_search(body.question, k=body.k + 1)
    seen, unique = set(), []
    for doc in docs:
        if doc.metadata['page'] not in seen:
            seen.add(doc.metadata['page'])
            unique.append(doc)

    context = "\n\n".join([
        f"[第{doc.metadata['page']+1}页]\n{doc.page_content}"
        for doc in unique
    ])

    chain = prompt | model

    def generate():
        for chunk in chain.stream({
            "context": context,
            "question": body.question,
        }):
            yield chunk.content

    return StreamingResponse(generate(), media_type="text/plain")

# ── 普通接口（带来源）────────────────────────────────
@app.post("/rag/answer")
def rag_answer(body: Question):
    docs = vectorstore.similarity_search(body.question, k=body.k + 1)
    seen, unique = set(), []
    for doc in docs:
        if doc.metadata['page'] not in seen:
            seen.add(doc.metadata['page'])
            unique.append(doc)

    context = "\n\n".join([
        f"[第{doc.metadata['page']+1}页]\n{doc.page_content}"
        for doc in unique
    ])

    chain = prompt | model
    response = chain.invoke({
        "context": context,
        "question": body.question,
    })

    return {
        "answer": response.content,
        "sources": [f"第{doc.metadata['page']+1}页" for doc in unique],
    }