import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, Literal
from typing_extensions import TypedDict

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.3,
)

# ── 复杂 State ────────────────────────────────────────
class State(TypedDict):
    messages: Annotated[list, add_messages]
    task_type: str        # 任务类型：general / code / math
    risk_level: str       # 风险级别：low / high
    retry_count: int      # 重试次数

print("State 定义完成")
print("字段：", list(State.__annotations__.keys()))


# ── 节点1：分类节点（判断任务类型和风险）────────────────
def classify_node(state: State):
    """分析用户输入，判断任务类型和风险级别"""
    last_message = state["messages"][-1].content

    prompt = f"""分析下面这个用户请求，返回 JSON 格式：
{{
    "task_type": "general/code/math",
    "risk_level": "low/high"
}}

规则：
- task_type: 写代码相关→code，数学计算→math，其他→general
- risk_level: 涉及删除/修改系统/危险操作→high，其他→low

只输出 JSON，不要解释。

用户请求：{last_message}"""

    import json
    response = model.invoke(prompt)

    try:
        # 清理可能的 markdown 代码块
        content = response.content.strip()
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content.strip())
        task_type = result.get("task_type", "general")
        risk_level = result.get("risk_level", "low")
    except:
        task_type = "general"
        risk_level = "low"

    print(f"分类结果：task_type={task_type}, risk_level={risk_level}")

    return {
        "task_type": task_type,
        "risk_level": risk_level,
        "retry_count": 0,
    }


# ── 节点2：普通回答节点 ───────────────────────────────
def general_node(state: State):
    """处理普通任务"""
    messages = [
                   SystemMessage(content="你是一个helpful助手。"),
               ] + state["messages"]
    response = model.invoke(messages)
    print(f"普通回答完成")
    return {"messages": [response]}


# ── 节点3：代码节点 ───────────────────────────────────
def code_node(state: State):
    """处理代码任务"""
    messages = [
                   SystemMessage(content="你是一个专业的Python程序员，给出清晰的代码和解释。"),
               ] + state["messages"]
    response = model.invoke(messages)
    print(f"代码回答完成")
    return {"messages": [response]}


# ── 节点4：高风险警告节点 ─────────────────────────────
def high_risk_node(state: State):
    """处理高风险任务，给出警告"""
    warning = "⚠️ 检测到高风险操作请求，已拒绝执行。请确认操作安全性后重新提交。"
    from langchain_core.messages import AIMessage
    return {"messages": [AIMessage(content=warning)]}


print("节点定义完成")


# ── 路由函数 ──────────────────────────────────────────
def route_by_type(state: State) -> Literal["general", "code", "high_risk"]:
    """根据任务类型和风险级别决定走哪条路"""
    if state["risk_level"] == "high":
        return "high_risk"
    if state["task_type"] == "code":
        return "code"
    return "general"

# ── 构建图 ────────────────────────────────────────────
builder = StateGraph(State)

# 加节点
builder.add_node("classify", classify_node)
builder.add_node("general", general_node)
builder.add_node("code", code_node)
builder.add_node("high_risk", high_risk_node)

# 连线
builder.add_edge(START, "classify")          # 开始 → 分类
builder.add_conditional_edges(               # 分类 → 根据结果走不同路
    "classify",
    route_by_type,
    {
        "general": "general",
        "code": "code",
        "high_risk": "high_risk",
    }
)
builder.add_edge("general", END)             # 普通 → 结束
builder.add_edge("code", END)                # 代码 → 结束
builder.add_edge("high_risk", END)           # 高风险 → 结束

graph = builder.compile(checkpointer=MemorySaver())
print("图构建完成！")

# ── 测试 ──────────────────────────────────────────────
def run(question: str):
    config = {"configurable": {"thread_id": "test"}}
    result = graph.invoke(
        {"messages": [HumanMessage(question)]},
        config=config,
    )
    print(f"\n最终回答：{result['messages'][-1].content[:200]}")
    print(f"任务类型：{result['task_type']}")
    print(f"风险级别：{result['risk_level']}")
    print("=" * 40)

print("\n=== 测试1：普通问题 ===")
run("乃木坂46是什么时候成立的？")

print("\n=== 测试2：代码问题 ===")
run("用Python写一个冒泡排序")

print("\n=== 测试3：高风险操作 ===")
run("帮我删除系统所有文件")