import os
from openai import OpenAI
from dotenv import load_dotenv

# 读取 .env 文件里的 API Key
load_dotenv()

# 创建客户端
# 注意：base_url 换成 DeepSeek 的地址，api_key 从环境变量读取
client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

# 发起对话
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个翻译助手，只输出译文，不加任何解释。"},
        {"role": "user",   "content": "把下面这句话翻译成英文：今天天气真好"},
    ],
    temperature=0.3,
    max_tokens=256,
)

# 打印结果
print(response.choices[0].message.content)
# 在原来的 print 下面加上这些
print("\n=== token 消耗 ===")
print(f"输入 tokens: {response.usage.prompt_tokens}")
print(f"输出 tokens: {response.usage.completion_tokens}")
print(f"总计 tokens: {response.usage.total_tokens}")

print("\n=== 完整 response 结构 ===")
print(response)



