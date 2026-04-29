import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse


load_dotenv()

app = FastAPI()

client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

def generate(question: str):
    """
        生成器函数：每生成一块内容就 yield 出去
        yield 和 return 的区别：
        - return：函数结束，返回一个值
        - yield：暂停函数，返回一个值，下次继续从这里执行
    """
    stream = client.chat.completions.create(
        model = "deepseek-v4-flash",
        messages=[{"role":"user","content":question}],
        temperature=0.7,
        max_tokens=512,
        stream = True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta # 生成一块，发一块
@app.get("/chat")
def chat(question: str):
    return StreamingResponse(
        generate(question),
        media_type="text/plain",
    )