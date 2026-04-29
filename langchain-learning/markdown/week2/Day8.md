# Day 08 复盘笔记 — 文档加载与文本切分

## 今天学了什么

### 1. 为什么需要 RAG
- 模型训练完知识固定，不知道私有文档/最新信息
- RAG = Retrieval（检索）+ Augmented（增强）+ Generation（生成）
- 流程：用户提问 → 检索相关文档块 → 塞给模型 → 模型回答

### 2. RAG 两个阶段
```
离线阶段（只做一次）：
文档 → 切分成小块 → 转成向量 → 存到向量数据库

在线阶段（每次问答）：
用户问题 → 转成向量 → 检索相似块 → 塞给模型 → 回答
```

### 3. PyPDFLoader 加载 PDF
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("path/to/file.pdf")
pages = loader.load()

# 每页是一个 Document 对象
page = pages[0]
print(page.page_content)  # 页面文字内容
print(page.metadata)      # 元数据
```

**metadata 包含：**
```python
{
    'source': 'day08/test.pdf',  # 文件路径
    'page': 0,                   # 页码（从0开始！）
    'page_label': '1',           # 显示页码（从1开始）
    'total_pages': 24,           # 总页数
    'author': 'Kurt Jensen',     # 作者
}
```

**注意：** `page` 从0开始，`page_label` 从1开始。

### 4. 元数据的两个用途
- **溯源：** 告诉用户"这段来自第X页"
- **过滤：** 只在特定文件里检索

### 5. 为什么要切分文档
- 模型上下文有限，整篇文档塞不进去
- 一页内容可能包含多个主题，整页检索不精准
- 切成小块 → 检索更准 + 模型更专注

### 6. RecursiveCharacterTextSplitter
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 每块最大500字符
    chunk_overlap=50,    # 相邻块重叠50字符
    separators=["\n\n", "\n", ".", " ", ""],  # 递归切分顺序
)

chunks = splitter.split_documents(pages)
```

**separators 递归逻辑：**
先按 `\n\n` 切，还是太大就按 `\n` 切，还是太大就按 `.` 切，以此类推。尽量保留语义完整性。

**chunk_overlap 的作用：**
```
块1：[===========================]
块2：                    [=============================]
                         ↑ 重叠部分保证上下文不丢失
```

### 7. chunk_size 选择
| chunk_size | 块数 | 平均字符 | 问题 |
|-----------|------|---------|------|
| 200 | 多 | 少 | 语义不完整，一句话被切断 |
| 500 | 适中 | 适中 | ✅ 推荐 |
| 1000 | 少 | 多 | 一块主题太多，检索不精准 |

**生产经验：**
- 法律/学术文档（长句）→ 600-800
- 新闻/FAQ（短句）→ 200-400
- 通用场景 → 300-500

### 8. 跨页 chunk 的元数据
跨页的 chunk 显示**起始页**的页码，以内容开始的那一页为准。

---

## 今天遇到的问题

### 问题1：langchain.text_splitter 找不到
**报错：** `No module named 'langchain.text_splitter'`  
**原因：** LangChain 1.0 把切分器移到独立包  
**解决：**
```bash
pip install langchain-text-splitters
```
```python
# 改成：
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

### 问题2：xxhash DLL 被 Windows 阻止
**报错：** `ImportError: DLL load failed while importing _xxhash`  
**原因：** Windows 应用程序控制策略阻止了 DLL  
**解决：** `pip uninstall xxhash -y && pip install xxhash`

---

## 面试考点

**Q：RAG 是什么？解决什么问题？**  
答：Retrieval-Augmented Generation，检索增强生成。解决模型不知道私有/最新知识的问题。先把文档切块存向量库，用户提问时检索相关块塞给模型，让模型基于这些内容回答。

**Q：为什么要把文档切成小块？**  
答：两个原因：一是模型上下文有限，整篇文档塞不进去；二是一页内可能有多个主题，整页检索不精准，小块语义更集中，检索更准确。

**Q：chunk_size 怎么选？**  
答：取决于文档类型和问题粒度。太小语义不完整，太大主题太杂。一般300-800，法律学术文档用600-800，FAQ用200-400。还要考虑Embedding模型的最大输入长度。

**Q：chunk_overlap 有什么用？**  
答：相邻块重叠一部分内容，防止语义在块边界处断裂。比如一句话被切成两半，重叠部分保证两个块都能理解完整意思。

**Q：RecursiveCharacterTextSplitter 的递归逻辑是什么？**  
答：按优先级尝试不同分隔符——先按双换行切（段落），还是太大就按单换行切，再按句号切，最后按空格切。尽量保留语义完整性，不到万不得已不硬切。

**Q：metadata 在 RAG 里有什么用？**  
答：两个用途：溯源（告诉用户答案来自哪个文档第几页）；过滤检索范围（只在特定文件或时间范围内检索）。

---

## 今日文件结构
```
day08/
├── test.pdf              ✅ 测试用 PDF（丹麦工业博士指南）
├── 01_load_pdf.py        ✅ PyPDFLoader、页面内容、元数据、清洗
└── 02_text_splitter.py   ✅ RecursiveCharacterTextSplitter、chunk_size对比
```

---

## 明天预告 — Day 09：Embedding 与向量数据库
- 什么是 Embedding（向量化）
- 为什么向量能表示语义相似度
- Chroma 向量数据库的使用
- 把今天的 chunks 存进向量库，做第一次语义检索