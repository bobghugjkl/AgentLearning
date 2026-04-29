# Day 09 复盘笔记 — Embedding 与向量数据库

## 今天学了什么

### 1. 什么是 Embedding
把文字转成向量（一串数字），语义相近的文字向量距离近：

```python
"苹果"  → [0.2, 0.8, 0.1, ...]
"香蕉"  → [0.3, 0.7, 0.2, ...]  # 和苹果距离近（都是水果）
"汽车"  → [0.9, 0.1, 0.8, ...]  # 和苹果距离远
```

**Embedding 模型 vs 对话模型：**
| | 对话模型（DeepSeek） | Embedding 模型 |
|--|---------------------|---------------|
| 输入 | 文字 | 文字 |
| 输出 | 文字 | 向量（数字数组） |
| 用途 | 生成回答 | 计算语义相似度 |
| 价格 | 贵 | 便宜（约1/10） |

### 2. 余弦相似度
衡量两个向量语义相似程度，范围 -1 到 1：
- 接近 1 → 语义非常相似
- 接近 0 → 语义无关
- 负数 → 语义相反

```python
import numpy as np

def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
```

**实验结果：**
```
语义相近的两句话：0.5860
语义无关的两句话：-0.0752
```

### 3. HuggingFace Embedding 模型
```python
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 国内镜像，必须加！

from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

vector = embeddings.embed_query("your text here")
print(len(vector))  # 384维
```

**注意：** `all-MiniLM-L6-v2` 是英文模型，中文检索效果差。
多语言场景用 `paraphrase-multilingual-MiniLM-L12-v2`。

### 4. Chroma 向量数据库

**创建并存储：**
```python
from langchain_community.vectorstores import Chroma

vectorstore = Chroma.from_documents(
    documents=chunks,              # 文档块列表
    embedding=embeddings,          # Embedding 模型
    persist_directory="chroma_db", # 持久化到硬盘（重要！）
)
```

**加载已有向量库：**
```python
vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings,
)
```

**语义检索：**
```python
results = vectorstore.similarity_search(query, k=3)  # 找最相关的3块

for doc in results:
    print(doc.page_content)          # 内容
    print(doc.metadata['page'] + 1)  # 来源页码（+1因为从0开始）
```

### 5. 向量数据库 vs 普通数据库

| | 普通数据库（MySQL） | 向量数据库（Chroma） |
|--|-------------------|-------------------|
| 匹配方式 | 字面精确匹配 | 语义相似匹配 |
| 查询语言 | SQL WHERE LIKE | similarity_search |
| 适合场景 | 精确查找 | 语义搜索、RAG |

**核心区别：**
> 普通数据库找"字面相同"，向量数据库找"语义相近"。
> 用户问的话和文档写的话往往不一样，RAG 必须用向量数据库。

### 6. persist_directory 的重要性
- 不设置 → 存内存，程序重启数据消失，每次重新计算
- 设置 → 存硬盘，下次直接加载，省时省钱

---

## 今天遇到的问题

### 问题1：HuggingFace 连不上
**报错：** `[WinError 10060] 连接超时`  
**原因：** HuggingFace 在国内被墙  
**解决：** 在代码最开头加：
```python
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
```

### 问题2：HuggingFaceEmbeddings 废弃警告
**警告：** `HuggingFaceEmbeddings was deprecated in LangChain 0.2.2`  
**解决：**
```bash
pip install langchain-huggingface
```
```python
from langchain_huggingface import HuggingFaceEmbeddings
```

---

## 面试考点

**Q：什么是 Embedding？为什么 RAG 需要它？**  
答：把文字转成固定维度的向量，语义相近的文字向量距离近。RAG 需要它是因为用户问的话和文档写的话往往字面不同但语义相近，只有向量才能做语义匹配。

**Q：向量数据库和普通数据库的区别？**  
答：普通数据库做字面精确匹配（LIKE），向量数据库做语义相似匹配（cosine similarity）。RAG 场景必须用向量数据库，因为用户表达和文档表达方式不同，字面匹配找不到正确内容。

**Q：余弦相似度是什么？**  
答：衡量两个向量方向的相似程度，范围-1到1。接近1表示语义非常相似，接近0表示无关，负数表示语义相反。RAG 检索时就是找余弦相似度最高的几个块。

**Q：为什么 Embedding 要持久化？**  
答：计算 Embedding 需要时间和金钱（调API的话）。持久化到硬盘后下次直接加载，不用重新计算，特别是文档量大时效果明显。

**Q：中文文档用英文 Embedding 模型会怎样？**  
答：效果很差。英文模型的向量空间是为英文优化的，中文文字的向量和英文语义不对齐，检索时中文问题找不到中文文档的相关内容。应该用多语言模型如 `paraphrase-multilingual-MiniLM-L12-v2` 或中文专用模型如 `BGE-M3`。

---

## 今日文件结构
```
day09/
├── 01_embedding.py   ✅ Embedding基础、余弦相似度验证
├── 02_chroma.py      ✅ 创建向量库、存储chunks、语义检索
├── 03_load_chroma.py ✅ 加载已有向量库、多查询测试
└── chroma_db/        ✅ 持久化的向量数据库文件
```

---

## 明天预告 — Day 10：基础 RAG 系统搭建
- 把文档加载、切分、向量库、检索全部串起来
- 加上 LLM 生成环节，完成完整问答闭环
- 实现引用溯源（回答时标注来自哪一页）
- 用 FastAPI 暴露为 API 接口