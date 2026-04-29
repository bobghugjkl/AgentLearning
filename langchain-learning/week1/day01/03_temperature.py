import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

prompt = "用一句话形容春天"

print("=== temperature 对比实验 ===\n")

for temp in [0.0, 0.7, 1.5]:
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
        max_tokens=64,
    )
    print(f"temperature={temp}  →  {resp.choices[0].message.content.strip()}")