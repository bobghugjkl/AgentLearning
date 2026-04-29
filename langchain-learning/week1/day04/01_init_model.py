import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# 一行初始化模型
# 不用自己创建 OpenAI client，不用写 base_url
model = init_chat_model(
    "deepseek-v4-flash",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.7,
)

# 最简单的调用
response = model.invoke("你好，介绍一下你自己")
print(response.content)

# 流式输出
print("\n=== 流式输出 ===")
for chunk in model.stream("用30字介绍乃木坂46"):
    print(chunk.content, end="", flush=True)