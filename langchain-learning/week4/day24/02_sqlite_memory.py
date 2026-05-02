import os
import json
import sqlite3
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)


# ── 长期记忆存储（SQLite）────────────────────────────
class LongTermMemory:
    def __init__(self, db_path: str = "week4/day24/memories.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """创建记忆表"""
        self.conn.execute("""
                          CREATE TABLE IF NOT EXISTS memories
                          (
                              id
                              INTEGER
                              PRIMARY
                              KEY
                              AUTOINCREMENT,
                              user_id
                              TEXT
                              NOT
                              NULL,
                              memory
                              TEXT
                              NOT
                              NULL,
                              created_at
                              TIMESTAMP
                              DEFAULT
                              CURRENT_TIMESTAMP
                          )
                          """)
        self.conn.commit()
        print("数据库初始化完成")

    def save(self, user_id: str, memory: str):
        """存入一条记忆"""
        self.conn.execute(
            "INSERT INTO memories (user_id, memory) VALUES (?, ?)",
            (user_id, memory)
        )
        self.conn.commit()

    def get_all(self, user_id: str) -> list:
        """取出用户的所有记忆"""
        cursor = self.conn.execute(
            "SELECT memory FROM memories WHERE user_id = ? ORDER BY created_at",
            (user_id,)
        )
        return [row[0] for row in cursor.fetchall()]

    def clear(self, user_id: str):
        """清空用户记忆"""
        self.conn.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
        self.conn.commit()


# ── 记忆提取器（用LLM判断值得存什么）─────────────────
extract_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个记忆提取专家。
从用户的话里提取值得长期记住的关键信息。
只提取：姓名、职业背景、兴趣爱好、目标计划、重要偏好。
不要提取：闲聊、问题、临时性内容。

如果有值得记住的信息，用一句话总结。
如果没有，只输出"无"。"""),
    ("human", "{message}"),
])

extract_chain = extract_prompt | model | StrOutputParser()


def extract_and_save(ltm: LongTermMemory, user_id: str, message: str):
    """提取重要信息并存入长期记忆"""
    extracted = extract_chain.invoke({"message": message})
    if extracted.strip() != "无":
        ltm.save(user_id, extracted)
        print(f"  💾 存入记忆：{extracted}")
    else:
        print(f"  ⏭️ 无需存储")


# ── 带长期记忆的聊天函数 ──────────────────────────────
def chat_with_memory(ltm: LongTermMemory, user_id: str, question: str) -> str:
    """带长期记忆的对话"""
    # 从数据库加载记忆
    memories = ltm.get_all(user_id)
    memory_text = "\n".join(f"- {m}" for m in memories) if memories else "暂无记忆"

    messages = [
        SystemMessage(content=f"""你是一个友善的助手。
关于这个用户，你记得以下信息：
{memory_text}

请根据这些信息个性化地回答。"""),
        HumanMessage(content=question),
    ]

    response = model.invoke(messages)
    return response.content


# ── 测试 ──────────────────────────────────────────────
ltm = LongTermMemory()
user_id = "runshi"
ltm.clear(user_id)  # 清空旧记忆

print("\n=== 第一次会话：存入信息 ===")
messages = [
    "我叫润实，是中国石油大学软件工程硕士",
    "我最喜欢乃木坂46，特别是斋藤飞鸟",
    "我在学LangChain，目标是做Agent工程师",
    "今天天气真好啊",  # 测试：这条不应该被存
]

for msg in messages:
    print(f"\n用户：{msg}")
    extract_and_save(ltm, user_id, msg)

print("\n\n=== 查看存储的记忆 ===")
for m in ltm.get_all(user_id):
    print(f"  • {m}")

print("\n\n=== 第二次会话：使用记忆 ===")
questions = [
    "你还记得我叫什么吗？",
    "根据我的情况，你觉得我应该重点学什么？",
]

for q in questions:
    print(f"\n问：{q}")
    answer = chat_with_memory(ltm, user_id, q)
    print(f"答：{answer[:200]}")