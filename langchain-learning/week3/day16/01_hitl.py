import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from typing import Annotated, Literal
from typing_extensions import TypedDict

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

# ── State ─────────────────────────────────────────────
class State(TypedDict):
    messages: Annotated[list, add_messages]
    risk_level: str
    approved: bool   # 人工是否批准

print("初始化完成")


# ── 节点1：风险评估 ───────────────────────────────────
def assess_risk(state: State):
    """评估用户请求的风险级别"""
    last_msg = state["messages"][-1].content

    # 简单规则判断风险（生产环境用LLM判断）
    high_risk_keywords = ["删除", "清空", "格式化", "delete", "remove", "drop"]
    is_high_risk = any(kw in last_msg.lower() for kw in high_risk_keywords)

    risk = "high" if is_high_risk else "low"
    print(f"风险评估：{risk}")
    return {"risk_level": risk, "approved": not is_high_risk}


# ── 节点2：人工审批（HIL 核心）────────────────────────
def human_approval(state: State):
    """
    暂停执行，等待人工审批
    interrupt() 会：
    1. 把当前 State 存到 checkpointer
    2. 把 interrupt 的值返回给调用方
    3. 暂停图的执行
    """
    last_msg = state["messages"][-1].content

    # 暂停！把需要确认的信息发给用户
    user_decision = interrupt({
        "message": f"⚠️ 检测到高风险操作：\n'{last_msg}'\n\n请确认是否执行？",
        "options": ["确认执行", "取消"],
    })

    # 用户回复后从这里继续
    approved = user_decision == "确认执行"
    print(f"人工决策：{'批准' if approved else '拒绝'}")
    return {"approved": approved}


# ── 节点3：执行操作 ───────────────────────────────────
def execute_action(state: State):
    """执行批准后的操作"""
    if state["risk_level"] == "high" and not state["approved"]:
        return {"messages": [AIMessage(content="操作已取消。")]}

    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}


# ── 路由函数 ──────────────────────────────────────────
def route_by_risk(state: State) -> Literal["human_approval", "execute"]:
    if state["risk_level"] == "high":
        return "human_approval"
    return "execute"


# ── 构建图 ────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("assess", assess_risk)
builder.add_node("human_approval", human_approval)
builder.add_node("execute", execute_action)

builder.add_edge(START, "assess")
builder.add_conditional_edges("assess", route_by_risk, {
    "human_approval": "human_approval",
    "execute": "execute",
})
builder.add_edge("human_approval", "execute")
builder.add_edge("execute", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
print("图构建完成！")

# ── 测试 HIL ──────────────────────────────────────────
config = {"configurable": {"thread_id": "hitl_test"}}

print("\n=== 测试1：低风险操作（直接执行）===")
result = graph.invoke(
    {"messages": [HumanMessage("乃木坂46有多少成员？")]},
    config={"configurable": {"thread_id": "low_risk"}},
)
print(f"回答：{result['messages'][-1].content[:100]}")

print("\n=== 测试2：高风险操作（需要人工审批）===")

# 第一次调用：图会在 interrupt() 处暂停
print("第一次调用（会暂停）...")
try:
    result = graph.invoke(
        {"messages": [HumanMessage("帮我删除所有临时文件")]},
        config=config,
    )
except Exception as e:
    print(f"图暂停了，等待人工审批")
    print(f"暂停信息类型：{type(e).__name__}")

# 查看当前 State
state_snapshot = graph.get_state(config)
print(f"\n当前图状态：{state_snapshot.next}")  # 下一步要执行哪个节点

# 人工审批：用 Command(resume=...) 继续
print("\n人工决定：确认执行")
result = graph.invoke(
    Command(resume="确认执行"),
    config=config,
)
print(f"最终回答：{result['messages'][-1].content[:150]}")

print("\n--- 测试取消操作 ---")
config2 = {"configurable": {"thread_id": "hitl_test2"}}

# 第一次调用
try:
    graph.invoke(
        {"messages": [HumanMessage("清空数据库所有数据")]},
        config=config2,
    )
except:
    pass

# 人工拒绝
print("人工决定：取消")
result = graph.invoke(
    Command(resume="取消"),
    config=config2,
)
print(f"最终回答：{result['messages'][-1].content}")