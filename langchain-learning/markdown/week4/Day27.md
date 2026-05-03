# Day 27 复盘笔记 — Week 4 收官：刹车片 Agent API

## 今天做了什么

把 Day 26 的刹车片 Agent 接入 FastAPI，加上 LangSmith 追踪，做成可部署的 HTTP 服务。

---

## API 架构

```
POST /detect
  ↓
FastAPI 接收 JSON（image_path + instruction）
  ↓
Agent（DeepSeek）
  ↓
detect_brake_pad → process_frame() → YOLOv8+ResNet50+FAISS
query_sop        → SOP 数据库查询
generate_report  → 生成报告保存文件
  ↓
返回 JSON（status + result）
```

---

## 关键代码

### 请求体定义
```python
class DetectRequest(BaseModel):
    image_path: str
    instruction: str = "检测刹车片型号，查询SOP建议，生成检测报告"
```

### 普通接口
```python
@app.post("/detect")
def detect(body: DetectRequest):
    if not os.path.exists(body.image_path):
        raise HTTPException(status_code=400, detail=f"图片不存在：{body.image_path}")
    
    result = agent.invoke({
        "messages": [HumanMessage(
            f"{body.instruction}，图片路径：{body.image_path}"
        )]
    })
    return {"status": "success", "result": result['messages'][-1].content}
```

### 流式接口
```python
@app.post("/detect/stream")
def detect_stream(body: DetectRequest):
    def generate():
        for chunk in agent.stream({"messages": [...]}):
            if "agent" in chunk:
                for msg in chunk["agent"]["messages"]:
                    if hasattr(msg, "content") and msg.content:
                        yield msg.content
    return StreamingResponse(generate(), media_type="text/plain")
```

### LangSmith 接入（两行）
```python
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "brake-pad-agent"
```

### 跨目录 sys.path 修复
```python
# day27 调用 day26 的代码，需要同时加两个路径
day26_dir = os.path.join(os.path.dirname(__file__), "../day26")
day26_src_dir = os.path.join(os.path.dirname(__file__), "../day26/src")
sys.path.insert(0, day26_dir)
sys.path.insert(0, day26_src_dir)
```

---

## 踩坑记录

### 坑：ModuleNotFoundError: No module named 'src'
**原因：** `BF_func.py` 里用了 `from src.build_match_fea import`，从 day27 目录运行时找不到 `src`。

**解决：** 同时把 `day26/` 和 `day26/src/` 都加入 `sys.path`，这样两种 import 方式都能找到。

---

## Week 4 完整回顾

| 天 | 核心内容 | 关键技术 |
|----|--------|---------|
| Day 22 | Subgraphs 子图 | 主图嵌套子图、共享State字段 |
| Day 23 | Send API 并行 | 条件边返回Send列表、operator.add防覆盖 |
| Day 24 | 长期记忆 | SQLite持久化、LLM提取关键信息 |
| Day 25 | LangSmith | 零代码追踪、@traceable自定义函数 |
| Day 26 | 刹车片Agent | YOLOv8+ResNet50+FAISS包装成工具 |
| Day 27 | FastAPI部署 | HTTP接口、流式响应、LangSmith监控 |

---

## 面试完整话术

**Q：介绍一下你的刹车片检测 Agent 项目**

> "我把公司的刹车片 CV 检测系统包装成了一个生产级 Agent 服务。
> 
> 底层是 YOLOv8 OBB 检测刹车片位置，透视变换摆正后，用 ResNet50 提取特征，FAISS 在 11928 张图的特征库（75个型号）里做相似度检索，识别型号。
> 
> 在这个基础上，我用 LangGraph 把它做成了 Agent——三个工具：detect_brake_pad 调用 CV 系统、query_sop 查处置建议、generate_report 生成报告。Agent 能自主决定调用顺序和参数。
> 
> 最后用 FastAPI 暴露成 HTTP 接口，接收图片路径返回 JSON，接入 LangSmith 追踪每次调用的 token 消耗和延迟。"

---

## 今日文件结构
```
week4/day27/
├── 01_brake_api.py  ✅ FastAPI + Agent + LangSmith
└── results/         ✅ 自动生成的检测结果
```

---

## 下周预告 — Week 5：生产化部署
- 缓存优化（减少重复 LLM 调用）
- 安全加固（API Key 管理、输入校验）
- Docker 容器化
- 性能监控与告警