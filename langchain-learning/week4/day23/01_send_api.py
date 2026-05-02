import os
import operator
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import Send
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, List
from typing_extensions import TypedDict

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

# ── State 定义 ────────────────────────────────────────
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    topics: List[str]                              # 要研究的主题列表
    results: Annotated[List[str], operator.add]    # 并行结果用 add 合并！
    final_report: str

# ── 子任务 State（每个并行节点用这个）────────────────
class TopicState(TypedDict):
    topic: str      # 当前要研究的主题
    results: Annotated[List[str], operator.add]  # 写回主图的 results

print("State 定义完成")
print("results 用 operator.add 合并，防止并行覆盖")


# ── 节点1：规划节点（决定并行哪些任务）──────────────
def planner_node(state: ResearchState):
    """把大任务拆成多个独立子任务"""
    msg = state["messages"][-1].content

    # 模拟从用户请求里提取研究主题
    # 真实场景用 LLM 提取
    topics = [
        f"{msg} - 技术原理",
        f"{msg} - 应用场景",
        f"{msg} - 发展趋势",
    ]

    print(f"📋 规划完成，并行研究 {len(topics)} 个主题：")
    for t in topics:
        print(f"  • {t}")

    return {"topics": topics}


# ── 节点2：Send API 分发（Map 阶段）──────────────────
def dispatch_research(state: ResearchState):
    """
    Send API 核心：动态创建多个并行任务
    每个 Send 都会创建一个独立的 research_node 实例，同时执行
    """
    return [
        Send("research", {"topic": topic, "results": []})
        for topic in state["topics"]
    ]


# ── 节点3：研究节点（并行执行）───────────────────────
def research_node(state: TopicState):
    """每个主题独立研究，并行执行"""
    topic = state["topic"]
    print(f"  🔍 并行研究：{topic[:40]}")

    # 模拟研究耗时
    result = f"【{topic}】研究完成：该主题技术成熟度高，市场前景广阔"

    return {"results": [result]}  # 返回列表，operator.add 会追加


# ── 节点4：汇总节点（Reduce 阶段）────────────────────
def reduce_node(state: ResearchState):
    """收集所有并行结果，生成最终报告"""
    print(f"\n📄 汇总 {len(state['results'])} 个研究结果...")

    results_text = "\n".join(state["results"])

    report_prompt = f"""根据以下研究结果生成简洁报告（100字以内）：

{results_text}"""

    response = model.invoke(report_prompt)

    return {
        "final_report": response.content,
        "messages": [AIMessage(content=response.content)],
    }


print("节点定义完成")

# ── 构建图 ────────────────────────────────────────────
builder = StateGraph(ResearchState)
builder.add_node("planner", planner_node)
# builder.add_node("dispatch", dispatch_node)
builder.add_node("research", research_node)
builder.add_node("reduce", reduce_node)

builder.add_edge(START, "planner")
# builder.add_edge("planner", "dispatch")

# dispatch 节点返回 Send 列表，LangGraph 自动并行
# 所有 research 节点完成后，自动汇聚到 reduce
# Send API 放在条件边里！
builder.add_conditional_edges(
    "planner",
    dispatch_research,  # ← 返回 Send 列表
)
builder.add_edge("research", "reduce")
builder.add_edge("reduce", END)

graph = builder.compile(checkpointer=MemorySaver())
print("图构建完成！")

# ── 测试 ──────────────────────────────────────────────
import time

config = {"configurable": {"thread_id": "send_test"}}

print("\n=== 测试并行执行 ===")
start = time.time()

result = graph.invoke(
    {
        "messages": [HumanMessage("LangGraph")],
        "topics": [],
        "results": [],
        "final_report": "",
    },
    config=config,
)

elapsed = time.time() - start

print(f"\n{'='*50}")
print(f"执行时间：{elapsed:.2f}秒")
print(f"研究主题数：{len(result['topics'])}")
print(f"收集结果数：{len(result['results'])}")
print(f"\n最终报告：\n{result['final_report']}")