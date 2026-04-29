import os
import numpy as np
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
load_dotenv()

# 使用本地 Embedding 模型（不花钱！）
# 第一次运行会自动下载模型，大概 400MB
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

# 把一段文字变成向量
text = "Industrial PhD applicants must have a master's degree"
vector = embeddings.embed_query(text)

print(f"文字：{text}")
print(f"向量维度：{len(vector)}")
print(f"向量前5个数字：{vector[:5]}")

def cosine_similarity(v1, v2):
    """计算两个向量的余弦相似度，值越接近1越相似"""
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# 三句话
s1 = "Industrial PhD applicants must have a master's degree"
s2 = "Candidates need a master's degree to apply"  # 语义相近
s3 = "The weather is nice today"                    # 语义无关

v1 = embeddings.embed_query(s1)
v2 = embeddings.embed_query(s2)
v3 = embeddings.embed_query(s3)

print(f"\ns1 vs s2 相似度（语义相近）：{cosine_similarity(v1, v2):.4f}")
print(f"s1 vs s3 相似度（语义无关）：{cosine_similarity(v1, v3):.4f}")