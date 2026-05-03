# Day 26 复盘笔记 — 刹车片检测 Agent

## 今天做了什么

把已有的 YOLOv8 刹车片检测系统包装成 LangGraph Agent，实现：
- 自动检测图片中的刹车片并识别型号
- 查询 SOP 处置建议
- 生成完整检测报告

---

## 系统架构

### 原有刹车片检测系统
```
输入：图片
    ↓
YOLOv8 OBB 检测 → 找到刹车片的旋转边界框
    ↓
透视变换 → 把倾斜的刹车片摆正
    ↓
ResNet50 提取特征 → 2048维向量
    ↓
FAISS 相似度搜索 → 在特征数据库里找最近邻（11928张图，75个型号）
    ↓
输出：型号ID + 置信度 + 标注后的图片
```

### Agent 架构
```
用户输入图片路径
    ↓
Agent（DeepSeek）
    ↓
工具1 detect_brake_pad → 调用 process_frame() 检测
工具2 query_sop        → 查询 SOP 处置建议
工具3 generate_report  → 生成检测报告并保存
    ↓
最终输出：检测结果 + 处置建议 + 保存报告
```

---

## 关键代码

### 目录结构
```
week4/day26/
├── models/
│   ├── brake_obb_best_20260124.pt   # OBB检测模型
│   └── feature_database.pkl         # 特征数据库（11928张，75型号）
├── src/
│   ├── BF_func.py                   # 主检测逻辑
│   └── build_match_fea.py           # 特征提取和FAISS搜索
├── results/                         # 输出目录（自动创建）
│   ├── annotated_result.jpg         # 标注后的图片
│   └── detection_report.txt         # 检测报告
├── 01_brake_agent.py                # Agent 主文件
└── 02_test_model.py                 # 模型加载测试
```

### 模型路径修改（跨目录调用关键）
```python
# BF_func.py 里的 loadmodels()
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
obb_model_path = os.path.join(base_dir, "../models/brake_obb_best_20260124.pt")
feature_database_path = os.path.join(base_dir, "../models/feature_database.pkl")
```

### 工具包装核心
```python
# 启动时只加载一次模型（不要每次调用工具都加载）
_state = loadmodels()
_system = _state['system']

@tool
def detect_brake_pad(image_path: str) -> str:
    """检测图像中的刹车片并识别型号。
    输入图像路径，返回检测到的刹车片数量、型号ID和置信度。
    
    Args:
        image_path: 图像文件的完整路径
    """
    image = cv2.imread(image_path)
    annotated, summary = process_frame(image, system=_system)
    
    # 保存标注图像
    cv2.imwrite(save_path, annotated)
    return f"{summary}\n标注图像已保存至：{save_path}"
```

---

## 今天踩到的坑

### 坑1：sys.path 要加在最前面
```python
# 必须在 import BF_func 之前加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from BF_func import loadmodels, process_frame
```

### 坑2：模型只加载一次
```python
# ❌ 错误：在工具函数里加载（每次调用都要等几十秒）
@tool
def detect_brake_pad(image_path: str) -> str:
    state = loadmodels()  # 每次都重新加载！

# ✅ 正确：启动时加载一次，工具函数直接用
_state = loadmodels()  # 启动时加载
@tool
def detect_brake_pad(image_path: str) -> str:
    annotated, summary = process_frame(image, system=_state['system'])
```

---

## 扩展方向

### 接入真实 SOP RAG
```python
# 现在是模拟数据库
sop_database = {"D1415W": "..."}

# 改成 Week 2 的 RAG 系统
from langchain_community.vectorstores import Chroma
vectorstore = Chroma(persist_directory="sop_chroma_db")

@tool
def query_sop(model_id: str) -> str:
    docs = vectorstore.similarity_search(f"型号{model_id}的处置规程", k=3)
    return "\n".join([doc.page_content for doc in docs])
```

### 接入 HIL（高风险操作确认）
```python
# 如果置信度低于阈值，触发人工确认
@tool
def detect_brake_pad(image_path: str) -> str:
    annotated, summary = process_frame(image, system=_system)
    
    if "recognition_confidence: 0.3" in summary:  # 低置信度
        decision = interrupt({"message": "置信度较低，是否继续？"})
```

### FastAPI 暴露为接口
```python
@app.post("/detect")
async def detect(image_path: str):
    result = agent.invoke({"messages": [HumanMessage(f"检测：{image_path}")]})
    return {"result": result['messages'][-1].content}
```

---

## 面试亮点

**这个项目的差异化价值：**
- 不只是调 API，把真实 CV 系统（YOLOv8+ResNet50+FAISS）包装成 Agent
- 数据库规模：11928张图，75个型号，真实工业场景
- 完整 pipeline：检测→识别→查询→报告，端到端自动化
- 可扩展：轻松接入 RAG（SOP文档）、HIL（人工确认）、LangSmith（监控）

**面试回答思路：**
> "我把公司的刹车片检测系统（YOLOv8 OBB检测+ResNet50特征匹配+FAISS检索）
> 包装成了 LangGraph Agent 工具，实现了从图片输入到检测报告输出的全自动流程。
> Agent 能自主决定调用哪些工具、以什么顺序调用，还能查询SOP文档给出处置建议。"

---

## 今日文件结构
```
week4/day26/
├── 01_brake_agent.py  ✅ 完整Agent：检测+SOP查询+报告生成
└── 02_test_model.py   ✅ 模型加载验证
```

---

## 明天预告 — Day 27：Week 4 收官
- 把 Day 26 的 Agent 接入 FastAPI
- 添加 LangSmith 追踪
- 整理代码，准备上传 GitHub
- Week 4 总结