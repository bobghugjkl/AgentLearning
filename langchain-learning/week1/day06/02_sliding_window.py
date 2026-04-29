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


class State(TypedDict):
    messages: Annotated[list, add_messages]


# ── 关键：只保留最近6条消息 ───────────────────────────
MAX_MESSAGES = 6


def chat_node(state: State):
    messages = state["messages"]

    # 超过限制就截断，只保留最近的
    if len(messages) > MAX_MESSAGES:
        messages = messages[-MAX_MESSAGES:]
        print(f"⚠️ 历史过长，截断为最近 {MAX_MESSAGES} 条")

    full_messages = [
                        SystemMessage(content="你是一个友善的助手。")
                    ] + messages

    response = model.invoke(full_messages)
    return {"messages": [response]}


checkpointer = MemorySaver()
builder = StateGraph(State)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "window_test"}}


def chat(user_input: str):
    result = graph.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
    )
    return result["messages"][-1].content


# 连续聊8轮，看第8轮还记不记得第1轮说的话
print(chat("第1轮：我叫润实"))
print(chat("第2轮：我喜欢乃木坂46"))
print(chat("第3轮：我在学LangChain"))
print(chat("第4轮：我想去日本工作"))
print(chat("第5轮：随便说点什么"))
print(chat("第6轮：随便说点什么"))
print(chat("第7轮：随便说点什么"))
print("\n关键测试↓")
print(chat("第8轮：我叫什么名字？我喜欢什么？"))