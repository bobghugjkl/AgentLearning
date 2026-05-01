"""
MCP Client：通过 MCP 协议调用工具
"""
import os
import asyncio
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)


async def main():
    # ── 连接 MCP Server ───────────────────────────────
    server_params = StdioServerParameters(
        command="python",
        args=["week3/day17/02_mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ── 加载 MCP 工具 ─────────────────────────
            tools = await load_mcp_tools(session)
            print(f"从 MCP Server 加载了 {len(tools)} 个工具：")
            for t in tools:
                print(f"  - {t.name}: {t.description[:50]}")

            # ── 创建 Agent 使用 MCP 工具 ──────────────
            agent = create_react_agent(model, tools)

            # ── 测试 ──────────────────────────────────
            questions = [
                "北京今天天气怎么样？",
                "帮我算 888*999 等于多少",
                "申请工业博士需要什么条件？",
            ]

            for q in questions:
                print(f"\n问：{q}")
                result = await agent.ainvoke({
                    "messages": [HumanMessage(q)]
                })
                print(f"答：{result['messages'][-1].content[:150]}")


if __name__ == "__main__":
    asyncio.run(main())