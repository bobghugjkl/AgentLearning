import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

load_dotenv()

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)


# ── LLM-as-Judge：用模型评估模型 ──────────────────────
class EvalResult(BaseModel):
    faithfulness_score: float = Field(description="忠实度分数 0-1，回答是否基于文档内容")
    relevancy_score: float = Field(description="相关性分数 0-1，回答是否回答了问题")
    faithfulness_reason: str = Field(description="忠实度评分理由")
    relevancy_reason: str = Field(description="相关性评分理由")


eval_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个 RAG 系统评估专家。
请评估以下 RAG 系统的回答质量。

评估标准：
1. 忠实度（Faithfulness）：回答是否完全基于提供的文档内容？有没有编造内容？
   - 1.0：完全基于文档，无编造
   - 0.5：大部分基于文档，少量推断
   - 0.0：大量编造或与文档矛盾

2. 相关性（Answer Relevancy）：回答是否真正回答了用户的问题？
   - 1.0：完全回答了问题
   - 0.5：部分回答
   - 0.0：答非所问

请严格按照 JSON 格式输出评分。"""),
    ("human", """
问题：{question}

检索到的文档内容：
{contexts}

模型回答：
{answer}

参考答案：
{ground_truth}
"""),
])

eval_chain = eval_prompt | model.with_structured_output(EvalResult)

# ── 测试数据 ──────────────────────────────────────────
test_data = [
    {
        "question": "How long does an Industrial PhD project last?",
        "contexts": """The duration of the project corresponds to the duration 
        of the education programme, which in Denmark is three years.""",
        "answer": "An Industrial PhD project lasts three years in Denmark.",
        "ground_truth": "The project lasts three years.",
    },
    {
        "question": "What is the monthly salary support?",
        "contexts": """Innovation Fund Denmark finances up to DKK 17,000 
        per month of the Industrial PhD student's salary for three years.""",
        "answer": "The monthly support is up to DKK 17,000 for three years.",
        "ground_truth": "Up to DKK 17,000 per month for three years.",
    },
    {
        "question": "Can the PhD student take leave?",
        "contexts": """The Industrial PhD student may ask for leave of absence. 
        The request must be submitted via E-grant.""",
        "answer": "Yes, students can take leave. They need to apply via E-grant, "
                  "and the leave period can last up to 12 months.",  # 编造了12个月！
        "ground_truth": "Yes, students can request leave via E-grant.",
    },
]

# ── 跑评估 ────────────────────────────────────────────
print("=== LLM-as-Judge 评估结果 ===\n")

total_faith = 0
total_rel = 0

for i, data in enumerate(test_data):
    result = eval_chain.invoke(data)
    total_faith += result.faithfulness_score
    total_rel += result.relevancy_score

    print(f"【测试 {i + 1}】{data['question'][:50]}")
    print(f"  忠实度：{result.faithfulness_score:.1f} — {result.faithfulness_reason}")
    print(f"  相关性：{result.relevancy_score:.1f} — {result.relevancy_reason}")
    print()

print(f"平均忠实度：{total_faith / len(test_data):.2f}")
print(f"平均相关性：{total_rel / len(test_data):.2f}")