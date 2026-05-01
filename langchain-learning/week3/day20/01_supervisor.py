import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

# ── 代码 Agent 的工具 ─────────────────────────────────
@tool
def run_python(code: str) -> str:
    """执行 Python 代码并返回结果。
    Args:
        code: 要执行的 Python 代码
    """
    try:
        import io
        import sys
        output = io.StringIO()
        sys.stdout = output
        exec(code)
        sys.stdout = sys.__stdout__
        result = output.getvalue()
        return result if result else "代码执行成功，无输出"
    except Exception as e:
        return f"执行错误：{e}"

@tool
def explain_code(code: str) -> str:
    """解释代码的功能和逻辑。
    Args:
        code: 需要解释的代码
    """
    return f"代码分析：这段代码实现了{code[:30]}...的功能"

# ── 写作 Agent 的工具 ─────────────────────────────────
@tool
def check_grammar(text: str) -> str:
    """检查文本的语法和表达是否正确。
    Args:
        text: 需要检查的文本
    """
    return f"语法检查完成：文本'{text[:30]}...'表达清晰，无明显语法错误"

@tool
def improve_style(text: str) -> str:
    """改善文本的写作风格，使其更专业。
    Args:
        text: 需要改善的文本
    """
    return f"风格改善完成：已将文本调整为更专业的表达方式"

# ── 数学 Agent 的工具 ─────────────────────────────────
@tool
def calculate(expression: str) -> str:
    """计算数学表达式。
    Args:
        expression: 数学表达式
    """
    try:
        return f"{expression} = {eval(expression)}"
    except Exception as e:
        return f"计算错误：{e}"

@tool
def solve_equation(equation: str) -> str:
    """求解数学方程。
    Args:
        equation: 数学方程描述
    """
    return f"方程'{equation}'的求解过程：通过代数方法得出结果"

print("工具定义完成")


# ── 三个专家 Agent ────────────────────────────────────
code_agent = create_react_agent(
    model,
    tools=[run_python, explain_code],
    name="code_agent",
    prompt="你是一个专业的Python程序员，专门处理代码相关问题。",
)

writing_agent = create_react_agent(
    model,
    tools=[check_grammar, improve_style],
    name="writing_agent",
    prompt="你是一个专业的写作助手，专门处理文字相关问题。",
)

math_agent = create_react_agent(
    model,
    tools=[calculate, solve_equation],
    name="math_agent",
    prompt="你是一个数学专家，专门处理数学计算和解题问题。",
)

# ── Supervisor ────────────────────────────────────────
supervisor = create_supervisor(
    agents=[code_agent, writing_agent, math_agent],
    model=model,
    prompt="""你是一个任务分配专家。
根据用户的请求，决定派给哪个专家处理：
- code_agent：代码编写、调试、解释相关问题
- writing_agent：写作、文章、语法相关问题  
- math_agent：数学计算、方程求解相关问题

选择最合适的专家，把任务交给他。""",
).compile()

print("Supervisor 系统构建完成！")
print("专家 Agent：code_agent、writing_agent、math_agent")


def run(question: str):
    print(f"\n问：{question}")
    print("-" * 40)
    result = supervisor.invoke({
        "messages": [HumanMessage(question)]
    })
    # 找到最终回答
    final = result["messages"][-1].content
    print(f"答：{final[:200]}")

print("\n=== 测试 Supervisor 路由 ===")

run("帮我写一段Python代码，计算1到100的和")
run("帮我检查这段话的语法：'I goes to school yesterday'")
run("帮我计算 (123+456) * 789 等于多少")