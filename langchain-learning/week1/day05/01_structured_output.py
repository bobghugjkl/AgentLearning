import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.7,
)
# 定义输出结构
class Weather(BaseModel):
    city: str = Field(description="城市名称")
    weather: str = Field(description="天气状况，比如晴天、多云、小雨")
    temperature: float = Field(description="温度，摄氏度")
    suggestion: str = Field(description="出行建议，一句话")

print("结构定义完成")
print(Weather.model_fields)

# with_structured_output：让模型输出符合 Weather 结构的 JSON
structured_model = model.with_structured_output(Weather)

# 调用
result = structured_model.invoke("北京今天天气怎么样？")

print("\n=== 结构化输出 ===")
print(type(result))           # 看看返回的是什么类型
print(result)                 # 完整对象
print(f"\n城市：{result.city}")
print(f"天气：{result.weather}")
print(f"温度：{result.temperature}")
print(f"建议：{result.suggestion}")