import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated
from typing_extensions import TypedDict

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.7,
)

# ── State 定义 ──────────────────────────────────────
# LangGraph 里所有节点共享这个状态
class State(TypedDict):
    messages: Annotated[list, add_messages]
    # Annotated[list, add_messages] 的意思：
    # messages 是个列表，每次更新用 add_messages 合并而不是覆盖

print("State 定义完成")


# ── 定义节点 ─────────────────────────────────────────
def chat_node(state: State):
    """聊天节点：拿到当前所有消息，调模型，返回回复"""
    messages = state["messages"]

    # 加上 system prompt
    full_messages = [
                        SystemMessage(content="你是一个友善的助手，记住用户说过的所有信息。")
                    ] + messages

    response = model.invoke(full_messages)
    return {"messages": [response]}  # 只返回新增的消息


# ── 构建图 ────────────────────────────────────────────
# MemorySaver 把每轮对话的 State 存在内存里
checkpointer = MemorySaver()

builder = StateGraph(State)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile(checkpointer=checkpointer)

print("图构建完成")

# ── 测试记忆效果 ──────────────────────────────────────
# thread_id 是会话ID，同一个 thread_id 共享记忆
config = {"configurable": {"thread_id": "test_001"}}

def chat(user_input: str):
    result = graph.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
    )
    # 取最后一条消息，就是模型的回复
    return result["messages"][-1].content

# 第一轮
print("第一轮：")
print(chat("我叫润实，我最喜欢乃木坂46"))

# 第二轮
print("\n第二轮：")
print(chat("我刚才说我最喜欢什么？"))

# 第三轮
print("\n第三轮：")
print(chat("我叫什么名字？"))