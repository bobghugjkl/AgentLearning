import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

# ── 加载 PDF ──────────────────────────────────────────
loader = PyPDFLoader("day08/test.pdf")
pages = loader.load()

print(f"总页数：{len(pages)}")
print(f"\n第1页内容（前200字）：")
print(pages[0].page_content[:200])
print(f"\n第1页的元数据：")
print(pages[0].metadata)


# ── 简单清洗：过滤掉内容太少的页面 ──────────────────
print("\n=== 各页内容长度 ===")
for i, page in enumerate(pages):
    content = page.page_content.strip()
    print(f"第{i+1}页：{len(content)} 字符")

# 过滤掉少于100字符的页面（封面、目录等）
valid_pages = [p for p in pages if len(p.page_content.strip()) > 100]
print(f"\n过滤前：{len(pages)} 页")
print(f"过滤后：{len(valid_pages)} 页")