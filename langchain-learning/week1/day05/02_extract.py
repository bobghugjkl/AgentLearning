import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from langchain_core.runnables import RunnableWithFallbacks
load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

# 定义要抽取的结构
class Person(BaseModel):
    name: str = Field(description="人物姓名")
    role: str = Field(description="人物身份或职业")
    fact: str = Field(description="关于这个人的一个关键事实")

class ArticleInfo(BaseModel):
    topic: str = Field(description="文章主题，一句话概括")
    persons: List[Person] = Field(description="文章中提到的人物列表")
    key_takeaway: str = Field(description="最重要的结论，一句话")

# 构建 chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个信息抽取助手，从文章中抽取结构化信息。"),
    ("human", "请从下面这段文字中抽取信息：\n\n{text}"),
])

structured_model = model.with_structured_output(ArticleInfo)
chain = prompt | structured_model

# 测试文章
article = """
乃木坂46成立于2011年，是AKB48的官方竞争对手。
白石麻衣作为团队的顶尖成员，以超模级颜值著称，
目前已转型为专业模特和演员。
斋藤飞鸟是继白石麻衣之后的王牌成员，
以清冷气质和强大的舞台表现力闻名，
2023年从团体毕业后开始专注演员事业。
"""

result = chain.invoke({"text": article})

print(f"主题：{result.topic}")
print(f"\n人物：")
for person in result.persons:
    print(f"  - {person.name}（{person.role}）：{person.fact}")
print(f"\n结论：{result.key_takeaway}")

# 加重试：失败最多重试2次


reliable_chain = chain.with_retry(
    stop_after_attempt=3,  # 最多试3次
)

result2 = reliable_chain.invoke({"text": article})
print(f"\n=== 带重试的结果 ===")
print(f"主题：{result2.topic}")