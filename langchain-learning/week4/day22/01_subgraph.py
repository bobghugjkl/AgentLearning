import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
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
    temperature=0,
)

# ── 子图 State（研究流程）────────────────────────────
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]  # 共享字段
    search_result: str    # 子图私有
    analysis_result: str  # 子图私有
    final_result: str     # 子图私有

# ── 子图节点 ──────────────────────────────────────────
def search_node(state: ResearchState):
    """第一步：搜索信息"""
    query = state["messages"][-1].content
    print(f"  🔍 搜索：{query[:30]}...")
    result = f"搜索结果：找到关于'{query[:20]}'的相关信息3条"
    return {"search_result": result}

def analyze_node(state: ResearchState):
    """第二步：分析搜索结果"""
    print(f"  📊 分析搜索结果...")
    analysis = f"分析结果：基于搜索数据，核心要点是技术创新性强、应用广泛"
    return {"analysis_result": analysis}

def summarize_node(state: ResearchState):
    """第三步：生成摘要"""
    print(f"  📝 生成摘要...")
    summary = f"研究摘要：{state['search_result']}。{state['analysis_result']}"
    return {
        "final_result": summary,
        "messages": [AIMessage(content=summary)],
    }

# ── 构建子图 ──────────────────────────────────────────
research_builder = StateGraph(ResearchState)
research_builder.add_node("search", search_node)
research_builder.add_node("analyze", analyze_node)
research_builder.add_node("summarize", summarize_node)

research_builder.add_edge(START, "search")
research_builder.add_edge("search", "analyze")
research_builder.add_edge("analyze", "summarize")
research_builder.add_edge("summarize", END)

# 编译子图（不加 checkpointer）
research_subgraph = research_builder.compile()
print("子图构建完成！")


# ── 主图 State ────────────────────────────────────────
class MainState(TypedDict):
    messages: Annotated[list, add_messages]  # 和子图共享
    task_type: str

# ── 主图节点 ──────────────────────────────────────────
def router_node(state: MainState):
    """判断任务类型"""
    msg = state["messages"][-1].content
    if any(kw in msg for kw in ["研究", "调研", "分析", "了解"]):
        task_type = "research"
    else:
        task_type = "general"
    print(f"路由判断：{task_type}")
    return {"task_type": task_type}

def general_node(state: MainState):
    """处理普通问题"""
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def route_task(state: MainState) -> str:
    return state["task_type"]

# ── 构建主图 ──────────────────────────────────────────
main_builder = StateGraph(MainState)
main_builder.add_node("router", router_node)
main_builder.add_node("general", general_node)

# ← 关键：把子图作为节点加入主图！
main_builder.add_node("research", research_subgraph)

main_builder.add_edge(START, "router")
main_builder.add_conditional_edges(
    "router",
    route_task,
    {
        "research": "research",  # → 子图
        "general": "general",
    }
)
main_builder.add_edge("research", END)
main_builder.add_edge("general", END)

graph = main_builder.compile(checkpointer=MemorySaver())
print("主图构建完成！")

# ── 测试 ──────────────────────────────────────────────
config = {"configurable": {"thread_id": "subgraph_test"}}

print("\n=== 测试1：研究任务（走子图）===")
result = graph.invoke(
    {"messages": [HumanMessage("帮我研究一下 LangGraph 的核心特性")]},
    config=config,
)
print(f"最终回答：{result['messages'][-1].content[:150]}")

print("\n=== 测试2：普通问题（不走子图）===")
config2 = {"configurable": {"thread_id": "subgraph_test2"}}
result2 = graph.invoke(
    {"messages": [HumanMessage("你好，今天天气怎么样？")]},
    config=config2,
)
print(f"最终回答：{result2['messages'][-1].content[:100]}")