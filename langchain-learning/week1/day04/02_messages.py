import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

model = init_chat_model(
    "deepseek-v4-flash",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.7,
)

# 用 LangChain 的消息类构造多轮对话
messages = [
    SystemMessage(content="你是斋藤飞鸟，用她的语气回答问题。"),
    HumanMessage(content="你最喜欢乃木坂46的哪首歌？"),
]

resp1 = model.invoke(messages)
print(f"第一轮：{resp1.content}")

# resp1 本身就是 AIMessage，直接塞回去
messages.append(resp1)
messages.append(HumanMessage(content="为什么喜欢这首？"))

resp2 = model.invoke(messages)
print(f"\n第二轮：{resp2.content}")