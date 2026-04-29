import os
import json
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from typing import Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.7,
)

# ── 工具定义 ──────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    fake_data = {
        "北京": "晴天，25°C，东风3级",
        "上海": "多云，22°C，南风2级",
        "广州": "小雨，28°C，西风1级",
        "东京": "晴天，20°C，微风",
    }
    return fake_data.get(city, f"{city}暂无天气数据")

@tool
def calculate(expression: str) -> str:
    """计算数学表达式，比如 1+1、25*4、100/5"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except:
        return f"计算出错：{expression}"

tools = [get_weather, calculate]

print("工具定义完成：", [t.name for t in tools])

# ── State ─────────────────────────────────────────────
class State(TypedDict):
    messages: Annotated[list, add_messages]

# ── 节点1：模型节点 ────────────────────────────────────
model_with_tools = model.bind_tools(tools)

def model_node(state: State):
    messages = state["messages"]
    full_messages = [
        SystemMessage(content="""你是一个友善的助手，名叫小助手。
你有两个工具：查天气和数学计算。
需要时主动使用工具，记住用户说过的所有信息。""")
    ] + messages
    response = model_with_tools.invoke(full_messages)
    return {"messages": [response]}

# ── 节点2：工具节点 ────────────────────────────────────
# ToolNode 自动执行所有 tool_calls，不用手写循环了！
tool_node = ToolNode(tools)

# ── 路由函数：决定下一步去哪 ───────────────────────────
def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"   # 有工具调用 → 去执行工具
    return END           # 没有 → 结束

# ── 构建图 ────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("model", model_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "model")
builder.add_conditional_edges("model", should_continue)
builder.add_edge("tools", "model")  # 工具执行完回到模型

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

print("图构建完成")

# ── 命令行交互循环 ─────────────────────────────────────
config = {"configurable": {"thread_id": "assistant_001"}}


def chat(user_input: str):
    """流式输出回复"""
    print("小助手：", end="", flush=True)

    for chunk, metadata in graph.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="messages",
    ):
        # 只打印模型节点的输出，不打印工具节点的
        if hasattr(chunk, "content") and chunk.content:
            if metadata.get("langgraph_node") == "model":
                print(chunk.content, end="", flush=True)

    print()  # 换行


def main():
    print("=" * 40)
    print("小助手已启动！输入 'quit' 退出")
    print("=" * 40)

    while True:
        user_input = input("\n你：").strip()

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("再见！")
            break

        chat(user_input)


if __name__ == "__main__":
    main()