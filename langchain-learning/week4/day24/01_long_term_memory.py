import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from mem0 import Memory
load_dotenv()

# 设置 OpenAI API Key 为 DeepSeek 的（Mem0 内部用）
os.environ["OPENAI_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com/v1"



model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.7,
)

# ── 初始化 Mem0（使用默认内置存储）─────────────────────
memory = Memory()
print("Mem0 初始化完成！")

# ── 测试1：存储记忆 ───────────────────────────────────
user_id = "runshi"

print("\n=== 第一次对话（存入记忆）===")
conversations = [
    "我叫润实，是中国石油大学的软件工程硕士",
    "我最喜欢乃木坂46，特别是斋藤飞鸟",
    "我在学习LangChain，目标是做Agent开发工程师",
    "我想以后去日本工作",
]

for msg in conversations:
    print(f"用户说：{msg}")
    memory.add(msg, user_id=user_id)

print("\n记忆存储完成！")

# ── 查看存了什么 ──────────────────────────────────────
print("\n=== 查看存储的记忆 ===")
all_memories = memory.get_all(user_id=user_id)
for i, mem in enumerate(all_memories, 1):
    print(f"{i}. {mem['memory']}")