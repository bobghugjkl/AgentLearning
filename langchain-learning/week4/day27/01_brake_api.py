import sys
import os

# 同时把 day26 和 day26/src 都加进去
day26_dir = os.path.join(os.path.dirname(__file__), "../day26")
day26_src_dir = os.path.join(os.path.dirname(__file__), "../day26/src")
sys.path.insert(0, day26_dir)
sys.path.insert(0, day26_src_dir)
# LangSmith 追踪（两行搞定）
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "brake-pad-agent"

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from BF_func import loadmodels, process_frame
import cv2

load_dotenv()

app = FastAPI(title="刹车片检测 Agent API")

# ── 启动时加载模型 ─────────────────────────────────
print("加载刹车片检测模型...")
_state = loadmodels()
_system = _state['system']
print("模型加载完成！")

model = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)


# ── 工具定义（和 Day 26 一样）────────────────────────
@tool
def detect_brake_pad(image_path: str) -> str:
    """检测图像中的刹车片并识别型号。
    Args:
        image_path: 图像文件的完整路径
    """
    image = cv2.imread(image_path)
    if image is None:
        return f"错误：无法读取图像 {image_path}"

    annotated, summary = process_frame(image, system=_system)

    save_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "annotated_result.jpg")
    cv2.imwrite(save_path, annotated)

    return f"{summary}\n标注图像已保存至：{save_path}"


@tool
def query_sop(model_id: str) -> str:
    """根据刹车片型号查询SOP处置建议。
    Args:
        model_id: 刹车片型号ID
    """
    sop_database = {
        "D1415W": "D1415W适用于丰田凯美瑞前轮，厚度低于3mm时立即更换。",
        "BFD3053N": "BFD3053N适用于福特F-150后轮，每30000km更换一次。",
        "DEFAULT": "未找到该型号SOP，请联系技术支持。"
    }
    return f"型号 {model_id} 的SOP：{sop_database.get(model_id, sop_database['DEFAULT'])}"


@tool
def generate_report(detection_summary: str, sop_advice: str) -> str:
    """生成完整检测报告。
    Args:
        detection_summary: 检测结果摘要
        sop_advice: SOP处置建议
    """
    from datetime import datetime
    report = f"""
========================================
        刹车片检测报告
========================================
检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
【检测结果】{detection_summary}
【处置建议】{sop_advice}
========================================
"""
    save_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "report.txt"), "w", encoding="utf-8") as f:
        f.write(report)
    return report


# ── Agent ─────────────────────────────────────────
agent = create_react_agent(model, tools=[detect_brake_pad, query_sop, generate_report])


# ── 请求体 ────────────────────────────────────────
class DetectRequest(BaseModel):
    image_path: str
    instruction: str = "检测刹车片型号，查询SOP建议，生成检测报告"


# ── 接口1：普通接口 ───────────────────────────────
@app.post("/detect")
def detect(body: DetectRequest):
    if not os.path.exists(body.image_path):
        raise HTTPException(status_code=400, detail=f"图片不存在：{body.image_path}")

    result = agent.invoke({
        "messages": [HumanMessage(
            f"{body.instruction}，图片路径：{body.image_path}"
        )]
    })

    return {
        "status": "success",
        "result": result['messages'][-1].content,
    }


# ── 接口2：流式接口 ───────────────────────────────
@app.post("/detect/stream")
def detect_stream(body: DetectRequest):
    if not os.path.exists(body.image_path):
        raise HTTPException(status_code=400, detail=f"图片不存在：{body.image_path}")

    def generate():
        for chunk in agent.stream({
            "messages": [HumanMessage(
                f"{body.instruction}，图片路径：{body.image_path}"
            )]
        }):
            # 只输出最终回答的流式内容
            if "agent" in chunk:
                for msg in chunk["agent"]["messages"]:
                    if hasattr(msg, "content") and msg.content:
                        yield msg.content

    return StreamingResponse(generate(), media_type="text/plain")


# ── 健康检查 ──────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}