import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# ── 加载已有向量库 ─────────────────────────────────────
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

vectorstore = Chroma(
    persist_directory="day09/chroma_db",
    embedding_function=embeddings,
)

# ── 初始化模型 ────────────────────────────────────────
model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,  # RAG 用0，要稳定不要随机
)

print("RAG 系统初始化完成！")


# # ── RAG 核心函数 ──────────────────────────────────────
# def rag_answer(question: str) -> dict:
#     """
#     RAG 问答：检索相关文档块 → 组合 prompt → LLM 生成回答
#     """
#     # 第一步：检索相关块
#     relevant_docs = vectorstore.similarity_search(question, k=3)
#
#     # 第二步：把检索到的内容拼成 context
#     context = "\n\n".join([
#         f"[来源：第{doc.metadata['page'] + 1}页]\n{doc.page_content}"
#         for doc in relevant_docs
#     ])
#
#     # 第三步：构建 prompt
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """你是一个文档问答助手。
# 请根据下面提供的文档内容回答用户的问题。
# 如果文档中没有相关信息，请说"文档中未找到相关信息"。
# 不要编造文档中没有的内容。
#
# 文档内容：
# {context}"""),
#         ("human", "{question}"),
#     ])
#
#     # 第四步：调用 LLM
#     chain = prompt | model
#     response = chain.invoke({
#         "context": context,
#         "question": question,
#     })
#
#     return {
#         "answer": response.content,
#         "sources": [f"第{doc.metadata['page'] + 1}页" for doc in relevant_docs],
#     }
#
#
# # ── 测试 ──────────────────────────────────────────────
# result = rag_answer("What are the grade requirements for Industrial PhD applicants?")
# print(f"回答：{result['answer']}")
# print(f"\n来源：{result['sources']}")


def rag_answer(question: str) -> dict:
    # 第一步：检索
    relevant_docs = vectorstore.similarity_search(question, k=4)

    # 第二步：去重（同一页只保留一个）
    seen_pages = set()
    unique_docs = []
    for doc in relevant_docs:
        page = doc.metadata['page']
        if page not in seen_pages:
            seen_pages.add(page)
            unique_docs.append(doc)

    # 第三步：拼接 context
    context = "\n\n".join([
        f"[来源：第{doc.metadata['page'] + 1}页]\n{doc.page_content}"
        for doc in unique_docs
    ])

    # 第四步：构建 prompt 并调用
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个文档问答助手。
请根据下面提供的文档内容回答用户的问题。
如果文档中没有相关信息，请说"文档中未找到相关信息"。
不要编造文档中没有的内容。

文档内容：
{context}"""),
        ("human", "{question}"),
    ])

    chain = prompt | model

    # 流式输出
    print("回答：", end="", flush=True)
    full_response = ""
    for chunk in chain.stream({"context": context, "question": question}):
        print(chunk.content, end="", flush=True)
        full_response += chunk.content
    print()

    return {
        "answer": full_response,
        "sources": list(set([f"第{doc.metadata['page'] + 1}页" for doc in unique_docs])),
    }


# 测试
result = rag_answer("What are the grade requirements for Industrial PhD applicants?")
print(f"\n来源：{result['sources']}")

print("\n" + "=" * 40)

# 测试文档中没有的信息
result2 = rag_answer("What is the application fee?")
print(f"\n来源：{result2['sources']}")