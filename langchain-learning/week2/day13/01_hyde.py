import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# ── 初始化 ────────────────────────────────────────────

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

# ── HyDE：生成假答案的 chain ──────────────────────────
hyde_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个文档问答助手。
请根据问题生成一个可能的答案，用英文回答，语气正式。
这个答案不需要完全正确，只需要和文档风格接近。
只输出答案，不要解释。"""),
    ("human", "{question}"),
])

hyde_chain = hyde_prompt | model | StrOutputParser()
# ── 测试 HyDE ─────────────────────────────────────────
question = "工业博士项目一般持续多长时间？"
# 生成假答案
hypothetical_answer = hyde_chain.invoke({"question": question})
print(f"原始问题：{question}")
print(f"\nHyDE假答案：{hypothetical_answer}")

# 用假答案检索
print("\n--- 用原始问题检索 ---")
for doc in vectorstore.similarity_search(question, k=2):
    print(f"第{doc.metadata['page']+1}页：{doc.page_content[:100]}")

print("\n--- 用假答案检索 ---")
for doc in vectorstore.similarity_search(hypothetical_answer, k=2):
    print(f"第{doc.metadata['page']+1}页：{doc.page_content[:100]}")


# ── 多查询改写 ────────────────────────────────────────
multi_query_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个检索优化助手。
把用户的问题改写成3个不同角度的英文问题，用于检索文档。
每行一个问题，只输出问题，不要编号和解释。"""),
    ("human", "{question}"),
])

multi_query_chain = multi_query_prompt | model | StrOutputParser()

question2 = "工业博士薪资待遇怎么样？"
queries = multi_query_chain.invoke({"question": question2})
print(f"\n原始问题：{question2}")
print(f"改写后的问题：\n{queries}")

# 用每个改写问题检索，合并结果
all_docs = []
for q in queries.strip().split("\n"):
    if q.strip():
        docs = vectorstore.similarity_search(q.strip(), k=2)
        all_docs.extend(docs)

# 去重
seen, unique_docs = set(), []
for doc in all_docs:
    if doc.metadata['page'] not in seen:
        seen.add(doc.metadata['page'])
        unique_docs.append(doc)

print(f"\n多查询检索到 {len(unique_docs)} 个不重复页面：")
for doc in unique_docs:
    print(f"第{doc.metadata['page']+1}页：{doc.page_content[:100]}")