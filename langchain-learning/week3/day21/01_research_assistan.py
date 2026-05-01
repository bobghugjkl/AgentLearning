import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage
load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.3,
)

print("初始化完成")

# ── 研究 Agent 的工具 ─────────────────────────────────
@tool
def search_topic(query: str) -> str:
    """搜索某个主题的相关信息。
    Args:
        query: 搜索关键词或主题
    """
    fake_results = {
        "LangChain": "LangChain是一个用于构建LLM应用的框架，支持Chain、Agent、RAG等模式",
        "LangGraph": "LangGraph是LangChain的扩展，支持有状态的多Agent工作流，基于图结构",
        "RAG": "RAG（检索增强生成）通过检索外部文档来增强LLM的回答质量",
        "Agent": "Agent是能够使用工具、做决策、完成复杂任务的AI系统",
    }
    for key in fake_results:
        if key.lower() in query.lower():
            return fake_results[key]
    return f"搜索'{query}'的结果：这是一个重要的AI技术领域，近年来发展迅速"

@tool
def analyze_topic(content: str) -> str:
    """深度分析某个主题的核心要点。
    Args:
        content: 需要分析的内容
    """
    return f"深度分析结果：'{content[:50]}...'的核心要点是技术创新性强、应用场景广泛、社区活跃"

@tool
def find_examples(topic: str) -> str:
    """查找某个主题的实际应用案例。
    Args:
        topic: 主题名称
    """
    return f"找到{topic}的3个典型应用案例：1.企业知识库 2.智能客服 3.代码助手"

# ── 写作 Agent 的工具 ─────────────────────────────────
@tool
def write_summary(content: str) -> str:
    """将内容整理成简洁的摘要。
    Args:
        content: 需要整理的内容
    """
    return f"摘要：{content[:100]}...（已整理为结构化摘要）"

@tool
def format_report(sections: str) -> str:
    """将多个章节整合成完整报告。
    Args:
        sections: 报告各章节内容
    """
    return f"## 研究报告\n\n{sections}\n\n---\n报告生成完成"

# ── 创建专家 Agent ────────────────────────────────────
research_agent = create_react_agent(
    model,
    tools=[search_topic, analyze_topic, find_examples],
    name="research_agent",
    prompt="""你是一个专业的研究员。
负责搜索信息、分析主题、寻找案例。
完成研究后给出详细的调研结果。""",
)

writing_agent = create_react_agent(
    model,
    tools=[write_summary, format_report],
    name="writing_agent",
    prompt="""你是一个专业的技术写作专家。
负责将研究结果整理成清晰的报告。
输出要结构化、易读、有条理。""",
)

print("专家 Agent 创建完成：research_agent、writing_agent")

# ── Supervisor ────────────────────────────────────────
supervisor = create_supervisor(
    agents=[research_agent, writing_agent],
    model=model,
    prompt="""你是一个研究项目的总监。

根据用户请求分配任务：
- research_agent：负责搜索、分析、找案例
- writing_agent：负责整理、写摘要、生成报告

复杂任务先让 research_agent 研究，再让 writing_agent 整理。
简单问题直接分配给对应专家。""",
).compile()


# ── 带 HIL 的完整系统 ─────────────────────────────────
class State(TypedDict):
    messages: Annotated[list, add_messages]
    need_approval: bool
    task_type: str


def check_approval(state: State):
    last_msg = state["messages"][-1].content
    sensitive = ["发布", "删除", "修改数据库", "发邮件", "邮件", "部署"]
    needs_approval = any(kw in last_msg for kw in sensitive)
    print(f"  敏感检测：{needs_approval}，触发词：{[kw for kw in sensitive if kw in last_msg]}")
    return {
        "need_approval": needs_approval,
        "task_type": "sensitive" if needs_approval else "normal",
    }


def human_approval_node(state: State):
    """HIL 节点：等待人工确认"""
    last_msg = state["messages"][-1].content

    decision = interrupt({
        "message": f"⚠️ 检测到敏感操作：\n'{last_msg[:100]}'\n\n是否继续？",
        "options": ["继续", "取消"],
    })

    if decision == "取消":
        return {
            "messages": [AIMessage(content="操作已取消，如需帮助请重新描述需求。")]
        }
    return {}


def research_node(state: State):
    """调用 Supervisor 处理研究任务"""
    result = supervisor.invoke({
        "messages": state["messages"]
    })
    last_msg = result["messages"][-1]
    return {"messages": [last_msg]}


def route_approval(state: State) -> str:
    if state["need_approval"]:
        return "approval"
    return "research"


# ── 构建完整图 ────────────────────────────────────────
builder = StateGraph(State)
builder.add_node("check", check_approval)
builder.add_node("approval", human_approval_node)
builder.add_node("research", research_node)

builder.add_edge(START, "check")
builder.add_conditional_edges(
    "check",
    route_approval,
    {
        "approval": "approval",
        "research": "research",
    }
)
builder.add_edge("approval", "research")
builder.add_edge("research", END)

graph = builder.compile(checkpointer=MemorySaver())
print("完整系统构建完成！")


def run(question: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    print(f"\n问：{question}")
    print("-" * 40)

    try:
        result = graph.invoke(
            {"messages": [HumanMessage(question)],
             "need_approval": False,
             "task_type": "normal"},
            config=config,
        )
        print(f"答：{result['messages'][-1].content[:200]}")
    except Exception as e:
        print(f"系统暂停（HIL）：{type(e).__name__}")
        # 查看暂停状态
        snapshot = graph.get_state(config)
        print(f"等待确认，下一步：{snapshot.next}")
        return config  # 返回 config 用于后续恢复

    return None


# print("\n=== 测试1：普通研究任务 ===")
# run("帮我研究一下 LangGraph 是什么，有什么应用场景", "test_001")
#
# print("\n=== 测试2：需要写报告 ===")
# run("帮我调研 RAG 技术并整理成报告", "test_002")

# print("\n=== 测试3：触发 HIL ===")
# config = run("帮我把研究结果发送邮件给团队", "test_003")
print("\n=== 测试3：触发 HIL ===")
config3 = {"configurable": {"thread_id": "test_003"}}

# 第一次调用
result3 = graph.invoke(
    {
        "messages": [HumanMessage("帮我把研究结果发送邮件给团队")],
        "need_approval": False,
        "task_type": "normal",
    },
    config=config3,
)

# 检查是否暂停在 HIL 节点
snapshot = graph.get_state(config3)
print(f"图状态：{snapshot.next}")

if snapshot.next == ("approval",):
    print("⚠️ 系统暂停，等待人工确认")

    # 人工取消
    print("人工决定：取消")
    result3 = graph.invoke(
        Command(resume="取消"),
        config=config3,
    )
    print(f"系统回复：{result3['messages'][-1].content}")
else:
    print(f"答：{result3['messages'][-1].content[:100]}")
if config3:
    print("\n人工决定：取消")
    result = graph.invoke(Command(resume="取消"), config=config)
    print(f"系统回复：{result['messages'][-1].content}")

