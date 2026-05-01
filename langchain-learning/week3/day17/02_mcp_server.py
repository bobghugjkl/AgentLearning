"""
MCP Server：把我们的工具标准化暴露出去
任何支持 MCP 的 Agent 都能调用这些工具
"""
from mcp.server.fastmcp import FastMCP

# 创建 MCP Server
mcp = FastMCP("我的工具箱")


# ── 用 @mcp.tool() 注册工具 ───────────────────────────
@mcp.tool()
def get_weather(city: str) -> str:
    """获取指定城市的实时天气信息，包括温度、天气状况和风力等级。

    Args:
        city: 城市名称，如北京、上海、东京
    """
    data = {
        "北京": "晴天，25°C，东风3级",
        "上海": "多云，22°C，南风2级",
        "东京": "小雨，18°C，北风1级",
    }
    return data.get(city, f"{city}暂无数据")


@mcp.tool()
def calculate(expression: str) -> str:
    """计算数学表达式，支持加减乘除、括号、幂运算。

    Args:
        expression: 数学表达式，如 123*456、(10+5)*3
    """
    try:
        return f"{expression} = {eval(expression)}"
    except Exception as e:
        return f"计算错误：{e}"


@mcp.tool()
def search_docs(query: str) -> str:
    """搜索文档库，返回相关内容片段。

    Args:
        query: 搜索关键词
    """
    # 模拟文档搜索
    fake_docs = {
        "申请": "申请需要提交学历证明和成绩单",
        "薪资": "薪资不低于国家博士标准",
        "时长": "项目持续三年",
    }
    for key, value in fake_docs.items():
        if key in query:
            return value
    return "未找到相关文档"


if __name__ == "__main__":
    print("MCP Server 启动！")
    print("工具列表：get_weather、calculate、search_docs")
    mcp.run()