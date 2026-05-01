import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)


# ══════════════════════════════════════════════════════
# 工具设计对比：好的 vs 差的
# ══════════════════════════════════════════════════════

# ── 差的工具设计 ──────────────────────────────────────
@tool
def bad_weather(city: str) -> str:
    """天气"""  # ← description 太短，模型不知道能干什么
    return f"{city}天气数据"


# ── 好的工具设计 ──────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """获取指定城市的实时天气信息，包括温度、天气状况和风力等级。
    适用于用户询问某城市天气、温度、是否需要带伞等问题。

    Args:
        city: 城市名称，如"北京"、"上海"、"东京"
    """
    # 模拟天气数据
    data = {
        "北京": "晴天，25°C，东风3级，空气质量良",
        "上海": "多云，22°C，南风2级，空气质量优",
        "东京": "小雨，18°C，北风1级，空气质量优",
    }
    result = data.get(city, f"{city}暂无天气数据")
    # 原则3：返回值截断，防止 token 爆炸
    return result[:200]


@tool
def calculate(expression: str) -> str:
    """计算数学表达式并返回结果。
    支持加减乘除、括号、幂运算等。
    适用于用户需要精确数学计算的场景。

    Args:
        expression: 数学表达式，如"123*456"、"(10+5)*3"
    """
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"


@tool
def search_database(query: str, limit: int = 5) -> str:
    """在产品数据库中搜索相关信息。
    适用于用户询问产品价格、库存、规格等信息。

    Args:
        query: 搜索关键词
        limit: 返回结果数量，默认5条，最多20条
    """
    # 模拟数据库查询
    fake_results = [
        f"产品{i}：价格{i * 100}元，库存{i * 10}件"
        for i in range(1, min(limit, 20) + 1)
    ]
    return "\n".join(fake_results)


print("工具定义完成")
print("工具列表：", [t.name for t in [get_weather, calculate, search_database]])

# ══════════════════════════════════════════════════════
# 对比：好工具 vs 差工具，模型选择有何不同
# ══════════════════════════════════════════════════════

# 用好工具的 Agent
good_agent = create_react_agent(
    model,
    tools=[get_weather, calculate, search_database],
)

# 用差工具的 Agent
bad_agent = create_react_agent(
    model,
    tools=[bad_weather, calculate],
)

def run_agent(agent, question: str, label: str):
    print(f"\n【{label}】问：{question}")
    result = agent.invoke({
        "messages": [HumanMessage(question)]
    })
    # 找到工具调用记录
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  → 调用工具：{tc['name']}，参数：{tc['args']}")
    print(f"  → 回答：{result['messages'][-1].content[:100]}")

# 测试1：天气问题
run_agent(good_agent, "北京今天适合出门吗？", "好工具Agent")
run_agent(bad_agent, "北京今天适合出门吗？", "差工具Agent")

# 测试2：计算问题
run_agent(good_agent, "帮我算一下 (123+456)*789 等于多少", "好工具Agent")