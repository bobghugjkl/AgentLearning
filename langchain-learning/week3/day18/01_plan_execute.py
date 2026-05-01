import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

# ── 工具定义 ──────────────────────────────────────────
@tool
def search_web(query: str) -> str:
    """搜索网络获取相关信息。
    Args:
        query: 搜索关键词
    """
    # 模拟搜索结果
    results = {
        "竞品": "主要竞品有A、B、C三家，市场份额分别为30%、25%、20%",
        "价格": "市场平均价格在100-500元之间，高端产品可达1000元以上",
        "用户": "主要用户群体为25-35岁的年轻专业人士，注重品质和体验",
        "趋势": "2024年市场规模预计增长20%，AI功能成为新卖点",
    }
    for key in results:
        if key in query:
            return results[key]
    return f"搜索'{query}'的结果：相关市场数据显示增长趋势良好"

@tool
def analyze_data(data: str) -> str:
    """分析数据并提取关键洞察。
    Args:
        data: 需要分析的数据内容
    """
    return f"分析结果：基于数据'{data[:50]}...'，关键洞察是市场机会明显，建议重点关注高端用户群体"

@tool
def write_report(content: str) -> str:
    """根据收集的信息生成报告章节。
    Args:
        content: 报告内容要点
    """
    return f"报告章节已生成：\n{content}\n[格式化为专业报告格式]"

tools = [search_web, analyze_data, write_report]
tools_dict = {t.name: t for t in tools}

print("初始化完成，工具：", [t.name for t in tools])


# ── State 定义 ────────────────────────────────────────
class Plan(BaseModel):
    steps: List[str] = Field(description="执行步骤列表，每步是一个具体任务")


class State(TypedDict):
    messages: Annotated[list, add_messages]
    plan: List[str]  # 规划的步骤列表
    current_step: int  # 当前执行到第几步
    results: List[str]  # 每步的执行结果
    final_report: str  # 最终报告


# ── Planner 节点 ──────────────────────────────────────
def planner_node(state: State):
    """根据用户任务生成执行计划"""
    task = state["messages"][-1].content

    planner_prompt = f"""你是一个任务规划专家。
请把下面的任务分解成3-5个具体的执行步骤。
每个步骤要具体、可执行，用一句话描述。

任务：{task}

请直接列出步骤，每行一个，不要编号，不要解释。"""

    response = model.invoke(planner_prompt)

    # 解析步骤
    steps = [
        step.strip()
        for step in response.content.strip().split("\n")
        if step.strip()
    ]

    print(f"\n📋 规划完成，共 {len(steps)} 步：")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")

    return {
        "plan": steps,
        "current_step": 0,
        "results": [],
        "final_report": "",
    }


print("Planner 节点定义完成")


# ── Executor 节点 ─────────────────────────────────────
def executor_node(state: State):
    """执行当前步骤"""
    current = state["current_step"]
    steps = state["plan"]

    if current >= len(steps):
        return {}

    step = steps[current]
    print(f"\n⚡ 执行第{current + 1}步：{step}")

    # 让模型决定用哪个工具执行这步
    executor_prompt = f"""你是一个任务执行专家。
请执行下面这个步骤，选择合适的工具完成任务。

步骤：{step}

可用工具：search_web（搜索信息）、analyze_data（分析数据）、write_report（写报告）

直接调用工具执行，不要解释。"""

    model_with_tools = model.bind_tools(tools)
    response = model_with_tools.invoke(executor_prompt)

    # 执行工具调用
    step_result = step  # 默认结果
    if response.tool_calls:
        for tc in response.tool_calls:
            tool_func = tools_dict.get(tc["name"])
            if tool_func:
                result = tool_func.invoke(tc["args"])
                step_result = result
                print(f"  → 调用工具：{tc['name']}")
                print(f"  → 结果：{result[:80]}")

    # 更新结果列表
    new_results = state["results"] + [f"步骤{current + 1}：{step_result}"]

    return {
        "current_step": current + 1,
        "results": new_results,
    }


# ── Reporter 节点 ─────────────────────────────────────
def reporter_node(state: State):
    """汇总所有步骤结果，生成最终报告"""
    results_text = "\n".join(state["results"])
    original_task = state["messages"][0].content

    report_prompt = f"""根据以下执行结果，为任务"{original_task}"生成一份简洁的总结报告。

执行结果：
{results_text}

请生成200字以内的报告总结。"""

    response = model.invoke(report_prompt)
    print(f"\n📄 报告生成完成")

    return {
        "final_report": response.content,
        "messages": [AIMessage(content=response.content)],
    }


# ── 路由函数 ──────────────────────────────────────────
def should_continue(state: State) -> str:
    """判断是否还有步骤需要执行"""
    if state["current_step"] >= len(state["plan"]):
        return "report"  # 所有步骤完成 → 生成报告
    return "execute"  # 还有步骤 → 继续执行


# ── 构建图 ────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("planner", planner_node)
builder.add_node("executor", executor_node)
builder.add_node("reporter", reporter_node)

builder.add_edge(START, "planner")
builder.add_edge("planner", "executor")
builder.add_conditional_edges(
    "executor",
    should_continue,
    {
        "execute": "executor",  # ← 回边！循环执行每一步
        "report": "reporter",
    }
)
builder.add_edge("reporter", END)

graph = builder.compile(checkpointer=MemorySaver())
print("图构建完成！")

# ── 测试 ──────────────────────────────────────────────
config = {"configurable": {"thread_id": "plan_test"}}

print("\n=== 测试 Plan-and-Execute ===")
result = graph.invoke(
    {"messages": [HumanMessage("帮我做一份智能手机市场的竞品分析报告")]},
    config=config,
)

print(f"\n{'=' * 50}")
print("最终报告：")
print(result["final_report"])
print(f"\n共执行 {len(result['results'])} 个步骤")