import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
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
    temperature=0.3,
)

# ── State ─────────────────────────────────────────────
class State(TypedDict):
    messages: Annotated[list, add_messages]
    task: str              # 原始任务
    attempts: List[str]    # 历次尝试的结果
    reflections: List[str] # 历次反思的内容
    attempt_count: int     # 尝试次数
    passed: bool           # 是否通过评估
    max_attempts: int      # 最大尝试次数

print("State 定义完成")
print("字段：", list(State.__annotations__.keys()))


# ── Actor 节点（执行者）──────────────────────────────
def actor_node(state: State):
    """尝试完成任务，如果有反思记录就带着教训重试"""
    task = state["task"]
    attempt_count = state["attempt_count"]
    reflections = state["reflections"]

    print(f"\n🎯 第 {attempt_count + 1} 次尝试...")

    # 构建 prompt，把之前的反思带进去
    if reflections:
        reflection_text = "\n".join([
            f"第{i + 1}次失败教训：{r}"
            for i, r in enumerate(reflections)
        ])
        prompt = f"""任务：{task}

你之前尝试过 {attempt_count} 次，以下是失败的教训：
{reflection_text}

请根据这些教训，改进后重新完成任务。"""
    else:
        prompt = f"请完成以下任务：{task}"

    response = model.invoke(prompt)
    result = response.content

    print(f"  尝试结果（前100字）：{result[:100]}")

    return {
        "attempts": state["attempts"] + [result],
        "attempt_count": attempt_count + 1,
        "messages": [AIMessage(content=result)],
    }


# ── Evaluator 节点（评估者）─────────────────────────
def evaluator_node(state: State):
    """评估最新一次尝试的结果是否合格"""
    task = state["task"]
    latest_attempt = state["attempts"][-1]

    eval_prompt = f"""你是一个极其严格的评估专家，标准非常高。

    任务要求：{task}

    候选答案：{latest_attempt}

    评估标准（必须全部满足才算通过）：
    1. 第一次尝试：直接回答"不通过|需要改进细节"
    2. 第二次之后：正常评估

    当前是第 {state['attempt_count']} 次尝试。

    请只回答"通过"或"不通过"，然后用一句话说明原因。
    格式：通过/不通过|原因"""

    response = model.invoke(eval_prompt)
    result = response.content.strip()

    # 解析结果
    passed = result.startswith("通过")
    print(f"  评估结果：{result[:80]}")

    return {"passed": passed}


# ── Reflection 节点（反思者）────────────────────────
def reflection_node(state: State):
    """分析失败原因，生成改进建议"""
    task = state["task"]
    latest_attempt = state["attempts"][-1]

    reflect_prompt = f"""任务要求：{task}

你的回答（未通过评估）：{latest_attempt}

请分析：
1. 这个回答哪里不足？
2. 下次应该怎么改进？

用2-3句话总结，直接说改进建议，不要废话。"""

    response = model.invoke(reflect_prompt)
    reflection = response.content.strip()

    print(f"  反思内容：{reflection[:100]}")

    return {
        "reflections": state["reflections"] + [reflection],
    }


print("三个节点定义完成")


# ── 路由函数 ──────────────────────────────────────────
def should_continue(state: State) -> str:
    """判断是继续重试还是结束"""
    if state["passed"]:
        return "end"       # 通过评估 → 结束
    if state["attempt_count"] >= state["max_attempts"]:
        return "end"       # 超过最大次数 → 强制结束
    return "reflect"       # 没通过且还有机会 → 去反思

# ── 构建图 ────────────────────────────────────────────
builder = StateGraph(State)

builder.add_node("actor", actor_node)
builder.add_node("evaluator", evaluator_node)
builder.add_node("reflection", reflection_node)

builder.add_edge(START, "actor")
builder.add_edge("actor", "evaluator")
builder.add_conditional_edges(
    "evaluator",
    should_continue,
    {
        "end": END,
        "reflect": "reflection",
    }
)
builder.add_edge("reflection", "actor")  # ← 反思完回去重试

graph = builder.compile(checkpointer=MemorySaver())
print("图构建完成！")

# ── 图的流程 ──────────────────────────────────────────
# actor → evaluator → 通过？→ END
#                   → 没通过且有机会 → reflection → actor（循环）
#                   → 超过次数 → END

# ── 测试 ──────────────────────────────────────────────
config = {"configurable": {"thread_id": "reflexion_test"}}

print("\n=== 测试 Reflexion ===")
result = graph.invoke(
    {
        "task": "用Python写一个函数，输入一个列表，返回列表中所有偶数的平方和，要有错误处理",
        "attempts": [],
        "reflections": [],
        "attempt_count": 0,
        "passed": False,
        "max_attempts": 3,
    },
    config=config,
)

print(f"\n{'='*50}")
print(f"总共尝试：{result['attempt_count']} 次")
print(f"最终通过：{result['passed']}")
print(f"\n最终结果：\n{result['attempts'][-1][:300]}")

if result["reflections"]:
    print(f"\n反思记录：")
    for i, r in enumerate(result["reflections"], 1):
        print(f"  第{i}次反思：{r[:100]}")

# 把原来的测试替换成这个
config2 = {"configurable": {"thread_id": "reflexion_test2"}}

print("\n=== 测试 Reflexion（更难的任务）===")
result2 = graph.invoke(
    {
        "task": """写一篇关于乃木坂46的英文介绍，要求：
1. 必须包含成立年份（2011年）
2. 必须提到至少3位成员名字
3. 必须包含代表作品名称
4. 全文必须超过150个英文单词
5. 必须用正式学术风格写作""",
        "attempts": [],
        "reflections": [],
        "attempt_count": 0,
        "passed": False,
        "max_attempts": 3,
    },
    config=config2,
)

print(f"\n{'='*50}")
print(f"总共尝试：{result2['attempt_count']} 次")
print(f"最终通过：{result2['passed']}")

if result2["reflections"]:
    print(f"\n触发了 {len(result2['reflections'])} 次反思：")
    for i, r in enumerate(result2["reflections"], 1):
        print(f"  第{i}次：{r[:120]}")
else:
    print("\n第一次就通过了（任务还是太简单）")

print(f"\n最终结果（前200字）：\n{result2['attempts'][-1][:200]}")