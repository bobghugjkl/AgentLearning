import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

model = init_chat_model(
    "deepseek-v4-flash",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.7,
)

# 第一步：定义 prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{language}翻译助手，只输出译文。"),
    ("human", "{text}"),
])

# 第二步：定义输出解析器（把 AIMessage 转成纯字符串）
parser = StrOutputParser()

# 第三步：用管道符组合成 chain
chain = prompt | model | parser

# 调用
result = chain.invoke({
    "language": "日语",
    "text": "今天天气真好",
})

print(result)