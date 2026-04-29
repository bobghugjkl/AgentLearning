import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# 加载 PDF
loader = PyPDFLoader("day08/test.pdf")
pages = loader.load()

# ── RecursiveCharacterTextSplitter ────────────────────
# 最常用的切分器，按层次分隔符递归切分
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 每块最大500字符
    chunk_overlap=50,    # 相邻块重叠50字符
    separators=["\n\n", "\n", ".", " ", ""],  # 按这个顺序尝试切分
)

chunks = splitter.split_documents(pages)

print(f"切分前：{len(pages)} 页")
print(f"切分后：{len(chunks)} 块")
print(f"\n第1块内容：")
print(chunks[0].page_content)
print(f"\n第1块元数据：")
print(chunks[0].metadata)

# ── 对比不同 chunk_size 的效果 ────────────────────────
print("\n=== 不同 chunk_size 对比 ===")
for size in [200, 500, 1000]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=20,
    )
    chunks = splitter.split_documents(pages)
    avg_len = sum(len(c.page_content) for c in chunks) / len(chunks)
    print(f"chunk_size={size}: {len(chunks)}块，平均{avg_len:.0f}字符/块")