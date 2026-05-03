import os
from dotenv import load_dotenv

load_dotenv()

# 验证环境变量
print("LANGSMITH_TRACING:", os.getenv("LANGSMITH_TRACING"))
print("LANGSMITH_PROJECT:", os.getenv("LANGSMITH_PROJECT"))
print("API KEY 存在:", bool(os.getenv("LANGSMITH_API_KEY")))

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.7,
)

# ── 测试1：简单调用 ───────────────────────────────────
print("\n=== 测试1：简单调用 ===")
response = model.invoke("用一句话介绍乃木坂46")
print(f"回答：{response.content}")

# ── 测试2：LCEL Chain ─────────────────────────────────
print("\n=== 测试2：LCEL Chain ===")
chain = (
    ChatPromptTemplate.from_messages([
        ("system", "你是一个{language}翻译助手，只输出译文。"),
        ("human", "{text}"),
    ])
    | model
    | StrOutputParser()
)

result = chain.invoke({
    "language": "日语",
    "text": "今天天气真好",
})
print(f"翻译结果：{result}")

print("\n✅ 所有调用已自动上传到 LangSmith！")
print("去 https://smith.langchain.com 查看 trace")

# ── 测试3：追踪 LangGraph Agent ──────────────────────
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}：晴天25°C"

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        return f"{expression} = {eval(expression)}"
    except:
        return "计算错误"

agent = create_react_agent(model, tools=[get_weather, calculate])

print("\n=== 测试3：追踪 Agent ===")
result = agent.invoke({
    "messages": [HumanMessage("北京天气怎样？另外 123*456 等于多少？")]
})
print(f"回答：{result['messages'][-1].content[:150]}")
print("\n去 LangSmith 查看 Agent 的完整 trace！")

# ── 测试4：追踪自定义函数 ─────────────────────────────
from langsmith import traceable


@traceable(name="RAG Pipeline")  # 自定义 trace 名字
def my_rag(question: str) -> str:
    """模拟一个 RAG 流程"""
    # 步骤1：检索
    context = f"检索到的内容：关于'{question}'的相关文档"

    # 步骤2：生成
    response = model.invoke(f"根据以下内容回答：{context}\n\n问题：{question}")
    return response.content


print("\n=== 测试4：自定义函数追踪 ===")
result = my_rag("LangSmith 是什么？")
print(f"回答：{result[:100]}")
print("\n去 LangSmith 查看 'RAG Pipeline' trace！")